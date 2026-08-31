"""Safe path resolution: pure preflight validation (design D4/D11).

`validate_plan(root, plan)` runs for the whole plan before any byte is written
and performs zero filesystem mutation — no probe writes, no writability
checks; writability is validated only by the actual write loop (design §2 D4
"No probe writes"). Checks, in order per destination:

1. Plan-path sanity: reject absolute destinations and `..` parts (defense in
   depth; unreachable by construction, asserted here too).
2. Ancestor symlink walk: every existing ancestor component is `os.lstat`ed;
   a symlink ancestor must `resolve()` inside the target root or the plan is
   rejected naming the symlink (REQ-F2).
3. Collision-path symlink hard error: if the destination itself exists and
   `lstat` reports a symlink (including broken symlinks, via lexists
   semantics) the plan is rejected regardless of symlink direction — the plan
   never writes through a symlink.
4. Parent-path check: an ancestor that exists as a non-directory is rejected.

`--force` never relaxes any of these (REQ-W4): force only affects collision
resolution (design §5). Violations are deterministic: sorted by
`(path, rule)` and each names the offending path.
"""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

from se_agent.planning import PlannedFile

RULE_ABSOLUTE = "absolute-path"
RULE_PARENT_REFERENCE = "parent-reference"
RULE_SYMLINK_ESCAPE = "symlink-escape"
RULE_SYMLINK_DESTINATION = "symlink-destination"
RULE_PARENT_NOT_DIRECTORY = "parent-not-directory"
RULE_ROOT_NOT_DIRECTORY = "root-not-directory"


@dataclass(frozen=True, order=True)
class Violation:
    """A named preflight rejection: the offending path and the violated rule."""

    path: str
    rule: str


def validate_plan(root: Path, plan: Iterable[PlannedFile]) -> list[Violation]:
    """Validate `plan` against target `root`; return all violations, sorted.

    Pure: reads the filesystem only through `os.path.lexists`, `os.lstat`,
    `Path.is_dir()` and `Path.resolve()` — never writes.
    """
    resolved_root = Path(root).resolve()
    if not resolved_root.is_dir():
        return [Violation(path=str(root), rule=RULE_ROOT_NOT_DIRECTORY)]

    violations: list[Violation] = []
    for item in plan:
        dest = item.dest_rel
        if dest.is_absolute():
            violations.append(Violation(dest.as_posix(), RULE_ABSOLUTE))
            continue
        if ".." in dest.parts:
            violations.append(Violation(dest.as_posix(), RULE_PARENT_REFERENCE))
            continue
        _check_destination(resolved_root, dest, violations)
    return sorted(violations)


def _check_destination(
    root: Path, dest: PurePosixPath, violations: list[Violation]
) -> None:
    """Walk the destination's ancestor chain from `root` downward.

    Follows internal symlinks (after proving they stay inside `root`), stops at
    the first missing component (nothing below it exists yet), and flags
    symlink escapes, symlink destinations, and non-directory ancestors.
    """
    current = root
    lexical: tuple[str, ...] = ()
    parts = dest.parts
    for index, part in enumerate(parts):
        candidate = current / part
        lexical = (*lexical, part)
        if not os.path.lexists(candidate):
            return  # nothing below a missing component exists to validate
        try:
            entry_stat = os.lstat(candidate)
        except FileNotFoundError:
            # Vanished between lexists and lstat: nothing below it exists.
            return
        is_last = index == len(parts) - 1
        if stat.S_ISLNK(entry_stat.st_mode):
            if is_last:
                # Hard error regardless of symlink direction (D4 step 4).
                violations.append(
                    Violation(dest.as_posix(), RULE_SYMLINK_DESTINATION)
                )
                return
            resolved = candidate.resolve()
            if not _is_inside(root, resolved):
                violations.append(
                    Violation("/".join(lexical), RULE_SYMLINK_ESCAPE)
                )
                return
            current = resolved
        elif stat.S_ISDIR(entry_stat.st_mode):
            current = candidate
        else:
            if not is_last:
                violations.append(
                    Violation("/".join(lexical), RULE_PARENT_NOT_DIRECTORY)
                )
            return  # destination existing as a regular file is a collision, not unsafe


def _is_inside(root: Path, resolved: Path) -> bool:
    return resolved == root or resolved.is_relative_to(root)
