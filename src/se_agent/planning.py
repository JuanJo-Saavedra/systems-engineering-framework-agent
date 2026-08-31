"""Plan model and static write-set expansion (design D4/D11).

The plan is built once from a static expansion of the committed payload
snapshot: no user input ever contributes a plan path. Destinations are
`PurePosixPath` (the write-set is defined in POSIX form; D11), the ordering is
the lexicographic tuple of `dest_rel.parts`, and the resulting write-set is
asserted sanitary (relative, no `..` — defense in depth, unreachable by
construction).

Dependency direction (design §3): this module imports `payload` only via the
`Traversable` handed in by the caller; nothing imports FS-mutating code.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources.abc import Traversable
from pathlib import PurePosixPath


@dataclass(frozen=True, order=True)
class PlannedFile:
    """One planned destination, frozen and orderable (D4)."""

    dest_rel: PurePosixPath  # relative to the target root
    payload_rel: PurePosixPath  # relative to the payload snapshot root


def build_plan(payload_root: Traversable) -> tuple[PlannedFile, ...]:
    """Expand `payload_root` into the deterministic, sorted write plan.

    Sort key: tuple of `dest_rel.parts` (lexicographic on parts), stable across
    runs, platforms, and filesystem enumeration order.
    """
    candidates: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    _walk(payload_root, (), candidates)
    candidates.sort(key=lambda pair: pair[0])
    plan = tuple(
        PlannedFile(PurePosixPath(*dest_parts), PurePosixPath(*payload_parts))
        for dest_parts, payload_parts in candidates
    )
    _assert_write_set(plan)
    return plan


def _walk(
    traversable: Traversable,
    prefix: tuple[str, ...],
    out: list[tuple[tuple[str, ...], tuple[str, ...]]],
) -> None:
    for entry in traversable.iterdir():
        parts = (*prefix, entry.name)
        if entry.is_dir():
            _walk(entry, parts, out)
        elif entry.is_file():
            out.append((parts, parts))


def _assert_write_set(plan: tuple[PlannedFile, ...]) -> None:
    """Plan-path sanity: every destination is relative and dot-free.

    Unreachable by construction (static expansion); any failure is a bug.
    """
    for item in plan:
        if item.dest_rel.is_absolute() or ".." in item.dest_rel.parts:
            raise AssertionError(f"unsanitary plan path: {item.dest_rel.as_posix()}")
