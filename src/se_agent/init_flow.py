"""Init flow orchestration (design §4, steps 3–9).

Normative sequence: resolve the target root, build the static plan, run the
complete safety preflight, detect and resolve ALL collisions — and only then
perform the ordered writes. No byte of the destination is touched before the
entire plan is validated (REQ-F1); exit 0 implies zero pending writes
(REQ-M2); every failure names a file or a violated rule (REQ-F3).
"""

from __future__ import annotations

import sys
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import TextIO

from .collision import (
    IsInteractive,
    PromptYesNo,
    _default_is_interactive,
    _default_prompt,
    detect_collisions,
    resolve_collisions,
)
from .payload import PAYLOAD_ROOT
from .planning import build_plan
from .safety import validate_plan
from .writer import CopyFile, WriteOutcome, execute_writes


def run_init(
    target: str,
    *,
    force: bool = False,
    is_interactive: IsInteractive | None = None,
    prompt_yes_no: PromptYesNo | None = None,
    copy_file: CopyFile | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Execute `init` for `target`; return the CLI exit code (design D5).

    Injectable seams (D9): `is_interactive`/`prompt_yes_no` drive the collision
    protocol (REQ-C3/C4); `copy_file` injects write failures for REQ-M1 tests.
    """
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr
    interactive = _default_is_interactive if is_interactive is None else is_interactive
    prompt = _default_prompt if prompt_yes_no is None else prompt_yes_no

    root = Path(target).resolve()  # step 3 (existence/type checked by preflight)
    plan = build_plan(PAYLOAD_ROOT)  # step 4 (static; no user input in paths)

    violations = validate_plan(root, plan)  # step 5 (REQ-F1/F2/F3)
    if violations:
        for violation in violations:
            print(
                f"se-agent: error: {violation.path}: violated rule '{violation.rule}'",
                file=err,
            )
        return 1

    collisions = detect_collisions(root, plan)  # step 6 (REQ-C1)
    if not resolve_collisions(  # step 7 (REQ-C2..C5); force never relaxes step 5
        collisions,
        force=force,
        is_interactive=interactive,
        prompt_yes_no=prompt,
        stderr=err,
    ):
        return 1

    outcome = execute_writes(root, plan, PAYLOAD_ROOT, copy_file)  # step 8 (REQ-M1)
    if outcome.error is not None:
        _report_partial_write(outcome, outcome.error, err)
        return 1

    print(f"Installed {len(outcome.written)} file(s):", file=out)  # step 9
    for rel in outcome.written:  # REQ-P6: enumerate every written path
        print(rel.as_posix(), file=out)
    return 0


def _report_partial_write(
    outcome: WriteOutcome, error: OSError, err: TextIO
) -> None:
    """REQ-M1/M2 report: stop already happened; keep written files, list pending."""
    print(f"se-agent: error: write failed: {error}", file=err)
    print("written:", file=err)
    for rel in outcome.written:
        print(f"  {rel.as_posix()}", file=err)
    print("pending:", file=err)
    for rel in outcome.pending:
        print(f"  {rel.as_posix()}", file=err)
    print(
        "Files already written belong to the consumer and were NOT rolled back; "
        "re-run 'se-agent init' later (already-written paths become collisions).",
        file=err,
    )
