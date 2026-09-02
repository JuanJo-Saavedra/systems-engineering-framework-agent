"""Registry↔skills coherence verifier (pure, read-only, schema-agnostic).

The registry (`runtime/catalogo/skill-registry.md`) is HAND-MAINTAINED free-form
documentation: this module asserts NO internal contract for it — no table
shape, column count or order, section names, frontmatter keys, backticks, or
installed ruta forms. The single coherence invariant is distribution-level:

1. every real skill directory under `runtime/skills/` that contains a
   `SKILL.md` (its directory name = its full id) must appear somewhere in the
   registry body as that complete id, matched with safe boundaries so an
   accidental longer identifier (e.g. `<id>-v2`) or a substring of another
   token is not accepted;
2. skill directory names follow the generic kebab-case executable-skill
   naming convention (conceptual capability ids elsewhere are out of scope);
3. the registry exists and is non-empty;
4. verification is strictly read-only: it never writes, generates, or modifies
   anything.

The check adapts dynamically to skills added or removed under
`runtime/skills/`: no id, inventory, count, section, or table structure is
encoded here. Pure stdlib (`re`, `pathlib`); works on the canonical repo paths
or on temp fixture copies; tests assert byte-invariance around every run.
"""

from __future__ import annotations

import re
from pathlib import Path

#: Generic executable-skill naming convention: kebab-case (lowercase letters and
#: digits, hyphen-separated). Conceptual capability ids (e.g. snake_case ids in
#: `framework/guias/skill-architecture.md`) are out of scope: this rule applies
#: only to executable skill directory names under `runtime/skills/`.
KEBAB_CASE_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")

#: Characters that may extend a kebab-case identifier left or right. A full-id
#: match must not be adjacent to any of these, so `<id>-v2`, `x<id>`, or
#: `<id>_suffix` never count as a mention of `<id>`.
_ID_EDGE_CHARS = "0-9A-Za-z-"


def skill_directories(skills_root: Path) -> set[str]:
    """Skill ids: directories under `skills_root` containing a `SKILL.md`."""
    if not skills_root.is_dir():
        return set()
    return {p.name for p in skills_root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()}


def id_boundary_pattern(skill_id: str) -> re.Pattern[str]:
    """Regex matching `skill_id` as a complete identifier with safe boundaries.

    Pure text matching: the identifier may appear anywhere in the registry body
    (table cell, list item, prose — any format), but a longer kebab-style token
    that merely contains it as a substring is rejected.
    """
    return re.compile(rf"(?<![{_ID_EDGE_CHARS}]){re.escape(skill_id)}(?![{_ID_EDGE_CHARS}])")


def registry_mentions_skill(text: str, skill_id: str) -> bool:
    """True if the registry body mentions `skill_id` as a complete identifier."""
    return id_boundary_pattern(skill_id).search(text) is not None


def check_coherence(skills_root: Path, registry_path: Path) -> list[str]:
    """Distribution-level registry↔skills check on arbitrary paths (canonical or temp fixtures).

    Pure read-only: reads the registry text and skill directory names, never
    writes. Returns human-readable problems; empty list = coherent.
    """
    problems: list[str] = []
    if not registry_path.is_file():
        return [f"registry file does not exist: {registry_path}"]
    text = registry_path.read_text(encoding="utf-8")
    if not text.strip():
        return [f"registry file is empty: {registry_path}"]

    if not skills_root.is_dir():
        return [*problems, f"skills source directory does not exist: {skills_root}"]

    skill_ids = skill_directories(skills_root)
    if not skill_ids:
        problems.append(f"no skill directories containing a SKILL.md found under: {skills_root}")

    for name in sorted(skill_ids):
        if not KEBAB_CASE_RE.fullmatch(name):
            problems.append(
                f"non-kebab-case skill directory {name!r}: executable skill ids must be kebab-case"
            )
        if not registry_mentions_skill(text, name):
            problems.append(
                f"registry does not mention skill {name!r}: complete id not found in registry body"
            )
    return problems
