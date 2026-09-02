"""Registry↔skills coherence as a general contract for arbitrary runtime skills.

Executable skills under `runtime/skills/` follow a generic kebab-case naming
convention; the frontmatter of every `SKILL.md` carries the identity/selection
metadata (`name`, `description`) that the orchestrator uses for discovery.

The hand-maintained registry (`runtime/catalogo/skill-registry.md`) and the skill
sources (`runtime/skills/*/SKILL.md`) must stay bidirectionally coherent for
whatever skills exist: every skill has exactly one correctly-named registry
entry, every entry resolves to an existing skill, counts match, and there are no
duplicates, stale or malformed rows. The verifier
(`tests/helpers/registry_check.py`) is pure, stdlib-only, and read-only: the
canonical registry must be byte-identical before and after every verification
run.

Skill-level validation here is deliberately structural and limited to
frontmatter identity/selection metadata: `name` must be a non-empty string equal
to the (kebab-case) directory name and `description` must be a non-empty string.
Semantic body content, authoritative references, and payload byte-identity are
out of scope (payload coherence is owned by `tests/unit/test_payload_coherence.py`).

Mutation-based rejection fixtures select ids, rows, and counts dynamically from
the parsed canonical data, and triangulation runs on temporary registries with
arbitrary synthetic skill definitions — the canonical registry and skill sources
are never mutated by a test.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "runtime" / "skills"
REGISTRY_PATH = REPO_ROOT / "runtime" / "catalogo" / "skill-registry.md"


def _load_registry_check():
    """Import `tests/helpers/registry_check.py` as a module (test helper, not a package)."""
    script = REPO_ROOT / "tests" / "helpers" / "registry_check.py"
    spec = importlib.util.spec_from_file_location("registry_check_under_test", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # required before exec_module (dataclass resolution, py3.14)
    spec.loader.exec_module(module)
    return module


registry_check = _load_registry_check()


def _skill_dirs(root: Path) -> set[str]:
    """Skill ids = directories under `root` containing a `SKILL.md` (helper contract)."""
    return registry_check.skill_directories(root)


# --- Canonical bidirectional coherence ------------------------------------------


def test_canonical_skills_and_registry_are_coherent() -> None:
    """Bidirectional check on the canonical repo sources passes with no problems,
    whatever the current set of skills is."""
    assert SKILLS_ROOT.is_dir(), f"skills source directory missing: {SKILLS_ROOT}"
    assert REGISTRY_PATH.is_file(), f"registry missing: {REGISTRY_PATH}"
    problems = registry_check.check_coherence(SKILLS_ROOT, REGISTRY_PATH)
    assert problems == [], "\n".join(problems)


def test_registry_row_level_structure_is_valid() -> None:
    """Structural half: rows parse, ruta form is exact, count matches frontmatter."""
    problems = registry_check.check_registry_text(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert problems == [], "\n".join(problems)


# --- Skill-level frontmatter identity/selection metadata (structural only) ------


def test_every_skill_frontmatter_carries_valid_identity_metadata() -> None:
    """Every discovered `runtime/skills/*/SKILL.md` parses as frontmatter (via the
    shared helper) and declares structural identity/selection metadata: `name` is a
    non-empty string equal to the kebab-case directory name, `description` is a
    non-empty string. Body semantics and references are not inspected here."""
    skill_dirs = _skill_dirs(SKILLS_ROOT)
    assert skill_dirs, "expected at least one discovered skill under runtime/skills/"
    problems: list[str] = []
    for name in sorted(skill_dirs):
        skill_text = (SKILLS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")
        front = registry_check.extract_frontmatter(skill_text)
        if not front:
            problems.append(f"skill {name!r}: SKILL.md does not parse as frontmatter")
            continue
        declared_name = front.get("name")
        if not isinstance(declared_name, str) or not declared_name.strip():
            problems.append(f"skill {name!r}: frontmatter name must be a non-empty string, got {declared_name!r}")
        elif declared_name != name:
            problems.append(f"skill {name!r}: frontmatter name {declared_name!r} != directory name")
        if not registry_check.KEBAB_CASE_RE.fullmatch(name):
            problems.append(f"skill {name!r}: directory name must be kebab-case")
        declared_description = front.get("description")
        if not isinstance(declared_description, str) or not declared_description.strip():
            problems.append(f"skill {name!r}: frontmatter description must be a non-empty string")
    assert problems == [], "\n".join(problems)


# --- Dynamic canonical-row/count mutation helpers --------------------------------


def _canonical_registry_text() -> str:
    return REGISTRY_PATH.read_text(encoding="utf-8")


def _canonical_rows() -> list:
    """Parsed canonical rows; at least one row is required for mutation fixtures."""
    _, rows, _ = registry_check.parse_registry(_canonical_registry_text())
    assert rows, "canonical registry must contain at least one skill row for mutation fixtures"
    return rows


def _row_line_index(text: str, skill_id: str) -> int:
    """Index of the unique table row naming `skill_id` in backticks."""
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.strip().startswith("|") and f"`{skill_id}`" in line]
    assert len(matches) == 1, f"expected exactly one registry row for {skill_id!r}, found {len(matches)}"
    return matches[0]


def _row_substituted(text: str, skill_id: str, replacement: str | None) -> str:
    """Replace the row naming `skill_id` with `replacement` (or drop the row if None)."""
    index = _row_line_index(text, skill_id)
    lines = text.splitlines()
    if replacement is None:
        del lines[index]
    else:
        lines[index] = replacement
    return "\n".join(lines) + "\n"


def _row_appended(text: str, after_id: str, extra_row: str) -> str:
    """Insert `extra_row` immediately after the row naming `after_id` (inside the table)."""
    index = _row_line_index(text, after_id)
    lines = text.splitlines()
    lines.insert(index + 1, extra_row)
    return "\n".join(lines) + "\n"


def _count_substituted(text: str, new_count: int) -> str:
    """Replace the frontmatter `skills_available` count with `new_count` (dynamically)."""
    substituted, n = re.subn(r"(?m)^skills_available:.*$", f"skills_available: {new_count}", text, count=1)
    assert n == 1, "frontmatter skills_available line not found for substitution"
    return substituted


def _declared_count(text: str) -> int:
    fields = registry_check.extract_frontmatter(text)
    raw = fields.get("skills_available")
    assert raw is not None and raw.isdigit(), f"canonical registry must declare an integer skills_available, got {raw!r}"
    return int(raw)


# --- Triangulation: synthetic temp registries with arbitrary skills --------------


def _skill_text(name: str, *, frontmatter_name: str | None = None) -> str:
    """A minimal, generic SKILL.md fixture (name defaults to the directory name)."""
    declared = name if frontmatter_name is None else frontmatter_name
    return f'---\nname: {declared}\ndescription: "generic capability fixture"\n---\n\ncuerpo generico\n'


def _write_skill_fixture(root: Path, name: str, *, frontmatter_name: str | None = None) -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(_skill_text(name, frontmatter_name=frontmatter_name), encoding="utf-8")


def _registry_fixture_text(rows: list[tuple[str, str]], *, declared: int | None = None) -> str:
    """A minimal registry fixture: frontmatter count + one row per (id, trigger)."""
    count = len(rows) if declared is None else declared
    lines = [
        "---",
        f"skills_available: {count}",
        "---",
        "",
        "## Skills disponibles",
        "",
        "| id | trigger | ruta |",
        "| -- | ------- | ---- |",
    ]
    for skill_id, trigger in rows:
        lines.append(f"| `{skill_id}` | {trigger} | `.agents/skills/{skill_id}/SKILL.md` |")
    return "\n".join(lines) + "\n"


def _temp_registry(tmp_path: Path, text: str) -> Path:
    """Write a registry fixture copy to tmp_path; the canonical registry is never touched."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    fixture = tmp_path / "skill-registry.md"
    fixture.write_text(text, encoding="utf-8")
    return fixture


FIXTURE_SKILLS = ("alpha-skill", "beta-skill", "gamma-skill")


def _coherent_fixture_registry_rows() -> list[tuple[str, str]]:
    """Rows for the synthetic valid fixture set (one row per fixture skill)."""
    return [(skill_id, f"trigger for {skill_id}") for skill_id in FIXTURE_SKILLS]


def test_multiple_valid_synthetic_skills_are_coherent(tmp_path: Path) -> None:
    """Arbitrary valid skills (no canonical content involved) pass the coherence check."""
    skills_root = tmp_path / "skills"
    for skill_id in FIXTURE_SKILLS:
        _write_skill_fixture(skills_root, skill_id)
    registry = _temp_registry(tmp_path / "registry", _registry_fixture_text(_coherent_fixture_registry_rows()))
    problems = registry_check.check_coherence(skills_root, registry)
    assert problems == [], "\n".join(problems)


def test_missing_registry_row_fails(tmp_path: Path) -> None:
    """A valid skill with no registry row fails, naming the dynamically selected skill."""
    missing_id = FIXTURE_SKILLS[-1]
    rows = [row for row in _coherent_fixture_registry_rows() if row[0] != missing_id]
    skills_root = tmp_path / "skills"
    for skill_id in FIXTURE_SKILLS:
        _write_skill_fixture(skills_root, skill_id)
    registry = _temp_registry(tmp_path / "registry", _registry_fixture_text(rows))
    problems = registry_check.check_coherence(skills_root, registry)
    assert problems, "missing registry row must be rejected"
    assert any("missing registry entry" in problem and missing_id in problem for problem in problems), "\n".join(problems)


def test_stale_registry_row_fails(tmp_path: Path) -> None:
    """A registry row with no matching skill fails, naming the stale id."""
    stale_id = "delta-ghost"
    assert stale_id not in FIXTURE_SKILLS, "stale fixture id must not exist as a skill"
    rows = [*_coherent_fixture_registry_rows(), (stale_id, f"trigger for {stale_id}")]
    skills_root = tmp_path / "skills"
    for skill_id in FIXTURE_SKILLS:
        _write_skill_fixture(skills_root, skill_id)
    registry = _temp_registry(tmp_path / "registry", _registry_fixture_text(rows))
    problems = registry_check.check_coherence(skills_root, registry)
    assert problems, "stale registry row must be rejected"
    assert any("stale registry entry" in problem and stale_id in problem for problem in problems), "\n".join(problems)


def test_frontmatter_name_mismatch_among_valid_peers_fails(tmp_path: Path) -> None:
    """One peer whose frontmatter name differs from its directory fails, naming it."""
    mismatched_id = FIXTURE_SKILLS[-1]
    renamed = "gamma-renamed"
    skills_root = tmp_path / "skills"
    for skill_id in FIXTURE_SKILLS:
        _write_skill_fixture(skills_root, skill_id, frontmatter_name=renamed if skill_id == mismatched_id else None)
    registry = _temp_registry(tmp_path / "registry", _registry_fixture_text(_coherent_fixture_registry_rows()))
    problems = registry_check.check_coherence(skills_root, registry)
    assert problems, "frontmatter name mismatch must be rejected"
    assert any("name mismatch" in problem and mismatched_id in problem for problem in problems), "\n".join(problems)


def test_non_kebab_directory_among_valid_peers_fails(tmp_path: Path) -> None:
    """One snake_case directory among valid peers fails, naming it."""
    bad_dir = "gamma_skill"
    skills_root = tmp_path / "skills"
    for skill_id in FIXTURE_SKILLS[:-1]:
        _write_skill_fixture(skills_root, skill_id)
    _write_skill_fixture(skills_root, bad_dir)
    rows = [
        *( (skill_id, f"trigger for {skill_id}") for skill_id in FIXTURE_SKILLS[:-1] ),
        (bad_dir, f"trigger for {bad_dir}"),
    ]
    registry = _temp_registry(tmp_path / "registry", _registry_fixture_text(rows))
    problems = registry_check.check_coherence(skills_root, registry)
    assert problems, "non-kebab skill directory must be rejected"
    assert any("kebab-case" in problem and bad_dir in problem for problem in problems), "\n".join(problems)


# --- Rejection fixtures on the canonical registry (dynamically mutated copies) ---


def test_rejects_non_kebab_case_registry_id(tmp_path: Path) -> None:
    """Generic convention: a registry row whose id is not kebab-case fails, naming the id.
    The invalid id is deterministic synthetic data (never derived from a canonical id,
    which may legitimately contain no hyphen); the ruta matches the synthetic id so the
    non-kebab-case rejection is isolated."""
    invalid_id = "invalid_skill_id"
    assert registry_check.KEBAB_CASE_RE.fullmatch(invalid_id) is None, "fixture id must actually be non-kebab"
    assert invalid_id not in {row.skill_id for row in _canonical_rows()}, "fixture id must not collide with canonical ids"
    first = _canonical_rows()[0]
    problems = registry_check.check_registry_text(
        _row_substituted(
            _canonical_registry_text(),
            first.skill_id,
            f"| `{invalid_id}` | {first.trigger} | `.agents/skills/{invalid_id}/SKILL.md` |",
        )
    )
    assert problems, "non-kebab registry id must be rejected"
    assert any("kebab-case" in problem and invalid_id in problem for problem in problems), "\n".join(problems)


def test_rejects_duplicate_registry_row(tmp_path: Path) -> None:
    """A duplicated entry fails, naming the duplicate."""
    first = _canonical_rows()[0]
    text = _row_appended(
        _count_substituted(_canonical_registry_text(), _declared_count(_canonical_registry_text()) + 1),
        first.skill_id,
        f"| `{first.skill_id}` | {first.trigger} | `{first.ruta}` |",
    )
    problems = registry_check.check_registry_text(text)
    assert problems, "duplicate row must be rejected"
    assert any("duplicate registry entry" in problem and first.skill_id in problem for problem in problems), "\n".join(problems)


def test_rejects_skill_without_entry_missing(tmp_path: Path) -> None:
    """A skill with no registry entry (missing) fails, naming the skill."""
    first = _canonical_rows()[0]
    text = _row_substituted(_canonical_registry_text(), first.skill_id, None)
    problems = registry_check.check_coherence(SKILLS_ROOT, _temp_registry(tmp_path, text))
    assert problems, "missing entry must be rejected"
    assert any("missing registry entry" in problem and first.skill_id in problem for problem in problems), "\n".join(problems)


def test_rejects_entry_without_skill_stale(tmp_path: Path) -> None:
    """A registry entry with no matching skill (stale) fails, naming the entry."""
    stale_id = "ghost-skill"
    assert stale_id not in _skill_dirs(SKILLS_ROOT), "stale fixture id must not exist as a skill"
    first = _canonical_rows()[0]
    text = _row_appended(
        _count_substituted(_canonical_registry_text(), _declared_count(_canonical_registry_text()) + 1),
        first.skill_id,
        f"| `{stale_id}` | orphan trigger | `.agents/skills/{stale_id}/SKILL.md` |",
    )
    problems = registry_check.check_coherence(SKILLS_ROOT, _temp_registry(tmp_path, text))
    assert problems, "stale entry must be rejected"
    assert any("stale registry entry" in problem and stale_id in problem for problem in problems), "\n".join(problems)


def test_rejects_count_mismatch(tmp_path: Path) -> None:
    """Frontmatter `skills_available` != number of rows fails, naming both values."""
    canonical_text = _canonical_registry_text()
    declared = _declared_count(canonical_text)
    row_count = len(_canonical_rows())
    wrong_count = declared + 2
    assert wrong_count != row_count, "fixture count must actually mismatch the row count"
    problems = registry_check.check_registry_text(_count_substituted(canonical_text, wrong_count))
    assert problems, "count mismatch must be rejected"
    assert any(
        "count mismatch" in problem and str(wrong_count) in problem and f"{row_count} row" in problem
        for problem in problems
    ), "\n".join(problems)


def test_rejects_malformed_row(tmp_path: Path) -> None:
    """A row with the wrong cell count fails, naming the malformed row."""
    first = _canonical_rows()[0]
    text = _row_substituted(_canonical_registry_text(), first.skill_id, f"| `{first.skill_id}` | only two cells |")
    problems = registry_check.check_registry_text(text)
    assert problems, "malformed row must be rejected"
    assert any("malformed registry row" in problem for problem in problems), "\n".join(problems)


def test_rejects_wrong_ruta(tmp_path: Path) -> None:
    """A `ruta` that is not exactly `.agents/skills/<id>/SKILL.md` fails."""
    first = _canonical_rows()[0]
    wrong_ruta = first.ruta.replace(".agents/skills/", ".skills/", 1)
    assert wrong_ruta != first.ruta, "fixture ruta must actually differ from the canonical ruta"
    problems = registry_check.check_registry_text(
        _row_substituted(
            _canonical_registry_text(),
            first.skill_id,
            f"| `{first.skill_id}` | {first.trigger} | `{wrong_ruta}` |",
        )
    )
    assert problems, "wrong ruta must be rejected"
    assert any("wrong ruta" in problem and first.skill_id in problem for problem in problems), "\n".join(problems)


# --- Read-only behavior (canonical sources stay byte-identical) ------------------


def test_verification_is_read_only_canonical_registry_byte_invariant() -> None:
    """A verification run (pass) leaves the registry and skill sources byte-identical."""
    registry_before = REGISTRY_PATH.read_bytes()
    skills_before = {p: p.read_bytes() for p in sorted(SKILLS_ROOT.rglob("*")) if p.is_file()}
    for _ in range(2):
        problems = registry_check.check_coherence(SKILLS_ROOT, REGISTRY_PATH)
        assert problems == [], "\n".join(problems)
    assert REGISTRY_PATH.read_bytes() == registry_before, "registry was modified by verification"
    skills_after = {p: p.read_bytes() for p in sorted(SKILLS_ROOT.rglob("*")) if p.is_file()}
    assert skills_after == skills_before, "skill sources were modified by verification"


def test_negative_fixtures_never_touch_canonical_registry(tmp_path: Path) -> None:
    """All rejection fixtures run on temp copies; the canonical registry and skill
    sources stay byte-identical across every negative scenario."""
    registry_before = REGISTRY_PATH.read_bytes()
    skills_before = {p: p.read_bytes() for p in sorted(SKILLS_ROOT.rglob("*")) if p.is_file()}
    test_rejects_duplicate_registry_row(tmp_path / "dup")
    test_rejects_skill_without_entry_missing(tmp_path / "missing")
    test_rejects_entry_without_skill_stale(tmp_path / "stale")
    test_rejects_count_mismatch(tmp_path / "count")
    test_rejects_malformed_row(tmp_path / "malformed")
    test_rejects_wrong_ruta(tmp_path / "ruta")
    test_rejects_non_kebab_case_registry_id(tmp_path / "kebab")
    test_multiple_valid_synthetic_skills_are_coherent(tmp_path / "valid")
    test_missing_registry_row_fails(tmp_path / "fixture-missing")
    test_stale_registry_row_fails(tmp_path / "fixture-stale")
    test_frontmatter_name_mismatch_among_valid_peers_fails(tmp_path / "fixture-name")
    test_non_kebab_directory_among_valid_peers_fails(tmp_path / "fixture-kebab")
    assert REGISTRY_PATH.read_bytes() == registry_before
    assert {p: p.read_bytes() for p in sorted(SKILLS_ROOT.rglob("*")) if p.is_file()} == skills_before
