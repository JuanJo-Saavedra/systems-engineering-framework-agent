"""AC-3/AC-5 — `init` installs exactly the payload expansion (REQ-P1/P2/P4/P5/P6).

The committed mirror `src/se_agent/_payload/` is the expected-tree oracle
(design D1): after a successful init the destination tree must contain exactly
the mirror expansion, byte-for-byte, with no extra path (no manifest, no
`.framework-agent/`, no cache — REQ-P5) and stdout must enumerate every
written path (REQ-P6).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

# pi-lens-ignore: Pyright:reportMissingImports
# pi-lens-ignore: reportMissingImports
import pytest  # pyright: ignore[reportMissingImports]

from se_agent import cli
from se_agent.payload import PAYLOAD_ROOT
from se_agent.planning import build_plan

_FORBIDDEN_STATE = (
    ".framework-agent",
    "manifest.json",
    "se-agent.lock",
    ".se-agent",
    "__pycache__",
    ".pytest_cache",
)


def _argv(target: Path) -> list[str]:
    return ["init", "--harness", "codex", "--target", str(target)]


def _expected_files() -> dict[str, bytes]:
    return {
        item.dest_rel.as_posix(): PAYLOAD_ROOT.joinpath(*item.payload_rel.parts).read_bytes()
        for item in build_plan(PAYLOAD_ROOT)
    }


def test_full_tree_equals_payload_expansion(make_target: Callable[[str], Path]) -> None:
    """REQ-P1/P2: installed tree == mirror expansion, byte-identical per file."""
    target = make_target("empty")
    assert cli.main(_argv(target)) == 0

    expected = _expected_files()
    actual = {
        p.relative_to(target).as_posix(): p.read_bytes()
        for p in sorted(target.rglob("*"))
        if p.is_file() and not p.is_symlink()
    }
    assert actual == expected


def test_rerun_determinism_across_equivalent_targets(make_target: Callable[[str], Path], tree_snapshot: Callable[[Path], dict[str, str]]) -> None:
    """REQ-P4: two runs over equivalent destinations produce identical bytes."""
    first = make_target("empty")
    second = make_target("empty")
    assert cli.main(_argv(first)) == 0
    assert cli.main(_argv(second)) == 0
    assert tree_snapshot(first) == tree_snapshot(second)


def test_no_residual_state_files(make_target: Callable[[str], Path]) -> None:
    """REQ-P5: no manifest, no `.framework-agent/`, no cache, no lockfile."""
    target = make_target("empty")
    assert cli.main(_argv(target)) == 0
    for forbidden in _FORBIDDEN_STATE:
        assert not (target / forbidden).exists(), forbidden


def test_stdout_enumerates_every_written_path(make_target: Callable[[str], Path], capsys: pytest.CaptureFixture[str]) -> None:
    """REQ-P6: success prints `Installed N file(s):` plus every written path."""
    target = make_target("empty")
    assert cli.main(_argv(target)) == 0
    out = capsys.readouterr().out
    expected = _expected_files()
    header = f"Installed {len(expected)} file(s):"
    assert header in out
    lines = out.splitlines()
    assert lines[lines.index(header) + 1:] == sorted(expected)
    for rel in expected:
        assert rel in out
