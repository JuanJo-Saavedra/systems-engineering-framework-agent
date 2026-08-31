"""AC-8 — `--force` scope (REQ-C5, REQ-W4, design D5/§5).

Force overwrites exactly the colliding write-set paths and never relaxes
safety: escapes and symlink destinations still fail with force, with zero
writes, exactly as if `--force` were absent.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

# pi-lens-ignore: Pyright:reportMissingImports
# pi-lens-ignore: reportMissingImports
import pytest  # pyright: ignore[reportMissingImports]

from se_agent import cli
from se_agent.payload import PAYLOAD_ROOT
from se_agent.planning import build_plan


def _argv(target: Path) -> list[str]:
    return ["init", "--harness", "codex", "--target", str(target), "--force"]


def _expected_bytes() -> dict[str, bytes]:
    return {
        item.dest_rel.as_posix(): PAYLOAD_ROOT.joinpath(*item.payload_rel.parts).read_bytes()
        for item in build_plan(PAYLOAD_ROOT)
    }


def test_force_overwrites_exactly_the_colliding_write_set_paths(
    make_target: Callable[[str], Path],
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = make_target("collision_files")
    (target / "unrelated.txt").write_bytes(b"consumer file\n")
    assert cli.main(_argv(target)) == 0
    expected = _expected_bytes()
    for rel in ("AGENTS.md", "marco/README.md", "catalogo/skill-registry.md"):
        assert (target / rel).read_bytes() == expected[rel]
    assert (target / "unrelated.txt").read_bytes() == b"consumer file\n"
    err = capsys.readouterr().err
    assert "[y/N]" not in err  # force never prompts (REQ-C2 path + REQ-C5)


def test_force_still_fails_on_symlink_escape(
    make_target: Callable[[str], Path],
    tree_snapshot: Callable[[Path], dict[str, str]],
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = make_target("symlink_escape")
    before = tree_snapshot(target)
    assert cli.main(_argv(target)) == 1
    assert "symlink-escape" in capsys.readouterr().err
    assert tree_snapshot(target) == before  # outside/secret.txt untouched


def test_force_still_fails_on_broken_symlink_destination(
    make_target: Callable[[str], Path],
    tree_snapshot: Callable[[Path], dict[str, str]],
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = make_target("empty")
    try:
        os.symlink("does-not-exist-anywhere", target / "AGENTS.md")
    except OSError:
        pytest.skip("filesystem cannot create symlinks (OS matrix is an open follow-up)")
    before = tree_snapshot(target)
    assert cli.main(_argv(target)) == 1
    assert "symlink-destination" in capsys.readouterr().err
    assert tree_snapshot(target) == before  # broken symlink left as-is
