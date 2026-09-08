"""Contract for the pure phase skill ``f1-stakeholders-preliminar``.

Static/packaging test: the skill has no scripts, so this pins its identity, the
exact 12-section phase template (with ``## Cambio atómico de apertura`` as a main
section placed after ``## Artefactos obligatorios`` and before ``## Review y
baseline``), the three recognized states with fail-closed handling (first-work
opening proposal after the explicit human request, normal continuation, closed
idempotence), the atomic opening block (``F1 preliminar: no_iniciada →
en_progreso``, ``active_phase: F0 → F1``, maturity and global state unchanged, and
the coherent creation of the four preliminary artifacts with ``doc_approval:
pendiente``) that the skill proposes but never opens by itself, the readiness
boundary against ``hito_aprobacion_trabajo``, allowed transversal records, and the
registry/payload/catalog coherence.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL = REPO_ROOT / "runtime" / "skills" / "f1-stakeholders-preliminar" / "SKILL.md"
GUIA = REPO_ROOT / "framework" / "guias" / "skill-architecture.md"
REGISTRY = REPO_ROOT / "runtime" / "catalogo" / "skill-registry.md"
PAYLOAD_SKILL = (
    REPO_ROOT / "src" / "se_agent" / "_payload" / ".agents" / "skills" / "f1-stakeholders-preliminar" / "SKILL.md"
)
PAYLOAD_REGISTRY = REPO_ROOT / "src" / "se_agent" / "_payload" / "catalogo" / "skill-registry.md"

ATOMIC_OPENING_HEADING = "Cambio atómico de apertura"

PHASE_SECTIONS = (
    "Objetivo operativo",
    "Rol y límites de fase",
    "Entradas mínimas",
    "Capacidades operacionales",
    "Salidas esperadas",
    "Artefactos obligatorios",
    "Cambio atómico de apertura",
    "Review y baseline",
    "Procesos y registros transversales",
    "Criterios de cierre",
    "Cierre, recomendación y handoff",
    "Referencias",
)

ARTIFACT_PAIRS = (
    ("proyecto/fases/f1_stakeholders/requisitos_stakeholders.md", "stakeholder_requirements"),
    ("proyecto/fases/f1_stakeholders/escenarios_operativos.md", "operational_scenarios"),
    ("proyecto/fases/f1_stakeholders/restricciones_externas.md", "external_constraints"),
    (
        "proyecto/fases/f1_stakeholders/matriz_necesidad_requisito_stakeholder.md",
        "need_stakeholder_requirement_matrix",
    ),
)

MUTABLE_RECORDS = ("requisitos.md", "interfaces.md", "riesgos.md")


def _skill_text() -> str:
    assert SKILL.is_file(), f"skill missing: {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _frontmatter_name(text: str) -> str | None:
    match = re.match(r"\A---\n(?P<header>.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    name = re.search(r"^name:\s*([^\s#]+)\s*$", match.group("header"), re.MULTILINE)
    return name.group(1) if name else None


def test_stakeholders_preliminar_surfaces_exist() -> None:
    """Grouped packaging gate: skill, both registries, and the payload skill mirror."""
    surfaces = (SKILL, REGISTRY, PAYLOAD_SKILL, PAYLOAD_REGISTRY)
    missing = [str(path.relative_to(REPO_ROOT)) for path in surfaces if not path.is_file()]
    assert missing == [], f"f1-stakeholders-preliminar surfaces missing: {missing}"


def test_skill_declares_the_exact_phase_identity_and_trigger() -> None:
    text = _skill_text()
    assert _frontmatter_name(text) == "f1-stakeholders-preliminar", (
        "SKILL.md must publish the exact phase skill id"
    )
    description = re.search(r'^description:\s*"(?P<text>.*)"\s*$', text, re.MULTILINE)
    assert description is not None, "frontmatter must carry a quoted selection description"
    for trigger in ("preproyecto_presupuesto", "F1", "hito de aprobación"):
        assert trigger in description.group("text"), f"description must name trigger {trigger!r}"


def test_skill_follows_the_twelve_section_phase_template() -> None:
    headings = re.findall(r"^##\s+(.+?)\s*$", _skill_text(), re.MULTILINE)
    assert headings == list(PHASE_SECTIONS), f"expected the 12-section phase template, got: {headings}"


def test_skill_recognizes_exactly_three_states_and_fails_closed() -> None:
    text = _skill_text()
    for state in (
        "preproyecto_presupuesto",
        "F1 preliminar: no_iniciada",
        "F1 preliminar: en_progreso",
        "F1 preliminar: cerrada",
    ):
        assert state in text, f"skill must recognize state {state!r}"
    assert re.search(r"[Ii]dempotent", text), "closed state must be handled idempotently"
    assert "fail-closed" in text.lower(), "contradictory or partial states must fail closed"
    assert "sin inferir reparaciones" in text, "fail-closed must not infer repairs"


def _section_body(text: str, heading: str) -> str:
    """Return the body of a ``## heading`` section, up to the next ``##`` heading."""
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE)
    assert match, f"section heading missing: {heading!r}"
    next_heading = re.search(r"^##\s+", text[match.end():], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end():end]


def test_atomic_first_opening_is_a_dedicated_main_section_in_position() -> None:
    """The mandatory first-work behavior is a main ``##`` section placed exactly
    after ``## Artefactos obligatorios`` and before ``## Review y baseline``."""
    text = _skill_text()
    match = re.search(rf"^##\s+{re.escape(ATOMIC_OPENING_HEADING)}\s*$", text, re.MULTILINE)
    assert match, "the atomic first-opening change must be a dedicated ## main section"
    assert f"**{ATOMIC_OPENING_HEADING}**" not in text, "the bold inline label must be replaced by the heading"
    headings = [(m.group(0), m.start()) for m in re.finditer(r"^##\s+.+$", text, re.MULTILINE)]
    position = headings.index((f"## {ATOMIC_OPENING_HEADING}", match.start()))
    assert headings[position - 1][0].startswith("## Artefactos obligatorios"), (
        "the atomic opening section must come immediately after Artefactos obligatorios"
    )
    assert headings[position + 1][0].startswith("## Review y baseline"), (
        "the atomic opening section must come immediately before Review y baseline"
    )


def test_atomic_opening_requires_prior_human_closure_and_explicit_request() -> None:
    """The opening happens only after the human closed and approved F0 and after an
    explicit human request to open F1 preliminar; the skill verifies fail-closed and
    never opens by its own decision."""
    section = _section_body(_skill_text(), ATOMIC_OPENING_HEADING)
    assert "pedido humano explícito" in section, "the human request for opening is the trigger"
    assert "cierre y la aprobación humana de fase `F0`" in section or (
        "cierre y la aprobación humana" in section
    ), "the prior F0 human closure and approval must be verified"
    for marker in (
        "`F0: cerrada`",
        "fail-closed",
        "preproyecto_presupuesto",
        "no_iniciada",
    ):
        assert marker in section, f"the opening preconditions must verify {marker!r}"
    assert re.search(r"no abre por decisi[oó]n propia", section), (
        "the skill must never open the phase by its own decision"
    )


def test_atomic_opening_proposes_the_exact_coherent_block() -> None:
    """The proposed block flips the F1 preliminar row and the active phase, keeps
    maturity and global state unchanged, and creates the four preliminary artifacts."""
    section = _section_body(_skill_text(), ATOMIC_OPENING_HEADING)
    for transition in (
        "F1 preliminar: no_iniciada → en_progreso",
        "active_phase: F0 → F1",
    ):
        assert transition in section, f"atomic opening must include {transition!r}"
    assert "`active_maturity: preliminar`" in section and "sin cambio" in section, (
        "the opening must state maturity and global values stay unchanged"
    )
    assert "preproyecto_presupuesto` (sin cambio)" in section, "the global state stays preproyecto_presupuesto"
    assert "único bloque coherente" in section, "the opening must be one coherent atomic block"
    assert "sin estados parciales" in section, "no intermediate states may exist"
    for marker in ("active_maturity: preliminar", "doc_approval: pendiente"):
        assert marker in section, f"artifact creation must set {marker!r}"
    assert re.search(r"[Ss]in contenido fabricado", section), "no fabricated content fills gaps"


def test_artifacts_live_in_canonical_shared_routes() -> None:
    text = _skill_text()
    for path, document_type in ARTIFACT_PAIRS:
        assert path in text and document_type in text, f"artifact pair missing: {path} / {document_type}"
    assert "active_maturity" in text and "doc_approval" in text, "the common frontmatter stays declared"
    assert "historial de aprobación" in text, "approver identity stays in the body history table"


def test_readiness_faces_the_hito_and_never_self_approves() -> None:
    text = _skill_text()
    assert "hito_aprobacion_trabajo" in text, "readiness is evaluated against the approval milestone"
    assert re.search(r"no propone aprobar ni completar", text), "the milestone is never proposed as approved"
    assert re.search(r"[Nn]unca te autoapruebes", text), "the skill never self-approves"
    assert "Stakeholder Requirements Review" in text, "the associated review stays declared"


def test_skill_scopes_mutations_to_allowed_records_only() -> None:
    text = _skill_text()
    for record in MUTABLE_RECORDS:
        assert record in text, f"mutable record {record!r} must be in scope"
    assert "trazabilidad de evidencia" in text, "datos_y_documentacion is treated as evidence traceability only"
    assert "No escribes" in text and "proyecto/**" in text, "single-writer: the skill never writes proyecto/**"


def test_skill_declares_the_evidence_model() -> None:
    text = _skill_text()
    for marker in ("Hechos verificados", "Supuestos", "Vacíos", "Contradicciones"):
        assert marker in text, f"the evidence model must include {marker!r}"


def _load_registry_check():
    script = REPO_ROOT / "tests" / "helpers" / "registry_check.py"
    spec = importlib.util.spec_from_file_location("registry_check_for_f1_prelim", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_registry_and_payload_mirrors_are_byte_coherent() -> None:
    registry_check = _load_registry_check()
    registry_text = REGISTRY.read_text(encoding="utf-8")
    assert registry_check.registry_mentions_skill(registry_text, "f1-stakeholders-preliminar"), (
        "canonical registry must mention the exact f1-stakeholders-preliminar id"
    )
    assert PAYLOAD_SKILL.read_bytes() == SKILL.read_bytes(), "payload skill mirror must be byte-identical"
    assert PAYLOAD_REGISTRY.read_bytes() == REGISTRY.read_bytes(), "payload registry mirror must be byte-identical"


def test_registry_trigger_covers_first_work_opening_and_continuation() -> None:
    """The registry trigger must let the parent select the skill for the first work
    (F0 closed/approved, F1 preliminar no_iniciada, explicit human request) while
    preserving selection for normal continuation (phase active / en_progreso)."""
    text = REGISTRY.read_text(encoding="utf-8")
    row = re.search(r"^\| `f1-stakeholders-preliminar` \|(?P<trigger>.*?)\| fase \|", text, re.MULTILINE)
    assert row is not None, "registry row for f1-stakeholders-preliminar missing"
    trigger = row.group("trigger")
    for marker in (
        "preproyecto_presupuesto",
        "F0",
        "no_iniciada",
        "pedido humano explícito",
        "cambio atómico de apertura",
    ):
        assert marker in trigger, f"registry trigger must cover {marker!r}"
    assert re.search(r"fase F1 preliminar activa|en_progreso", trigger), (
        "registry trigger must preserve selection for normal continuation"
    )


def _ficha_section(text: str, capability: str) -> str:
    """Return the body of the ``#### ``capability```` ficha up to the next ficha heading."""
    match = re.search(rf"^####\s+`{re.escape(capability)}`\s*$", text, re.MULTILINE)
    assert match, f"ficha for {capability!r} not found"
    body_start = match.end()
    next_heading = re.search(r"^####\s+", text[body_start:], re.MULTILINE)
    body_end = body_start + next_heading.start() if next_heading else len(text)
    return text[body_start:body_end]


def test_catalog_maps_f1_stakeholders_preliminar_to_the_implemented_skill() -> None:
    """The conceptual catalog ficha must carry the same `mapeada` + `Bindings` convention as implemented peers."""
    text = GUIA.read_text(encoding="utf-8")
    ficha = _ficha_section(text, "f1_stakeholders_preliminar")
    assert "**Estado de implementación**: `mapeada`" in ficha, (
        "ficha must override the default `definida` maturity with `mapeada`"
    )
    assert (
        "**Bindings**: `f1_stakeholders_preliminar` → skill `f1-stakeholders-preliminar` "
        "(`runtime/skills/f1-stakeholders-preliminar/SKILL.md`; "
        "instalada como `.agents/skills/f1-stakeholders-preliminar/SKILL.md`)"
    ) in ficha, "ficha must bind to the implemented skill via the canonical Bindings convention"
    assert SKILL.is_file(), "the bound skill must exist in runtime"
    summary = re.search(r"^Estado por defecto:.*$", text, re.MULTILINE)
    assert summary is not None, "mapped-skill summary line must exist"
    assert "`f1_stakeholders_preliminar`" in summary.group(0), (
        "mapped-skill summary must list f1_stakeholders_preliminar among the capabilities with bindings"
    )
