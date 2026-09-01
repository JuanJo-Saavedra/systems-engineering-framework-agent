[CmdletBinding()]
param(
    [string]$Version,
    [string]$OutputDir = "dist",
    [string]$ZipName,
    [string]$SourceRoot
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Get-RepoRoot {
    if ($SourceRoot) {
        if (-not (Test-Path -LiteralPath $SourceRoot)) {
            throw "No existe -SourceRoot: $SourceRoot"
        }
        return (Resolve-Path -LiteralPath $SourceRoot).Path
    }
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
}

function Get-ProjectVersion {
    param([string]$RepoRoot)
    if ($Version) {
        return $Version
    }

    $pyproject = Join-Path $RepoRoot "pyproject.toml"
    $versionLine = Select-String -LiteralPath $pyproject -Pattern '^\s*version\s*=\s*"([^"]+)"' | Select-Object -First 1
    if (-not $versionLine) {
        throw "No se pudo leer version desde pyproject.toml. Pasa -Version."
    }
    return $versionLine.Matches[0].Groups[1].Value
}

function Convert-RelPath {
    param([string]$RelativePath)
    return ($RelativePath -replace "\\", "/").Trim("/")
}

function Test-ShouldSkip {
    param(
        [string]$RelativePath,
        [string]$Name
    )

    $normalized = Convert-RelPath $RelativePath
    if (-not $normalized) {
        return $false
    }

    if ($normalized -eq ".git" -or $normalized.StartsWith(".git/")) { return $true }
    if ($normalized -eq "dist" -or $normalized.StartsWith("dist/")) { return $true }
    if ($normalized -eq "build" -or $normalized.StartsWith("build/")) { return $true }
    if ($normalized -eq "tmp" -or $normalized.StartsWith("tmp/")) { return $true }
    if ($normalized -eq ".venv" -or $normalized.StartsWith(".venv/")) { return $true }
    if ($normalized -eq ".pytest_cache" -or $normalized.StartsWith(".pytest_cache/")) { return $true }
    if ($Name -like "*.egg-info") { return $true }
    if ($normalized -like "*.egg-info/*") { return $true }
    if ($Name -eq "__pycache__") { return $true }
    if ($normalized -like "*/__pycache__/*") { return $true }
    if ($Name -like "*.pyc" -or $Name -like "*.pyo") { return $true }
    return $false
}

function Test-IsReparse {
    param([string]$Path)
    try {
        $attrs = [System.IO.File]::GetAttributes($Path)
        return ($attrs -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
    }
    catch {
        return $false
    }
}

function Copy-MvpTree {
    param(
        [string]$SourceRoot,
        [string]$DestinationRoot
    )

    $copiedFiles = 0
    $skippedReparseDirs = 0
    $queue = New-Object System.Collections.Generic.Queue[hashtable]
    $queue.Enqueue(@{ Abs = $SourceRoot; Rel = "" })

    while ($queue.Count -gt 0) {
        $current = $queue.Dequeue()
        try {
            $entries = [System.IO.Directory]::EnumerateFileSystemEntries($current.Abs)
        }
        catch {
            Write-Warning "No se pudo leer directorio: $($current.Abs)"
            continue
        }

        foreach ($entry in $entries) {
            $name = [System.IO.Path]::GetFileName($entry)
            $rel = if ($current.Rel) { Join-Path $current.Rel $name } else { $name }
            $relNorm = Convert-RelPath $rel

            if (Test-ShouldSkip -RelativePath $relNorm -Name $name) {
                continue
            }

            $attrs = [System.IO.FileAttributes]0
            try {
                $attrs = [System.IO.File]::GetAttributes($entry)
            }
            catch {
                Write-Warning "No se pudieron leer atributos: $relNorm"
                continue
            }

            $isReparse = ($attrs -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
            $isDirectory = ($attrs -band [System.IO.FileAttributes]::Directory) -ne 0

            if ($isReparse -and $isDirectory) {
                Write-Warning "Omitiendo carpeta reparse (junction/OneDrive placeholder): $relNorm"
                $skippedReparseDirs++
                continue
            }

            $destination = Join-Path $DestinationRoot $rel

            if ($isDirectory) {
                New-Item -ItemType Directory -Force -Path $destination | Out-Null
                $queue.Enqueue(@{ Abs = $entry; Rel = $rel })
                continue
            }

            $destDir = Split-Path -Parent $destination
            New-Item -ItemType Directory -Force -Path $destDir | Out-Null

            try {
                if ($isReparse) {
                    $bytes = [System.IO.File]::ReadAllBytes($entry)
                    [System.IO.File]::WriteAllBytes($destination, $bytes)
                }
                else {
                    [System.IO.File]::Copy($entry, $destination, $true)
                }
            }
            catch {
                throw "No se pudo copiar contenido real de '$relNorm': $($_.Exception.Message)"
            }

            $copied = Get-Item -LiteralPath $destination -Force
            if ($copied.Length -lt 0) {
                throw "Copia invalida (tamano negativo): $relNorm"
            }
            $copiedFiles++
        }
    }

    return @{ Files = $copiedFiles; SkippedReparseDirs = $skippedReparseDirs }
}

function Assert-RequiredFile {
    param(
        [string]$Root,
        [string]$RelativePath,
        [switch]$AllowEmpty
    )
    $path = Join-Path $Root ($RelativePath -replace "/", "\")
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Falta archivo requerido en el staging: $RelativePath"
    }
    $item = Get-Item -LiteralPath $path -Force
    if ($item.PSIsContainer) {
        throw "Se esperaba un archivo y hay un directorio: $RelativePath"
    }
    if (-not $AllowEmpty -and $item.Length -le 0) {
        throw "Archivo requerido vacio (posible placeholder OneDrive): $RelativePath"
    }
    return $item.Length
}

function Assert-RequiredTree {
    param(
        [string]$Root,
        [string]$RelativePath
    )
    $path = Join-Path $Root ($RelativePath -replace "/", "\")
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Falta directorio requerido en el staging: $RelativePath"
    }
    $files = Get-ChildItem -LiteralPath $path -Recurse -File -Force -ErrorAction SilentlyContinue
    $nonzero = @($files | Where-Object { $_.Length -gt 0 })
    if ($nonzero.Count -eq 0) {
        throw "Directorio requerido sin archivos con tamano > 0: $RelativePath"
    }
    return $nonzero.Count
}

function Assert-StagedPayload {
    param([string]$StagePackage)

    $requiredFiles = @(
        "pyproject.toml",
        "README-INSTALACION.md",
        "src/se_agent/__init__.py",
        "src/se_agent/cli.py",
        "src/se_agent/_payload/AGENTS.md",
        "src/se_agent/_payload/marco/README.md",
        "src/se_agent/_payload/catalogo/skill-registry.md",
        "src/se_agent/_payload/.agents/skills/f0_factibilidad/SKILL.md",
        "src/se_agent/_payload/.codex/config.toml",
        "release/windows/1-instalar.ps1",
        "release/windows/2-inicializar-en-proyecto.ps1",
        "release/windows/crear-zip-mvp.ps1",
        "docs/guides/instalacion-mvp-veng.md"
    )

    Write-Host "Validando staging..."
    foreach ($rel in $requiredFiles) {
        $size = Assert-RequiredFile -Root $StagePackage -RelativePath $rel
        Write-Host ("  OK {0,-72} {1,8} bytes" -f $rel, $size)
    }

    $payloadCount = Assert-RequiredTree -Root $StagePackage -RelativePath "src/se_agent/_payload"
    Write-Host "  OK src/se_agent/_payload/ ($payloadCount archivos con tamano > 0)"

    $emptyPayload = @(Get-ChildItem -LiteralPath (Join-Path $StagePackage "src\se_agent\_payload") -Recurse -File -Force |
        Where-Object { $_.Length -le 0 })
    if ($emptyPayload.Count -gt 0) {
        $names = ($emptyPayload | ForEach-Object { $_.FullName.Substring($StagePackage.Length) }) -join ", "
        throw "Payload con archivos vacios (no se empaqueta): $names"
    }
}

function Assert-ZipPayload {
    param(
        [string]$ZipPath,
        [string]$FolderName
    )

    $required = @(
        "$FolderName/pyproject.toml",
        "$FolderName/README-INSTALACION.md",
        "$FolderName/src/se_agent/__init__.py",
        "$FolderName/src/se_agent/_payload/AGENTS.md",
        "$FolderName/src/se_agent/_payload/.agents/skills/f0_factibilidad/SKILL.md",
        "$FolderName/src/se_agent/_payload/.codex/config.toml",
        "$FolderName/release/windows/1-instalar.ps1",
        "$FolderName/release/windows/2-inicializar-en-proyecto.ps1"
    )

    $zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        $entries = @{}
        foreach ($entry in $zip.Entries) {
            $name = $entry.FullName -replace "\\", "/"
            $entries[$name] = $entry.Length
        }

        Write-Host "Validando ZIP ($($entries.Count) entradas)..."
        foreach ($rel in $required) {
            if (-not $entries.ContainsKey($rel)) {
                throw "El ZIP no contiene: $rel"
            }
            if ($entries[$rel] -le 0) {
                throw "El ZIP tiene entrada vacia: $rel"
            }
            Write-Host ("  OK {0,-72} {1,8} bytes" -f $rel, $entries[$rel])
        }

        $payloadEntries = @($entries.Keys | Where-Object { $_ -like "$FolderName/src/se_agent/_payload/*" -and $_ -notlike "*/" })
        $payloadNonEmpty = @($payloadEntries | Where-Object { $entries[$_] -gt 0 })
        if ($payloadNonEmpty.Count -eq 0) {
            throw "El ZIP no tiene archivos reales en src/se_agent/_payload/"
        }
        Write-Host "  OK payload en ZIP: $($payloadNonEmpty.Count) archivos con tamano > 0"
    }
    finally {
        $zip.Dispose()
    }
}

$repoRoot = Get-RepoRoot
$projectVersion = Get-ProjectVersion -RepoRoot $repoRoot
$folderName = "se-agent-mvp-$projectVersion"

if (-not $ZipName) {
    $ZipName = "$folderName.zip"
}

if ([System.IO.Path]::IsPathRooted($OutputDir)) {
    $outputPath = $OutputDir
}
else {
    $outputPath = Join-Path $repoRoot $OutputDir
}

New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

$stageRoot = Join-Path $repoRoot "dist\mvp-stage"
$stagePackage = Join-Path $stageRoot $folderName
$zipPath = Join-Path $outputPath $ZipName

if (Test-Path -LiteralPath $stageRoot) {
    Remove-Item -LiteralPath $stageRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $stagePackage | Out-Null

Write-Host "Origen:   $repoRoot"
Write-Host "Staging:  $stagePackage"
Write-Host "Copiando contenido real (sin seguir reparse/junctions)..."
$copyStats = Copy-MvpTree -SourceRoot $repoRoot -DestinationRoot $stagePackage
Write-Host "Archivos copiados: $($copyStats.Files)"
if ($copyStats.SkippedReparseDirs -gt 0) {
    Write-Warning "Se omitieron $($copyStats.SkippedReparseDirs) carpetas reparse."
}

Assert-StagedPayload -StagePackage $stagePackage

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

Write-Host "Creando ZIP: $zipPath"
# includeBaseDirectory=true deja se-agent-mvp-<version>/ como raiz del ZIP.
# Al descomprimir, 1-instalar.ps1 resuelve pyproject.toml dos niveles arriba de release/windows.
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    $stagePackage,
    $zipPath,
    [System.IO.Compression.CompressionLevel]::Optimal,
    $true
)

Assert-ZipPayload -ZipPath $zipPath -FolderName $folderName

$zipItem = Get-Item -LiteralPath $zipPath
Write-Host ""
Write-Host "ZIP MVP creado:"
Write-Host "  $zipPath"
Write-Host ("  tamano: {0:N0} bytes" -f $zipItem.Length)
Write-Host ""
Write-Host "Prueba de usuario:"
Write-Host "  1. Descomprimir el ZIP (queda la carpeta $folderName con pyproject.toml adentro)."
Write-Host "  2. Entrar a esa carpeta y ejecutar .\release\windows\1-instalar.ps1"
Write-Host "  3. Si el instalador pide terminal nueva, cerrar y abrir otra."
Write-Host "  4. Ejecutar .\release\windows\2-inicializar-en-proyecto.ps1 -Target <proyecto>"
