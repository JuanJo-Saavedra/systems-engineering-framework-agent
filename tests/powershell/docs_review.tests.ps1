# Native Windows PowerShell 5.1 RED contract for runtime/skills/docs-review/scripts/docs_review.ps1.
# No Pester, modules, Python, Git, pwsh, or external executables are used.  This
# file returns 0 only when every assertion passes; it is intentionally RED until
# the docs-review backend exists.
# Scope-lock concurrency coverage is intentionally static/pending: no readable,
# real PS5.1 runspace scenario was added, and this suite must not simulate one.
#
# v1 request/output choice (to be copied into the manifest-contract by the parent):
# request = { schema_version: 1, project_root: <absolute>, package_specification:
# { package_id, scope, phase, maturity, revision, predecessor_package_id, artifacts },
# package_path?: <project-relative>, attestation?: <object>, decision?: <object> }
# result = { ok: <bool>, operation: <exact operation>, blocked: <bool>, state:
# <state|null>, errors: <array>, package_path?: <project-relative> }.  All output
# is one JSON object and no diagnostic prose is permitted on stdout.

if ($PSVersionTable.PSEdition -ne 'Desktop' -or $PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1) {
    [Console]::Error.WriteLine('docs-review native contract requires Windows PowerShell Desktop 5.1; this suite did not run.')
    exit 1
}

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:Failures = New-Object System.Collections.ArrayList
$script:TestRoot = $null
$script:Backend = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'runtime\skills\docs-review\scripts\docs_review.ps1'

function Add-Failure([string]$Message) {
    [void]$script:Failures.Add($Message)
    [Console]::Error.WriteLine("FAIL: $Message")
}

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function Assert-Equal($Expected, $Actual, [string]$Message) {
    if ($Expected -cne $Actual) { throw "$Message. Expected: [$Expected]; actual: [$Actual]" }
}

function Assert-BytesEqual([byte[]]$Expected, [byte[]]$Actual, [string]$Message) {
    if ($Expected.Length -ne $Actual.Length) { throw "$Message. Byte lengths differ." }
    for ($i = 0; $i -lt $Expected.Length; $i++) {
        if ($Expected[$i] -ne $Actual[$i]) { throw "$Message. Byte differs at offset $i." }
    }
}

function Invoke-Case([string]$Name, [scriptblock]$Body) {
    try {
        & $Body
        [Console]::WriteLine("PASS: $Name")
    }
    catch {
        Add-Failure "$Name -- $($_.Exception.Message)"
    }
}

function Write-Utf8NoBom([string]$Path, [string]$Text) {
    $directory = Split-Path -Parent $Path
    if (-not [IO.Directory]::Exists($directory)) { [IO.Directory]::CreateDirectory($directory) | Out-Null }
    [IO.File]::WriteAllText($Path, $Text, (New-Object Text.UTF8Encoding($false)))
}

function Read-Bytes([string]$Path) { return [IO.File]::ReadAllBytes($Path) }

function Get-Sha256([string]$Path) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes($Path)))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
}

function New-TestProject([string]$Name) {
    $root = Join-Path $script:TestRoot $Name
    [IO.Directory]::CreateDirectory($root) | Out-Null
    $live = Join-Path $root 'proyecto\fases\alpha'
    [IO.Directory]::CreateDirectory($live) | Out-Null
    # Preserve non-text raw bytes as part of the hash contract.
    [IO.File]::WriteAllBytes((Join-Path $live 'uno.md'), [byte[]](0x75,0x6e,0x6f,0x0d,0x0a,0xff))
    Write-Utf8NoBom (Join-Path $live 'dos.md') "dos`n"
    return $root
}

function New-Artifact([string]$Path, [string]$DocumentType, $CarriedForwardFrom = $null) {
    return [ordered]@{
        path = $Path
        document_type = $DocumentType
        source_path = "proyecto/fases/alpha/$Path"
        carried_forward_from = $CarriedForwardFrom
    }
}

function New-PackageSpecification([string]$PackageId = 'alpha-formal-r001', [int]$Revision = 1, $Predecessor = $null, $Artifacts = $null) {
    if ($null -eq $Artifacts) {
        $Artifacts = @(
            (New-Artifact 'uno.md' 'alpha_primary'),
            (New-Artifact 'dos.md' 'alpha_secondary')
        )
    }
    return [ordered]@{
        package_id = $PackageId
        scope = 'alpha'
        phase = 'ALPHA'
        maturity = 'formal'
        revision = $Revision
        predecessor_package_id = $Predecessor
        artifacts = $Artifacts
    }
}

function New-Request([string]$ProjectRoot, $Specification, [string]$PackagePath = $null, $Attestation = $null, $Decision = $null) {
    $request = [ordered]@{
        schema_version = 1
        project_root = $ProjectRoot
        package_specification = $Specification
    }
    if ($null -ne $PackagePath) { $request.package_path = $PackagePath }
    if ($null -ne $Attestation) { $request.attestation = $Attestation }
    if ($null -ne $Decision) { $request.decision = $Decision }
    return $request
}

function Write-Request([string]$ProjectRoot, $Request, [string]$Name) {
    $path = Join-Path $ProjectRoot ("$Name.request.json")
    Write-Utf8NoBom $path ($Request | ConvertTo-Json -Depth 12)
    return $path
}

function Assert-ResultShape($Result, [string]$Operation) {
    foreach ($name in @('ok', 'operation', 'blocked', 'state', 'errors')) {
        Assert-True ($null -ne $Result.PSObject.Properties[$name]) "result lacks required '$name'"
    }
    Assert-Equal $Operation ([string]$Result.operation) 'result operation is not correlated to request'
    Assert-True (($Result.ok -is [bool]) -and ($Result.blocked -is [bool])) 'result ok and blocked must be JSON booleans'
    Assert-True ($Result.errors -is [System.Collections.IEnumerable]) 'result errors must be an array'
}

function Invoke-DocsReview([string]$Operation, [string]$RequestPath, [bool]$ExpectSuccess) {
    Assert-True ([IO.File]::Exists($script:Backend)) "backend absent: $script:Backend"
    $stderrPath = [IO.Path]::GetTempFileName()
    try {
        $global:LASTEXITCODE = 0
        $lines = @(& $script:Backend -Operation $Operation -RequestPath $RequestPath 2> $stderrPath)
        $exitCode = $global:LASTEXITCODE
        $json = (($lines | ForEach-Object { [string]$_ }) -join "`n").Trim()
        if ([string]::IsNullOrWhiteSpace($json)) {
$stderr = [IO.File]::ReadAllText($stderrPath).Trim()
if ([string]::IsNullOrWhiteSpace($stderr)) { throw 'backend emitted no JSON result' }
throw "backend emitted no JSON result; stderr: $stderr"
        }
        try { $result = $json | ConvertFrom-Json -ErrorAction Stop }
        catch {
$stderr = [IO.File]::ReadAllText($stderrPath).Trim()
if ([string]::IsNullOrWhiteSpace($stderr)) { throw "backend stdout must be a single machine-readable JSON object: $json" }
throw "backend stdout must be a single machine-readable JSON object: $json; stderr: $stderr"
        }
        Assert-ResultShape $result $Operation
        if ($ExpectSuccess) {
Assert-Equal 0 $exitCode "successful $Operation must exit zero"
Assert-True ([bool]$result.ok) "successful $Operation result must set ok=true"
Assert-True (-not [bool]$result.blocked) "successful $Operation result must set blocked=false"
        } else {
Assert-True ($exitCode -ne 0) "blocked $Operation must exit non-zero"
Assert-True (-not [bool]$result.ok) "blocked $Operation result must set ok=false"
Assert-True ([bool]$result.blocked) "blocked $Operation result must set blocked=true"
Assert-True (@($result.errors).Count -gt 0) "blocked $Operation must describe at least one error"
        }
        return $result
    }
    finally {
        if ([IO.File]::Exists($stderrPath)) { [IO.File]::Delete($stderrPath) }
    }
}

function Get-PackageRelativePath($Result) {
    Assert-True ($null -ne $Result.PSObject.Properties['package_path']) 'successful package operation must return package_path'
    $path = [string]$Result.package_path
    Assert-True (-not [IO.Path]::IsPathRooted($path)) 'result package_path must be project-relative'
    Assert-True ($path -notmatch '(^|[\\/])\.\.([\\/]|$)') 'result package_path must not traverse'
    Assert-True ($path -match '/') 'result package_path must remain slash-separated canonical contract data'
    Assert-True ($path -notmatch '\\') 'result package_path must not be rewritten with filesystem separators'
    return $path
}

function Get-ManifestJson([string]$ManifestPath) {
    $bytes = Read-Bytes $ManifestPath
    Assert-True (($bytes.Length -lt 3) -or -not ($bytes[0] -eq 0xef -and $bytes[1] -eq 0xbb -and $bytes[2] -eq 0xbf)) 'manifest must be UTF-8 without BOM'
    $text = [Text.Encoding]::UTF8.GetString($bytes)
    Assert-True ($text.IndexOf("`r") -lt 0) 'manifest must use LF, never CRLF'
    $match = [regex]::Match($text, '\A---\n(?<json>.*?)\n---\n', [Text.RegularExpressions.RegexOptions]::Singleline)
    Assert-True $match.Success 'manifest must begin with exactly one JSON frontmatter block'
    $json = $match.Groups['json'].Value
    Assert-True ($json.TrimStart().StartsWith('{')) 'frontmatter must be JSON, not free YAML'
    try { return $json | ConvertFrom-Json -ErrorAction Stop }
    catch { throw 'manifest frontmatter JSON is not parseable by Windows PowerShell 5.1 ConvertFrom-Json' }
}

function Prepare-Package([string]$ProjectRoot, $Specification = $null) {
    if ($null -eq $Specification) { $Specification = New-PackageSpecification }
    $request = New-Request $ProjectRoot $Specification
    $result = Invoke-DocsReview 'Prepare' (Write-Request $ProjectRoot $request 'prepare') $true
    $relative = Get-PackageRelativePath $result
    $package = Join-Path $ProjectRoot $relative
    Assert-True ([IO.Directory]::Exists($package)) 'Prepare did not publish returned package_path'
    Assert-Equal 'pendiente' ([string]$result.state) 'Prepare must create pendiente package'
    return [pscustomobject]@{ Result = $result; Package = $package; Relative = $relative; Specification = $Specification }
}

function Submit-Package([string]$ProjectRoot, $Prepared) {
    $attestation = [ordered]@{ identity = 'submitter@example.test'; role = 'author'; at = '2026-01-02T03:04:05Z'; source = 'explicit human instruction' }
    $request = New-Request $ProjectRoot $Prepared.Specification $Prepared.Relative $attestation $null
    $result = Invoke-DocsReview 'Submit' (Write-Request $ProjectRoot $request 'submit') $true
    Assert-Equal 'en_verificacion' ([string]$result.state) 'Submit must transition pendiente to en_verificacion'
    return [pscustomobject]@{ Result = $result; Request = $request }
}

function Record-Decision([string]$ProjectRoot, $Prepared, [string]$Value) {
    $decision = [ordered]@{
        value = $Value
        reviewer = 'reviewer@example.test'
        role = 'independent reviewer'
        at = '2026-01-03T03:04:05Z'
        source = 'explicit human decision'
        findings = @([ordered]@{ path = 'uno.md'; outcome = $Value; note = 'human finding' })
    }
    $request = New-Request $ProjectRoot $Prepared.Specification $Prepared.Relative $null $decision
    return Invoke-DocsReview 'RecordDecision' (Write-Request $ProjectRoot $request "decision-$Value") $true
}

function Snapshot-Tree([string]$Root) {
    $snapshot = @{}
    Get-ChildItem -LiteralPath $Root -Recurse -Force | Where-Object { -not $_.PSIsContainer } | ForEach-Object {
        $relative = $_.FullName.Substring($Root.Length).TrimStart('\\')
        $snapshot[$relative] = Read-Bytes $_.FullName
    }
    return $snapshot
}

function Assert-TreesByteIdentical([string]$ExpectedRoot, [string]$ActualRoot, [string]$Message) {
    $expected = Snapshot-Tree $ExpectedRoot
    $actual = Snapshot-Tree $ActualRoot
    Assert-Equal (($expected.Keys | Sort-Object) -join '|') (($actual.Keys | Sort-Object) -join '|') "$Message file set"
    foreach ($key in $expected.Keys) { Assert-BytesEqual $expected[$key] $actual[$key] "$Message $key" }
}

function Assert-BlockedPrepare([string]$Name, [string]$ProjectRoot, $Specification) {
    $request = New-Request $ProjectRoot $Specification
    return Invoke-DocsReview 'Prepare' (Write-Request $ProjectRoot $request $Name) $false
}

$script:TestRoot = Join-Path ([IO.Path]::GetTempPath()) ('docs-review-contract-' + [Guid]::NewGuid().ToString('N'))
try {
    Invoke-Case 'backend exists at the sole PS5.1 product path' {
        Assert-True ([IO.File]::Exists($script:Backend)) "missing docs-review backend: $script:Backend"
    }

    Invoke-Case 'Prepare creates a complete pending package with raw-byte SHA-256' {
        $root = New-TestProject 'prepare'
        $prepared = Prepare-Package $root
        $manifest = Get-ManifestJson (Join-Path $prepared.Package 'manifest.md')
        Assert-Equal 'pendiente' ([string]$manifest.state) 'manifest state after Prepare'
        Assert-Equal 2 @($manifest.artifacts).Count 'Prepare must snapshot the exact requested artifact set'
        $one = @($manifest.artifacts | Where-Object { $_.path -eq 'uno.md' })[0]
        Assert-Equal (Get-Sha256 (Join-Path $root 'proyecto\fases\alpha\uno.md')) ([string]$one.content_sha256) 'content_sha256 must hash raw source bytes'
        Assert-Equal $null $one.carried_forward_from 'r001 artifacts must declare carried_forward_from null'
    }

    Invoke-Case 'package_path stays slash-canonical when the harness forwards it to the backend' {
        $root = New-TestProject 'package-path-canonical'
        $prepared = Prepare-Package $root
        Assert-True ($prepared.Relative -match '^proyecto/docs-verificacion/') 'Prepare must return canonical slash-separated package_path'
        Assert-True ($prepared.Relative -notmatch '\\') 'harness must not convert package_path to filesystem separators'
        $submitted = Submit-Package $root $prepared
        Assert-Equal $prepared.Relative ([string]$submitted.Request.package_path) 'Submit request must forward package_path unchanged'
    }

    Invoke-Case 'Prepare is idempotent and never mutates a coherent pending package' {
        $root = New-TestProject 'prepare-idempotent'
        $spec = New-PackageSpecification
        $first = Prepare-Package $root $spec
        $before = Snapshot-Tree $first.Package
        $second = Prepare-Package $root $spec
        Assert-Equal $first.Relative $second.Relative 'idempotent Prepare must return the original package'
        $after = Snapshot-Tree $first.Package
        Assert-Equal (($before.Keys | Sort-Object) -join '|') (($after.Keys | Sort-Object) -join '|') 'idempotent Prepare file set'
        foreach ($key in $before.Keys) { Assert-BytesEqual $before[$key] $after[$key] "idempotent Prepare $key" }
    }

    Invoke-Case 'Submit requires explicit stable attestation and is idempotent only for the same data' {
        $root = New-TestProject 'submit'
        $prepared = Prepare-Package $root
        $submitted = Submit-Package $root $prepared
        $before = Snapshot-Tree $prepared.Package
        $again = Invoke-DocsReview 'Submit' (Write-Request $root $submitted.Request 'submit-again') $true
        Assert-Equal 'en_verificacion' ([string]$again.state) 'same Submit must be idempotent'
        $after = Snapshot-Tree $prepared.Package
        foreach ($key in $before.Keys) { Assert-BytesEqual $before[$key] $after[$key] "idempotent Submit $key" }
        $changed = $submitted.Request
        $changed.attestation.identity = 'other@example.test'
        Invoke-DocsReview 'Submit' (Write-Request $root $changed 'submit-conflict') $false | Out-Null
    }

    Invoke-Case 'RecordDecision refuses an implicit decision, then records only explicit human approval' {
        $root = New-TestProject 'decision-explicit'
        $prepared = Prepare-Package $root
        Submit-Package $root $prepared | Out-Null
        $before = Snapshot-Tree $prepared.Package
        $missing = New-Request $root $prepared.Specification $prepared.Relative $null $null
        Invoke-DocsReview 'RecordDecision' (Write-Request $root $missing 'missing-decision') $false | Out-Null
        $after = Snapshot-Tree $prepared.Package
        foreach ($key in $before.Keys) { Assert-BytesEqual $before[$key] $after[$key] "implicit decision must not mutate $key" }
        $result = Record-Decision $root $prepared 'aprobado'
        Assert-Equal 'aprobado' ([string]$result.state) 'explicit human approval must be recorded'
    }

    Invoke-Case 'terminal package is immutable and incompatible decisions are rejected' {
        $root = New-TestProject 'terminal'
        $prepared = Prepare-Package $root
        Submit-Package $root $prepared | Out-Null
        Record-Decision $root $prepared 'aprobado' | Out-Null
        $before = Snapshot-Tree $prepared.Package
        $same = Record-Decision $root $prepared 'aprobado'
        Assert-Equal 'aprobado' ([string]$same.state) 'same terminal decision must be read-idempotent'
        Invoke-DocsReview 'RecordDecision' (Write-Request $root (New-Request $root $prepared.Specification $prepared.Relative $null ([ordered]@{ value = 'rechazado'; reviewer = 'reviewer@example.test'; role = 'independent reviewer'; at = '2026-01-03T03:04:05Z'; source = 'explicit human decision'; findings = @() })) 'terminal-conflict') $false | Out-Null
        $after = Snapshot-Tree $prepared.Package
        foreach ($key in $before.Keys) { Assert-BytesEqual $before[$key] $after[$key] "terminal package changed: $key" }
    }

    Invoke-Case 'rejection is package-wide and cannot be promoted as partial approval' {
        $root = New-TestProject 'rejected'
        $prepared = Prepare-Package $root
        Submit-Package $root $prepared | Out-Null
        $result = Record-Decision $root $prepared 'rechazado'
        Assert-Equal 'rechazado' ([string]$result.state) 'rejection must make the whole package terminal'
        Assert-True ([IO.File]::Exists((Join-Path $prepared.Package 'uno.md'))) 'rejected package must retain complete snapshots'
        Assert-True ([IO.File]::Exists((Join-Path $prepared.Package 'dos.md'))) 'rejected package must retain complete snapshots'
        Invoke-DocsReview 'Promote' (Write-Request $root (New-Request $root $prepared.Specification $prepared.Relative ([ordered]@{ identity = 'promoter@example.test'; at = '2026-01-04T03:04:05Z'; source = 'explicit human instruction' }) $null) 'reject-promote') $false | Out-Null
    }

    Invoke-Case 'submitted live-source changes block a decision and preserve state' {
        $root = New-TestProject 'frozen-live'
        $prepared = Prepare-Package $root
        Submit-Package $root $prepared | Out-Null
        Write-Utf8NoBom (Join-Path $root 'proyecto\fases\alpha\uno.md') "changed after submit`n"
        $before = Read-Bytes (Join-Path $prepared.Package 'manifest.md')
        $decision = New-Request $root $prepared.Specification $prepared.Relative $null ([ordered]@{ value = 'aprobado'; reviewer = 'reviewer@example.test'; role = 'independent reviewer'; at = '2026-01-03T03:04:05Z'; source = 'explicit human decision'; findings = @() })
        Invoke-DocsReview 'RecordDecision' (Write-Request $root $decision 'frozen-decision') $false | Out-Null
        Assert-BytesEqual $before (Read-Bytes (Join-Path $prepared.Package 'manifest.md')) 'failed decision must not alter manifest'
    }

    Invoke-Case 'Promote requires explicit approval and produces an idempotent byte-identical copy' {
        $root = New-TestProject 'promote'
        $prepared = Prepare-Package $root
        Invoke-DocsReview 'Promote' (Write-Request $root (New-Request $root $prepared.Specification $prepared.Relative ([ordered]@{ identity = 'promoter@example.test'; at = '2026-01-04T03:04:05Z'; source = 'explicit human instruction' }) $null) 'premature-promote') $false | Out-Null
        Submit-Package $root $prepared | Out-Null
        Record-Decision $root $prepared 'aprobado' | Out-Null
        $promotion = [ordered]@{ identity = 'promoter@example.test'; at = '2026-01-04T03:04:05Z'; source = 'explicit human instruction' }
        $result = Invoke-DocsReview 'Promote' (Write-Request $root (New-Request $root $prepared.Specification $prepared.Relative $promotion $null) 'promote') $true
        $approvedRelative = Get-PackageRelativePath $result
        $approved = Join-Path $root $approvedRelative
        Assert-True ($approvedRelative -like 'proyecto/docs-aprobados/*') 'Promote must publish under proyecto/docs-aprobados'
        Assert-TreesByteIdentical $prepared.Package $approved 'promotion must be byte-identical'
        $again = Invoke-DocsReview 'Promote' (Write-Request $root (New-Request $root $prepared.Specification $prepared.Relative $promotion $null) 'promote-again') $true
        Assert-Equal $approvedRelative (Get-PackageRelativePath $again) 'identical existing promotion must be idempotent'
    }

    Invoke-Case 'Validate is read-only and rejects partial packages, extras, and noncanonical JSON' {
        $root = New-TestProject 'validate'
        $prepared = Prepare-Package $root
        $before = Snapshot-Tree $prepared.Package
        $valid = Invoke-DocsReview 'Validate' (Write-Request $root (New-Request $root $prepared.Specification $prepared.Relative) 'validate-good') $true
        Assert-Equal 'pendiente' ([string]$valid.state) 'Validate reports observed state'
        $after = Snapshot-Tree $prepared.Package
        foreach ($key in $before.Keys) { Assert-BytesEqual $before[$key] $after[$key] "Validate wrote $key" }
        [IO.File]::WriteAllBytes((Join-Path $prepared.Package 'unexpected.md'), [byte[]](1))
        Invoke-DocsReview 'Validate' (Write-Request $root (New-Request $root $prepared.Specification $prepared.Relative) 'validate-extra') $false | Out-Null
        [IO.File]::Delete((Join-Path $prepared.Package 'unexpected.md'))
        [IO.File]::Delete((Join-Path $prepared.Package 'dos.md'))
        Invoke-DocsReview 'Validate' (Write-Request $root (New-Request $root $prepared.Specification $prepared.Relative) 'validate-partial') $false | Out-Null
        # Fresh package isolates the canonical-JSON violation from the partial fixture.
        $canonicalRoot = New-TestProject 'validate-canonical'
        $canonical = Prepare-Package $canonicalRoot
        $manifestPath = Join-Path $canonical.Package 'manifest.md'
        $manifestText = [Text.Encoding]::UTF8.GetString((Read-Bytes $manifestPath)).Replace('"manifest_version": 1', '"manifest_version" : 1')
        Write-Utf8NoBom $manifestPath $manifestText
        $canonicalRequest = New-Request $canonicalRoot $canonical.Specification $canonical.Relative
        Invoke-DocsReview 'Validate' (Write-Request $canonicalRoot $canonicalRequest 'validate-noncanonical') $false | Out-Null
    }

    Invoke-Case 'Validate rejects an extra empty package directory without writing' {
        $root = New-TestProject 'validate-empty-directory'
        $prepared = Prepare-Package $root
        $manifestBefore = Read-Bytes (Join-Path $prepared.Package 'manifest.md')
        [IO.Directory]::CreateDirectory((Join-Path $prepared.Package 'unexpected-empty-directory')) | Out-Null
        $request = New-Request $root $prepared.Specification $prepared.Relative
        Invoke-DocsReview 'Validate' (Write-Request $root $request 'validate-empty-directory') $false | Out-Null
        Assert-BytesEqual $manifestBefore (Read-Bytes (Join-Path $prepared.Package 'manifest.md')) 'blocked Validate must not write manifest for an empty directory'
        Assert-True ([IO.Directory]::Exists((Join-Path $prepared.Package 'unexpected-empty-directory'))) 'Validate must not remove the unexpected empty directory'
    }

    Invoke-Case 'Validate blocks an active package when the live source diverges and writes nothing' {
        $root = New-TestProject 'validate-live-diverged'
        $prepared = Prepare-Package $root
        Write-Utf8NoBom (Join-Path $root 'proyecto\fases\alpha\uno.md') "changed before validation`n"
        $before = Snapshot-Tree $prepared.Package
        $request = New-Request $root $prepared.Specification $prepared.Relative
        Invoke-DocsReview 'Validate' (Write-Request $root $request 'validate-live-diverged') $false | Out-Null
        $after = Snapshot-Tree $prepared.Package
        Assert-Equal (($before.Keys | Sort-Object) -join '|') (($after.Keys | Sort-Object) -join '|') 'blocked Validate changed package file set'
        foreach ($key in $before.Keys) { Assert-BytesEqual $before[$key] $after[$key] "blocked Validate wrote $key" }
    }

    Invoke-Case 'Prepare rejects traversal, absolute paths, duplicate artifacts, and reparse-point escapes' {
        $root = New-TestProject 'invalid-input'
        $traversal = New-PackageSpecification 'alpha-formal-r001' 1 $null @((New-Artifact '../escape.md' 'bad'))
        Assert-BlockedPrepare 'traversal' $root $traversal | Out-Null
        $absolute = New-PackageSpecification 'alpha-formal-r001' 1 $null @((New-Artifact 'C:\escape.md' 'bad'))
        Assert-BlockedPrepare 'absolute' $root $absolute | Out-Null
        $duplicates = New-PackageSpecification 'alpha-formal-r001' 1 $null @((New-Artifact 'uno.md' 'one'), (New-Artifact 'uno.md' 'two'))
        Assert-BlockedPrepare 'duplicate' $root $duplicates | Out-Null
        $outside = Join-Path $root 'outside'
        [IO.Directory]::CreateDirectory($outside) | Out-Null
        Write-Utf8NoBom (Join-Path $outside 'secret.md') "not a source`n"
        $link = Join-Path $root 'proyecto\fases\alpha\linked'
        New-Item -ItemType Junction -Path $link -Target $outside | Out-Null
        $reparse = New-PackageSpecification 'alpha-formal-r001' 1 $null @((New-Artifact 'linked/secret.md' 'bad'))
        Assert-BlockedPrepare 'reparse' $root $reparse | Out-Null
    }

    Invoke-Case 'Prepare rejects colon ADS syntax in every relative-path position' {
        $root = New-TestProject 'ads-segments'
        foreach ($path in @('ads:stream/uno.md', 'nested/uno.md:stream')) {
            $specification = New-PackageSpecification 'alpha-formal-r001' 1 $null @((New-Artifact $path 'bad'))
            Assert-BlockedPrepare ('ads-' + $path.Replace('/', '-').Replace(':', '-')) $root $specification | Out-Null
        }
        $prepared = Prepare-Package $root
        $adsPackagePath = $prepared.Relative.Replace('alpha-formal-r001', 'alpha-formal-r001:stream')
        $request = New-Request $root $prepared.Specification $adsPackagePath
        Invoke-DocsReview 'Validate' (Write-Request $root $request 'ads-package-path') $false | Out-Null
    }

    Invoke-Case 'Prepare rejects Windows reserved names and trailing dot-or-space segments' {
        $root = New-TestProject 'windows-segments'
        foreach ($path in @('CON.md', 'nested/AUX/uno.md', 'trailing./uno.md', 'nested /uno.md')) {
            $specification = New-PackageSpecification 'alpha-formal-r001' 1 $null @((New-Artifact $path 'bad'))
            Assert-BlockedPrepare ('windows-' + $path.Replace('/', '-').Replace(' ', 'space')) $root $specification | Out-Null
        }
    }

    Invoke-Case 'Prepare rejects roots reached through an ancestor junction, UNC paths, and device syntax' {
        $realRoot = New-TestProject 'root-ancestor-target\project'
        $ancestorJunction = Join-Path $script:TestRoot 'root-ancestor-junction'
        New-Item -ItemType Junction -Path $ancestorJunction -Target (Split-Path -Parent $realRoot) | Out-Null
        $throughJunction = Join-Path $ancestorJunction (Split-Path -Leaf $realRoot)
        Assert-BlockedPrepare 'root-ancestor-junction' $throughJunction (New-PackageSpecification) | Out-Null

        # The request files remain local so the backend can run before rejecting the
        # hostile project_root values themselves.
        $uncRequest = New-Request '\\server\share\project' (New-PackageSpecification)
        Invoke-DocsReview 'Prepare' (Write-Request $realRoot $uncRequest 'root-unc-path') $false | Out-Null
        $extendedDeviceRequest = New-Request ('\\?\' + $realRoot) (New-PackageSpecification)
        Invoke-DocsReview 'Prepare' (Write-Request $realRoot $extendedDeviceRequest 'root-extended-device-path') $false | Out-Null
        $localDeviceRequest = New-Request ('\\.\' + $realRoot) (New-PackageSpecification)
        Invoke-DocsReview 'Prepare' (Write-Request $realRoot $localDeviceRequest 'root-local-device-path') $false | Out-Null
    }

    Invoke-Case 'carried_forward_from requires a terminal predecessor and byte-identical snapshot' {
        $root = New-TestProject 'carried-forward'
        $first = Prepare-Package $root
        Submit-Package $root $first | Out-Null
        Record-Decision $root $first 'aprobado' | Out-Null
        $carried = [ordered]@{ package_id = 'alpha-formal-r001'; path = 'uno.md' }
        $artifacts = @((New-Artifact 'uno.md' 'alpha_primary' $carried), (New-Artifact 'dos.md' 'alpha_secondary'))
        $secondSpec = New-PackageSpecification 'alpha-formal-r002' 2 'alpha-formal-r001' $artifacts
        $second = Prepare-Package $root $secondSpec
        $manifest = Get-ManifestJson (Join-Path $second.Package 'manifest.md')
        $entry = @($manifest.artifacts | Where-Object { $_.path -eq 'uno.md' })[0]
        Assert-Equal 'alpha-formal-r001' ([string]$entry.carried_forward_from.package_id) 'manifest preserves carried predecessor'
        Assert-Equal 'uno.md' ([string]$entry.carried_forward_from.path) 'manifest preserves carried artifact path'
        Assert-Equal (Get-Sha256 (Join-Path $first.Package 'uno.md')) ([string]$entry.content_sha256) 'carried snapshot hash must stay byte-identical'
        Submit-Package $root $second | Out-Null
        Record-Decision $root $second 'aprobado' | Out-Null
        $carriedFromImmediate = [ordered]@{ package_id = 'alpha-formal-r002'; path = 'uno.md' }
        $thirdArtifacts = @((New-Artifact 'uno.md' 'alpha_primary' $carriedFromImmediate), (New-Artifact 'dos.md' 'alpha_secondary'))
        Write-Utf8NoBom (Join-Path $root 'proyecto\fases\alpha\uno.md') "diverged`n"
        $badSpec = New-PackageSpecification 'alpha-formal-r003' 3 'alpha-formal-r002' $thirdArtifacts
        $blocked = Assert-BlockedPrepare 'carried-diverged' $root $badSpec
        $errors = (@($blocked.errors) -join "`n")
        Assert-True ($errors -match '(?i)(snapshot|hash|bytes).*(diff|diverg)') 'r003 carried-forward failure must report byte/hash divergence from terminal r002'
        Assert-True ($errors -notmatch '(?i)immediate prior') 'r003 must cite r002 so failure cannot be predecessor-chain validation'
    }
}
finally {
    # Test roots are generated fixtures only. Do not clean an existing root if setup
    # did not own it; the GUID makes collision infeasible and preserves diagnostics.
    if ($null -ne $script:TestRoot -and [IO.Directory]::Exists($script:TestRoot)) {
        [IO.Directory]::Delete($script:TestRoot, $true)
    }
}

if ($script:Failures.Count -gt 0) {
    [Console]::Error.WriteLine("docs-review contract failures: $($script:Failures.Count)")
    exit 1
}
exit 0
