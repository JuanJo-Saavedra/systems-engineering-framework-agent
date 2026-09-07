"""Contract for the pure phase skill ``f1-stakeholders-formal``.

Static/packaging test in the spirit of ``test_docs_review_contract.py``: the
skill has no scripts, so this pins its identity, the 12-section phase template,
the three recognized states with fail-closed handling, the atomic first-opening
proposal, allowed vs read-only scopes, the review integration by emission only
(exact ``f1-stakeholders-formal-r<NNN>`` package specification), the
promoted-package + explicit-human-authorization closure gate, and the
registry/payload byte coherence.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL = REPO_ROOT / "runtime" / "skills" / "f1-stakeholders-formal" / "SKILL.md"
GUIA = REPO_ROOT / "framework" / "guias" / "skill-architecture.md"
MARCO_DOC = REPO_ROOT / "docs" / "architecture" / "design-skill-marco.md"
BOUNDARY_DOC = REPO_ROOT / "docs" / "architecture" / "domain-harness-boundary.md"
HANDOFF_DOC = REPO_ROOT / "docs" / "architecture" / "design-f1-stakeholders-handoff.md"
REGISTRY = REPO_ROOT / "runtime" / "catalogo" / "skill-registry.md"
PAYLOAD_SKILL = (
    REPO_ROOT / "src" / "se_agent" / "_payload" / ".agents" / "skills" / "f1-stakeholders-formal" / "SKILL.md"
)
PAYLOAD_REGISTRY = REPO_ROOT / "src" / "se_agent" / "_payload" / "catalogo" / "skill-registry.md"

PACKAGE_ID = "f1-stakeholders-formal-r<NNN>"

ARTIFACT_PAIRS = (
    ("proyecto/fases/f1_stakeholders/requisitos_stakeholders.md", "stakeholder_requirements"),
    ("proyecto/fases/f1_stakeholders/escenarios_operativos.md", "operational_scenarios"),
    ("proyecto/fases/f1_stakeholders/restricciones_externas.md", "external_constraints"),
    (
        "proyecto/fases/f1_stakeholders/matriz_necesidad_requisito_stakeholder.md",
        "need_stakeholder_requirement_matrix",
    ),
)

PHASE_SECTIONS = (
    "Objetivo operativo",
    "Rol y límites de fase",
    "Entradas mínimas",
    "Capacidades operacionales",
    "Salidas esperadas",
    "Artefactos obligatorios",
    "Review y baseline",
    "Revisión de documentos obligatorios",
    "Procesos y registros transversales",
    "Criterios de cierre",
    "Cierre, recomendación y handoff",
    "Referencias",
)

MUTABLE_RECORDS = ("requisitos.md", "interfaces.md", "riesgos.md")
READ_ONLY_RECORDS = ("configuracion.md", "vv.md", "decisiones_tecnicas.md")


def _skill_text() -> str:
    assert SKILL.is_file(), f"skill missing: {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _frontmatter_name(text: str) -> str | None:
    match = re.match(r"\A---\n(?P<header>.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    name = re.search(r"^name:\s*([^\s#]+)\s*$", match.group("header"), re.MULTILINE)
    return name.group(1) if name else None


def test_stakeholders_formal_surfaces_exist() -> None:
    """Grouped packaging gate: skill, both registries, and the payload skill mirror.

    The grouped assertion deliberately names *all* absent surfaces so the initial
    RED result is actionable rather than failing one missing path at a time.
    """
    surfaces = (SKILL, REGISTRY, PAYLOAD_SKILL, PAYLOAD_REGISTRY)
    missing = [str(path.relative_to(REPO_ROOT)) for path in surfaces if not path.is_file()]
    assert missing == [], f"f1-stakeholders-formal surfaces missing: {missing}"


def test_skill_declares_the_exact_phase_identity_and_trigger() -> None:
    text = _skill_text()
    assert _frontmatter_name(text) == "f1-stakeholders-formal", "SKILL.md must publish the exact phase skill id"
    description = re.search(r'^description:\s*"(?P<text>.*)"\s*$', text, re.MULTILINE)
    assert description is not None, "frontmatter must carry a quoted selection description"
    for trigger in ("aprobado_en_transicion", "proyecto_formal", "formal"):
        assert trigger in description.group("text"), f"description must name trigger state {trigger!r}"


def test_skill_follows_the_twelve_section_phase_template() -> None:
    headings = re.findall(r"^##\s+(.+?)\s*$", _skill_text(), re.MULTILINE)
    assert headings == list(PHASE_SECTIONS), f"expected the 12-section phase template, got: {headings}"


def test_skill_recognizes_exactly_three_states_and_fails_closed() -> None:
    text = _skill_text()
    for state in (
        "aprobado_en_transicion",
        "F1 formal: no_iniciada",
        "proyecto_formal",
        "F1 formal: en_progreso",
        "F1 formal: cerrada",
    ):
        assert state in text, f"skill must recognize state {state!r}"
    assert re.search(r"[Ii]dempotent", text), "closed state must be handled idempotently"
    assert "fail-closed" in text.lower(), "contradictory or partial states must fail closed"
    assert "sin inferir reparaciones" in text, "fail-closed must not infer repairs"
    for contradictorio in (
        "`proyecto_formal` con fila `F1 formal: no_iniciada`",
        "`aprobado_en_transicion` con fila `en_progreso`",
    ):
        assert contradictorio in text, f"skill must name the contradictory combination {contradictorio!r}"
    assert "`project_start_authorized: true`" in text, "consolidated handoff is an entry precondition"


def test_skill_proposes_the_atomic_first_opening_change() -> None:
    text = _skill_text()
    for transition in (
        "aprobado_en_transicion → proyecto_formal",
        "no_iniciada → en_progreso",
        "preliminar → formal",
        "aprobado (preliminar) → pendiente",
    ):
        assert transition in text, f"atomic opening must include {transition!r}"
    assert re.search(r"único bloque coherente", text), "opening must be one coherent atomic block"
    assert "F2" in text and "no_iniciada" in text, "F2 row must stay no_iniciada"
    assert "historial de aprobación preliminar" in text, "preliminary approval history must be preserved"


def test_skill_scopes_mutations_to_allowed_records_only() -> None:
    text = _skill_text()
    for record in MUTABLE_RECORDS:
        assert record in text, f"mutable record {record!r} must be in scope"
    for record in READ_ONLY_RECORDS:
        assert record in text, f"continuity record {record!r} must be referenced"
    assert "lecciones_aprendidas" in text and "no se toca" in text
    assert "No escribes" in text and "proyecto/**" in text, "single-writer: the skill never writes proyecto/**"


def test_skill_integrates_review_only_by_emitting_the_package_specification() -> None:
    text = _skill_text()
    assert PACKAGE_ID in text, "skill must emit the exact package id pattern"
    assert "`f1-stakeholders`" in text, "package scope must be f1-stakeholders"
    assert "predecessor_package_id" in text or "predecesor" in text
    assert "r<NNN+1>" in text, "resubmissions must use the next revision id"
    for path, document_type in ARTIFACT_PAIRS:
        assert path in text and document_type in text, f"package spec must pair {path} with {document_type}"
    assert "en_verificacion" in text, "must wait while the active package is en_verificacion"
    assert "rechazado" in text, "must handle a rejected package"
    assert "content_sha256" in text, "read-only hash validation must be named"
    assert "docs-verificacion" in text and "docs-aprobados" in text, "review surfaces are read-only for the skill"
    assert re.search(r"nunca copias, promueves, revisas, apruebas, firmas ni invocas[^.\n]*docs-review", text), (
        "review integration is emission-only: the skill never operates docs-review"
    )


REVIEW_BASELINE_HEADING = "Review y baseline"
DOCUMENT_REVIEW_HEADING = "Revisión de documentos obligatorios"

DOCUMENT_REVIEW_MARKERS = (
    PACKAGE_ID,
    "stakeholder_requirements",
    "operational_scenarios",
    "external_constraints",
    "need_stakeholder_requirement_matrix",
    "en_verificacion",
    "rechazado",
    "r<NNN+1>",
    "content_sha256",
    "docs-verificacion",
    "docs-aprobados",
    "docs-review",
)


def _section_body(text: str, heading: str) -> str:
    """Return the body of a ``## heading`` section, up to the next ``##`` heading."""
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE)
    assert match, f"section heading missing: {heading!r}"
    next_heading = re.search(r"^##\s+", text[match.end():], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end():end]


def test_document_review_block_is_separated_from_review_and_baseline() -> None:
    """``Review y baseline`` keeps only the technical review boundary; the whole
    package/document-review cycle lives under ``Revisión de documentos
    obligatorios``, in that order, and the two reviews are declared independent
    controls. Marker-based, so it does not snapshot full paragraphs."""
    text = _skill_text()
    headings = re.findall(r"^##\s+(.+?)\s*$", text, re.MULTILINE)
    assert REVIEW_BASELINE_HEADING in headings and DOCUMENT_REVIEW_HEADING in headings, (
        "both the technical review heading and the document-review heading must exist"
    )
    assert headings.index(REVIEW_BASELINE_HEADING) < headings.index(DOCUMENT_REVIEW_HEADING), (
        "the document-review section must come immediately after Review y baseline"
    )
    baseline = _section_body(text, REVIEW_BASELINE_HEADING)
    doc_review = _section_body(text, DOCUMENT_REVIEW_HEADING)
    assert "Stakeholder Requirements Review" in baseline, "technical review identity stays in Review y baseline"
    assert "no aplica baseline formal de sistema" in baseline, "baseline boundary stays in Review y baseline"
    for marker in DOCUMENT_REVIEW_MARKERS:
        assert marker in doc_review, f"package-review material {marker!r} must live under the document-review section"
        assert marker not in baseline, f"package-review material {marker!r} must not leak into Review y baseline"
    assert "controles independientes" in doc_review, (
        "document approval must be declared independent of the Stakeholder Requirements Review verdict"
    )


def test_skill_closes_only_with_promoted_package_and_explicit_human_authorization() -> None:
    text = _skill_text()
    assert "aprobado" in text and "promovido" in text, "closure requires the complete approved and promoted package"
    assert "gates" in text, "closure gates must be explicit"
    assert "autorización del usuario" in text or "autorización humana explícita" in text
    assert "elegib" in text, "F2 eligibility is reported as an observation only"
    assert re.search(r"fila `F2`[^.\n]*`no_iniciada`", text), "F2 row must remain no_iniciada at closure"


def _load_registry_check():
    script = REPO_ROOT / "tests" / "helpers" / "registry_check.py"
    spec = importlib.util.spec_from_file_location("registry_check_for_f1_formal", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_registry_and_payload_mirrors_are_byte_coherent() -> None:
    registry_check = _load_registry_check()
    registry_text = REGISTRY.read_text(encoding="utf-8")
    assert registry_check.registry_mentions_skill(registry_text, "f1-stakeholders-formal"), (
        "canonical registry must mention the exact f1-stakeholders-formal id"
    )
    assert PAYLOAD_SKILL.read_bytes() == SKILL.read_bytes(), "payload skill mirror must be byte-identical"
    assert PAYLOAD_REGISTRY.read_bytes() == REGISTRY.read_bytes(), "payload registry mirror must be byte-identical"


def _ficha_section(text: str, capability: str) -> str:
    """Return the body of the ``#### ``capability```` ficha up to the next ficha heading."""
    match = re.search(rf"^####\s+`{re.escape(capability)}`\s*$", text, re.MULTILINE)
    assert match, f"ficha for {capability!r} not found"
    body_start = match.end()
    next_heading = re.search(r"^####\s+", text[body_start:], re.MULTILINE)
    body_end = body_start + next_heading.start() if next_heading else len(text)
    return text[body_start:body_end]


def test_catalog_maps_f1_stakeholders_formal_to_the_implemented_skill() -> None:
    """The conceptual catalog ficha must carry the same `mapeada` + `Bindings` convention as implemented peers."""
    text = GUIA.read_text(encoding="utf-8")
    ficha = _ficha_section(text, "f1_stakeholders_formal")
    assert "**Estado de implementación**: `mapeada`" in ficha, (
        "ficha must override the default `definida` maturity with `mapeada`"
    )
    assert (
        "**Bindings**: `f1_stakeholders_formal` → skill `f1-stakeholders-formal` "
        "(`runtime/skills/f1-stakeholders-formal/SKILL.md`; "
        "instalada como `.agents/skills/f1-stakeholders-formal/SKILL.md`)"
    ) in ficha, "ficha must bind to the implemented skill via the canonical Bindings convention"
    assert SKILL.is_file(), "the bound skill must exist in runtime"
    summary = re.search(r"^Estado por defecto:.*$", text, re.MULTILINE)
    assert summary is not None, "mapped-skill summary line must exist"
    assert "`f1_stakeholders_formal`" in summary.group(0), (
        "mapped-skill summary must list f1_stakeholders_formal among the capabilities with bindings"
    )


def test_architecture_docs_do_not_defer_the_f1_formal_skill() -> None:
    """Architecture docs must not claim the implemented skill is missing or its integration deferred."""
    marco = MARCO_DOC.read_text(encoding="utf-8")
    assert "sigue sin skill ejecutable" not in marco, (
        "marco doc still claims f1_stakeholders_formal has no executable skill"
    )
    boundary = BOUNDARY_DOC.read_text(encoding="utf-8")
    assert "La integración de F1 sigue diferida" not in boundary, "boundary doc still defers F1 integration"
    assert "no está implementada" not in boundary, "boundary doc still claims the skill is unimplemented"


FORMAL_HOJA_HEADING = "## Hoja de diseño: `f1_stakeholders_formal`"


def _formal_design_section() -> str:
    """Return the concrete design section of ``f1_stakeholders_formal``, up to
    the deferred-decisions section that closes the handoff design doc."""
    text = HANDOFF_DOC.read_text(encoding="utf-8")
    start = text.find(FORMAL_HOJA_HEADING)
    assert start != -1, f"formal design hoja missing: {FORMAL_HOJA_HEADING!r}"
    end = text.find("## Decisiones diferidas", start)
    return text[start:end] if end != -1 else text[start:]


def _schema_row(section: str, number: int, section_name: str) -> str:
    """Return the content cell of a schema table row (``| <n> | <name> | ... |``)."""
    row = re.search(
        rf"^\|\s*{number}\s*\|\s*{re.escape(section_name)}\s*\|(?P<body>.*?)\|\s*$",
        section,
        re.MULTILINE,
    )
    assert row is not None, f"schema row {number} ({section_name!r}) missing in the concrete design"
    return row.group("body")


def test_design_docs_sync_the_twelve_section_schema_with_document_review_separation() -> None:
    """Design-sync gate: the concrete F1 formal design must mirror the implemented
    12-section template — ``Review y baseline`` limited to the technical review,
    readiness and the no-baseline boundary, with the whole package lifecycle and
    authority boundary under the distinct ``Revisión de documentos obligatorios``
    section — and the generic marco template must not fold the package cycle into
    ``Review y baseline``. Scoped to the formal hoja, so the preliminary skill
    (not adapted to the package cycle) keeps its own 11-section schema."""
    formal = _formal_design_section()
    assert "plantilla de fase, once secciones" not in formal, (
        "formal skill schema still uses the stale 11-section framing"
    )
    assert "plantilla de fase, doce secciones" in formal, (
        "formal skill schema must declare the 12-section template"
    )
    baseline_row = _schema_row(formal, 7, "Review y baseline")
    doc_review_row = _schema_row(formal, 8, "Revisión de documentos obligatorios")
    for limited in ("Stakeholder Requirements Review", "readiness", "no aplica baseline formal de sistema"):
        assert limited in baseline_row, f"Review y baseline row must stay limited to {limited!r}"
    for stale in ("en_verificacion", "docs-review", "docs-verificacion", "docs-aprobados", "r<NNN"):
        assert stale not in baseline_row, f"package-review material {stale!r} must not stay in Review y baseline"
    for marker in (
        "f1-stakeholders-formal-r<NNN>",
        "en_verificacion",
        "r<NNN+1>",
        "docs-verificacion",
        "docs-aprobados",
        "docs-review",
    ):
        assert marker in doc_review_row, (
            f"package lifecycle/authority material {marker!r} must live under Revisión de documentos obligatorios"
        )

    marco = MARCO_DOC.read_text(encoding="utf-8")
    marco_baseline_row = _schema_row(marco, 7, "Review y baseline")
    assert "Revisión de documentos obligatorios" in marco_baseline_row, (
        "marco template must point the package cycle to the dedicated document-review section"
    )
    assert "en_verificacion" not in marco_baseline_row and "promovido" not in marco_baseline_row, (
        "marco template must not fold package mechanics into Review y baseline"
    )


def test_handoff_doc_does_not_describe_the_formal_skill_as_future_work() -> None:
    """The handoff design doc must describe the formal skill as implemented, without stale future wording."""
    handoff = HANDOFF_DOC.read_text(encoding="utf-8")
    assert "implementación posterior de la skill formal" not in handoff, (
        "handoff doc still frames the formal skill as a future implementation"
    )
    assert "no implementa** `runtime/skills/f1-stakeholders-formal`" not in handoff, (
        "handoff doc still claims the review core does not implement the formal skill"
    )
    assert "`f1_stakeholders_formal` está implementada como skill de fase pura" in handoff, (
        "substantive truth must remain: the formal skill is a pure phase skill"
    )
