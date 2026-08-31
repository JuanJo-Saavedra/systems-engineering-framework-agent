"""D7 / REQ-R1..R3 — registry↔skills coherence verifier (pure, read-only).

Parses the hand-maintained registry (`runtime/catalogo/skill-registry.md`) and
proves bidirectional coherence with `runtime/skills/*/SKILL.md`:

1. registry structure: rows parse under `## Skills disponibles`, no duplicates,
   no malformed rows, each `ruta` has the exact installed form
   `.agents/skills/<id>/SKILL.md`, and the frontmatter `skills_available` count
   equals the number of rows;
2. skills side: every skill directory's frontmatter `name` equals its
   directory name (D6/D7);
3. bidirectional set equality: skill ids ≡ registry ids (missing → fail,
   stale → fail).

The registry is HAND-MAINTAINED (REQ-R3): this module never writes, never
generates, and never modifies anything. It is pure stdlib (`re`, `pathlib`,
`hashlib`, `dataclasses`) and works on the canonical repo paths or on temp
fixture copies; tests assert byte-invariance around every run.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

#: Registry section where skill rows live (design D7).
SECTION_HEADER = "## Skills disponibles"

#: Fixed table header cells per design D7.
HEADER_CELLS = ("id", "trigger", "ruta")

#: Exact installed ruta form for a skill id (D7).
RUTA_TEMPLATE = ".agents/skills/{skill_id}/SKILL.md"

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n?---[ \t]*\n", re.DOTALL)
_ROW_SPLIT_RE = re.compile(r"\s*\|\s*")
_SEPARATOR_CELL_RE = re.compile(r"-+")


@dataclass(frozen=True)
class RegistryRow:
    """One parsed registry table row: `| id | trigger | ruta |`."""

    skill_id: str
    trigger: str
    ruta: str


def extract_frontmatter(text: str) -> dict[str, str]:
    """Shared simple frontmatter extractor: `key: value` lines between leading `---` fences.

    Used by both the registry parser (`skills_available`) and the AC-12 test
    (skill `name`) — one extraction rule, no duplication.
    """
    match = _FRONTMATTER_RE.match(text)
    if match is None:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields


def parse_registry(text: str) -> tuple[list[str], list[RegistryRow], int | None]:
    """Parse registry text → (problems, rows, declared `skills_available`).

    Pure text parsing: malformed rows are reported, never raised, so one bad
    row cannot hide the others.
    """
    problems: list[str] = []
    rows: list[RegistryRow] = []

    fields = extract_frontmatter(text)
    raw_count = fields.get("skills_available")
    declared: int | None = None
    if raw_count is None or not raw_count.isdigit():
        problems.append(f"frontmatter skills_available missing or not an integer: {raw_count!r}")
    else:
        declared = int(raw_count)

    lines = text.splitlines()
    try:
        section_start = lines.index(SECTION_HEADER)
    except ValueError:
        problems.append(f"registry section not found: {SECTION_HEADER!r}")
        return problems, rows, declared

    seen_table = False
    for line in lines[section_start + 1 :]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break  # next section header: table ended
        if not stripped.startswith("|"):
            if seen_table and stripped:
                break  # prose after the table: table ended
            continue  # blank lines / prose before the table
        cells = [cell.strip() for cell in _ROW_SPLIT_RE.split(stripped.strip("|"))]
        if tuple(cells) == HEADER_CELLS:
            continue  # fixed D7 table header row
        if cells and all(_SEPARATOR_CELL_RE.fullmatch(cell) for cell in cells):
            continue  # markdown table separator row
        if len(cells) != 3 or not all(cells):
            problems.append(f"malformed registry row (expected 3 cells: id, trigger, ruta): {stripped!r}")
            seen_table = True
            continue
        rows.append(
            RegistryRow(
                skill_id=cells[0].strip().strip("`"),
                trigger=cells[1].strip(),
                ruta=cells[2].strip().strip("`"),
            )
        )
        seen_table = True
    return problems, rows, declared


def check_registry_text(text: str) -> list[str]:
    """Row-level structural checks on registry text (no filesystem access).

    Fails on: malformed rows, duplicate ids, wrong `ruta` form, and a
    `skills_available` count that does not equal the number of rows (REQ-R2).
    """
    problems, rows, declared = parse_registry(text)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row.skill_id] = counts.get(row.skill_id, 0) + 1
    for skill_id, count in sorted(counts.items()):
        if count > 1:
            problems.append(f"duplicate registry entry for skill {skill_id!r} ({count} rows)")

    for row in rows:
        expected = RUTA_TEMPLATE.format(skill_id=row.skill_id)
        if row.ruta != expected:
            problems.append(f"wrong ruta for skill {row.skill_id!r}: {row.ruta!r} (expected {expected!r})")

    if declared is not None and declared != len(rows):
        problems.append(
            f"skills_available count mismatch: frontmatter declares {declared}, registry has {len(rows)} row(s)"
        )
    return problems


def skill_directories(skills_root: Path) -> set[str]:
    """Skill ids: directories under `skills_root` containing a `SKILL.md` (D7)."""
    if not skills_root.is_dir():
        return set()
    return {p.name for p in skills_root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()}


def check_coherence(skills_root: Path, registry_path: Path) -> list[str]:
    """REQ-R1/R2 bidirectional check on arbitrary paths (canonical or temp fixtures).

    Pure read-only: reads the registry text and each skill's frontmatter, never
    writes. Returns human-readable problems; empty list = coherent.
    """
    problems: list[str] = []
    if not registry_path.is_file():
        return [f"registry file does not exist: {registry_path}"]
    text = registry_path.read_text(encoding="utf-8")
    problems.extend(check_registry_text(text))

    if not skills_root.is_dir():
        problems.append(f"skills source directory does not exist: {skills_root}")
        return problems

    skill_ids = skill_directories(skills_root)
    for name in sorted(skill_ids):
        skill_text = (skills_root / name / "SKILL.md").read_text(encoding="utf-8")
        declared_name = extract_frontmatter(skill_text).get("name")
        if declared_name != name:
            problems.append(f"frontmatter name mismatch for skill {name!r}: name={declared_name!r}")

    _, rows, _ = parse_registry(text)
    registry_ids = {row.skill_id for row in rows}
    for missing in sorted(skill_ids - registry_ids):
        problems.append(f"missing registry entry for skill {missing!r}")
    for stale in sorted(registry_ids - skill_ids):
        problems.append(f"stale registry entry (no matching skill directory): {stale!r}")
    return problems


def file_digest(path: Path) -> str:
    """sha256 hex digest of a file's bytes (content-hash self-assertion support)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()
