"""AC-4 — `proyecto/` is untouchable in every mode (REQ-W2, design §5).

The recursive hash of a populated `proyecto/` must be identical before and
after `init` in all modes: clean success, `--force` success over collisions
elsewhere, and every abort path. `proyecto/` is never in the plan, so this is
proven byte-identity, not policy.
"""

from __future__ import annotations

import io
from collections.abc import Callable
from pathlib import Path

from se_agent import cli


def _argv(target: Path, *extra: str) -> list[str]:
    return ["init", "--harness", "codex", "--target", str(target), *extra]


def _add_collisions_elsewhere(target: Path) -> None:
    """Collide with write-set destinations far away from `proyecto/`."""
    marco = target / "marco"
    marco.mkdir(exist_ok=True)
    (target / "AGENTS.md").write_bytes(b"stale AGENTS.md (consumer)\n")
    (marco / "README.md").write_bytes(b"stale marco README (consumer)\n")


def _proyecto_snapshot(tree_snapshot: Callable[[Path], dict[str, str]], target: Path):
    return {k: v for k, v in tree_snapshot(target).items() if k.startswith("proyecto/")}


def test_success_leaves_proyecto_byte_identical(
    make_target: Callable[[str], Path], tree_snapshot: Callable[[Path], dict[str, str]]
) -> None:
    target = make_target("populated_proyecto")
    before = _proyecto_snapshot(tree_snapshot, target)
    assert cli.main(_argv(target)) == 0
    assert _proyecto_snapshot(tree_snapshot, target) == before


def test_force_success_leaves_proyecto_byte_identical(
    make_target: Callable[[str], Path], tree_snapshot: Callable[[Path], dict[str, str]]
) -> None:
    target = make_target("populated_proyecto")
    _add_collisions_elsewhere(target)
    before = _proyecto_snapshot(tree_snapshot, target)
    assert cli.main(_argv(target, "--force")) == 0
    assert _proyecto_snapshot(tree_snapshot, target) == before


def test_non_interactive_abort_leaves_proyecto_byte_identical(
    make_target: Callable[[str], Path],
    tree_snapshot: Callable[[Path], dict[str, str]],
    fake_stdin: Callable[..., io.StringIO],
) -> None:
    target = make_target("populated_proyecto")
    _add_collisions_elsewhere(target)
    before = _proyecto_snapshot(tree_snapshot, target)
    fake_stdin(is_tty=False, answer="")
    assert cli.main(_argv(target)) == 1
    assert _proyecto_snapshot(tree_snapshot, target) == before


def test_interactive_rejection_leaves_proyecto_byte_identical(
    make_target: Callable[[str], Path],
    tree_snapshot: Callable[[Path], dict[str, str]],
    fake_stdin: Callable[..., io.StringIO],
) -> None:
    target = make_target("populated_proyecto")
    _add_collisions_elsewhere(target)
    before = _proyecto_snapshot(tree_snapshot, target)
    fake_stdin(is_tty=True, answer="N\n")
    assert cli.main(_argv(target)) == 1
    assert _proyecto_snapshot(tree_snapshot, target) == before


def test_force_never_deletes_non_write_set_content(
    make_target: Callable[[str], Path], tree_snapshot: Callable[[Path], dict[str, str]]
) -> None:
    """REQ-W3: `--force` deletes/tidies nothing outside the write-set."""
    target = make_target("populated_proyecto")
    _add_collisions_elsewhere(target)
    (target / "notes" / "keep.txt").parent.mkdir()
    (target / "notes" / "keep.txt").write_bytes(b"keep me\n")
    before = tree_snapshot(target)
    assert cli.main(_argv(target, "--force")) == 0
    after = tree_snapshot(target)
    assert after["notes/keep.txt"] == before["notes/keep.txt"]
    assert after["proyecto/registros/riesgos.md"] == before["proyecto/registros/riesgos.md"]
