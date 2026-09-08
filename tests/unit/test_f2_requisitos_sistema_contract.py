"""Contract for the pure phase skill ``f2-requisitos-sistema``.

Static/packaging test in the spirit of ``test_f1_stakeholders_formal_contract.py``:
the skill has no scripts, so this pins its identity, the exact 12-section phase
template, the three recognized states with fail-closed handling, the absence of a
preliminary mode, the atomic first-opening proposal, the two separate traceability
matrices with immutable ``SYS-REQ-0001`` ids, the vv-summary schema with maturity
separated from execution, allowed vs forbidden record mutations, review
integration by emission only (exact ``f2-requisitos-sistema-formal-r<NNN>``
package specification), the mandatory frozen review sequence as a concise six-stage
table (dossier →
``Prepare``+``Submit`` → ``en_verificacion`` → SRR against the frozen review →
verdict → separated post-verdict documental decision), the dedicated
``### Cambio atómico de apertura`` subsection without a 13th top-level section,
the absence of the duplicate closure-expectations block, and the conjunction-gated
closure with the atomic Functional Baseline registration, and the
registry/payload/catalog coherence.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL = REPO_ROOT / "runtime" / "skills" / "f2-requisitos-sistema" / "SKILL.md"
GUIA = REPO_ROOT / "framework" / "guias" / "skill-architecture.md"
REGISTRY = REPO_ROOT / "runtime" / "catalogo" / "skill-registry.md"
PAYLOAD_SKILL = (
    REPO_ROOT / "src" / "se_agent" / "_payload" / ".agents" / "skills" / "f2-requisitos-sistema" / "SKILL.md"
)
PAYLOAD_REGISTRY = REPO_ROOT / "src" / "se_agent" / "_payload" / "catalogo" / "skill-registry.md"

PACKAGE_ID = "f2-requisitos-sistema-formal-r<NNN>"

ARTIFACT_PAIRS = (
    ("proyecto/fases/f2_requisitos_sistema/requisitos_sistema.md", "system_requirements"),
    ("proyecto/fases/f2_requisitos_sistema/matriz_necesidad_requisito_sistema.md", "need_system_requirement_matrix"),
    (
        "proyecto/fases/f2_requisitos_sistema/matriz_requisito_metodo_verificacion.md",
        "system_requirement_verification_method_matrix",
    ),
    ("proyecto/fases/f2_requisitos_sistema/supuestos_y_restricciones.md", "assumptions_and_constraints"),
    ("proyecto/fases/f2_requisitos_sistema/plan_vv_preliminar.md", "preliminary_vv_plan"),
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

MUTABLE_RECORDS = ("requisitos.md", "vv.md", "configuracion.md", "riesgos.md")

REVIEW_BASELINE_HEADING = "Review y baseline"
DOCUMENT_REVIEW_HEADING = "Revisión de documentos obligatorios"

ATOMIC_OPENING_HEADING = "Cambio atómico de apertura"

# The six user-requested stages of the frozen review sequence, in canonical order.
REVIEW_SEQUENCE_STAGES = (
    "Fase en curso",
    "Preparación de Review",
    "Autorización y verificación de documentos",
    "Revisión técnica SRR",
    "Resultados de la revisión técnica",
    "Documento aprobado y Functional Baseline",
)

REVIEW_SEQUENCE_TABLE_HEADER = "| Etapa | Actor / autoridad | Acción / evidencia | Resultado / paso siguiente |"


def _skill_text() -> str:
    assert SKILL.is_file(), f"skill missing: {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _frontmatter_name(text: str) -> str | None:
    match = re.match(r"\A---\n(?P<header>.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    name = re.search(r"^name:\s*([^\s#]+)\s*$", match.group("header"), re.MULTILINE)
    return name.group(1) if name else None


def test_f2_requisitos_sistema_surfaces_exist() -> None:
    """Grouped packaging gate: skill, both registries, and the payload skill mirror.

    The grouped assertion deliberately names *all* absent surfaces so the initial
    RED result is actionable rather than failing one missing path at a time.
    """
    surfaces = (SKILL, REGISTRY, PAYLOAD_SKILL, PAYLOAD_REGISTRY)
    missing = [str(path.relative_to(REPO_ROOT)) for path in surfaces if not path.is_file()]
    assert missing == [], f"f2-requisitos-sistema surfaces missing: {missing}"


def test_skill_declares_the_exact_phase_identity_and_trigger() -> None:
    text = _skill_text()
    assert _frontmatter_name(text) == "f2-requisitos-sistema", "SKILL.md must publish the exact phase skill id"
    description = re.search(r'^description:\s*"(?P<text>.*)"\s*$', text, re.MULTILINE)
    assert description is not None, "frontmatter must carry a quoted selection description"
    for trigger in ("proyecto_formal", "F2", "requerimientos de sistema", "SRR", "Functional Baseline"):
        assert trigger in description.group("text"), f"description must name trigger {trigger!r}"


def test_skill_follows_the_twelve_section_phase_template() -> None:
    headings = re.findall(r"^##\s+(.+?)\s*$", _skill_text(), re.MULTILINE)
    assert headings == list(PHASE_SECTIONS), f"expected the 12-section phase template, got: {headings}"


def test_skill_recognizes_exactly_three_states_and_fails_closed() -> None:
    text = _skill_text()
    for state in (
        "proyecto_formal",
        "F1 formal: cerrada",
        "F2: no_iniciada",
        "F2: en_progreso",
        "F2: cerrada",
    ):
        assert state in text, f"skill must recognize state {state!r}"
    assert re.search(r"[Ii]dempotent", text), "closed state must be handled idempotently"
    assert "fail-closed" in text.lower(), "contradictory or partial states must fail closed"
    assert "sin inferir reparaciones" in text, "fail-closed must not infer repairs"
    for contradictorio in (
        "`F1 formal` no `cerrada`",
        "paquete `f1-stakeholders` sin promover",
    ):
        assert contradictorio in text, f"skill must name the contradictory combination {contradictorio!r}"


def test_skill_has_no_preliminary_mode() -> None:
    """F2 nace formal: no maturity reset cycle exists in this phase."""
    text = _skill_text()
    assert "sin modo preliminar" in text or "no existe modo preliminar" in text, (
        "the skill must declare that F2 has no preliminary mode"
    )
    assert "`active_maturity: preliminar`" not in text, "no F2 artifact may ever adopt preliminary maturity"
    assert "preliminar → formal" not in text, "no preliminary→formal maturity cycle may exist in F2"
    assert "`active_maturity: formal`" in text and "`doc_approval: pendiente`" in text, (
        "opening artifacts are created formal with pending approval"
    )


def test_skill_proposes_the_atomic_first_opening_change() -> None:
    text = _skill_text()
    for transition in (
        "F2: no_iniciada → en_progreso",
        "active_phase: F1 → F2",
    ):
        assert transition in text, f"atomic opening must include {transition!r}"
    assert "project_status" in text and "active_maturity" in text, (
        "opening must state project_status and active_maturity stay unchanged"
    )
    assert re.search(r"sin cambio", text), "unchanged global values must be stated explicitly"
    assert re.search(r"único bloque coherente", text), "opening must be one coherent atomic block"
    for _, document_type in ARTIFACT_PAIRS:
        assert document_type in text, f"the five mandatory artifacts must include {document_type}"
    assert re.search(r"cinco artefactos", text, re.IGNORECASE), "the five mandatory artifacts must be named"


def test_skill_produces_two_separate_traceability_matrices_with_immutable_ids() -> None:
    text = _skill_text()
    assert re.search(r"dos matrices separadas", text), "the two matrices must stay separate artifacts"
    assert "no se fusionan" in text or "nunca se fusionan" in text, "the matrices must never be merged"
    for pair in ARTIFACT_PAIRS[1:3]:
        assert pair[0] in text and pair[1] in text, f"matrix artifact pair missing: {pair}"
    assert "SYS-REQ-0001" in text, "requirement ids use the immutable SYS-REQ-0001 format"
    assert "cuatro dígitos" in text, "the id format (fixed prefix + four digits) must be pinned"
    assert re.search(r"nunca se reutilizan, renumeran ni reciclan", text), "ids are never reused or renumbered"
    for surface in ("SyRS", "requisitos.md", "vv.md"):
        assert surface in text, f"id identity spans SyRS, both matrices, requisitos.md and vv.md: missing {surface!r}"
    assert re.search(r"contradicci[oó]n declarada", text) and "renumera" in text, (
        "divergences are declared contradictions, never resolved by renumbering"
    )


def test_skill_scopes_mutations_to_allowed_records_only() -> None:
    text = _skill_text()
    for record in MUTABLE_RECORDS:
        assert record in text, f"mutable record {record!r} must be in scope"
    assert "no muta `interfaces` ni `lecciones_aprendidas`" in text, (
        "interfaces and lecciones_aprendidas stay outside the phase mutation scope"
    )
    assert "trazabilidad de evidencia" in text, "datos_y_documentacion is treated as evidence traceability only"
    assert "No escribes" in text and "proyecto/**" in text, "single-writer: the skill never writes proyecto/**"


def test_vv_record_receives_only_summaries_with_separated_maturity() -> None:
    text = _skill_text()
    for marker in ("madurez_vv: preliminar", "referencia_plan", "estado_verificacion: no_iniciada"):
        assert marker in text, f"vv summary schema must include {marker!r}"
    assert "no duplica el plan" in text or "no duplica" in text, "the vv record references the plan, never duplicates it"
    assert "validación" in text and "no_iniciada" in text, "validation state stays no_iniciada until F7"
    assert re.search(r"sin evidencia disponible", text), "no verification evidence is recorded in F2"


def test_skill_integrates_review_only_by_emitting_the_package_specification() -> None:
    text = _skill_text()
    assert PACKAGE_ID in text, "skill must emit the exact package id pattern"
    assert "`f2-requisitos-sistema`" in text, "package scope must be f2-requisitos-sistema"
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


def test_frozen_review_sequence_is_mandatory() -> None:
    """v1.2 frozen sequence: submission freezes the exact revision; the SRR is
    conducted against it; the documental decision is separated and post-verdict."""
    text = _skill_text()
    assert "preparacion-de-review" in text, "the dossier preparation is composed by the parent with the generic skill"
    assert "bloqueos" in text, "a dossier with blockers returns the flow to phase work"
    assert re.search(r"Prepare`\?`\+`?Submit|Prepare` \+ `Submit|Prepare\+Submit|Prepare` y `Submit", text), (
        "Prepare+Submit must be named as the human-authorized pre-review operations"
    )
    assert "revisión congelada" in text or "revisión exacta congelada" in text, (
        "the SRR is conducted against the exact frozen review"
    )
    assert re.search(r"veredicto[^.\n]*(package_id|paquete_id)|package_id[^.\n]*congelado", text, re.IGNORECASE), (
        "the verdict is tied to the frozen package id"
    )
    assert "hashes del manifest" in text or "hashes" in text, "the verdict is tied to the manifest hashes"
    assert re.search(r"RecordDecision", text) and re.search(r"Promote", text), (
        "the post-verdict documental decision must be named"
    )
    assert re.search(r"post-veredicto", text), "RecordDecision+Promote are post-verdict operations"
    assert re.search(r"el veredicto técnico nunca[^.\n]*automáticamente", text), (
        "the technical verdict never chooses the documental decision automatically"
    )
    assert "bloqueadores abiertos" in text, "an unfavorable/conditioned verdict with open blockers blocks closure"
    assert re.search(r"r<NNN\+1>[^.\n]*(preparación|preparacion-de-review)|preparación[^.\n]*review", text), (
        "a resubmission repeats preparation and technical review"
    )


def _frozen_sequence_region(text: str) -> str:
    """Return the skill slice from the frozen-sequence label to the controls paragraph."""
    start = text.index("Secuencia congelada obligatoria")
    end = text.index("Separación de controles", start)
    return text[start:end]


def test_atomic_first_opening_is_a_dedicated_subsection() -> None:
    """The mandatory first-work behavior gets a visible ``###`` subsection while
    the exact 12 top-level ``##`` phase template is preserved."""
    text = _skill_text()
    match = re.search(rf"^###\s+{re.escape(ATOMIC_OPENING_HEADING)}\s*$", text, re.MULTILINE)
    assert match, "the atomic first-opening change must be a dedicated ### subsection"
    assert f"**{ATOMIC_OPENING_HEADING}**" not in text, "the bold inline label must be replaced by the heading"
    prior_sections = [m for m in re.finditer(r"^##\s+.+$", text, re.MULTILINE) if m.start() < match.start()]
    assert prior_sections and prior_sections[-1].group(0).startswith("## Artefactos obligatorios"), (
        "the ### subsection must live inside the existing artifacts section, not a 13th top-level section"
    )
    next_heading = re.search(r"^#{2,3}\s+", text[match.end():], re.MULTILINE)
    subsection = text[match.end(): match.end() + next_heading.start()] if next_heading else text[match.end():]
    for marker in (
        "F2: no_iniciada → en_progreso",
        "active_phase: F1 → F2",
        "único bloque coherente",
        "sin estados parciales",
        "fail-closed",
    ):
        assert marker in subsection, f"the atomic opening subsection must keep {marker!r}"


def test_duplicate_closure_expectations_block_is_removed() -> None:
    """The 'Expectativas al cierre' paragraph duplicated ``## Criterios de cierre``."""
    text = _skill_text()
    assert "Expectativas al cierre" not in text, (
        "the duplicate closure-expectations paragraph must be removed; closure expectations "
        "live only in ## Criterios de cierre"
    )
    criteria = text.split("## Criterios de cierre", 1)[1].split("\n## ", 1)[0]
    for marker in (
        "matriz necesidad ↔ requisito completa",
        "matriz requisito ↔ método completa",
        "paquete completo",
    ):
        assert marker in criteria, f"the closure criteria must keep representing {marker!r}"


def test_frozen_sequence_is_a_concise_table_in_the_exact_six_stage_order() -> None:
    """The numbered ceremony becomes a concise table with the six canonical stages."""
    text = _skill_text()
    region = _frozen_sequence_region(text)
    assert "Secuencia congelada obligatoria" in region, "the frozen-sequence label must be preserved"
    assert REVIEW_SEQUENCE_TABLE_HEADER in region, "the table must expose actor, action and outcome columns"
    assert re.search(r"^\d+\.\s", region, re.MULTILINE) is None, "the numbered ceremony must be replaced by the table"
    positions = []
    for stage in REVIEW_SEQUENCE_STAGES:
        assert region.count(stage) == 1, f"stage {stage!r} must appear exactly once in the sequence table"
        positions.append(region.index(stage))
    assert positions == sorted(positions), "the six stages must keep the canonical order"


def test_frozen_sequence_table_preserves_all_mandatory_semantics() -> None:
    """The concise table keeps every mandatory frozen-sequence semantic."""
    region = _frozen_sequence_region(_skill_text())
    for marker in (
        "readiness",  # readiness is observation, never authorization
        "bloqueos",  # dossier blockers return to phase work
        "trabajo de fase",
        "Prepare` + `Submit",  # human authorization for the pre-review operations
        "en_verificacion",  # frozen package
        "congelados",
        "content_sha256",
        "revisión exacta congelada",  # human SRR against the frozen revision
        "package_id` congelado",  # verdict binding
        "hashes del manifest",
        "bloqueadores abiertos",
        "r<NNN+1>",  # unfavorable/conditioned resubmission
        "predecessor_package_id",
        "preparacion-de-review",
        "RecordDecision",  # favorable does not imply the post-verdict decision
        "Promote",
        "post-veredicto",
        "mismo cambio",  # atomic baseline
        "autorización humana",  # explicit human closure
    ):
        assert marker in region, f"the frozen-sequence table must preserve {marker!r}"


def test_readiness_is_an_observation_and_the_verdict_is_never_hers() -> None:
    text = _skill_text()
    assert re.search(r"[Rr]eadiness no equivale a autorización", text), "readiness is an observation, never a grant"
    assert re.search(r"nunca convoca, conduce ni emite veredicto", text), (
        "the phase skill never convenes, conducts or emits the review verdict"
    )


def test_skill_closes_only_with_the_full_conjunction_and_atomic_baseline() -> None:
    text = _skill_text()
    assert re.search(r"conjunci[oó]n", text, re.IGNORECASE), "closure requires the exact conjunction"
    for condition in ("SRR favorable", "promovido", "autorización humana"):
        assert condition in text, f"closure conjunction requires {condition!r}"
    assert "F2: en_progreso → cerrada" in text, "the closure flips the phase row atomically"
    assert "doc_approval: pendiente → aprobado" in text, "the closure persists the derived doc_approval mirrors"
    assert "Functional Baseline" in text and "configuracion.md" in text, (
        "the Functional Baseline is registered in configuracion.md"
    )
    assert re.search(r"mismo cambio", text), "the baseline registration happens in the same atomic change"
    assert re.search(r"cerrada[^.\n]*baseline no registrada|baseline registrada[^.\n]*en_progreso", text), (
        "row-closed-without-baseline and baseline-with-open-phase are forbidden states"
    )
    assert re.search(r"nunca abre[^.\n]*F3|F3[^.\n]*no_iniciada", text), "F3 stays no_iniciada and is never opened"
    assert re.search(r"[Ee]legib", text), "F3 eligibility is reported as an observation only"
    assert re.search(r"no existe skill de transición", text) or re.search(r"sin skill de transición", text), (
        "no dedicated F2→F3 transition skill exists"
    )


def _load_registry_check():
    script = REPO_ROOT / "tests" / "helpers" / "registry_check.py"
    spec = importlib.util.spec_from_file_location("registry_check_for_f2", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_registry_and_payload_mirrors_are_byte_coherent() -> None:
    registry_check = _load_registry_check()
    registry_text = REGISTRY.read_text(encoding="utf-8")
    assert registry_check.registry_mentions_skill(registry_text, "f2-requisitos-sistema"), (
        "canonical registry must mention the exact f2-requisitos-sistema id"
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


def test_catalog_maps_f2_requisitos_sistema_to_the_implemented_skill() -> None:
    """The conceptual catalog ficha must carry the same `mapeada` + `Bindings` convention as implemented peers."""
    text = GUIA.read_text(encoding="utf-8")
    ficha = _ficha_section(text, "f2_requisitos_sistema")
    assert "**Estado de implementación**: `mapeada`" in ficha, (
        "ficha must override the default `definida` maturity with `mapeada`"
    )
    assert (
        "**Bindings**: `f2_requisitos_sistema` → skill `f2-requisitos-sistema` "
        "(`runtime/skills/f2-requisitos-sistema/SKILL.md`; "
        "instalada como `.agents/skills/f2-requisitos-sistema/SKILL.md`)"
    ) in ficha, "ficha must bind to the implemented skill via the canonical Bindings convention"
    assert SKILL.is_file(), "the bound skill must exist in runtime"
    summary = re.search(r"^Estado por defecto:.*$", text, re.MULTILINE)
    assert summary is not None, "mapped-skill summary line must exist"
    assert "`f2_requisitos_sistema`" in summary.group(0), (
        "mapped-skill summary must list f2_requisitos_sistema among the capabilities with bindings"
    )
