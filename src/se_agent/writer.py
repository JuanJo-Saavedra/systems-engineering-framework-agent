"""Ordered writer (design D5/§5, REQ-M1/M2).

`execute_writes` walks the already-validated plan in its deterministic order
(sort key: tuple of `dest_rel.parts`), creating missing parent directories
just-in-time on the validated chain, and copies payload bytes. On the first
`OSError` it stops: no rollback and no deletion — the already-written files
belong to the consumer (REQ-M1) — and reports `written:`/`pending:` blocks so
success can never be claimed with pending writes (REQ-M2, enforced by
`init_flow` exiting non-zero whenever `error` is set). Failure injection goes
through the `copy_file` seam, never through permission assumptions.
"""

from __future__ import annotations

import shutil
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from importlib.resources.abc import Traversable
from pathlib import Path, PurePosixPath

from se_agent.planning import PlannedFile

#: Injectable copy step (design D9 seams): reads the payload entry, writes dest.
CopyFile = Callable[[Traversable, PlannedFile, Path], None]


@dataclass(frozen=True)
class WriteOutcome:
    """Result of the ordered write loop (REQ-M1 report payload)."""

    written: tuple[PurePosixPath, ...]
    pending: tuple[PurePosixPath, ...]
    error: OSError | None


def execute_writes(
    root: Path,
    plan: Sequence[PlannedFile],
    payload_root: Traversable,
    copy_file: CopyFile | None = None,
) -> WriteOutcome:
    """Write every planned file in deterministic order; stop at first OSError.

    The plan must already be safety-validated (preflight, design §4 step 5);
    this function performs no validation and never rolls back.
    """
    written: list[PurePosixPath] = []
    for index, item in enumerate(plan):
        destination = root.joinpath(*item.dest_rel.parts)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if copy_file is None:
                source = payload_root.joinpath(*item.payload_rel.parts)
                # Byte-for-byte copy (D11): read `rb`, write `wb`, no metadata.
                with source.open("rb") as src, open(destination, "wb") as out:
                    shutil.copyfileobj(src, out)
            else:
                copy_file(payload_root, item, destination)
        except OSError as error:
            pending = tuple(item.dest_rel for item in plan[index:])
            return WriteOutcome(tuple(written), pending, error)
        written.append(item.dest_rel)
    return WriteOutcome(tuple(written), (), None)
