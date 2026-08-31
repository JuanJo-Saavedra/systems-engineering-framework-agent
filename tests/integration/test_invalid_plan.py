"""AC-9 — invalid plans are rejected with zero writes (REQ-F1/F3, design §4).

Any invalid plan — destination not a directory, symlink escape, symlink at a
collision path, non-directory ancestor — produces a non-zero exit, a stderr
message naming the offending path and violated rule, and a byte-invariant
destination tree.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

# pi-lens-ignore: Pyright:reportMissingImports
# pi-lens-ignore: reportMissingImports
import pytest  # pyright: ignore[reportMissingImports]

from se_agent import cli


def _argv(target: Path) -> list[str]:
    return ["init", "--harness", "codex", "--target", str(target)]


def _assert_invariant_rejection(
    target: Path,
    tree_snapshot: Callable[[Path], dict[str, str]],
    capsys: pytest.CaptureFixture[str],
    rule: str,
) -> None:
    before = tree_snapshot(target)
    assert cli.main(_argv(target)) == 1
    err = capsys.readouterr().err
    assert rule in err, err
    assert "se-agent: error:" in err
    assert tree_snapshot(target) == before


def test_missing_destination_is_rejected(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(_argv(tmp_path / "no-such-dir")) == 1
    assert "root-not-directory" in capsys.readouterr().err


def test_destination_is_a_file_is_rejected(
    tmp_path: Path,
    tree_snapshot: Callable[[Path], dict[str, str]],
    capsys: pytest.CaptureFixture[str],
) -> None:
    not_a_dir = tmp_path / "plain-file"
    not_a_dir.write_bytes(b"i am a file\n")
    before = tree_snapshot(tmp_path)
    assert cli.main(_argv(not_a_dir)) == 1
    assert "root-not-directory" in capsys.readouterr().err
    assert tree_snapshot(tmp_path) == before


def test_ancestor_symlink_escape_is_rejected(
    make_target: Callable[[str], Path],
    tree_snapshot: Callable[[Path], dict[str, str]],
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = make_target("symlink_escape")
    _assert_invariant_rejection(target, tree_snapshot, capsys, "symlink-escape")
    assert (target / "marco").is_symlink()  # untouched


def test_parent_not_directory_is_rejected(
    make_target: Callable[[str], Path],
    tree_snapshot: Callable[[Path], dict[str, str]],
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = make_target("empty")
    (target / "catalogo").write_bytes(b"a file named catalogo\n")
    _assert_invariant_rejection(target, tree_snapshot, capsys, "parent-not-directory")
    assert (target / "catalogo").read_bytes() == b"a file named catalogo\n"


def test_symlink_destination_is_rejected(
    make_target: Callable[[str], Path],
    tree_snapshot: Callable[[Path], dict[str, str]],
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = make_target("empty")
    inside = target / "sibling"
    inside.mkdir()
    try:
        os.symlink("sibling", target / "AGENTS.md")  # even pointing inside
    except OSError:
        pytest.skip("filesystem cannot create symlinks (OS matrix is an open follow-up)")
    _assert_invariant_rejection(target, tree_snapshot, capsys, "symlink-destination")


def test_broken_symlink_destination_is_rejected(
    make_target: Callable[[str], Path],
    tree_snapshot: Callable[[Path], dict[str, str]],
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = make_target("empty")
    try:
        os.symlink("nowhere", target / "AGENTS.md")  # lexists() counts it
    except OSError:
        pytest.skip("filesystem cannot create symlinks (OS matrix is an open follow-up)")
    _assert_invariant_rejection(target, tree_snapshot, capsys, "symlink-destination")
