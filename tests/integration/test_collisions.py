"""AC-6/AC-7 — collision protocol (REQ-C1..C4, design D5/§5).

The complete collision list is computed before the first write; the decision
(accept/abort) is made before any byte is modified, so every abort below is
zero-write by construction.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

import pytest

from se_agent import cli, collision
from se_agent.payload import PAYLOAD_ROOT, enumerate_payload
from se_agent.planning import build_plan

_FORCE_HINT = "Re-run with --force to overwrite."


def _argv(target: Path) -> list[str]:
    return ["init", "--harness", "codex", "--target", str(target)]


def _collisions(target: Path) -> list[str]:
    plan = build_plan(PAYLOAD_ROOT)
    return [
        rel.as_posix() for rel in collision.detect_collisions(target, plan)
    ]


def _expected_bytes(target: Path) -> dict[str, bytes]:
    from se_agent.payload import PAYLOAD_ROOT as ROOT

    return {
        item.dest_rel.as_posix(): ROOT.joinpath(*item.payload_rel.parts).read_bytes()
        for item in build_plan(ROOT)
    }


def test_no_collisions_proceeds_without_prompt(
    make_target: Callable[[str], Path],
    fake_stdin: Callable[..., object],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """REQ-C2: destinations without write-set collisions are written silently."""
    target = make_target("populated_proyecto")
    fake_stdin(is_tty=True, answer="y\n")  # would be consumed only if a prompt leaked
    assert cli.main(_argv(target)) == 0
    err = capsys.readouterr().err
    assert "[y/N]" not in err
    assert "collision" not in err


def test_non_interactive_collisions_abort_listing_all(
    make_target: Callable[[str], Path],
    fake_stdin: Callable[..., object],
    capsys: pytest.CaptureFixture[str],
    tree_snapshot: Callable[[Path], dict[str, str]],
) -> None:
    """REQ-C4: no TTY + collisions => exit 1, ALL paths on stderr + --force hint, zero writes."""
    target = make_target("collision_files")
    before = tree_snapshot(target)
    fake_stdin(is_tty=False, answer="")
    assert cli.main(_argv(target)) == 1
    err = capsys.readouterr().err
    colliding = _collisions(target)
    assert colliding, "fixture must produce collisions"
    for rel in colliding:
        assert rel in err
    assert _FORCE_HINT in err
    assert tree_snapshot(target) == before


def test_interactive_yes_proceeds_and_overwrites(
    make_target: Callable[[str], Path],
    fake_stdin: Callable[..., object],
) -> None:
    """REQ-C3: answering `y` overwrites the colliding write-set paths."""
    target = make_target("collision_files")
    fake_stdin(is_tty=True, answer="y\n")
    assert cli.main(_argv(target)) == 0
    for rel, payload_bytes in _expected_bytes(target).items():
        assert (target / rel).read_bytes() == payload_bytes


@pytest.mark.parametrize("answer", ["y\n", "yes\n", "YES\n", "Yes\n", " y\n", "y \n"])
def test_interactive_accepted_answers_case_and_whitespace_insensitive(
    answer: str,
    make_target: Callable[[str], Path],
    fake_stdin: Callable[..., object],
    tree_snapshot: Callable[[Path], dict[str, str]],
) -> None:
    """REQ-C3 triangulation: y/yes accepted case-insensitively, whitespace stripped."""
    target = make_target("collision_files")
    before = tree_snapshot(target)
    fake_stdin(is_tty=True, answer=answer)
    assert cli.main(_argv(target)) == 0
    for rel, payload_bytes in _expected_bytes(target).items():
        assert (target / rel).read_bytes() == payload_bytes
    del before  # zero-write invariant does not apply: accepted answers overwrite


@pytest.mark.parametrize("answer", ["N\n", "no\n", "maybe\n", "\n", "n foo\n", "yes no\n"])
def test_interactive_rejection_aborts_with_zero_writes(
    answer: str,
    make_target: Callable[[str], Path],
    fake_stdin: Callable[..., object],
    tree_snapshot: Callable[[Path], dict[str, str]],
) -> None:
    """REQ-C3: any answer other than y/yes aborts with the tree byte-invariant."""
    target = make_target("collision_files")
    before = tree_snapshot(target)
    fake_stdin(is_tty=True, answer=answer)
    assert cli.main(_argv(target)) == 1
    assert tree_snapshot(target) == before


def test_interactive_eof_aborts_with_zero_writes(
    make_target: Callable[[str], Path],
    fake_stdin: Callable[..., object],
    tree_snapshot: Callable[[Path], dict[str, str]],
) -> None:
    """REQ-C3: EOF at the prompt aborts with zero writes."""
    target = make_target("collision_files")
    before = tree_snapshot(target)
    fake_stdin(is_tty=True, answer=None)  # empty stream => EOF
    assert cli.main(_argv(target)) == 1
    assert tree_snapshot(target) == before


def test_collision_list_is_subset_of_write_set(
    make_target: Callable[[str], Path],
) -> None:
    """REQ-C5 structural basis: the plan IS the write-set, so the collision
    list can never contain a non-write-set path — `--force` is therefore
    structurally incapable of granting extra privilege (REQ-W4)."""
    target = make_target("collision_files")
    (target / "unrelated.txt").write_bytes(b"not in the write-set\n")
    plan = build_plan(PAYLOAD_ROOT)
    write_set = {item.dest_rel.as_posix() for item in plan}
    enumerated = {dest.as_posix() for dest, _payload in enumerate_payload()}
    assert write_set == enumerated  # plan == write-set invariant (design §5)
    colliding = _collisions(target)
    assert set(colliding) <= write_set
    assert os.path.lexists(target / "unrelated.txt") and "unrelated.txt" not in colliding
