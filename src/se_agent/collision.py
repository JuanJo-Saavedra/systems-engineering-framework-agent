"""Collision detection and resolution (design D5/§5, REQ-C1..C5).

The complete collision list is computed before the first write (REQ-C1) and
the decision — force, accept, abort — is made before any byte is modified, so
an abort after the prompt is zero-write by construction (§5). A collision is
`os.path.lexists(root / dest_rel)` on a plan path, so broken symlinks count
and every colliding path is, by construction, a member of the write-set:
`--force` cannot be granted extra privilege because the collision list cannot
contain a non-write-set path (REQ-C5/REQ-W4, structural not policed).
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable, Iterable
from pathlib import Path, PurePosixPath
from typing import TextIO

from se_agent.planning import PlannedFile

#: Prompt answer accepted to proceed (REQ-C3): exactly y/yes, case-insensitive.
ACCEPTED_ANSWERS = frozenset({"y", "yes"})

#: Suggestion appended to the non-interactive collision abort (REQ-C4).
FORCE_HINT = "Re-run with --force to overwrite."

IsInteractive = Callable[[], bool]
PromptYesNo = Callable[[str], "str | None"]


def detect_collisions(
    root: Path, plan: Iterable[PlannedFile]
) -> tuple[PurePosixPath, ...]:
    """Return the complete list of planned destinations that already exist.

    Pure read-only detection via `os.path.lexists` (catches broken symlinks);
    computed on the full plan before the first write (REQ-C1).
    """
    return tuple(
        item.dest_rel
        for item in plan
        if os.path.lexists(root.joinpath(*item.dest_rel.parts))
    )


def resolve_collisions(
    collisions: Iterable[PurePosixPath],
    *,
    force: bool,
    is_interactive: IsInteractive,
    prompt_yes_no: PromptYesNo,
    stderr: TextIO,
) -> bool:
    """Decide whether to proceed over the listed collisions — before any write.

    - `--force` proceeds (overwrite exactly the colliding write-set paths).
    - Interactive: list ALL collisions on stderr, prompt `[y/N]`; only
      y/yes (case-insensitive, stripped) proceeds; any other answer or EOF
      aborts (REQ-C3).
    - Non-interactive without force: list ALL collisions on stderr plus the
      `--force` hint and abort (REQ-C4).

    Returns True to proceed, False to abort.
    """
    listed = tuple(collisions)
    if not listed:
        return True
    if force:
        return True
    _print_collisions(listed, stderr)
    if not is_interactive():
        print(FORCE_HINT, file=stderr)
        return False
    answer = prompt_yes_no("Overwrite the listed path(s)? [y/N] ")
    return answer is not None and answer.strip().lower() in ACCEPTED_ANSWERS


def _print_collisions(collisions: Iterable[PurePosixPath], stderr: TextIO) -> None:
    for rel in collisions:
        print(f"se-agent: collision: {rel.as_posix()}", file=stderr)


def _default_is_interactive() -> bool:
    """TTY seam default (D5): a session is interactive when stdin is a TTY."""
    return sys.stdin.isatty()


def _default_prompt(prompt: str) -> str | None:
    """Prompt seam default (D5): prompt on stderr, read one line from stdin.

    Returns None on EOF (an empty readline), which aborts (REQ-C3).
    """
    print(prompt, file=sys.stderr, end="", flush=True)
    line = sys.stdin.readline()
    return None if line == "" else line
