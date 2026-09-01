[CmdletBinding()]
param(
    [string]$PackageSource,
    [string]$PythonCommand,
    [switch]$SkipEnsurePath
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Get-SessionPathEntries {
    @($env:PATH -split ";" | ForEach-Object { $_.Trim().TrimEnd("\") } | Where-Object { $_ })
}

function Get-PersistentPathEntries {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    @(($machine + ";" + $user) -split ";" | ForEach-Object { $_.Trim().TrimEnd("\") } | Where-Object { $_ })
}

function Update-SessionPathFromPersistent {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($machine -and $user) {
        $env:PATH = "$machine;$user"
    }
    elseif ($user) {
        $env:PATH = $user
    }
    elseif ($machine) {
        $env:PATH = $machine
    }
}

function Get-PipxBinDirs {
    @(
        (Join-Path $env:USERPROFILE ".local\bin"),
        (Join-Path $env:APPDATA "Python\Python312\Scripts"),
        (Join-Path $env:APPDATA "Python\Python313\Scripts")
    )
}

function Test-PathListContainsDir {
    param(
        [string[]]$Entries,
        [string]$Directory
    )
    $normalized = $Directory.Trim().TrimEnd("\")
    foreach ($entry in $Entries) {
        if ($entry -ieq $normalized) {
            return $true
        }
    }
    return $false
}

function Resolve-RepoRoot {
    if ($PackageSource) {
        if (-not (Test-Path -LiteralPath $PackageSource)) {
            throw "No existe -PackageSource: $PackageSource"
        }
        return (Resolve-Path -LiteralPath $PackageSource).Path
    }
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
}

function Invoke-Python {
    param(
        [string[]]$Arguments,
        [switch]$AllowFailure
    )

    if (-not $script:PythonInvocation) {
        throw "Python no fue detectado."
    }

    $command = $script:PythonInvocation[0]
    $prefix = @()
    if ($script:PythonInvocation.Count -gt 1) {
        $prefix = $script:PythonInvocation[1..($script:PythonInvocation.Count - 1)]
    }

    & $command @prefix @Arguments
    $exitCode = $LASTEXITCODE
    if (-not $AllowFailure -and $exitCode -ne 0) {
        throw "Fallo comando Python: $command $($prefix -join ' ') $($Arguments -join ' ')"
    }
    return $exitCode
}

function Get-PythonVersionText {
    param([string[]]$Invocation)
    try {
        $command = Get-Command $Invocation[0] -ErrorAction Stop
        $prefix = @()
        if ($Invocation.Count -gt 1) {
            $prefix = $Invocation[1..($Invocation.Count - 1)]
        }
        $output = & $command.Source @prefix --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            return $null
        }
        return ($output | Select-Object -First 1).ToString()
    }
    catch {
        return $null
    }
}

function Test-Python312 {
    param([string]$VersionText)
    if ($VersionText -match "Python\s+(\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        return ($major -gt 3) -or ($major -eq 3 -and $minor -ge 12)
    }
    return $false
}

function Find-Python {
    if ($PythonCommand) {
        $parts = @($PythonCommand -split "\s+" | Where-Object { $_ })
        $versionText = Get-PythonVersionText -Invocation $parts
        if (-not $versionText -or -not (Test-Python312 $versionText)) {
            throw "El comando Python indicado no es Python >= 3.12: $PythonCommand"
        }
        Write-Host "Python detectado: $versionText ($PythonCommand)"
        return $parts
    }

    $candidates = @(
        @("py", "-3.12"),
        @("python")
    )

    foreach ($candidate in $candidates) {
        $versionText = Get-PythonVersionText -Invocation $candidate
        if ($versionText -and (Test-Python312 $versionText)) {
            Write-Host "Python detectado: $versionText"
            return $candidate
        }
    }

    throw "No se encontro Python >= 3.12. Instala Python 3.12 y volve a ejecutar este script."
}

function Find-SeAgent {
    $cmd = Get-Command se-agent -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $candidates = @(
        (Join-Path $env:USERPROFILE ".local\bin\se-agent.exe"),
        (Join-Path $env:USERPROFILE ".local\bin\se-agent"),
        (Join-Path $env:APPDATA "Python\Python312\Scripts\se-agent.exe"),
        (Join-Path $env:APPDATA "Python\Python313\Scripts\se-agent.exe"),
        (Join-Path $env:USERPROFILE ".local\pipx\venvs\se-agent\Scripts\se-agent.exe")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }
    return $null
}

$repoRoot = Resolve-RepoRoot
$sessionPathAtStart = Get-SessionPathEntries
$persistentPathBefore = Get-PersistentPathEntries
$pipxBinDirs = Get-PipxBinDirs

Write-Step "Verificando paquete local"
if (-not (Test-Path -LiteralPath (Join-Path $repoRoot "pyproject.toml"))) {
    throw "No se encontro pyproject.toml en $repoRoot. Entra a la carpeta descomprimida (la que tiene pyproject.toml) o pasa -PackageSource."
}
Write-Host "Paquete: $repoRoot"

Write-Step "Verificando Python"
$script:PythonInvocation = Find-Python

Write-Step "Verificando pipx"
$pipShowArgs = @("-m", "pip", "show", "pipx")
$command = $script:PythonInvocation[0]
$prefix = @()
if ($script:PythonInvocation.Count -gt 1) {
    $prefix = $script:PythonInvocation[1..($script:PythonInvocation.Count - 1)]
}
& $command @prefix @pipShowArgs 1>$null 2>$null
$pipxInstalled = $LASTEXITCODE -eq 0
$pipxNewlyInstalled = $false
if (-not $pipxInstalled) {
    Write-Host "pipx no esta instalado. Instalando en el perfil del usuario..."
    Invoke-Python -Arguments @("-m", "pip", "install", "--user", "pipx") | Out-Null
    $pipxNewlyInstalled = $true
}
else {
    Write-Host "pipx ya esta instalado."
}

$ensurePathRan = $false
if (-not $SkipEnsurePath) {
    Write-Step "Asegurando PATH de pipx"
    Invoke-Python -Arguments @("-m", "pipx", "ensurepath") | Out-Null
    $ensurePathRan = $true
}

Update-SessionPathFromPersistent
foreach ($binDir in $pipxBinDirs) {
    if ((Test-Path -LiteralPath $binDir) -and -not (Test-PathListContainsDir -Entries (Get-SessionPathEntries) -Directory $binDir)) {
        $env:PATH = "$binDir;$env:PATH"
    }
}

Write-Step "Instalando se-agent con pipx desde el paquete local"
Invoke-Python -Arguments @("-m", "pipx", "install", "--force", $repoRoot) | Out-Null

Write-Step "Verificando se-agent"
$seAgent = Find-SeAgent
$seAgentOnPath = [bool](Get-Command se-agent -ErrorAction SilentlyContinue)
if ($seAgent) {
    & $seAgent --version
    if ($LASTEXITCODE -ne 0) {
        throw "se-agent fue encontrado pero no pudo imprimir version: $seAgent"
    }
    Write-Host "se-agent: $seAgent"
    Write-Host "Instalacion completada."
}
else {
    Write-Warning "pipx termino, pero no se encontro se-agent.exe. Abri una terminal nueva y prueba 'se-agent --version'."
}

$persistentPathAfter = Get-PersistentPathEntries
$userPathChanged = Compare-Object $persistentPathBefore $persistentPathAfter | Where-Object { $_.SideIndicator -eq "=>" }
$sessionMissingPipxBin = $false
foreach ($binDir in $pipxBinDirs) {
    $inPersistent = Test-PathListContainsDir -Entries $persistentPathAfter -Directory $binDir
    $inSessionAtStart = Test-PathListContainsDir -Entries $sessionPathAtStart -Directory $binDir
    if ($inPersistent -and -not $inSessionAtStart) {
        $sessionMissingPipxBin = $true
    }
}

$restartReasons = @()
if ($pipxNewlyInstalled) {
    $restartReasons += "se instalo pipx en esta corrida"
}
if ($ensurePathRan -and $userPathChanged) {
    $restartReasons += "pipx ensurepath actualizo el PATH persistente de Windows"
}
if ($sessionMissingPipxBin) {
    $restartReasons += "esta terminal no tenia el directorio de pipx en PATH (Windows no lo refresca en la misma sesion)"
}
if (-not $seAgentOnPath) {
    $restartReasons += "el comando se-agent no queda en el PATH de esta sesion"
}

$initHint = Join-Path $repoRoot "release\windows\2-inicializar-en-proyecto.ps1"

Write-Host ""
if ($restartReasons.Count -gt 0) {
    Write-Host "================================================================" -ForegroundColor Yellow
    Write-Host " ACCION OBLIGATORIA: cerra ESTA terminal y abri una NUEVA." -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow
    Write-Host "Motivo: $($restartReasons -join '; ')."
    Write-Host "Windows no refresca el PATH en la misma sesion. Si seguis aca,"
    Write-Host "el comando se-agent puede no encontrarse (aunque la instalacion haya andado)."
    Write-Host ""
    Write-Host "En la terminal NUEVA, en tu proyecto consumidor:"
    Write-Host "  $initHint -Target ."
}
else {
    Write-Host "pipx y el PATH ya estaban en esta sesion. Podes seguir aca."
    Write-Host "Siguiente paso, en tu proyecto consumidor:"
    Write-Host "  $initHint -Target ."
}
