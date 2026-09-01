"""WU5 — REQ-R1/R2/R3, REQ-S1, AC-10/AC-12 — registry↔skills coherence and F0 skill reference integrity.

Executable skills under `runtime/skills/` follow a generic kebab-case naming
convention (`f0-factibilidad`); the stable conceptual capability id
(`f0_factibilidad`, snake_case) lives only in the capability catalog
(`framework/guias/skill-architecture.md`) and is never used as an executable
name or path.

The hand-maintained registry (`runtime/catalogo/skill-registry.md`) and the skill
sources (`runtime/skills/*/SKILL.md`) must stay bidirectionally coherent: every
skill has exactly one correctly-named registry entry, every entry resolves to an
existing skill, counts match, and there are no duplicates, stale or malformed
rows (REQ-R1/R2). The verifier (`tests/helpers/registry_check.py`) is pure,
stdlib-only, and read-only: the canonical registry must be byte-identical before
and after every verification run (REQ-R3).

The F0 skill (`f0-factibilidad`) must be exactly one functional skill whose
references resolve in the installed tree, form-checked for `proyecto/` state
references (REQ-S1 / AC-12). It is an adaptive, state-aware capability: it
works from evidence, distinguishes facts/assumptions/gaps, asks progressive
questions, matures drafts, and evaluates handoff readiness without ever
approving the phase transition itself (approval is explicit and human).
Installed-tree resolution is proven
against the committed payload mirror (`src/se_agent/_payload/`), which is the
byte-exact oracle of what `se-agent init` installs (D1).

The skill body is a state-aware capability description, not an activation
contract or a task checklist: the orchestrator selects the skill from project
state (the frontmatter description is the sole discovery/selection trigger
surface), so the body must contain no activation/trigger section — not even
under renamed headings — and no fixed numbered procedure/checklist section.

Negative (triangulation) cases run against temp copies only — the canonical
registry and skill sources are never mutated by a test.
"""

from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "runtime" / "skills"
REGISTRY_PATH = REPO_ROOT / "runtime" / "catalogo" / "skill-registry.md"
PAYLOAD_ROOT = REPO_ROOT / "src" / "se_agent" / "_payload"
EXPECTED_SKILL_ID = "f0-factibilidad"

#: Stable conceptual capability id (snake_case) that must NOT be used as an
#: executable skill name/path but must remain in the capability catalog.
CAPABILITY_ID = "f0_factibilidad"
SKILL_ARCHITECTURE_PATH = REPO_ROOT / "framework" / "guias" / "skill-architecture.md"


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


def _load_path_refs():
    """Import `tests/helpers/path_refs.py` (shared reference extraction, WU6 refactor)."""
    script = REPO_ROOT / "tests" / "helpers" / "path_refs.py"
    spec = importlib.util.spec_from_file_location("path_refs_under_test", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


path_refs = _load_path_refs()


def _skill_dirs(root: Path) -> set[str]:
    """Skill ids = directories under `root` containing a `SKILL.md` (helper contract)."""
    return registry_check.skill_directories(root)


# --- Canonical bidirectional coherence (REQ-R1) ---------------------------------


def test_canonical_skills_and_registry_are_coherent() -> None:
    """REQ-R1: bidirectional check on the canonical repo sources passes with no problems."""
    assert SKILLS_ROOT.is_dir(), f"skills source directory missing: {SKILLS_ROOT}"
    assert REGISTRY_PATH.is_file(), f"registry missing: {REGISTRY_PATH}"
    problems = registry_check.check_coherence(SKILLS_ROOT, REGISTRY_PATH)
    assert problems == [], "\n".join(problems)


def test_registry_row_level_structure_is_valid() -> None:
    """REQ-R1/R2 structural half: rows parse, ruta form is exact, count matches frontmatter."""
    problems = registry_check.check_registry_text(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert problems == [], "\n".join(problems)


# --- REQ-S1 / AC-12: exactly one functional F0 skill ----------------------------


def test_exactly_one_skill_exists_in_sources() -> None:
    """REQ-S1: exactly one skill (the F0 skill) exists under `runtime/skills/`."""
    skill_dirs = _skill_dirs(SKILLS_ROOT)
    assert skill_dirs == {EXPECTED_SKILL_ID}, f"expected exactly one skill {EXPECTED_SKILL_ID!r}, got {sorted(skill_dirs)}"


def test_exactly_one_skill_installed_in_payload_mirror() -> None:
    """REQ-S1: the installed `.agents/skills/` (mirrored destination-preserving as
    `_payload/.agents/skills/`, D4/REQ-P1) contains exactly one skill directory,
    byte-identical to its source."""
    mirror_skills = PAYLOAD_ROOT / ".agents" / "skills"
    assert mirror_skills.is_dir(), f"payload mirror has no skills/ directory: {mirror_skills}"
    mirror_dirs = _skill_dirs(mirror_skills)
    assert mirror_dirs == {EXPECTED_SKILL_ID}, f"expected exactly one installed skill, got {sorted(mirror_dirs)}"
    mirror_skill = mirror_skills / EXPECTED_SKILL_ID / "SKILL.md"
    source_skill = SKILLS_ROOT / EXPECTED_SKILL_ID / "SKILL.md"
    assert mirror_skill.read_bytes() == source_skill.read_bytes(), "installed skill is not byte-identical to source"


def test_skill_frontmatter_name_equals_directory_name() -> None:
    """D6/D7: frontmatter `name` must equal the directory name (checked by the verifier)."""
    skill_text = (SKILLS_ROOT / EXPECTED_SKILL_ID / "SKILL.md").read_text(encoding="utf-8")
    front = registry_check.extract_frontmatter(skill_text)
    assert front.get("name") == EXPECTED_SKILL_ID


# --- AC-12: reference integrity of the F0 skill ---------------------------------
# (extraction lives in tests/helpers/path_refs.py — shared with the WU6 Codex test)


def test_skill_references_resolve_in_installed_tree() -> None:
    """AC-12 / REQ-S1: every reference resolves in the installed tree (payload mirror).

    `proyecto/…` references are FORM-CHECKED ONLY (relative, no `..`, never
    absolute) and deliberately not existence-checked: they denote runtime-authored
    state in the consumer project, which does not exist at install time. The
    skill no longer cites `AGENTS.md` (runtime-contract guardrails are inherited
    from the harness layer, not repeated per phase); install-time payload
    references (`marco/**`, `catalogo/**`) must resolve to existing installed files.
    """
    skill_text = (SKILLS_ROOT / EXPECTED_SKILL_ID / "SKILL.md").read_text(encoding="utf-8")
    refs = path_refs.extract_path_references(skill_text)
    assert refs, "the skill must reference its authoritative sources"
    installed_refs = [ref for ref in refs if not ref.startswith("proyecto/")]
    proyecto_refs = [ref for ref in refs if ref.startswith("proyecto/")]
    assert installed_refs, "skill must reference install-time payload sources"
    assert proyecto_refs, "skill must reference the proyecto/ authoritative state it reads"
    problems: list[str] = []
    for ref in refs:
        if ref.startswith("proyecto/"):
            parts = PurePosixPath(ref).parts
            if PurePosixPath(ref).is_absolute() or ".." in parts:
                problems.append(f"malformed proyecto/ reference (must be relative, no '..'): {ref}")
            continue
        installed = PAYLOAD_ROOT / Path(*PurePosixPath(ref).parts)
        if not installed.exists():
            problems.append(f"broken reference (not in installed tree): {ref}")
    assert problems == [], "\n".join(problems)


# --- Adaptive, state-aware capability contract ----------------------------------


def test_skill_body_excludes_redundant_sections() -> None:
    """The skill body has no redundant `Disparador`/`Autoridad` sections: activation
    lives in the frontmatter description + registry trigger, and authority mapping
    lives in `framework/guias/skill-architecture.md` (capability catalog)."""
    skill_text = (SKILLS_ROOT / EXPECTED_SKILL_ID / "SKILL.md").read_text(encoding="utf-8")
    for header in ("Disparador", "Autoridad"):
        assert f"## {header}" not in skill_text, f"redundant section must be removed: {header}"

#: Activation/trigger contract sections are forbidden in the body, including
#: renamed equivalents: the orchestrator selects the skill from project state.
ACTIVATION_HEADER_PATTERN = re.compile(
    r"^##\s+.*(?:contrato de activaci|activaci|disparador|trigger|cu[áa]ndo activar|cu[áa]ndo usar).*$",
    re.IGNORECASE | re.MULTILINE,
)

#: Fixed procedure/checklist sections are forbidden in the body, including
#: renamed equivalents: the skill is a capability, not a task sequence.
PROCEDURE_HEADER_PATTERN = re.compile(
    r"^##\s+.*(?:procedimiento|checklist|lista de tareas|pasos|plan de trabajo).*$",
    re.IGNORECASE | re.MULTILINE,
)

#: A body-level run of consecutive numbered list items (a fixed task sequence).
NUMBERED_LIST_RUN_PATTERN = re.compile(r"^(?:\d+\.\s+.+\n)+", re.MULTILINE)

def _skill_body() -> str:
    """Return the skill text below the frontmatter (the description may legitimately
    contain trigger words; only body sections are checked here)."""
    skill_text = (SKILLS_ROOT / EXPECTED_SKILL_ID / "SKILL.md").read_text(encoding="utf-8")
    lines = skill_text.splitlines(keepends=True)
    assert lines[0].rstrip("\n") == "---", "skill file must start with a frontmatter delimiter"
    end = next(i for i in range(1, len(lines)) if lines[i].rstrip("\n") == "---")
    return "".join(lines[end + 1:])

def test_skill_body_has_no_activation_or_trigger_section() -> None:
    """The body assumes the skill is already loaded: no activation/trigger contract,
    not even under renamed headings (`Contrato de activación`, `Disparador`,
    `Trigger`, …). Selection is done by the orchestrator from project state."""
    matches = ACTIVATION_HEADER_PATTERN.findall(_skill_body())
    assert not matches, f"activation/trigger section must be removed from the body: {matches}"

def test_skill_body_has_no_fixed_procedure_or_checklist() -> None:
    """The body is a state-aware capability, not a task checklist: no procedure/
    checklist section under any heading, and no fixed numbered sequence of five or
    more ordered steps (which would prescribe a task order regardless of state)."""
    body = _skill_body()
    header_matches = PROCEDURE_HEADER_PATTERN.findall(body)
    assert not header_matches, f"fixed procedure/checklist section must be removed from the body: {header_matches}"
    checklist_runs = [
        run for run in NUMBERED_LIST_RUN_PATTERN.findall(body)
        if len(run.strip().splitlines()) >= 5
    ]
    assert not checklist_runs, f"fixed numbered checklist (>=5 ordered steps) must be removed: {checklist_runs}"

def test_skill_body_uses_approved_capability_sections() -> None:
    """The approved concise capability structure: adaptive operating mode, output
    contract, closing/handoff verdicts, and authoritative references."""
    body = _skill_body()
    for header in ("## Modo de operación", "## Contrato de salida", "## Cierre y handoff", "## Referencias"):
        assert header in body, f"missing approved capability section: {header}"


def test_skill_body_does_not_cite_agents_md() -> None:
    """`AGENTS.md` is not a phase-specific authoritative reference of the skill."""
    skill_text = (SKILLS_ROOT / EXPECTED_SKILL_ID / "SKILL.md").read_text(encoding="utf-8")
    assert "AGENTS.md" not in skill_text, "AGENTS.md must not appear in the skill body"


def test_skill_body_keeps_phase_risk_and_decision_sources() -> None:
    """The skill keeps the F0 phase contract, risk register, and technical-decision
        register as authoritative sources and respects `madurez: preliminar`."""
    body = _skill_body()
    for source in (
        "marco/fases/fase_0_concepto_y_factibilidad.md",
        "proyecto/registros/riesgos.md",
        "proyecto/registros/decisiones_tecnicas.md",
    ):
        assert source in body, f"missing authoritative source: {source}"
    assert "preliminar" in body, "skill must respect madurez: preliminar"


def test_skill_body_is_adaptive_state_aware_capability() -> None:
    """The skill is an adaptive, state-aware capability (not a fixed task checklist):
    it works from evidence distinguishing facts/assumptions/gaps, detects missing,
    ambiguous or contradictory information, asks progressive questions (never a
    fixed questionnaire), produces structured drafts with identified gaps when
    evidence is incomplete, and matures drafts as new evidence appears without
    unnecessary restarts."""
    skill_text = (SKILLS_ROOT / EXPECTED_SKILL_ID / "SKILL.md").read_text(encoding="utf-8")
    for concept in (
        "hecho",
        "supuesto",
        "vacíos",
        "progresiv",
        "cuestionario fijo",
        "borrador",
        "reinici",
    ):
        assert concept in skill_text.lower(), f"missing adaptive capability concept: {concept!r}"


def test_skill_body_declares_full_output_contract() -> None:
    """The output contract covers structured drafts of: opportunity/need, stakeholder
    map, problem statement, preliminary CONOPS, preliminary needs, initial risks,
    ROM estimate, feasibility/continuity report, Go/No-Go recommendation, and
    evidence/gaps/contradictions, plus handoff readiness to F1 preliminary."""
    skill_text = (SKILLS_ROOT / EXPECTED_SKILL_ID / "SKILL.md").read_text(encoding="utf-8")
    for output in (
        "necesidad",
        "stakeholder",
        "problema",
        "CONOPS",
        "riesgos iniciales",
        "ROM",
        "factibilidad",
        "Go / No-Go",
        "contradicci",
        "handoff",
    ):
        assert output in skill_text, f"missing output contract element: {output!r}"
    assert "F1" in skill_text, "skill must evaluate handoff readiness toward F1 preliminary"


CLOSING_HEADER = "## Cierre y handoff"

def _closing_section(skill_text: str) -> str:
    """Return the `## Cierre y handoff` section: the skill's output/readiness verdict contract."""
    start = skill_text.index(CLOSING_HEADER)
    rest = skill_text[start + len(CLOSING_HEADER):]
    next_header = rest.find("\n## ")
    return rest if next_header == -1 else rest[:next_header]

def _declared_readiness_verdicts(closing: str) -> set[str]:
    """Backtick-quoted verdicts enumerated in the closing `veredictos` declaration."""
    declaration = closing[closing.index("veredictos"):]
    declaration = declaration.split(".", 1)[0]
    return set(re.findall(r"`([^`]+)`", declaration))

def test_skill_body_never_self_approves() -> None:
    """The readiness verdict contract (`Cierre y handoff`) declares the approved
    verdicts — `borrador`, `listo para revisión`, `no recomendable avanzar` — with
    no self-issued approval verdict among them, and delegates the F0→F1 transition
    approval to an explicit human decision. Prohibitive or otherwise harmless prose
    mentioning approval outside the verdict declaration is out of scope."""
    skill_text = (SKILLS_ROOT / EXPECTED_SKILL_ID / "SKILL.md").read_text(encoding="utf-8")
    closing = _closing_section(skill_text)

    verdicts = _declared_readiness_verdicts(closing)
    for verdict in ("borrador", "listo para revisión", "no recomendable avanzar"):
        assert verdict in verdicts, f"missing approved readiness verdict: {verdict!r}"
    approval_verdicts = [v for v in verdicts if "aprob" in v.lower()]
    assert not approval_verdicts, f"verdict contract must not declare a self-issued approval verdict: {approval_verdicts}"

    assert "nunca otorga la aprobación" in closing, "the skill must not grant the phase-transition approval itself"
    assert "aprobación explícita y humana" in closing, "transition approval must be delegated to an explicit human decision"


# --- Generic kebab-case executable-skill naming convention ----------------------


def test_rejects_non_kebab_case_registry_id(tmp_path: Path) -> None:
    """Generic convention: a registry row whose id is not kebab-case fails, naming the id."""
    text = _row_substituted(
        _canonical_registry_text(),
        f"| `{CAPABILITY_ID}` | trigger | `.agents/skills/{CAPABILITY_ID}/SKILL.md` |",
    )
    problems = registry_check.check_registry_text(text)
    assert problems, "snake_case registry id must be rejected"
    assert any("kebab-case" in problem and CAPABILITY_ID in problem for problem in problems), "\n".join(problems)


def test_rejects_non_kebab_case_skill_directory(tmp_path: Path) -> None:
    """Generic convention: a snake_case skill directory (with matching frontmatter)
    fails the coherence check, naming the skill."""
    fixture_root = tmp_path / "skills"
    skill_dir = fixture_root / CAPABILITY_ID
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {CAPABILITY_ID}\ndescription: \"x\"\n---\n\ncuerpo\n",
        encoding="utf-8",
    )
    row = f"| `{CAPABILITY_ID}` | trigger | `.agents/skills/{CAPABILITY_ID}/SKILL.md` |"
    text = _row_appended(_canonical_registry_text().replace("skills_available: 1", "skills_available: 2"), row)
    problems = registry_check.check_coherence(fixture_root, _temp_registry(tmp_path, text))
    assert problems, "snake_case skill directory must be rejected"
    assert any("kebab-case" in problem and CAPABILITY_ID in problem for problem in problems), "\n".join(problems)


def test_conceptual_capability_id_retained_in_catalog() -> None:
    """The stable conceptual capability id stays defined in the capability catalog:
    renaming the executable skill must not rename the capability id."""
    catalog_text = SKILL_ARCHITECTURE_PATH.read_text(encoding="utf-8")
    assert f"#### `{CAPABILITY_ID}`" in catalog_text, "conceptual capability id must remain in skill-architecture.md"


# --- Triangulation (REQ-R2): rejection fixtures on temp copies only ------------


def _temp_registry(tmp_path: Path, text: str) -> Path:
    """Write a registry fixture copy to tmp_path; the canonical registry is never touched."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    fixture = tmp_path / "skill-registry.md"
    fixture.write_text(text, encoding="utf-8")
    return fixture


def _canonical_registry_text() -> str:
    return REGISTRY_PATH.read_text(encoding="utf-8")


def _row_substituted(text: str, replacement: str) -> str:
    """Replace the single canonical skill row with `replacement` (or drop it if replacement is '')."""
    lines = text.splitlines()
    out: list[str] = []
    replaced = False
    for line in lines:
        if "`f0-factibilidad`" in line and line.strip().startswith("|"):
            if replacement:
                out.append(replacement)
            replaced = True
            continue
        out.append(line)
    assert replaced, "canonical row not found for substitution"
    return "\n".join(out) + "\n"


def _row_appended(text: str, extra_row: str) -> str:
    """Insert `extra_row` immediately after the canonical row (inside the table)."""
    lines = text.splitlines()
    out: list[str] = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and "`f0-factibilidad`" in line and line.strip().startswith("|"):
            out.append(extra_row)
            inserted = True
    assert inserted, "canonical row not found for insertion"
    return "\n".join(out) + "\n"


def test_rejects_duplicate_registry_row(tmp_path: Path) -> None:
    """REQ-R2: a duplicated entry fails, naming the duplicate."""
    row = "| `f0-factibilidad` | dup trigger | `.agents/skills/f0-factibilidad/SKILL.md` |"
    text = _row_appended(_canonical_registry_text().replace("skills_available: 1", "skills_available: 2"), row)
    problems = registry_check.check_registry_text(text)
    assert problems, "duplicate row must be rejected"
    assert any("duplicate registry entry" in problem and "f0-factibilidad" in problem for problem in problems), "\n".join(problems)


def test_rejects_skill_without_entry_missing(tmp_path: Path) -> None:
    """REQ-R2: a skill with no registry entry (missing) fails, naming the skill."""
    text = _row_substituted(_canonical_registry_text(), "")
    problems = registry_check.check_coherence(SKILLS_ROOT, _temp_registry(tmp_path, text))
    assert problems, "missing entry must be rejected"
    assert any("missing registry entry" in problem and "f0-factibilidad" in problem for problem in problems), "\n".join(problems)


def test_rejects_entry_without_skill_stale(tmp_path: Path) -> None:
    """REQ-R2: a registry entry with no matching skill (stale) fails, naming the entry."""
    stale_row = "| `skill-fantasma` | trigger huérfano | `.agents/skills/skill-fantasma/SKILL.md` |"
    text = _row_appended(_canonical_registry_text().replace("skills_available: 1", "skills_available: 2"), stale_row)
    problems = registry_check.check_coherence(SKILLS_ROOT, _temp_registry(tmp_path, text))
    assert problems, "stale entry must be rejected"
    assert any("stale registry entry" in problem and "skill-fantasma" in problem for problem in problems), "\n".join(problems)


def test_rejects_count_mismatch(tmp_path: Path) -> None:
    """REQ-R2/D7: frontmatter `skills_available` != number of rows fails, naming both values."""
    text = _canonical_registry_text().replace("skills_available: 1", "skills_available: 5")
    problems = registry_check.check_registry_text(text)
    assert problems, "count mismatch must be rejected"
    assert any("count mismatch" in problem and "5" in problem and "1 row" in problem for problem in problems), "\n".join(problems)


def test_rejects_malformed_row(tmp_path: Path) -> None:
    """REQ-R2: a row with the wrong cell count fails, naming the malformed row."""
    text = _row_substituted(_canonical_registry_text(), "| `f0-factibilidad` | solo dos celdas |")
    problems = registry_check.check_registry_text(text)
    assert problems, "malformed row must be rejected"
    assert any("malformed registry row" in problem for problem in problems), "\n".join(problems)


def test_rejects_wrong_ruta(tmp_path: Path) -> None:
    """REQ-R1/D7: a `ruta` that is not exactly `.agents/skills/<id>/SKILL.md` fails."""
    text = _row_substituted(
        _canonical_registry_text(),
        "| `f0-factibilidad` | trigger | `.skills/f0-factibilidad/SKILL.md` |",
    )
    problems = registry_check.check_registry_text(text)
    assert problems, "wrong ruta must be rejected"
    assert any("wrong ruta" in problem and "f0-factibilidad" in problem for problem in problems), "\n".join(problems)


def test_rejects_frontmatter_name_mismatch(tmp_path: Path) -> None:
    """D6/D7: a skill whose frontmatter `name` != directory name fails, naming the skill."""
    fixture_root = tmp_path / "skills"
    skill_dir = fixture_root / "mala-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: otro-nombre\ndescription: \"x\"\n---\n\ncuerpo\n",
        encoding="utf-8",
    )
    row = "| `mala-skill` | trigger | `.agents/skills/mala-skill/SKILL.md` |"
    text = _row_appended(_canonical_registry_text().replace("skills_available: 1", "skills_available: 2"), row)
    problems = registry_check.check_coherence(fixture_root, _temp_registry(tmp_path, text))
    assert problems, "name mismatch must be rejected"
    assert any("name mismatch" in problem and "mala-skill" in problem for problem in problems), "\n".join(problems)


def test_negative_fixtures_never_touch_canonical_registry(tmp_path: Path) -> None:
    """REQ-R3: all rejection fixtures run on temp copies; the canonical registry stays byte-identical."""
    digest_before = registry_check.file_digest(REGISTRY_PATH)
    skills_before = {p: p.read_bytes() for p in sorted(SKILLS_ROOT.rglob("*")) if p.is_file()}
    test_rejects_duplicate_registry_row(tmp_path / "dup")
    test_rejects_skill_without_entry_missing(tmp_path / "missing")
    test_rejects_entry_without_skill_stale(tmp_path / "stale")
    test_rejects_count_mismatch(tmp_path / "count")
    test_rejects_malformed_row(tmp_path / "malformed")
    test_rejects_wrong_ruta(tmp_path / "ruta")
    test_rejects_frontmatter_name_mismatch(tmp_path / "name")
    assert registry_check.file_digest(REGISTRY_PATH) == digest_before
    assert {p: p.read_bytes() for p in sorted(SKILLS_ROOT.rglob("*")) if p.is_file()} == skills_before


# --- REQ-R3: verification is pure and read-only ---------------------------------


def test_verification_is_read_only_canonical_registry_byte_invariant() -> None:
    """REQ-R3: a verification run (pass) leaves the registry and skill sources byte-identical."""
    registry_before = REGISTRY_PATH.read_bytes()
    skills_before = {p: p.read_bytes() for p in sorted(SKILLS_ROOT.rglob("*")) if p.is_file()}
    for _ in range(2):
        problems = registry_check.check_coherence(SKILLS_ROOT, REGISTRY_PATH)
        assert problems == [], "\n".join(problems)
    assert REGISTRY_PATH.read_bytes() == registry_before, "registry was modified by verification"
    skills_after = {p: p.read_bytes() for p in sorted(SKILLS_ROOT.rglob("*")) if p.is_file()}
    assert skills_after == skills_before, "skill sources were modified by verification"
