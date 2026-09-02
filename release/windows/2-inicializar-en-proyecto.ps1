[CmdletBinding()]
param(
    [string]$Target = ".",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Find-SeAgent {
    $cmd = Get-Command se-agent -ErrorAction SilentlyContinue
    if ($cmd) {
        return @{ Path = $cmd.Source; FromPath = $true }
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
            return @{ Path = $candidate; FromPath = $false }
        }
    }
    return $null
}

function Resolve-TargetDirectory {
    param([string]$TargetPath)

    if (-not $TargetPath) {
        throw "Pasa -Target con la carpeta destino (por defecto '.')."
    }

    if ([System.IO.Path]::IsPathRooted($TargetPath)) {
        $full = [System.IO.Path]::GetFullPath($TargetPath)
    }
    else {
        $full = [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $TargetPath))
    }

    if (Test-Path -LiteralPath $full) {
        $item = Get-Item -LiteralPath $full -Force
        if (-not $item.PSIsContainer) {
            throw "El target existe pero no es un directorio: $full"
        }
        return $item.FullName
    }

    Write-Host "El directorio target no existe. Creandolo: $full"
    New-Item -ItemType Directory -Path $full -Force | Out-Null
    return (Resolve-Path -LiteralPath $full).Path
}

$targetPath = Resolve-TargetDirectory -TargetPath $Target
$seAgentInfo = Find-SeAgent

if (-not $seAgentInfo) {
    throw @"
No se encontro el comando se-agent.

Primero ejecuta:
  .\release\windows\1-instalar.ps1

Si ya lo ejecutaste, cerra esta terminal y abri una nueva para que Windows cargue el PATH actualizado.
"@
}

$seAgent = $seAgentInfo.Path
Write-Host "se-agent: $seAgent"
Write-Host "Target:   $targetPath"
if (-not $seAgentInfo.FromPath) {
    Write-Warning "se-agent se encontro por una ruta conocida, no por el PATH de esta terminal. El init va a correr igual. Si despues queres escribir 'se-agent' a mano, cerra esta terminal y abri una nueva."
}
Write-Host ""

$arguments = @("init", "--harness", "codex", "--target", $targetPath)
if ($Force) {
    $arguments += "--force"
}

& $seAgent @arguments
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    throw "se-agent init fallo con codigo $exitCode."
}

Write-Host ""
Write-Host "Inicializacion completada."
Write-Host "El target debe tener AGENTS.md, marco/, catalogo/, .agents/ y .codex/. proyecto/ no se toca."
Write-Host "Abrir Codex en el proyecto target para usar el framework instalado."
