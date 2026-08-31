"""Payload snapshot access (design D1).

The committed snapshot `src/se_agent/_payload/` travels inside the installed
package, so `init` is offline (REQ-V3) and byte-deterministic per tag
(REQ-P4). This module exposes the snapshot root as an `importlib.resources`
Traversable and enumerates its files as sorted plan candidates.

Dependency direction (D §3): nothing here imports filesystem-mutating code;
`planning`/`safety`/`collision`/`writer`/`init_flow` may import this module,
never the reverse. This module performs no filesystem writes.
"""

from __future__ import annotations

import importlib.resources
from importlib.resources.abc import Traversable
from pathlib import PurePosixPath


def _payload_root() -> Traversable:
    """Resolve the snapshot root as a Traversable.

    `se_agent._payload` is a data-only directory (no `__init__.py`), importable
    as a namespace subpackage, so `importlib.resources.files()` works both for
    the editable install (points at `src/`) and the wheel-installed copy
    (points at site-packages) without importing any code from it.
    """
    return importlib.resources.files("se_agent._payload")


#: Root of the committed payload snapshot.
PAYLOAD_ROOT: Traversable = _payload_root()


def enumerate_payload() -> tuple[tuple[PurePosixPath, PurePosixPath], ...]:
    """Enumerate plan candidates from the snapshot, sorted by destination parts.

    Returns `(dest_rel, payload_rel)` pairs of `PurePosixPath` (D4/D11: the
    write-set is defined in POSIX form and never derived from user input).
    Deterministic order: lexicographic on the tuple of `dest_rel.parts`.
    WU3's `build_plan()` wraps these candidates into frozen `PlannedFile`s.
    """
    relative: list[tuple[str, ...]] = []

    def walk(traversable: Traversable, prefix: tuple[str, ...]) -> None:
        for entry in traversable.iterdir():
            parts = (*prefix, entry.name)
            if entry.is_dir():
                walk(entry, parts)
            elif entry.is_file():
                relative.append(parts)

    walk(PAYLOAD_ROOT, ())
    relative.sort()
    return tuple((PurePosixPath(*parts), PurePosixPath(*parts)) for parts in relative)
