"""D1 / REQ-P1, REQ-P2, REQ-P4 — payload mirror coherence oracle.

The committed snapshot under `src/se_agent/_payload/` must be byte-identical
to the canonical product sources for every mapped path, and must contain
EXACTLY the mapped expansion (no extra, no missing files). The mirror is the
AC-3 expected-tree oracle; drift fails here instead of shipping a stale payload.

This test never writes: it only reads repo sources and the mirror. The
`tools/sync_payload.py` dev script (never run by CI, REQ-CI1) is the only
writer of the mirror.

Single-table rule (WU2 refactor): the source->mirror path map is defined ONCE
in `tools/sync_payload.py` and imported here, so the coherence test proves the
exact table the sync mechanism applies. Triangulation negative cases mutate a
temp copy of the mirror — the real snapshot is never touched by a test.
"""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_sync_payload():
    """Import `tools/sync_payload.py` as a module (repo tooling, not a package)."""
    script = REPO_ROOT / "tools" / "sync_payload.py"
    spec = importlib.util.spec_from_file_location("sync_payload_under_test", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sync_payload = _load_sync_payload()

#: Shared table (single source of truth lives in tools/sync_payload.py).
FILE_MAP = sync_payload.FILE_MAP
DIR_MAP = sync_payload.DIR_MAP
SKIP_NAMES = sync_payload.SKIP_NAMES
PAYLOAD_ROOT = sync_payload.PAYLOAD_ROOT
expected_expansion = sync_payload.mapped_expansion


def mirror_diff(mirror_root: Path, expansion: dict[PurePosixPath, Path]) -> list[str]:
    """Pure oracle: problems making `mirror_root` != `expansion` (empty list = coherent)."""
    if not mirror_root.is_dir():
        return [f"mirror does not exist: {mirror_root}"]
    problems: list[str] = []
    actual: set[PurePosixPath] = set()
    for path in sorted(mirror_root.rglob("*")):
        if path.is_file():
            actual.add(PurePosixPath(*path.relative_to(mirror_root).parts))
    for rel in sorted(set(expansion) - actual, key=lambda p: p.parts):
        problems.append(f"missing from mirror: {rel}")
    for rel in sorted(actual - set(expansion), key=lambda p: p.parts):
        problems.append(f"extra file in mirror: {rel}")
    for rel in sorted(set(expansion) & actual, key=lambda p: p.parts):
        expected_bytes = expansion[rel].read_bytes()
        actual_bytes = (mirror_root / Path(*rel.parts)).read_bytes()
        if actual_bytes != expected_bytes:
            problems.append(f"byte mismatch: {rel}")
    return problems


def _mirror_copy(tmp_path: Path) -> Path:
    """Temp copy of the mirror for negative cases; the real snapshot is never mutated."""
    destination = tmp_path / "mirror-copy"
    shutil.copytree(PAYLOAD_ROOT, destination)
    return destination


def _first_rel(expansion: dict[PurePosixPath, Path]) -> PurePosixPath:
    return min(expansion, key=lambda p: p.parts)


def test_mirror_is_byte_identical_to_canonical_sources() -> None:
    """REQ-P2: every mapped file is a byte-for-byte copy of its canonical source."""
    problems = mirror_diff(PAYLOAD_ROOT, expected_expansion())
    assert problems == [], "\n".join(problems)


def test_mirror_contains_exactly_the_mapped_expansion() -> None:
    """REQ-P1: the mirror contains exactly the mapped expansion (no extra/missing)."""
    assert PAYLOAD_ROOT.is_dir(), f"mirror does not exist: {PAYLOAD_ROOT}"
    actual = {
        PurePosixPath(*path.relative_to(PAYLOAD_ROOT).parts)
        for path in PAYLOAD_ROOT.rglob("*")
        if path.is_file()
    }
    expected = set(expected_expansion())
    assert actual == expected, (
        f"missing: {sorted(expected - actual, key=lambda p: p.parts)}; "
        f"extra: {sorted(actual - expected, key=lambda p: p.parts)}"
    )


def test_optional_sources_absent_from_mirror_when_absent() -> None:
    """D1 (WU2-green): optional sources (`runtime/skills/`, `adapters/codex/`) are
    mirrored when present and asserted absent from the mirror when absent."""
    for src_dir, prefix in DIR_MAP.items():
        src_root = REPO_ROOT / src_dir
        has_files = src_root.is_dir() and any(
            p.is_file() and p.name not in SKIP_NAMES for p in src_root.rglob("*")
        )
        mirror_prefix = PAYLOAD_ROOT / Path(*prefix)
        assert mirror_prefix.is_dir() == has_files, (
            f"optional source {src_dir} present={has_files} but mirror prefix "
            f"{mirror_prefix} present={mirror_prefix.is_dir()}"
        )


def test_enumerate_payload_matches_mirror_expansion() -> None:
    """D1/D4: enumerate_payload() returns the sorted destination-preserving plan
    candidates of the mirror; dest_rel == payload_rel because the mirror layout
    is destination-preserving (prefix renamed, same relative structure)."""
    from se_agent import payload

    candidates = payload.enumerate_payload()
    expected = {rel for rel in expected_expansion()}
    dests = [dest for dest, _ in candidates]
    assert set(dests) == expected
    assert dests == sorted(expected, key=lambda p: p.parts), "candidates must be sorted"
    for dest, payload_rel in candidates:
        assert isinstance(dest, PurePosixPath) and isinstance(payload_rel, PurePosixPath)
        assert dest == payload_rel


# --- Triangulation: the oracle must FAIL on every drift class (temp copies only). ---


def test_oracle_fails_on_one_extra_byte(tmp_path: Path) -> None:
    """Triangulation: a single extra byte in any mirrored file -> byte mismatch."""
    expansion = expected_expansion()
    mirror = _mirror_copy(tmp_path)
    target = _first_rel(expansion)
    target_path = mirror / Path(*target.parts)
    target_path.write_bytes(target_path.read_bytes() + b"\n")
    problems = mirror_diff(mirror, expansion)
    assert problems, "oracle must detect a one-byte drift"
    assert any("byte mismatch" in problem and str(target) in problem for problem in problems), "\n".join(problems)


def test_oracle_fails_on_extra_mirror_file(tmp_path: Path) -> None:
    """Triangulation: a file in the mirror outside the mapped expansion -> extra."""
    expansion = expected_expansion()
    mirror = _mirror_copy(tmp_path)
    extra = mirror / "unmapped_extra.md"
    extra.write_bytes(b"stray content\n")
    problems = mirror_diff(mirror, expansion)
    assert problems, "oracle must detect an extra mirror file"
    assert any("extra file in mirror" in problem and "unmapped_extra.md" in problem for problem in problems), "\n".join(
        problems
    )


def test_oracle_fails_on_deleted_mirror_file(tmp_path: Path) -> None:
    """Triangulation: a deleted mirror file -> missing."""
    expansion = expected_expansion()
    mirror = _mirror_copy(tmp_path)
    target = _first_rel(expansion)
    (mirror / Path(*target.parts)).unlink()
    problems = mirror_diff(mirror, expansion)
    assert problems, "oracle must detect a deleted mirror file"
    assert any("missing from mirror" in problem and str(target) in problem for problem in problems), "\n".join(problems)


def test_real_mirror_untouched_by_negative_cases(tmp_path: Path) -> None:
    """REQ-R3 analog for the mirror: negative-case runs leave the real snapshot byte-identical."""
    before = {p: p.read_bytes() for p in sorted(PAYLOAD_ROOT.rglob("*")) if p.is_file()}
    for i in range(2):
        mirror = _mirror_copy(tmp_path / f"iteration-{i}")
        (mirror / "unmapped_extra.md").write_bytes(b"x\n")
        mirror_diff(mirror, expected_expansion())
    after = {p: p.read_bytes() for p in sorted(PAYLOAD_ROOT.rglob("*")) if p.is_file()}
    assert before == after
