[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Prepare', 'Submit', 'RecordDecision', 'Promote', 'Validate')]
    [string]$Operation,

    [Parameter(Mandatory = $true)]
    [string]$RequestPath
)

# This backend intentionally uses only Windows PowerShell 5.1 and the .NET framework.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:Utf8 = New-Object System.Text.UTF8Encoding($false)
$script:Utf8Strict = New-Object System.Text.UTF8Encoding($false, $true)
$script:ObservedState = $null
$script:ObservedPackagePath = $null

function Write-Result([bool]$Ok, [string]$Message) {
    $errors = @()
    if (-not $Ok) { $errors = @($Message) }
    $result = [ordered]@{
        ok = $Ok
        operation = $Operation
        blocked = (-not $Ok)
        state = $script:ObservedState
        errors = $errors
    }
    if ($null -ne $script:ObservedPackagePath) { $result.package_path = $script:ObservedPackagePath }
    $bytes = $script:Utf8.GetBytes((ConvertTo-CanonicalJson $result))
    $stream = [Console]::OpenStandardOutput()
    try { $stream.Write($bytes, 0, $bytes.Length) }
    finally { $stream.Dispose() }
    if ($Ok) { exit 0 }
    exit 1
}

function Stop-Blocked([string]$Message) { throw [System.InvalidOperationException]::new($Message) }
function Assert-That([bool]$Condition, [string]$Message) { if (-not $Condition) { Stop-Blocked $Message } }

function ConvertTo-JsonString([string]$Value) {
    $builder = New-Object System.Text.StringBuilder
    [void]$builder.Append('"')
    foreach ($character in $Value.ToCharArray()) {
        $code = [int][char]$character
        switch ($code) {
            34 { [void]$builder.Append('\"'); break }
            92 { [void]$builder.Append('\\'); break }
            8 { [void]$builder.Append('\b'); break }
            9 { [void]$builder.Append('\t'); break }
            10 { [void]$builder.Append('\n'); break }
            12 { [void]$builder.Append('\f'); break }
            13 { [void]$builder.Append('\r'); break }
            default {
                if ($code -lt 32) { [void]$builder.Append(('\u{0:x4}' -f $code)) }
                else { [void]$builder.Append($character) }
            }
        }
    }
    [void]$builder.Append('"')
    return $builder.ToString()
}

function ConvertTo-CanonicalJson($Value, [int]$Depth = 0) {
    $indent = (' ' * (2 * $Depth))
    $nextIndent = (' ' * (2 * ($Depth + 1)))
    if ($null -eq $Value) { return 'null' }
    if ($Value -is [bool]) { if ($Value) { return 'true' }; return 'false' }
    if ($Value -is [string]) { return ConvertTo-JsonString $Value }
    if ($Value -is [System.Collections.IDictionary]) {
        $keys = @($Value.Keys)
        if ($keys.Count -eq 0) { return '{}' }
        $lines = @()
        foreach ($key in $keys) {
            $lines += $nextIndent + (ConvertTo-JsonString ([string]$key)) + ': ' + (ConvertTo-CanonicalJson $Value[$key] ($Depth + 1))
        }
        return "{`n" + ($lines -join ",`n") + "`n$indent}"
    }
    if ($Value -is [pscustomobject]) {
        $properties = @($Value.PSObject.Properties)
        if ($properties.Count -eq 0) { return '{}' }
        $lines = @()
        foreach ($property in $properties) {
            $lines += $nextIndent + (ConvertTo-JsonString $property.Name) + ': ' + (ConvertTo-CanonicalJson $property.Value ($Depth + 1))
        }
        return "{`n" + ($lines -join ",`n") + "`n$indent}"
    }
    if (($Value -is [System.Collections.IEnumerable]) -and -not ($Value -is [string])) {
        $items = @($Value)
        if ($items.Count -eq 0) { return '[]' }
        $lines = @()
        foreach ($item in $items) { $lines += $nextIndent + (ConvertTo-CanonicalJson $item ($Depth + 1)) }
        return "[`n" + ($lines -join ",`n") + "`n$indent]"
    }
    if ($Value -is [System.IFormattable]) { return $Value.ToString($null, [Globalization.CultureInfo]::InvariantCulture) }
    Stop-Blocked 'A value could not be represented as canonical JSON.'
}

# ConvertFrom-Json does not expose duplicate object member names.  This small scanner
# only rejects duplicate names; ConvertFrom-Json remains the JSON parser used for data.
function Skip-JsonWhitespace([string]$Text, [ref]$Index) {
    while ($Index.Value -lt $Text.Length -and [char]::IsWhiteSpace($Text[$Index.Value])) { $Index.Value++ }
}
function Read-JsonStringForScan([string]$Text, [ref]$Index) {
    Assert-That ($Text[$Index.Value] -eq '"') 'Malformed JSON string.'
    $Index.Value++
    $builder = New-Object System.Text.StringBuilder
    while ($Index.Value -lt $Text.Length) {
        $character = $Text[$Index.Value]
        $Index.Value++
        if ($character -eq '"') { return $builder.ToString() }
        if ($character -eq '\') {
            Assert-That ($Index.Value -lt $Text.Length) 'Malformed JSON escape.'
            $escape = $Text[$Index.Value]
            $Index.Value++
            switch ($escape) {
                '"' { [void]$builder.Append('"') }
                '\' { [void]$builder.Append('\') }
                '/' { [void]$builder.Append('/') }
                'b' { [void]$builder.Append([char]8) }
                'f' { [void]$builder.Append([char]12) }
                'n' { [void]$builder.Append([char]10) }
                'r' { [void]$builder.Append([char]13) }
                't' { [void]$builder.Append([char]9) }
                'u' {
                    Assert-That (($Index.Value + 4) -le $Text.Length) 'Malformed JSON unicode escape.'
                    $hex = $Text.Substring($Index.Value, 4)
                    Assert-That ($hex -match '^[0-9a-fA-F]{4}$') 'Malformed JSON unicode escape.'
                    [void]$builder.Append([char][Convert]::ToInt32($hex, 16))
                    $Index.Value += 4
                }
                default { Stop-Blocked 'Malformed JSON escape.' }
            }
        }
        else {
            Assert-That ([int][char]$character -ge 32) 'JSON strings cannot contain control characters.'
            [void]$builder.Append($character)
        }
    }
    Stop-Blocked 'Unterminated JSON string.'
}
function Scan-JsonValue([string]$Text, [ref]$Index) {
    Skip-JsonWhitespace $Text $Index
    Assert-That ($Index.Value -lt $Text.Length) 'Unexpected end of JSON.'
    $character = $Text[$Index.Value]
    if ($character -eq '"') { [void](Read-JsonStringForScan $Text $Index); return }
    if ($character -eq '{') {
        $Index.Value++
        $names = @{}
        Skip-JsonWhitespace $Text $Index
        if ($Index.Value -lt $Text.Length -and $Text[$Index.Value] -eq '}') { $Index.Value++; return }
        while ($true) {
            Skip-JsonWhitespace $Text $Index
            $name = Read-JsonStringForScan $Text $Index
            Assert-That (-not $names.ContainsKey($name)) "JSON contains duplicate key '$name'."
            $names[$name] = $true
            Skip-JsonWhitespace $Text $Index
            Assert-That ($Index.Value -lt $Text.Length -and $Text[$Index.Value] -eq ':') 'JSON object lacks a colon.'
            $Index.Value++
            Scan-JsonValue $Text $Index
            Skip-JsonWhitespace $Text $Index
            Assert-That ($Index.Value -lt $Text.Length) 'Unterminated JSON object.'
            if ($Text[$Index.Value] -eq '}') { $Index.Value++; return }
            Assert-That ($Text[$Index.Value] -eq ',') 'JSON object lacks a comma.'
            $Index.Value++
        }
    }
    if ($character -eq '[') {
        $Index.Value++
        Skip-JsonWhitespace $Text $Index
        if ($Index.Value -lt $Text.Length -and $Text[$Index.Value] -eq ']') { $Index.Value++; return }
        while ($true) {
            Scan-JsonValue $Text $Index
            Skip-JsonWhitespace $Text $Index
            Assert-That ($Index.Value -lt $Text.Length) 'Unterminated JSON array.'
            if ($Text[$Index.Value] -eq ']') { $Index.Value++; return }
            Assert-That ($Text[$Index.Value] -eq ',') 'JSON array lacks a comma.'
            $Index.Value++
        }
    }
    while ($Index.Value -lt $Text.Length -and $Text[$Index.Value] -notmatch '[\s,\]\}]') { $Index.Value++ }
}
function Assert-NoDuplicateJsonKeys([string]$Text) {
    $index = 0
    Scan-JsonValue $Text ([ref]$index)
    Skip-JsonWhitespace $Text ([ref]$index)
    Assert-That ($index -eq $Text.Length) 'JSON has trailing content.'
}

function Assert-Keys($Object, [string[]]$Expected, [string]$Label) {
    Assert-That ($null -ne $Object -and $Object -is [pscustomobject]) "$Label must be an object."
    $actual = @($Object.PSObject.Properties | ForEach-Object { $_.Name })
    Assert-That (($actual -join '|') -ceq ($Expected -join '|')) "$Label has missing, unknown, duplicate, or unordered keys."
}
function Test-Array($Value) { return (($Value -is [System.Collections.IEnumerable]) -and -not ($Value -is [string]) -and -not ($Value -is [pscustomobject])) }
function Assert-String($Value, [string]$Label) {
    Assert-That ($Value -is [string]) "$Label must be a string."
    Assert-That (-not [string]::IsNullOrEmpty($Value) -and $Value.IndexOf([char]0) -lt 0 -and $Value.IndexOf("`n") -lt 0 -and $Value.IndexOf("`r") -lt 0) "$Label must be a nonempty one-line string."
}
function Assert-Integer($Value, [string]$Label) {
    Assert-That (($Value -is [int]) -or ($Value -is [long])) "$Label must be an integer."
}
function Assert-IsoDate([string]$Value, [string]$Label) {
    Assert-String $Value $Label
    Assert-That ($Value -match '(Z|[+-][0-9]{2}:[0-9]{2})$') "$Label must include an explicit time zone."
    $parsed = [DateTimeOffset]::MinValue
    Assert-That ([DateTimeOffset]::TryParse($Value, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind, [ref]$parsed)) "$Label must be ISO 8601."
}
function Assert-RelativePath([string]$Value, [string]$Label) {
    Assert-String $Value $Label
    Assert-That ($Value.IndexOf('\') -lt 0 -and -not [IO.Path]::IsPathRooted($Value) -and $Value -notmatch '^[A-Za-z]:' -and -not $Value.StartsWith('/')) "$Label must be a slash-separated relative path."
    $segments = @($Value.Split('/'))
    foreach ($segment in $segments) {
        Assert-That (-not [string]::IsNullOrEmpty($segment) -and $segment -ne '.' -and $segment -ne '..') "$Label contains traversal or an empty segment."
        Assert-That ($segment.IndexOf(':') -lt 0) "$Label cannot contain colon or ADS syntax."
        Assert-That ($segment.IndexOfAny([IO.Path]::GetInvalidFileNameChars()) -lt 0) "$Label contains an invalid Windows filename character."
        Assert-That (-not ($segment.EndsWith('.') -or $segment.EndsWith(' '))) "$Label contains a segment with a trailing dot or space."
        $dot = $segment.IndexOf('.')
        $baseName = if ($dot -lt 0) { $segment } else { $segment.Substring(0, $dot) }
        Assert-That (-not ($baseName.ToUpperInvariant() -match '^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$')) "$Label contains a reserved DOS device name."
    }
    return $segments
}
function Test-Reparse([string]$Path) {
    return (([IO.File]::GetAttributes($Path) -band [IO.FileAttributes]::ReparsePoint) -ne 0)
}
function Assert-SafeRoot([string]$Root) {
    Assert-String $Root 'project_root'
    # Reject UNC and device spellings before normalization, which can otherwise hide them.
    # This is equivalent to a Path.GetDirectoryName ancestor walk, but proceeds downward from Path.GetPathRoot.
    Assert-That (-not $Root.StartsWith('\\?\', [StringComparison]::Ordinal)) 'project_root cannot use the \\?\ device path prefix.'
    Assert-That (-not $Root.StartsWith('\\.\', [StringComparison]::Ordinal)) 'project_root cannot use the \\.\ device path prefix.'
    Assert-That (-not $Root.StartsWith('\\', [StringComparison]::Ordinal)) 'project_root cannot be a UNC path.'
    Assert-That ($Root -match '^[A-Za-z]:[\\/]') 'project_root must be an absolute local Windows volume path.'
    Assert-That ([IO.Directory]::Exists($Root)) 'project_root must be an existing absolute directory.'
    $full = [IO.Path]::GetFullPath($Root)
    $volumeRoot = [IO.Path]::GetPathRoot($full)
    Assert-That (-not [string]::IsNullOrEmpty($volumeRoot) -and $volumeRoot -match '^[A-Za-z]:[\\/]$') 'project_root must resolve to a local Windows volume.'
    if ($full.Length -gt $volumeRoot.Length) { $full = $full.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar) }
    $current = $volumeRoot
    Assert-That (-not (Test-Reparse $current)) 'project_root has a reparse-point volume ancestor.'
    $tail = $full.Substring($volumeRoot.Length)
    foreach ($part in @($tail -split '[\\/]' | Where-Object { -not [string]::IsNullOrEmpty($_) })) {
        $current = [IO.Path]::Combine($current, $part)
        Assert-That (-not (Test-Reparse $current)) 'project_root has a reparse-point ancestor or final directory.'
    }
    return $full
}
function Open-ScopeLock([string]$Root, [string]$Scope) {
    $checkedRoot = Assert-SafeRoot $Root
    $project = Resolve-SafePath $checkedRoot 'proyecto' $false $false
    if (-not [IO.Directory]::Exists($project)) { [IO.Directory]::CreateDirectory($project) | Out-Null }
    Assert-That ([IO.Directory]::Exists($project) -and -not (Test-Reparse $project)) 'Lock infrastructure project directory is unsafe.'
    $verification = Resolve-SafePath $checkedRoot 'proyecto/docs-verificacion' $false $false
    if (-not [IO.Directory]::Exists($verification)) { [IO.Directory]::CreateDirectory($verification) | Out-Null }
    Assert-That ([IO.Directory]::Exists($verification) -and -not (Test-Reparse $verification)) 'Lock infrastructure verification directory is unsafe.'
    $scopePath = Resolve-SafePath $checkedRoot ('proyecto/docs-verificacion/' + $Scope) $false $false
    if (-not [IO.Directory]::Exists($scopePath)) { [IO.Directory]::CreateDirectory($scopePath) | Out-Null }
    Assert-That ([IO.Directory]::Exists($scopePath) -and -not (Test-Reparse $scopePath)) 'Lock infrastructure scope directory is unsafe.'
    $lockPath = [IO.Path]::Combine($scopePath, '.docs-review.lock')
    if ([IO.File]::Exists($lockPath)) { Assert-That (-not (Test-Reparse $lockPath)) 'Scope lock is a reparse point.' }
    Assert-That (-not [IO.Directory]::Exists($lockPath)) 'Scope lock path is a directory.'
    return (New-Object IO.FileStream($lockPath, [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None))
}
function Invoke-WithScopeLock([string]$Root, [string]$Scope, [scriptblock]$Action) {
    $stream = $null
    try {
        $stream = Open-ScopeLock $Root $Scope
        $stream.Lock(0, 1)
        & $Action
    }
    finally {
        if ($null -ne $stream) {
            try { $stream.Unlock(0, 1) } catch { }
            $stream.Dispose()
        }
    }
}
function Resolve-SafePath([string]$Root, [string]$Relative, [bool]$RequireExisting, [bool]$RequireFile) {
    $segments = @(Assert-RelativePath $Relative 'relative path')
    $current = $Root
    for ($i = 0; $i -lt $segments.Count; $i++) {
        $current = [IO.Path]::Combine($current, $segments[$i])
        $existsDirectory = [IO.Directory]::Exists($current)
        $existsFile = [IO.File]::Exists($current)
        if ($existsDirectory -or $existsFile) {
            Assert-That (-not (Test-Reparse $current)) 'A path segment is a reparse point.'
            if ($i -lt ($segments.Count - 1)) { Assert-That $existsDirectory 'An intermediate path segment is not a directory.' }
        }
        elseif ($RequireExisting) {
            Stop-Blocked 'A required path segment does not exist.'
        }
    }
    if ($RequireExisting) {
        if ($RequireFile) { Assert-That ([IO.File]::Exists($current)) 'Expected a regular file.' }
        else { Assert-That ([IO.Directory]::Exists($current)) 'Expected a directory.' }
    }
    return $current
}
function Get-Sha256([string]$Path) {
    $hash = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($hash.ComputeHash([IO.File]::ReadAllBytes($Path)))).Replace('-', '').ToLowerInvariant() }
    finally { $hash.Dispose() }
}
function Test-BytesEqual([byte[]]$Left, [byte[]]$Right) {
    if ($Left.Length -ne $Right.Length) { return $false }
    for ($i = 0; $i -lt $Left.Length; $i++) { if ($Left[$i] -ne $Right[$i]) { return $false } }
    return $true
}

function Read-JsonObject([string]$Path, [string]$Label) {
    Assert-That ([IO.File]::Exists($Path) -and -not (Test-Reparse $Path)) "$Label does not exist or is a reparse point."
    $bytes = [IO.File]::ReadAllBytes($Path)
    Assert-That (-not ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191)) "$Label cannot have a UTF-8 BOM."
    try { $text = $script:Utf8Strict.GetString($bytes) } catch { Stop-Blocked "$Label is not valid UTF-8." }
    Assert-NoDuplicateJsonKeys $text
    try { $value = $text | ConvertFrom-Json -ErrorAction Stop } catch { Stop-Blocked "$Label is not valid JSON." }
    Assert-That ($value -is [pscustomobject]) "$Label must be a JSON object."
    return $value
}

function Assert-CarriedObject($Value, [string]$Label) {
    if ($null -eq $Value) { return }
    Assert-Keys $Value @('package_id', 'path') $Label
    Assert-String $Value.package_id "$Label.package_id"
    Assert-RelativePath $Value.path "$Label.path" | Out-Null
}
function Assert-PackageSpecification($Spec) {
    $base = @('package_id', 'scope', 'phase', 'maturity', 'revision', 'predecessor_package_id')
    $names = @($Spec.PSObject.Properties | ForEach-Object { $_.Name })
    $expected = @($base)
    if ($names -contains 'source_git_revision') { $expected += 'source_git_revision' }
    $expected += 'artifacts'
    Assert-Keys $Spec $expected 'package_specification'
    Assert-String $Spec.package_id 'package_specification.package_id'
    Assert-String $Spec.scope 'package_specification.scope'
    Assert-String $Spec.phase 'package_specification.phase'
    Assert-That ($Spec.scope -match '^[a-z0-9]+(-[a-z0-9]+)*$') 'package_specification.scope is invalid.'
    Assert-That ($Spec.phase -match '^[A-Za-z0-9_-]+$') 'package_specification.phase is invalid.'
    Assert-That ($Spec.maturity -is [string] -and $Spec.maturity -in @('preliminar', 'formal')) 'package_specification.maturity is invalid.'
    Assert-Integer $Spec.revision 'package_specification.revision'
    Assert-That ($Spec.revision -ge 1) 'package_specification.revision must be positive.'
    $idMatch = [regex]::Match($Spec.package_id, '^([a-z0-9]+(?:-[a-z0-9]+)*)-(preliminar|formal)-r([0-9]{3,})$')
    Assert-That $idMatch.Success 'package_specification.package_id is invalid.'
    Assert-That ($idMatch.Groups[1].Value -ceq $Spec.scope -and $idMatch.Groups[2].Value -ceq $Spec.maturity -and [Int64]::Parse($idMatch.Groups[3].Value) -eq $Spec.revision) 'package_id does not match scope, maturity, and revision.'
    if ($Spec.revision -eq 1) { Assert-That ($null -eq $Spec.predecessor_package_id) 'revision one cannot have a predecessor.' }
    else {
        Assert-String $Spec.predecessor_package_id 'package_specification.predecessor_package_id'
        $predecessorMatch = [regex]::Match($Spec.predecessor_package_id, '^([a-z0-9]+(?:-[a-z0-9]+)*)-(preliminar|formal)-r([0-9]{3,})$')
        Assert-That ($predecessorMatch.Success -and $predecessorMatch.Groups[1].Value -ceq $Spec.scope -and ([Int64]::Parse($predecessorMatch.Groups[3].Value) -eq ($Spec.revision - 1))) 'predecessor_package_id must be the immediate prior revision in the scope.'
    }
    if ($names -contains 'source_git_revision') { Assert-That (($null -eq $Spec.source_git_revision) -or ($Spec.source_git_revision -is [string] -and $Spec.source_git_revision.IndexOf([char]0) -lt 0 -and $Spec.source_git_revision.IndexOf("`n") -lt 0 -and $Spec.source_git_revision.IndexOf("`r") -lt 0)) 'source_git_revision is invalid.' }
    Assert-That (Test-Array $Spec.artifacts) 'package_specification.artifacts must be an array.'
    $artifacts = @($Spec.artifacts)
    Assert-That ($artifacts.Count -gt 0) 'package_specification.artifacts cannot be empty.'
    $paths = New-Object System.Collections.Hashtable([StringComparer]::OrdinalIgnoreCase)
    $types = New-Object System.Collections.Hashtable([StringComparer]::OrdinalIgnoreCase)
    $sources = New-Object System.Collections.Hashtable([StringComparer]::OrdinalIgnoreCase)
    $previous = $null
    foreach ($artifact in $artifacts) {
        Assert-Keys $artifact @('path', 'document_type', 'source_path', 'carried_forward_from') 'artifact'
        if ($Spec.revision -eq 1) { Assert-That ($null -eq $artifact.carried_forward_from) 'revision one artifacts cannot carry forward.' }
        Assert-RelativePath $artifact.path 'artifact.path' | Out-Null
        Assert-That ($artifact.path -notmatch '^proyecto/') 'artifact.path is a snapshot-relative path.'
        Assert-String $artifact.document_type 'artifact.document_type'
        Assert-That ($artifact.document_type -match '^[a-z0-9]+(_[a-z0-9]+)*$') 'artifact.document_type is invalid.'
        Assert-RelativePath $artifact.source_path 'artifact.source_path' | Out-Null
        Assert-That ($artifact.source_path -match '^proyecto/') 'artifact.source_path must be under proyecto/.'
        Assert-CarriedObject $artifact.carried_forward_from 'artifact.carried_forward_from'
        Assert-That (-not $paths.ContainsKey($artifact.path) -and -not $types.ContainsKey($artifact.document_type) -and -not $sources.ContainsKey($artifact.source_path)) 'Artifact paths, source paths, and document types must be unique.'
        if ($null -ne $previous) { Assert-That ([string]::CompareOrdinal($previous, $artifact.path) -lt 0) 'Artifacts must be strictly ordered by path.' }
        $paths[$artifact.path] = $true; $types[$artifact.document_type] = $true; $sources[$artifact.source_path] = $true; $previous = $artifact.path
    }
    foreach ($left in $paths.Keys) { foreach ($right in $paths.Keys) { if ($left -cne $right) { Assert-That (-not $right.StartsWith($left + '/')) 'Artifact paths cannot collide with directories.' } } }
}
function Get-SourceGitRevision($Spec) { if ($null -ne $Spec.PSObject.Properties['source_git_revision']) { return $Spec.source_git_revision }; return $null }
function Assert-SpecMatchesManifest($Spec, $Manifest) {
    foreach ($name in @('package_id', 'scope', 'phase', 'maturity', 'revision', 'predecessor_package_id')) { Assert-That ($Spec.$name -ceq $Manifest.$name) "Request specification differs from manifest field '$name'." }
    Assert-That ((Get-SourceGitRevision $Spec) -ceq $Manifest.source_git_revision) 'Request specification differs from manifest source_git_revision.'
    $requested = @($Spec.artifacts); $actual = @($Manifest.artifacts)
    Assert-That ($requested.Count -eq $actual.Count) 'Request artifacts differ from manifest.'
    for ($i = 0; $i -lt $requested.Count; $i++) {
        foreach ($name in @('path', 'document_type', 'source_path')) { Assert-That ($requested[$i].$name -ceq $actual[$i].$name) "Request artifact differs from manifest field '$name'." }
        $a = $requested[$i].carried_forward_from; $b = $actual[$i].carried_forward_from
        Assert-That (($null -eq $a) -eq ($null -eq $b)) 'Request carried_forward_from differs from manifest.'
        if ($null -ne $a) { Assert-That ($a.package_id -ceq $b.package_id -and $a.path -ceq $b.path) 'Request carried_forward_from differs from manifest.' }
    }
}

function Assert-Attestation($Value, [bool]$Promotion) {
    if ($Promotion) { Assert-Keys $Value @('identity', 'at', 'source') 'attestation' }
    else { Assert-Keys $Value @('identity', 'role', 'at', 'source') 'attestation' }
    Assert-String $Value.identity 'attestation.identity'; Assert-IsoDate $Value.at 'attestation.at'; Assert-String $Value.source 'attestation.source'
    if (-not $Promotion) { Assert-String $Value.role 'attestation.role' }
}
function Assert-Decision($Decision, $Spec) {
    Assert-Keys $Decision @('value', 'reviewer', 'role', 'at', 'source', 'findings') 'decision'
    Assert-That ($Decision.value -is [string] -and $Decision.value -in @('aprobado', 'rechazado')) 'decision.value is invalid.'
    Assert-String $Decision.reviewer 'decision.reviewer'; Assert-String $Decision.role 'decision.role'; Assert-IsoDate $Decision.at 'decision.at'; Assert-String $Decision.source 'decision.source'
    Assert-That (Test-Array $Decision.findings) 'decision.findings must be an array.'
    $known = @{}; foreach ($artifact in @($Spec.artifacts)) { $known[$artifact.path] = $true }
    $seen = @{}; $previous = $null
    foreach ($finding in @($Decision.findings)) {
        Assert-Keys $finding @('path', 'outcome', 'note') 'finding'
        Assert-String $finding.path 'finding.path'; Assert-That $known.ContainsKey($finding.path) 'finding.path is not an artifact.'
        Assert-That ($finding.outcome -is [string] -and $finding.outcome -in @('aprobado', 'rechazado')) 'finding.outcome is invalid.'
        Assert-String $finding.note 'finding.note'; Assert-That (-not $seen.ContainsKey($finding.path)) 'Only one finding per artifact is allowed.'
        if ($null -ne $previous) { Assert-That ([string]::CompareOrdinal($previous, $finding.path) -lt 0) 'Findings must be ordered by path.' }
        $seen[$finding.path] = $true; $previous = $finding.path
        if ($finding.outcome -eq 'rechazado') { Assert-That ($Decision.value -eq 'rechazado') 'A rejected finding requires a rejected package.' }
    }
}

function Escape-MarkdownValue([string]$Value) { return $Value.Replace('\', '\\').Replace('`', '\`') }
function Unescape-MarkdownValue([string]$Value) {
    $builder = New-Object System.Text.StringBuilder
    for ($i = 0; $i -lt $Value.Length; $i++) {
        if ($Value[$i] -eq '\' -and ($i + 1) -lt $Value.Length -and ($Value[$i + 1] -eq '\' -or $Value[$i + 1] -eq '`')) { [void]$builder.Append($Value[$i + 1]); $i++ }
        else { [void]$builder.Append($Value[$i]) }
    }
    return $builder.ToString()
}
function New-ManifestBody($Manifest, $Submit, $Review, $Findings) {
    $predecessor = if ($null -eq $Manifest.predecessor_package_id) { 'ninguno' } else { $Manifest.predecessor_package_id }
    $lines = @('## Propósito del paquete', '', ('- Scope: ' + (Escape-MarkdownValue $Manifest.scope)), ('- Fase: ' + (Escape-MarkdownValue $Manifest.phase)), ('- Madurez: ' + (Escape-MarkdownValue $Manifest.maturity)), ('- Revisión: ' + $Manifest.revision), ('- Predecesor: ' + (Escape-MarkdownValue $predecessor)), '', '## Attestation de sometimiento', '')
    if ($null -eq $Submit) { $lines += '`No registrada.`' }
    else { $lines += @('- Identidad: ' + (Escape-MarkdownValue $Submit.identity), '- Rol: ' + (Escape-MarkdownValue $Submit.role), '- Fecha: ' + (Escape-MarkdownValue $Submit.at), '- Fuente: ' + (Escape-MarkdownValue $Submit.source)) }
    $lines += @('', '## Attestation de revisión', '')
    if ($null -eq $Review) { $lines += '`No registrada.`' }
    else { $lines += @('- Revisor: ' + (Escape-MarkdownValue $Review.reviewer), '- Rol: ' + (Escape-MarkdownValue $Review.role), '- Fecha: ' + (Escape-MarkdownValue $Review.at), '- Fuente: ' + (Escape-MarkdownValue $Review.source), '- Decisión: ' + $Review.value) }
    $lines += @('', '## Hallazgos', '')
    if (@($Findings).Count -eq 0) { $lines += '`Sin hallazgos.`' }
    else { foreach ($finding in @($Findings)) { $lines += ('- ' + (Escape-MarkdownValue $finding.path) + ': ' + $finding.outcome + ' — ' + (Escape-MarkdownValue $finding.note)) } }
    return ($lines -join "`n") + "`n"
}
function Get-BodyValue([string]$Line, [string]$Prefix) {
    Assert-That $Line.StartsWith($Prefix, [StringComparison]::Ordinal) 'Manifest body has an invalid line.'
    return Unescape-MarkdownValue $Line.Substring($Prefix.Length)
}
function Read-ManifestBody([string]$Body, $Manifest) {
    Assert-That ($Body.EndsWith("`n") -and $Body.IndexOf("`r") -lt 0) 'Manifest body must use exact LF lines.'
    $lines = @($Body.Substring(0, $Body.Length - 1).Split("`n"))
    $fixed = @('## Propósito del paquete', '', '- Scope: ' + (Escape-MarkdownValue $Manifest.scope), '- Fase: ' + (Escape-MarkdownValue $Manifest.phase), '- Madurez: ' + (Escape-MarkdownValue $Manifest.maturity), '- Revisión: ' + $Manifest.revision, '- Predecesor: ' + (Escape-MarkdownValue $(if ($null -eq $Manifest.predecessor_package_id) { 'ninguno' } else { $Manifest.predecessor_package_id })), '', '## Attestation de sometimiento', '')
    for ($i = 0; $i -lt $fixed.Count; $i++) { Assert-That ($lines[$i] -ceq $fixed[$i]) 'Manifest body purpose section is invalid.' }
    $index = $fixed.Count; $submit = $null
    if ($lines[$index] -ceq '`No registrada.`') { $index++ }
    else {
        $submit = [ordered]@{ identity = (Get-BodyValue $lines[$index] '- Identidad: '); role = (Get-BodyValue $lines[$index + 1] '- Rol: '); at = (Get-BodyValue $lines[$index + 2] '- Fecha: '); source = (Get-BodyValue $lines[$index + 3] '- Fuente: ') }
        $index += 4
    }
    Assert-That ($lines[$index] -ceq '' -and $lines[$index + 1] -ceq '## Attestation de revisión' -and $lines[$index + 2] -ceq '') 'Manifest body review heading is invalid.'
    $index += 3; $review = $null
    if ($lines[$index] -ceq '`No registrada.`') { $index++ }
    else {
        $review = [ordered]@{ reviewer = (Get-BodyValue $lines[$index] '- Revisor: '); role = (Get-BodyValue $lines[$index + 1] '- Rol: '); at = (Get-BodyValue $lines[$index + 2] '- Fecha: '); source = (Get-BodyValue $lines[$index + 3] '- Fuente: '); value = (Get-BodyValue $lines[$index + 4] '- Decisión: ') }
        $index += 5
    }
    Assert-That ($lines[$index] -ceq '' -and $lines[$index + 1] -ceq '## Hallazgos' -and $lines[$index + 2] -ceq '') 'Manifest body findings heading is invalid.'
    $index += 3; $findings = @()
    if ($index -lt $lines.Count -and $lines[$index] -ceq '`Sin hallazgos.`') { $index++ }
    else {
        while ($index -lt $lines.Count) {
            $match = [regex]::Match($lines[$index], '^- (.+): (aprobado|rechazado) — (.+)$')
            Assert-That $match.Success 'Manifest body finding is invalid.'
            $findings += [ordered]@{ path = (Unescape-MarkdownValue $match.Groups[1].Value); outcome = $match.Groups[2].Value; note = (Unescape-MarkdownValue $match.Groups[3].Value) }
            $index++
        }
    }
    Assert-That ($index -eq $lines.Count) 'Manifest body contains extra text.'
    $expected = New-ManifestBody $Manifest $submit $review $findings
    Assert-That ($Body -ceq $expected) 'Manifest body is not canonical.'
    return [pscustomobject]@{ Submit = $submit; Review = $review; Findings = $findings }
}

function New-Manifest($Spec, [string]$State, $Submit, $Review, $Findings, $Hashes, $Outcomes) {
    $artifacts = @()
    foreach ($artifact in @($Spec.artifacts)) {
        $carried = $null
        if ($null -ne $artifact.carried_forward_from) { $carried = [ordered]@{ package_id = $artifact.carried_forward_from.package_id; path = $artifact.carried_forward_from.path } }
        $artifacts += [ordered]@{ path = $artifact.path; document_type = $artifact.document_type; source_path = $artifact.source_path; carried_forward_from = $carried; content_sha256 = $Hashes[$artifact.path]; review_outcome = $Outcomes[$artifact.path] }
    }
    return [ordered]@{
        manifest_version = 1; package_id = $Spec.package_id; scope = $Spec.scope; phase = $Spec.phase; maturity = $Spec.maturity; revision = $Spec.revision; predecessor_package_id = $Spec.predecessor_package_id; state = $State
        submitted_by = if ($null -eq $Submit) { $null } else { $Submit.identity }; submitted_at = if ($null -eq $Submit) { $null } else { $Submit.at }
        reviewer = if ($null -eq $Review) { $null } else { $Review.reviewer }; review_decision = if ($null -eq $Review) { $null } else { $Review.value }; reviewed_at = if ($null -eq $Review) { $null } else { $Review.at }
        source_git_revision = Get-SourceGitRevision $Spec; artifacts = $artifacts
    }
}
function Get-ManifestText($Manifest, $BodyData) { return "---`n" + (ConvertTo-CanonicalJson $Manifest) + "`n---`n" + (New-ManifestBody $Manifest $BodyData.Submit $BodyData.Review $BodyData.Findings) }
function Write-AtomicManifest([string]$Root, [string]$Package, [string]$Relative, [string]$Text) {
    $temporary = [IO.Path]::Combine((Split-Path -Parent $Package), ('.docs-review-manifest-' + [Guid]::NewGuid().ToString('N') + '.tmp'))
    [IO.File]::WriteAllBytes($temporary, $script:Utf8.GetBytes($Text))
    try {
        # The caller holds the scope lock; revalidate root, package, and ancestors immediately before publication.
        $checkedRoot = Assert-SafeRoot $Root
        $checkedPackage = Resolve-SafePath $checkedRoot $Relative $true $false
        Assert-That ($checkedPackage -ceq $Package) 'Manifest package path changed before publication.'
        Resolve-SafePath $checkedPackage 'manifest.md' $true $true | Out-Null
        [IO.File]::Replace($temporary, [IO.Path]::Combine($checkedPackage, 'manifest.md'), $null)
    }
    catch { Stop-Blocked 'The manifest transition could not be published atomically; its temporary sibling was preserved.' }
}

function Read-Manifest([string]$Package) {
    $path = Resolve-SafePath $Package 'manifest.md' $true $true
    $bytes = [IO.File]::ReadAllBytes($path)
    Assert-That (-not ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191)) 'manifest.md cannot have a UTF-8 BOM.'
    try { $text = $script:Utf8Strict.GetString($bytes) } catch { Stop-Blocked 'manifest.md is not valid UTF-8.' }
    Assert-That ($text.IndexOf("`r") -lt 0) 'manifest.md must use LF only.'
    $match = [regex]::Match($text, '\A---\n(?<json>.*?)\n---\n(?<body>.*)\z', [Text.RegularExpressions.RegexOptions]::Singleline)
    Assert-That $match.Success 'manifest.md has an invalid frontmatter envelope.'
    $json = $match.Groups['json'].Value
    Assert-NoDuplicateJsonKeys $json
    try { $manifest = $json | ConvertFrom-Json -ErrorAction Stop } catch { Stop-Blocked 'manifest.md frontmatter is not JSON.' }
    Assert-Keys $manifest @('manifest_version', 'package_id', 'scope', 'phase', 'maturity', 'revision', 'predecessor_package_id', 'state', 'submitted_by', 'submitted_at', 'reviewer', 'review_decision', 'reviewed_at', 'source_git_revision', 'artifacts') 'manifest'
    Assert-That ($json -ceq (ConvertTo-CanonicalJson $manifest)) 'manifest.md frontmatter is not byte-canonical JSON.'
    return [pscustomobject]@{ Manifest = $manifest; Body = $match.Groups['body'].Value }
}
function Assert-ManifestShape($Manifest) {
    Assert-That ($Manifest.manifest_version -is [int] -or $Manifest.manifest_version -is [long]) 'manifest_version must be an integer.'
    Assert-That ($Manifest.manifest_version -eq 1) 'manifest_version is unsupported.'
    $spec = [pscustomobject]@{ package_id = $Manifest.package_id; scope = $Manifest.scope; phase = $Manifest.phase; maturity = $Manifest.maturity; revision = $Manifest.revision; predecessor_package_id = $Manifest.predecessor_package_id; source_git_revision = $Manifest.source_git_revision; artifacts = @() }
    foreach ($artifact in @($Manifest.artifacts)) {
        Assert-Keys $artifact @('path', 'document_type', 'source_path', 'carried_forward_from', 'content_sha256', 'review_outcome') 'manifest artifact'
        $spec.artifacts += [pscustomobject]@{ path = $artifact.path; document_type = $artifact.document_type; source_path = $artifact.source_path; carried_forward_from = $artifact.carried_forward_from }
        Assert-That ($artifact.content_sha256 -is [string] -and $artifact.content_sha256 -match '^[0-9a-f]{64}$') 'Manifest artifact hash is invalid.'
        Assert-That (($null -eq $artifact.review_outcome) -or ($artifact.review_outcome -is [string] -and $artifact.review_outcome -in @('aprobado', 'rechazado'))) 'Manifest artifact review outcome is invalid.'
    }
    Assert-PackageSpecification $spec
    Assert-That ($Manifest.state -is [string] -and $Manifest.state -in @('pendiente', 'en_verificacion', 'aprobado', 'rechazado')) 'Manifest state is invalid.'
    return $spec
}
function Assert-StateAndBody($Manifest, $BodyData) {
    $state = $Manifest.state
    if ($state -eq 'pendiente') {
        foreach ($field in @('submitted_by', 'submitted_at', 'reviewer', 'review_decision', 'reviewed_at')) { Assert-That ($null -eq $Manifest.$field) 'Pending manifest contains review metadata.' }
        Assert-That ($null -eq $BodyData.Submit -and $null -eq $BodyData.Review -and @($BodyData.Findings).Count -eq 0) 'Pending manifest body contains review metadata.'
        foreach ($artifact in @($Manifest.artifacts)) { Assert-That ($null -eq $artifact.review_outcome) 'Pending manifest has a review outcome.' }
    }
    elseif ($state -eq 'en_verificacion') {
        Assert-String $Manifest.submitted_by 'manifest.submitted_by'; Assert-IsoDate $Manifest.submitted_at 'manifest.submitted_at'
        foreach ($field in @('reviewer', 'review_decision', 'reviewed_at')) { Assert-That ($null -eq $Manifest.$field) 'Submitted manifest contains terminal metadata.' }
        Assert-That ($null -ne $BodyData.Submit -and $null -eq $BodyData.Review -and @($BodyData.Findings).Count -eq 0) 'Submitted manifest body is invalid.'
        Assert-That ($BodyData.Submit.identity -ceq $Manifest.submitted_by -and $BodyData.Submit.at -ceq $Manifest.submitted_at) 'Submitted manifest body differs from frontmatter.'
        Assert-String $BodyData.Submit.role 'Submit role'; Assert-String $BodyData.Submit.source 'Submit source'
        foreach ($artifact in @($Manifest.artifacts)) { Assert-That ($null -eq $artifact.review_outcome) 'Submitted manifest has a review outcome.' }
    }
    else {
        Assert-String $Manifest.submitted_by 'manifest.submitted_by'; Assert-IsoDate $Manifest.submitted_at 'manifest.submitted_at'; Assert-String $Manifest.reviewer 'manifest.reviewer'; Assert-IsoDate $Manifest.reviewed_at 'manifest.reviewed_at'
        Assert-That ($Manifest.review_decision -ceq $state) 'Terminal manifest decision differs from state.'
        Assert-That ($null -ne $BodyData.Submit -and $null -ne $BodyData.Review) 'Terminal manifest body lacks metadata.'
        Assert-That ($BodyData.Submit.identity -ceq $Manifest.submitted_by -and $BodyData.Submit.at -ceq $Manifest.submitted_at -and $BodyData.Review.reviewer -ceq $Manifest.reviewer -and $BodyData.Review.at -ceq $Manifest.reviewed_at -and $BodyData.Review.value -ceq $state) 'Terminal manifest body differs from frontmatter.'
        Assert-String $BodyData.Submit.role 'Submit role'; Assert-String $BodyData.Submit.source 'Submit source'; Assert-String $BodyData.Review.role 'Review role'; Assert-String $BodyData.Review.source 'Review source'
        $findingOutcomes = @{}; $artifactPaths = @{}; $previousPath = $null
        foreach ($artifact in @($Manifest.artifacts)) { $artifactPaths[$artifact.path] = $true }
        foreach ($finding in @($BodyData.Findings)) {
            Assert-That ($artifactPaths.ContainsKey($finding.path) -and -not $findingOutcomes.ContainsKey($finding.path)) 'Terminal manifest body has an invalid finding path.'
            Assert-That ($finding.outcome -in @('aprobado', 'rechazado') -and -not [string]::IsNullOrEmpty($finding.note)) 'Terminal manifest body has an invalid finding.'
            if ($null -ne $previousPath) { Assert-That ([string]::CompareOrdinal($previousPath, $finding.path) -lt 0) 'Terminal manifest findings are not ordered.' }
            if ($finding.outcome -eq 'rechazado') { Assert-That ($state -eq 'rechazado') 'A rejected finding requires a rejected package.' }
            $findingOutcomes[$finding.path] = $finding.outcome; $previousPath = $finding.path
        }
        foreach ($artifact in @($Manifest.artifacts)) { Assert-That ($artifact.review_outcome -ceq $findingOutcomes[$artifact.path]) 'Terminal artifact outcome differs from findings.' }
    }
}
function Get-AllFiles([string]$Root, [string]$Relative = '') {
    $directory = if ([string]::IsNullOrEmpty($Relative)) { $Root } else { Resolve-SafePath $Root $Relative $true $false }
    Assert-That (-not (Test-Reparse $directory)) 'Package contains a reparse-point directory.'
    $files = @()
    foreach ($entry in [IO.Directory]::GetFileSystemEntries($directory)) {
        Assert-That (-not (Test-Reparse $entry)) 'Package contains a reparse point.'
        $name = [IO.Path]::GetFileName($entry); $child = if ([string]::IsNullOrEmpty($Relative)) { $name } else { $Relative + '/' + $name }
        if ([IO.Directory]::Exists($entry)) { $files += Get-AllFiles $Root $child }
        elseif ([IO.File]::Exists($entry)) { $files += $child }
        else { Stop-Blocked 'Package contains an unsupported filesystem object.' }
    }
    return $files
}
function Get-AllDirectories([string]$Root, [string]$Relative = '') {
    $directory = if ([string]::IsNullOrEmpty($Relative)) { $Root } else { Resolve-SafePath $Root $Relative $true $false }
    Assert-That (-not (Test-Reparse $directory)) 'Package contains a reparse-point directory.'
    $directories = @()
    foreach ($entry in [IO.Directory]::GetFileSystemEntries($directory)) {
        Assert-That (-not (Test-Reparse $entry)) 'Package contains a reparse point.'
        $name = [IO.Path]::GetFileName($entry); $child = if ([string]::IsNullOrEmpty($Relative)) { $name } else { $Relative + '/' + $name }
        if ([IO.Directory]::Exists($entry)) {
            $directories += $child
            $directories += Get-AllDirectories $Root $child
        }
        elseif (-not [IO.File]::Exists($entry)) { Stop-Blocked 'Package contains an unsupported filesystem object.' }
    }
    return $directories
}
function Assert-PredecessorAndCarried($Root, $Spec, [hashtable]$Hashes) {
    if ($Spec.revision -eq 1) { return }
    $predecessorRelative = 'proyecto/docs-verificacion/' + $Spec.scope + '/' + $Spec.predecessor_package_id
    $predecessorPath = Resolve-SafePath $Root $predecessorRelative $true $false
    $predecessor = Test-Package $Root $predecessorPath $predecessorRelative $false
    Assert-That ($predecessor.Manifest.state -in @('aprobado', 'rechazado')) 'Predecessor is not terminal.'
    foreach ($artifact in @($Spec.artifacts)) {
        if ($null -ne $artifact.carried_forward_from) {
            Assert-That ($artifact.carried_forward_from.package_id -ceq $Spec.predecessor_package_id) 'carried_forward_from must cite the immediate predecessor.'
            $old = @($predecessor.Manifest.artifacts | Where-Object { $_.path -ceq $artifact.carried_forward_from.path })
            Assert-That ($old.Count -eq 1) 'carried_forward_from artifact does not exist.'
            Assert-That ($Hashes[$artifact.path] -ceq $old[0].content_sha256) 'carried_forward_from snapshot differs from predecessor.'
            $oldPath = Resolve-SafePath $predecessorPath $old[0].path $true $true
            Assert-That (Test-BytesEqual ([IO.File]::ReadAllBytes((Resolve-SafePath $Root $artifact.source_path $true $true))) ([IO.File]::ReadAllBytes($oldPath))) 'carried_forward_from bytes differ from predecessor.'
        }
    }
}
function Assert-PackageCarriedReferences($Root, [string]$Package, $Manifest) {
    if ($Manifest.revision -eq 1) { return }
    $predecessorRelative = 'proyecto/docs-verificacion/' + $Manifest.scope + '/' + $Manifest.predecessor_package_id
    $predecessorPath = Resolve-SafePath $Root $predecessorRelative $true $false
    $predecessor = Test-Package $Root $predecessorPath $predecessorRelative $false
    Assert-That ($predecessor.Manifest.state -in @('aprobado', 'rechazado')) 'Manifest predecessor is not terminal.'
    foreach ($artifact in @($Manifest.artifacts)) {
        if ($null -ne $artifact.carried_forward_from) {
            Assert-That ($artifact.carried_forward_from.package_id -ceq $Manifest.predecessor_package_id) 'Manifest carried_forward_from does not cite its predecessor.'
            $old = @($predecessor.Manifest.artifacts | Where-Object { $_.path -ceq $artifact.carried_forward_from.path })
            Assert-That ($old.Count -eq 1) 'Manifest carried_forward_from artifact is absent.'
            Assert-That ($artifact.content_sha256 -ceq $old[0].content_sha256) 'Manifest carried_forward_from hash differs from predecessor.'
            Assert-That (Test-BytesEqual ([IO.File]::ReadAllBytes((Resolve-SafePath $Package $artifact.path $true $true))) ([IO.File]::ReadAllBytes((Resolve-SafePath $predecessorPath $old[0].path $true $true)))) 'Manifest carried_forward_from bytes differ from predecessor.'
        }
    }
}
function Test-Package($Root, [string]$Package, [string]$Relative, [bool]$CheckLive, [bool]$CheckLiveWhenActive = $false) {
    $read = Read-Manifest $Package; $manifest = $read.Manifest; $spec = Assert-ManifestShape $manifest; $body = Read-ManifestBody $read.Body $manifest; Assert-StateAndBody $manifest $body
    $expected = New-Object System.Collections.Hashtable([StringComparer]::OrdinalIgnoreCase)
    $expected['manifest.md'] = $true
    $expectedDirectories = New-Object System.Collections.Hashtable([StringComparer]::OrdinalIgnoreCase)
    foreach ($artifact in @($manifest.artifacts)) {
        $expected[$artifact.path] = $true
        $parts = @($artifact.path.Split('/'))
        $parent = @()
        for ($index = 0; $index -lt ($parts.Count - 1); $index++) {
            $parent += $parts[$index]
            $expectedDirectories[$parent -join '/'] = $true
        }
    }
    $files = @(Get-AllFiles $Package)
    Assert-That ($files.Count -eq $expected.Count) 'Package has missing or extra files.'
    foreach ($file in $files) { Assert-That $expected.ContainsKey($file) 'Package has an unexpected file.' }
    $directories = @(Get-AllDirectories $Package)
    Assert-That ($directories.Count -eq $expectedDirectories.Count) 'Package has missing or extra directories.'
    foreach ($directory in $directories) { Assert-That $expectedDirectories.ContainsKey($directory) 'Package has an unexpected directory.' }
    $mustCheckLive = $CheckLive -or ($CheckLiveWhenActive -and $manifest.state -in @('pendiente', 'en_verificacion'))
    foreach ($artifact in @($manifest.artifacts)) {
        $snapshot = Resolve-SafePath $Package $artifact.path $true $true
        Assert-That ((Get-Sha256 $snapshot) -ceq $artifact.content_sha256) 'A snapshot hash differs from the manifest.'
        if ($mustCheckLive) {
            $live = Resolve-SafePath $Root $artifact.source_path $true $true
            Assert-That ((Get-Sha256 $live) -ceq $artifact.content_sha256) 'A live source differs from its frozen snapshot.'
        }
    }
    Assert-PackageCarriedReferences $Root $Package $manifest
    return [pscustomobject]@{ Manifest = $manifest; Spec = $spec; BodyData = $body; Package = $Package; Relative = $Relative }
}

function Read-Request($Request, [ref]$Root) {
    $request = $Request
    $base = @('schema_version', 'project_root', 'package_specification')
    $expected = @($base)
    if ($Operation -ne 'Prepare') { $expected += 'package_path' }
    if ($Operation -in @('Submit', 'Promote')) { $expected += 'attestation' }
    if ($Operation -eq 'RecordDecision') { $expected += 'decision' }
    Assert-Keys $request $expected 'request'
    Assert-Integer $request.schema_version 'schema_version'; Assert-That ($request.schema_version -eq 1) 'schema_version is unsupported.'
    $Root.Value = Assert-SafeRoot $request.project_root
    Assert-PackageSpecification $request.package_specification
    if ($Operation -ne 'Prepare') {
        Assert-RelativePath $request.package_path 'package_path' | Out-Null
        $expectedVerification = 'proyecto/docs-verificacion/' + $request.package_specification.scope + '/' + $request.package_specification.package_id
        if ($Operation -eq 'Validate') {
            $expectedApproved = 'proyecto/docs-aprobados/' + $request.package_specification.scope + '/' + $request.package_specification.package_id
            Assert-That ($request.package_path -ceq $expectedVerification -or $request.package_path -ceq $expectedApproved) 'package_path does not identify the requested package.'
        } else { Assert-That ($request.package_path -ceq $expectedVerification) 'package_path does not identify the verification package.' }
        $script:ObservedPackagePath = $request.package_path
    }
    if ($Operation -in @('Submit', 'Promote')) { Assert-Attestation $request.attestation ($Operation -eq 'Promote') }
    if ($Operation -eq 'RecordDecision') { Assert-Decision $request.decision $request.package_specification }
    return $request
}
function Assert-NoOtherActivePackage([string]$Root, $Spec, [string]$Destination) {
    $scopeRelative = 'proyecto/docs-verificacion/' + $Spec.scope
    $scopePath = Resolve-SafePath $Root $scopeRelative $false $false
    if (-not [IO.Directory]::Exists($scopePath)) { return }
    foreach ($entry in [IO.Directory]::GetDirectories($scopePath)) {
        Assert-That (-not (Test-Reparse $entry)) 'Verification scope contains a reparse point.'
        if ($entry -cne $Destination) {
            $relative = $scopeRelative + '/' + [IO.Path]::GetFileName($entry)
            $candidate = Test-Package $Root $entry $relative $false
            if ($candidate.Manifest.state -in @('pendiente', 'en_verificacion')) { Stop-Blocked 'The scope already has an active package.' }
        }
    }
}
function Invoke-Prepare($Root, $Request) {
    $spec = $Request.package_specification
    $relative = 'proyecto/docs-verificacion/' + $spec.scope + '/' + $spec.package_id
    $script:ObservedPackagePath = $relative
    $destination = Resolve-SafePath $Root $relative $false $false
    if ([IO.Directory]::Exists($destination) -or [IO.File]::Exists($destination)) {
        Assert-That ([IO.Directory]::Exists($destination) -and -not (Test-Reparse $destination)) 'Package destination collides with a non-directory or reparse point.'
        $existing = Test-Package $Root $destination $relative $true
        Assert-SpecMatchesManifest $spec $existing.Manifest
        Assert-That ($existing.Manifest.state -eq 'pendiente') 'An existing package is not an idempotent pending package.'
        $script:ObservedState = $existing.Manifest.state
        return
    }
    Assert-NoOtherActivePackage $Root $spec $destination
    $hashes = @{}
    foreach ($artifact in @($spec.artifacts)) { $live = Resolve-SafePath $Root $artifact.source_path $true $true; $hashes[$artifact.path] = Get-Sha256 $live }
    Assert-PredecessorAndCarried $Root $spec $hashes
    $parent = [IO.Path]::GetDirectoryName($destination)
    if (-not [IO.Directory]::Exists($parent)) {
        $projectDirectory = Resolve-SafePath $Root 'proyecto' $false $false
        if (-not [IO.Directory]::Exists($projectDirectory)) { [IO.Directory]::CreateDirectory($projectDirectory) | Out-Null }
        $verificationDirectory = [IO.Path]::Combine($projectDirectory, 'docs-verificacion')
        if (-not [IO.Directory]::Exists($verificationDirectory)) { [IO.Directory]::CreateDirectory($verificationDirectory) | Out-Null }
        Assert-That (-not (Test-Reparse $verificationDirectory)) 'Verification root is a reparse point.'
        [IO.Directory]::CreateDirectory($parent) | Out-Null
    }
    Assert-That (-not (Test-Reparse $parent)) 'Package destination parent is a reparse point.'
    $staging = [IO.Path]::Combine($parent, ('.docs-review-staging-' + [Guid]::NewGuid().ToString('N')))
    [IO.Directory]::CreateDirectory($staging) | Out-Null
    try {
        foreach ($artifact in @($spec.artifacts)) {
            $snapshot = [IO.Path]::Combine($staging, $artifact.path.Replace('/', [IO.Path]::DirectorySeparatorChar))
            $snapshotParent = [IO.Path]::GetDirectoryName($snapshot)
            if (-not [IO.Directory]::Exists($snapshotParent)) { [IO.Directory]::CreateDirectory($snapshotParent) | Out-Null }
            [IO.File]::Copy((Resolve-SafePath $Root $artifact.source_path $true $true), $snapshot)
        }
        $outcomes = @{}; foreach ($artifact in @($spec.artifacts)) { $outcomes[$artifact.path] = $null }
        $manifest = New-Manifest $spec 'pendiente' $null $null @() $hashes $outcomes
        [IO.File]::WriteAllBytes([IO.Path]::Combine($staging, 'manifest.md'), $script:Utf8.GetBytes((Get-ManifestText $manifest ([pscustomobject]@{ Submit = $null; Review = $null; Findings = @() }))))
        $checked = Test-Package $Root $staging $relative $true
        Assert-That ($checked.Manifest.state -eq 'pendiente') 'Staged package has an invalid state.'
        # The caller holds the scope lock; revalidate destination ancestors immediately before publication.
        $checkedRoot = Assert-SafeRoot $Root
        $checkedDestination = Resolve-SafePath $checkedRoot $relative $false $false
        Assert-That ($checkedDestination -ceq $destination -and -not [IO.Directory]::Exists($checkedDestination) -and -not [IO.File]::Exists($checkedDestination)) 'Package destination changed before publication.'
        [IO.Directory]::Move($staging, $checkedDestination)
    }
    catch { throw }
    $script:ObservedState = 'pendiente'
}
function Invoke-Submit($Root, $Request) {
    $package = Resolve-SafePath $Root $Request.package_path $true $false
    $current = Test-Package $Root $package $Request.package_path $true
    Assert-SpecMatchesManifest $Request.package_specification $current.Manifest
    $script:ObservedState = $current.Manifest.state
    if ($current.Manifest.state -eq 'en_verificacion') {
        $same = $current.BodyData.Submit
        Assert-That ($null -ne $same -and $same.identity -ceq $Request.attestation.identity -and $same.role -ceq $Request.attestation.role -and $same.at -ceq $Request.attestation.at -and $same.source -ceq $Request.attestation.source) 'Submit attestation conflicts with the existing submission.'
        return
    }
    Assert-That ($current.Manifest.state -eq 'pendiente') 'Submit requires a pending package.'
    $hashes = @{}; $outcomes = @{}; foreach ($artifact in @($current.Manifest.artifacts)) { $hashes[$artifact.path] = $artifact.content_sha256; $outcomes[$artifact.path] = $null }
    $manifest = New-Manifest $Request.package_specification 'en_verificacion' $Request.attestation $null @() $hashes $outcomes
    Write-AtomicManifest $Root $package $Request.package_path (Get-ManifestText $manifest ([pscustomobject]@{ Submit = $Request.attestation; Review = $null; Findings = @() }))
    $script:ObservedState = 'en_verificacion'
}
function Test-SameDecision($BodyData, $Decision) {
    $review = $BodyData.Review
    if ($null -eq $review -or $review.reviewer -cne $Decision.reviewer -or $review.role -cne $Decision.role -or $review.at -cne $Decision.at -or $review.source -cne $Decision.source -or $review.value -cne $Decision.value) { return $false }
    $left = @($BodyData.Findings); $right = @($Decision.findings)
    if ($left.Count -ne $right.Count) { return $false }
    for ($i = 0; $i -lt $left.Count; $i++) { if ($left[$i].path -cne $right[$i].path -or $left[$i].outcome -cne $right[$i].outcome -or $left[$i].note -cne $right[$i].note) { return $false } }
    return $true
}
function Invoke-RecordDecision($Root, $Request) {
    $package = Resolve-SafePath $Root $Request.package_path $true $false
    $current = Test-Package $Root $package $Request.package_path $true
    Assert-SpecMatchesManifest $Request.package_specification $current.Manifest
    $script:ObservedState = $current.Manifest.state
    if ($current.Manifest.state -in @('aprobado', 'rechazado')) { Assert-That (Test-SameDecision $current.BodyData $Request.decision) 'Terminal decision conflicts with the existing decision.'; return }
    Assert-That ($current.Manifest.state -eq 'en_verificacion') 'RecordDecision requires a submitted package.'
    $hashes = @{}; $outcomes = @{}; $findingMap = @{}
    foreach ($finding in @($Request.decision.findings)) { $findingMap[$finding.path] = $finding.outcome }
    foreach ($artifact in @($current.Manifest.artifacts)) { $hashes[$artifact.path] = $artifact.content_sha256; $outcomes[$artifact.path] = $findingMap[$artifact.path] }
    $manifest = New-Manifest $Request.package_specification $Request.decision.value $current.BodyData.Submit $Request.decision @($Request.decision.findings) $hashes $outcomes
    Write-AtomicManifest $Root $package $Request.package_path (Get-ManifestText $manifest ([pscustomobject]@{ Submit = $current.BodyData.Submit; Review = $Request.decision; Findings = @($Request.decision.findings) }))
    $script:ObservedState = $Request.decision.value
}
function Assert-TreesIdentical([string]$Source, [string]$Destination) {
    $sourceFiles = @(Get-AllFiles $Source | Sort-Object); $destinationFiles = @(Get-AllFiles $Destination | Sort-Object)
    Assert-That (($sourceFiles -join '|') -ceq ($destinationFiles -join '|')) 'Promotion destination has a different file set.'
    foreach ($file in $sourceFiles) { Assert-That (Test-BytesEqual ([IO.File]::ReadAllBytes((Resolve-SafePath $Source $file $true $true))) ([IO.File]::ReadAllBytes((Resolve-SafePath $Destination $file $true $true)))) 'Promotion destination bytes differ.' }
}
function Invoke-Promote($Root, $Request) {
    $source = Resolve-SafePath $Root $Request.package_path $true $false
    $current = Test-Package $Root $source $Request.package_path $true
    Assert-SpecMatchesManifest $Request.package_specification $current.Manifest
    $script:ObservedState = $current.Manifest.state
    Assert-That ($current.Manifest.state -eq 'aprobado') 'Promote requires an approved package.'
    $destinationRelative = 'proyecto/docs-aprobados/' + $current.Manifest.scope + '/' + $current.Manifest.package_id
    $script:ObservedPackagePath = $destinationRelative
    $destination = Resolve-SafePath $Root $destinationRelative $false $false
    if ([IO.Directory]::Exists($destination) -or [IO.File]::Exists($destination)) {
        Assert-That ([IO.Directory]::Exists($destination) -and -not (Test-Reparse $destination)) 'Promotion destination is incompatible.'
        $approved = Test-Package $Root $destination $destinationRelative $false
        Assert-That ($approved.Manifest.state -eq 'aprobado') 'Promotion destination is not approved.'
        Assert-TreesIdentical $source $destination
        return
    }
    $parent = [IO.Path]::GetDirectoryName($destination)
    if (-not [IO.Directory]::Exists($parent)) {
        $projectDirectory = Resolve-SafePath $Root 'proyecto' $false $false
        if (-not [IO.Directory]::Exists($projectDirectory)) { [IO.Directory]::CreateDirectory($projectDirectory) | Out-Null }
        $approvedDirectory = [IO.Path]::Combine($projectDirectory, 'docs-aprobados')
        if (-not [IO.Directory]::Exists($approvedDirectory)) { [IO.Directory]::CreateDirectory($approvedDirectory) | Out-Null }
        Assert-That (-not (Test-Reparse $approvedDirectory)) 'Approved root is a reparse point.'
        [IO.Directory]::CreateDirectory($parent) | Out-Null
    }
    Assert-That (-not (Test-Reparse $parent)) 'Promotion destination parent is a reparse point.'
    $staging = [IO.Path]::Combine($parent, ('.docs-review-staging-' + [Guid]::NewGuid().ToString('N')))
    [IO.Directory]::CreateDirectory($staging) | Out-Null
    foreach ($file in @(Get-AllFiles $source)) {
        $target = [IO.Path]::Combine($staging, $file.Replace('/', [IO.Path]::DirectorySeparatorChar)); $targetParent = [IO.Path]::GetDirectoryName($target)
        if (-not [IO.Directory]::Exists($targetParent)) { [IO.Directory]::CreateDirectory($targetParent) | Out-Null }
        [IO.File]::Copy((Resolve-SafePath $source $file $true $true), $target)
    }
    Assert-TreesIdentical $source $staging
    # The caller holds the scope lock; revalidate source and destination ancestors immediately before publication.
    $checkedRoot = Assert-SafeRoot $Root
    $checkedSource = Resolve-SafePath $checkedRoot $Request.package_path $true $false
    $checkedDestination = Resolve-SafePath $checkedRoot $destinationRelative $false $false
    Assert-That ($checkedSource -ceq $source -and $checkedDestination -ceq $destination -and -not [IO.Directory]::Exists($checkedDestination) -and -not [IO.File]::Exists($checkedDestination)) 'Promotion destination changed before publication.'
    Assert-TreesIdentical $checkedSource $staging
    [IO.Directory]::Move($staging, $checkedDestination)
}
function Invoke-Validate($Root, $Request) {
    $package = Resolve-SafePath $Root $Request.package_path $true $false
    # Validate is read-only: active verification packages recheck live sources; terminal history and approved copies do not.
    $current = Test-Package $Root $package $Request.package_path $false $true
    Assert-SpecMatchesManifest $Request.package_specification $current.Manifest
    $script:ObservedState = $current.Manifest.state
    if ($Request.package_path -match '^proyecto/docs-aprobados/') { Assert-That ($current.Manifest.state -eq 'aprobado') 'An approved-copy path must contain an approved package.' }
}

try {
    Assert-That ($PSVersionTable.PSEdition -eq 'Desktop' -and $PSVersionTable.PSVersion.Major -eq 5 -and $PSVersionTable.PSVersion.Minor -eq 1) 'This backend requires Windows PowerShell 5.1 Desktop.'
    $request = Read-JsonObject $RequestPath 'Request JSON'
    $root = $null
    $request = Read-Request $request ([ref]$root)
    if ($Operation -eq 'Validate') {
        Invoke-Validate $root $request
    }
    else {
        # The persistent lock is infrastructure outside every package, scoped by project root and scope.
        Invoke-WithScopeLock $root $request.package_specification.scope {
            # The captured request is never re-read; only filesystem state is revalidated under the lock.
            $lockedRoot = Assert-SafeRoot $root
            switch ($Operation) {
                'Prepare' { Invoke-Prepare $lockedRoot $request }
                'Submit' { Invoke-Submit $lockedRoot $request }
                'RecordDecision' { Invoke-RecordDecision $lockedRoot $request }
                'Promote' { Invoke-Promote $lockedRoot $request }
            }
        }
    }
    Write-Result $true ''
}
catch {
    $message = $_.Exception.Message
    if ([string]::IsNullOrWhiteSpace($message)) { $message = 'The operation was blocked.' }
    Write-Result $false $message
}
