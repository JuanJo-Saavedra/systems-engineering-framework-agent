"""RED contract for the generic ``docs-review`` product surface.

This is intentionally a static/packaging test: Windows PowerShell 5.1 behaviour
belongs to ``tests/powershell/docs_review.tests.ps1``.  It makes the future
product boundaries and install mirror observable without requiring PowerShell on
this Linux test runner.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = REPO_ROOT / "runtime" / "skills" / "docs-review"
SKILL = SKILL_ROOT / "SKILL.md"
SCRIPT = SKILL_ROOT / "scripts" / "docs_review.ps1"
REFERENCE = SKILL_ROOT / "references" / "manifest-contract.md"
REGISTRY = REPO_ROOT / "runtime" / "catalogo" / "skill-registry.md"
PAYLOAD_ROOT = REPO_ROOT / "src" / "se_agent" / "_payload" / ".agents" / "skills" / "docs-review"

# A docs-review package is a payload-bearing skill.  The committed payload must
# mirror every product file, including the reference consumed by the skill.
REQUIRED_CANONICAL = (SKILL, SCRIPT, REFERENCE)


def _relative(root: Path, path: Path) -> PurePosixPath:
    return PurePosixPath(*path.relative_to(root).parts)


def _frontmatter_name(text: str) -> str | None:
    match = re.match(r"\A---\n(?P<header>.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    name = re.search(r"^name:\s*([^\s#]+)\s*$", match.group("header"), re.MULTILINE)
    return name.group(1) if name else None


def test_docs_review_required_product_surfaces_exist() -> None:
    """RED packaging gate: implementation must add skill, PS5.1 backend, and reference.

    The grouped assertion deliberately names *all* absent surfaces so the initial
    RED result is actionable rather than failing one missing path at a time.
    """
    missing = [str(path.relative_to(REPO_ROOT)) for path in REQUIRED_CANONICAL if not path.is_file()]
    assert missing == [], f"docs-review product surfaces missing: {missing}"


def test_docs_review_skill_declares_the_generic_contract_only() -> None:
    """The skill is the reusable docs-review capability, not an F1 implementation."""
    text = SKILL.read_text(encoding="utf-8")
    assert _frontmatter_name(text) == "docs-review", "SKILL.md must publish the exact executable skill id"
    assert "docs_review" in text, "skill must name the conceptual docs_review capability"
    assert "scripts/docs_review.ps1" in text, "skill must bind its sole mechanical backend"
    assert "references/manifest-contract.md" in text, "skill must bind the versioned request/output reference"
    assert "f1-stakeholders-formal" not in text, "generic docs-review must not implement or compose F1"


def test_docs_review_reference_records_the_minimum_machine_contract() -> None:
    """The reference keeps operation request/output vocabulary stable for all consumers.

    The approved design locates the reference at
    ``runtime/skills/docs-review/references/manifest-contract.md``; it defines a v1 JSON
    request with ``project_root`` and operation-specific data, plus a JSON result
    containing ``ok``, ``operation``, ``blocked``, ``state``, and ``errors``.
    """
    text = REFERENCE.read_text(encoding="utf-8")
    for required in (
        "schema_version",
        "project_root",
        "package_specification",
        "package_path",
        '"ok"',
        '"operation"',
        '"blocked"',
        '"state"',
        '"errors"',
        "Prepare",
        "Submit",
        "RecordDecision",
        "Promote",
        "Validate",
    ):
        assert required in text, f"contract reference must define {required!r}"


def test_docs_review_registry_marks_the_exact_generic_catalog_type() -> None:
    """The canonical registry must discover docs-review as only ``tarea puntual``."""
    text = REGISTRY.read_text(encoding="utf-8")
    match = re.search(r"^.*\bdocs-review\b.*$", text, re.MULTILINE)
    assert match is not None, "runtime registry must contain the exact docs-review id"
    assert "tarea puntual" in match.group(0).lower(), "docs-review registry row must use only 'tarea puntual'"


def test_docs_review_payload_is_an_exact_byte_identical_skill_mirror() -> None:
    """Installed `.agents/skills/docs-review` is exact: no missing, extra, or drifted files."""
    assert SKILL_ROOT.is_dir(), f"canonical docs-review skill directory missing: {SKILL_ROOT}"
    assert PAYLOAD_ROOT.is_dir(), f"docs-review payload mirror missing: {PAYLOAD_ROOT}"
    canonical = {
        _relative(SKILL_ROOT, path): path
        for path in sorted(SKILL_ROOT.rglob("*"))
        if path.is_file() and path.name != ".gitkeep"
    }
    mirrored = {
        _relative(PAYLOAD_ROOT, path): path
        for path in sorted(PAYLOAD_ROOT.rglob("*"))
        if path.is_file() and path.name != ".gitkeep"
    }
    assert set(mirrored) == set(canonical), (
        f"payload missing: {sorted(set(canonical) - set(mirrored))}; "
        f"payload extra: {sorted(set(mirrored) - set(canonical))}"
    )
    for rel, source in canonical.items():
        assert mirrored[rel].read_bytes() == source.read_bytes(), f"payload byte mismatch: {rel}"


def _ps_function_body(text: str, name: str) -> str:
    """Return a PowerShell function's lexical body for static contract checks only."""
    match = re.search(
        rf"^function\s+{re.escape(name)}\b(?P<body>.*?)(?=^function\s+|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None, f"backend must define {name}"
    return match.group("body")


def _ps_braced_body(text: str, opening_brace: int) -> str:
    """Return the lexical body paired with ``opening_brace`` for static checks."""
    assert text[opening_brace] == "{", "PowerShell block must start with an opening brace"
    depth = 0
    for index in range(opening_brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[opening_brace + 1 : index]
    raise AssertionError("PowerShell block must have a matching closing brace")


def test_docs_review_backend_has_the_static_ps51_and_fail_closed_guards() -> None:
    """Static essentials only; operational gates are exercised natively on Windows."""
    text = SCRIPT.read_text(encoding="utf-8")
    for operation in ("Prepare", "Submit", "RecordDecision", "Promote", "Validate"):
        assert operation in text, f"backend must expose operation {operation}"
    assert re.search(r"\bOperation\b", text), "backend must accept -Operation"
    assert re.search(r"\bRequestPath\b", text), "backend must accept -RequestPath"
    for required in ("ConvertFrom-Json", "SHA256", "UTF8Encoding", "reparse", "carried_forward_from"):
        assert required.lower() in text.lower(), f"backend must visibly guard {required}"
    assert re.search(r"UTF8Encoding\s*\(\s*\$false\s*\)", text), "generated text must use UTF-8 without BOM"
    assert "`r`n" not in text, "generated output must not select CRLF"
    forbidden = ("Set-ExecutionPolicy", "ExecutionPolicy Bypass", "pwsh", "python", "git ", "Invoke-WebRequest")
    found = [token for token in forbidden if token.lower() in text.lower()]
    assert found == [], f"PS5.1 backend must not depend on or bypass via: {found}"


def test_docs_review_backend_has_static_local_root_path_directory_and_scope_lock_guards() -> None:
    """Make audit-policy implementation anchors visible without claiming runtime behavior.

    Native Windows tests cover the externally observable rejections.  These are only
    lexical regression guards so Linux packaging checks expose removal of the local
    root, segment/directory, and per-scope exclusive-lock policy.
    """
    text = SCRIPT.read_text(encoding="utf-8")
    safe_root = _ps_function_body(text, "Assert-SafeRoot")
    relative_path = _ps_function_body(text, "Assert-RelativePath")
    package_check = _ps_function_body(text, "Test-Package")

    for marker in ("UNC", "\\\\?\\", "\\\\.\\", "Test-Reparse"):
        assert marker.lower() in safe_root.lower(), f"Assert-SafeRoot must visibly reject/check {marker!r}"
    assert re.search(r"Get(?:DirectoryName|Parent)", safe_root), "Assert-SafeRoot must walk and check root ancestors"
    assert re.search(r"IndexOf\s*\(\s*['\"]:\s*['\"]\s*\)|-match\s+['\"][^'\"]*:[^'\"]*['\"]", relative_path), (
        "Assert-RelativePath must visibly reject colon/ADS segments"
    )
    assert re.search(r"TrimEnd|EndsWith\s*\(\s*['\"][. ]", relative_path), (
        "Assert-RelativePath must visibly reject trailing dot-or-space segments"
    )
    for marker in ("CON", "LPT"):
        assert marker.lower() in relative_path.lower(), f"Assert-RelativePath must visibly guard {marker!r}"
    assert re.search(r"expected.*director|director.*expected", package_check, re.IGNORECASE | re.DOTALL), (
        "Test-Package must visibly compare package directories, including empty directories"
    )

    mutex_lock = all(marker in text for marker in ("Mutex", "WaitOne", "ReleaseMutex"))
    file_lock = all(marker in text for marker in ("FileStream", ".Lock(", ".Unlock("))
    assert mutex_lock or file_lock, "mutating operations must visibly use an exclusive lock primitive"
    assert re.search(r"scope", text, re.IGNORECASE), "exclusive lock selection must remain scoped"


def test_docs_review_backend_reads_the_validated_request_once_before_mutating_dispatch() -> None:
    """A request replacement cannot switch the lock scope after validation.

    The request parser is the sole point that dereferences ``RequestPath``.  The
    main dispatch must obtain that validated object before taking a mutating lock,
    then use that *same variable* both as the lock's scope source and as every
    mutating operation's request.  These coupled data-flow checks reject merely
    adding a comment or an unused early read while retaining a second read.
    """
    text = SCRIPT.read_text(encoding="utf-8")
    request_path_reads = re.findall(
        r"^\s*\$[A-Za-z_][A-Za-z0-9_]*\s*=\s*Read-JsonObject\s+\$RequestPath\b",
        text,
        re.MULTILINE,
    )
    assert len(request_path_reads) == 1, (
        "RequestPath must be dereferenced and parsed exactly once; a later read can "
        "change the request after its lock scope was selected"
    )

    dispatch_tries = []
    for candidate in re.finditer(r"\btry\s*(?P<opening>\{)", text):
        body = _ps_braced_body(text, candidate.start("opening"))
        if "$PSVersionTable" in body and "Invoke-WithScopeLock" in body:
            dispatch_tries.append(body)
    assert len(dispatch_tries) == 1, "backend must retain one PSVersionTable-guarded main dispatch"
    main_body = dispatch_tries[0]

    request_read = re.search(
        r"\$request\s*=\s*Read-JsonObject\s+\$RequestPath\s+['\"]Request JSON['\"]",
        main_body,
    )
    request_validation = re.search(
        r"\$request\s*=\s*Read-Request\s+\$request\s+\(\s*\[ref\]\s*\$root\s*\)",
        main_body,
    )
    lock = re.search(
        r"\bInvoke-WithScopeLock\s+\$[A-Za-z_][A-Za-z0-9_]*\s+"
        r"\$request\.package_specification\.scope\s*(?P<opening>\{)",
        main_body,
    )
    assert request_read is not None, "main dispatch must read the sole request from RequestPath"
    assert request_validation is not None, "main dispatch must validate the single request object"
    assert lock is not None, "mutating lock scope must come from the validated $request object"
    assert request_read.start() < request_validation.start() < lock.start(), (
        "request reading and validation must precede mutating lock dispatch"
    )

    locked_dispatch = _ps_braced_body(main_body, lock.start("opening"))
    operations = ("Invoke-Prepare", "Invoke-Submit", "Invoke-RecordDecision", "Invoke-Promote")
    for operation in operations:
        assert re.search(
            rf"{operation}\s+\$[A-Za-z_][A-Za-z0-9_]*\s+\$request\b",
            locked_dispatch,
        ), f"{operation} must receive the same validated $request that selected the lock scope"
