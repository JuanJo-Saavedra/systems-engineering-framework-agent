"""WU3 unit tests: safe path resolution and zero-write preflight (design D4/D11).

`validate_plan(root, plan)` is a pure preflight over `pathlib`/`os.lstat`:
it rejects plan-path escapes (`..`, absolute), ancestor symlinks that resolve
outside the target root, destinations that are themselves symlinks (including
broken ones, via lexists semantics), and ancestors that exist as non-directories.
It performs zero filesystem mutation.
"""

from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path, PurePosixPath

import pytest  # pyright: ignore[reportMissingImports]

from se_agent.planning import PlannedFile
from se_agent.safety import validate_plan


def plan(*relpaths: str) -> tuple[PlannedFile, ...]:
    return tuple(
        PlannedFile(PurePosixPath(rel), PurePosixPath(rel)) for rel in relpaths
    )


def symlink_ok(tmp_path: Path) -> bool:
    probe = tmp_path / "_symlink_probe"
    try:
        os.symlink("nowhere", probe)
    except (OSError, NotImplementedError):
        return False
    finally:
        if probe.is_symlink():
            probe.unlink()
    return True


def test_valid_plan_on_empty_root(tmp_path):
    assert validate_plan(tmp_path, plan("AGENTS.md", "marco/README.md")) == []


def test_root_must_be_existing_directory(tmp_path):
    missing = tmp_path / "nope"
    violations = validate_plan(missing, plan("AGENTS.md"))
    assert [v.rule for v in violations] == ["root-not-directory"]


def _make_two_level_escape(root: Path) -> None:
    """root/l1 -> root/real (internal), root/real/l2 -> outside (escape)."""
    (root / "real").mkdir()
    os.symlink(str(root / "real"), root / "l1")
    os.symlink(str(root.parent / "outside"), root / "real" / "l2")


@pytest.mark.parametrize(
    ("name", "setup", "dest_rel", "expected_rule", "expected_path"),
    [
        (
            "dotdot-escape",
            None,
            "../escape.txt",
            "parent-reference",
            "../escape.txt",
        ),
        (
            "absolute-escape",
            None,
            "/etc/passwd",
            "absolute-path",
            "/etc/passwd",
        ),
        # Ancestor symlink resolving outside the target root (D4 step 3).
        (
            "ancestor-symlink-escape",
            lambda root: os.symlink(str(root.parent / "outside"), root / "link"),
            "link/AGENTS.md",
            "symlink-escape",
            "link",
        ),
        # Destination itself a symlink: hard error regardless of direction.
        (
            "destination-symlink-outside",
            lambda root: os.symlink(str(root.parent / "outside" / "x"), root / "AGENTS.md"),
            "AGENTS.md",
            "symlink-destination",
            "AGENTS.md",
        ),
        (
            "destination-symlink-inside",
            lambda root: os.symlink("elsewhere.md", root / "AGENTS.md"),
            "AGENTS.md",
            "symlink-destination",
            "AGENTS.md",
        ),
        # Broken symlink at a collision path: lexists semantics must flag it.
        (
            "broken-symlink-destination",
            lambda root: os.symlink("does-not-exist", root / "gone.txt"),
            "gone.txt",
            "symlink-destination",
            "gone.txt",
        ),
        # Ancestor component exists as a non-directory (D4 step 5).
        (
            "parent-not-directory",
            lambda root: (root / "marco").write_bytes(b"file, not dir"),
            "marco/fases/x.md",
            "parent-not-directory",
            "marco",
        ),
        # Multi-level: second-level symlink inside an already-followed internal link.
        # The violation names the offending symlink as reached from the plan
        # (lexical chain), here `l1/l2`.
        (
            "multi-level-symlink-escape",
            _make_two_level_escape,
            "l1/l2/evil.txt",
            "symlink-escape",
            "l1/l2",
        ),
    ],
)
def test_unsafe_plan_paths_rejected(
    tmp_path, symlink_support, name, setup, dest_rel, expected_rule, expected_path
):
    if setup is not None:
        setup(tmp_path)
    violations = validate_plan(tmp_path, plan(dest_rel))
    assert len(violations) == 1, f"case {name}: {violations}"
    assert violations[0].rule == expected_rule
    assert violations[0].path == expected_path


def test_symlink_inside_target_resolving_inside_target_passes(tmp_path, symlink_support):
    (tmp_path / "real").mkdir()
    os.symlink(str(tmp_path / "real"), tmp_path / "link")
    assert validate_plan(tmp_path, plan("link/AGENTS.md", "real/marco/x.md")) == []


def test_destination_symlink_resolving_inside_target_still_fails(tmp_path, symlink_support):
    (tmp_path / "elsewhere.md").write_bytes(b"target inside root")
    os.symlink("elsewhere.md", tmp_path / "AGENTS.md")
    violations = validate_plan(tmp_path, plan("AGENTS.md"))
    assert [v.rule for v in violations] == ["symlink-destination"]


def test_two_hops_through_internal_link_caught(tmp_path, symlink_support):
    _make_two_level_escape(tmp_path)
    violations = validate_plan(tmp_path, plan("l1/l2/evil.txt"))
    assert len(violations) == 1
    assert violations[0].rule == "symlink-escape"
    assert violations[0].path == "l1/l2"


def test_violations_are_named_and_deterministically_sorted(tmp_path):
    (tmp_path / "marco").write_bytes(b"file")
    multi = plan("marco/fases/x.md", "../up.txt", "/etc/passwd")
    first = validate_plan(tmp_path, multi)
    second = validate_plan(tmp_path, multi)
    assert first == second  # deterministic across runs
    assert [(v.path, v.rule) for v in first] == sorted(
        (v.path, v.rule) for v in first
    )
    assert all(v.path and v.rule for v in first)  # every violation names its path


def test_preflight_performs_zero_mutation(tmp_path, symlink_support):
    """Zero-write preflight: the validated tree is byte-invariant (design D4)."""
    (tmp_path / "real").mkdir()
    (tmp_path / "real" / "AGENTS.md").write_bytes(b"payload bytes")
    (tmp_path / "marco").mkdir()
    (tmp_path / "marco" / "fases").mkdir()
    (tmp_path / "marco" / "fases" / "f0.md").write_bytes(b"\x00\x01fase")
    os.symlink(str(tmp_path / "real"), tmp_path / "link")
    os.symlink("../outside", tmp_path / "escape-link")

    before = _tree_snapshot(tmp_path)
    plan_items = plan(
        "real/AGENTS.md",
        "marco/fases/f0.md",
        "link/AGENTS.md",
        "escape-link/AGENTS.md",
        "gone.txt",
    )
    validate_plan(tmp_path, plan_items)
    assert _tree_snapshot(tmp_path) == before
    assert not (tmp_path / "real" / "AGENTS.md").read_bytes() != b"payload bytes"


def _tree_snapshot(root: Path) -> dict[str, tuple[str, ...]]:
    snapshot: dict[str, tuple[str, ...]] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        entry_stat = os.lstat(path)
        if stat.S_ISLNK(entry_stat.st_mode):
            snapshot[rel] = ("link", os.readlink(path))
        elif stat.S_ISDIR(entry_stat.st_mode):
            snapshot[rel] = ("dir",)
        else:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            snapshot[rel] = ("file", digest)
    return snapshot


@pytest.fixture()
def symlink_support(tmp_path):
    """Skip symlink fixtures where the filesystem cannot create them (D11)."""
    if not symlink_ok(tmp_path):
        pytest.skip(
            "filesystem cannot create symlinks (no OS matrix asserted; design D11)"
        )
