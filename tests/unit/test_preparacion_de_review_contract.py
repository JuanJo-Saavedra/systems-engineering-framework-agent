"""Contract for the generic one-shot task skill ``preparacion-de-review``.

Static/packaging test in the spirit of ``test_docs_review_contract.py``: the
skill has no scripts, so this pins its identity, the nine-section task schema,
the embedded map of ALL ten formal reviews selected by (review type, active
phase), the read-only/stateless/zero-side-effect execution boundary, the
eight-section logical dossier output, the never-a-verdict authority frontier,
the reviews.md proposal-only registration, the three-class baseline mapping,
the frozen review sequence with the conditioned-verdict closure block, the
fail-closed selection, and the registry/payload/catalog coherence.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL = REPO_ROOT / "runtime" / "skills" / "preparacion-de-review" / "SKILL.md"
GUIA = REPO_ROOT / "framework" / "guias" / "skill-architecture.md"
REGISTRY = REPO_ROOT / "runtime" / "catalogo" / "skill-registry.md"
PAYLOAD_SKILL = (
    REPO_ROOT / "src" / "se_agent" / "_payload" / ".agents" / "skills" / "preparacion-de-review" / "SKILL.md"
)
PAYLOAD_REGISTRY = REPO_ROOT / "src" / "se_agent" / "_payload" / "catalogo" / "skill-registry.md"

TASK_SECTIONS = (
    "Objetivo operativo",
    "Rol y límites",
    "Entradas mínimas",
    "Capacidades operacionales",
    "Salidas esperadas",
    "Mapeo review/baseline",
    "Frontera de autoridad",
    "Registro de reviews",
    "Referencias",
)

#: All ten formal reviews of the marco catalog (catalogo_reviews.md).
REVIEW_TOKENS = (
    "MCR",
    "SRR",
    "PDR",
    "CDR",
    "SIR",
    "EMR",
    "TRR",
    "TRB",
    "SAR",
    "Production Readiness / Transfer Review",
)

#: The eight logical sections of the `paquete técnico de review` dossier.
DOSSIER_SECTIONS = (
    "tipo de review y fase",
    "inventario de evidencia",
    "criterios de entrada y salida",
    "bloqueos y faltantes",
    "hallazgos y riesgos abiertos",
    "agenda propuesta",
    "conclusión de readiness",
    "propuesta de entrada",
)

BASELINE_CLASSES = ("Sin baseline", "Prepara", "Evalúa")


def _skill_text() -> str:
    assert SKILL.is_file(), f"skill missing: {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _frontmatter_name(text: str) -> str | None:
    match = re.match(r"\A---\n(?P<header>.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    name = re.search(r"^name:\s*([^\s#]+)\s*$", match.group("header"), re.MULTILINE)
    return name.group(1) if name else None


def test_preparacion_de_review_surfaces_exist() -> None:
    """Grouped packaging gate: skill, both registries, and the payload skill mirror.

    The grouped assertion deliberately names *all* absent surfaces so the initial
    RED result is actionable rather than failing one missing path at a time.
    """
    surfaces = (SKILL, REGISTRY, PAYLOAD_SKILL, PAYLOAD_REGISTRY)
    missing = [str(path.relative_to(REPO_ROOT)) for path in surfaces if not path.is_file()]
    assert missing == [], f"preparacion-de-review surfaces missing: {missing}"


def test_skill_declares_the_exact_task_identity_and_trigger() -> None:
    text = _skill_text()
    assert _frontmatter_name(text) == "preparacion-de-review", "SKILL.md must publish the exact task skill id"
    description = re.search(r'^description:\s*"(?P<text>.*)"\s*$', text, re.MULTILINE)
    assert description is not None, "frontmatter must carry a quoted selection description"
    for trigger in ("review", "tipo de review", "fase activa", "dossier", "readiness"):
        assert trigger in description.group("text"), f"description must name trigger {trigger!r}"


def test_skill_follows_the_nine_section_task_schema() -> None:
    headings = re.findall(r"^##\s+(.+?)\s*$", _skill_text(), re.MULTILINE)
    assert headings == list(TASK_SECTIONS), f"expected the 9-section task schema, got: {headings}"


def test_single_generic_executable_covers_all_ten_reviews() -> None:
    text = _skill_text()
    for token in REVIEW_TOKENS:
        assert token in text, f"the embedded map must cover review {token!r}"
    assert re.search(r"un solo ejecutable|una sola capacidad|un único ejecutable", text), (
        "one single executable serves every review"
    )
    assert re.search(r"no existen skills dedicadas por review", text), "no dedicated per-review skills may exist"
    assert re.search(r"tipo de review[^.\n]*fase activa|fase activa[^.\n]*tipo de review", text), (
        "selection is by (review type, active phase)"
    )
    for momento in ("entrada de fase", "cierre de fase"):
        assert momento in text, f"the map must distinguish the review moment {momento!r}"


def test_execution_is_read_only_stateless_and_side_effect_free() -> None:
    text = _skill_text()
    assert "solo lectura" in text, "the skill reads proyecto/** only"
    assert re.search(r"[Ss]in efectos secundarios", text), "zero side effects at execution"
    assert re.search(r"[Ss]tateless", text), "no state is kept between executions"
    assert "No escribes" in text and "proyecto/**" in text, "single-writer: the skill never writes proyecto/**"
    assert re.search(r"no crea[^.\n]*(paquete|manifest|snapshot|directorios)", text), (
        "the skill creates no packages, manifests, snapshots or persistent directories"
    )


def test_output_is_the_eight_section_logical_dossier_referencing_not_operating() -> None:
    text = _skill_text()
    assert re.search(r"dossier", text), "the output is the technical review dossier"
    for section in DOSSIER_SECTIONS:
        assert section in text, f"dossier section missing: {section!r}"
    assert "scope" in text and "package_id" in text, "the dossier references the expected package scope and id"
    assert re.search(r"sin crear[^.\n]*paquete|nunca[^.\n]*crea[^.\n]*opera", text), (
        "the dossier references the package without creating or operating it"
    )
    assert re.search(r"no es (un|una) paquete `?docs-review|no es un paquete docs-review", text), (
        "the dossier is not a docs-review package"
    )


def test_skill_never_emits_interprets_or_anticipates_the_verdict() -> None:
    text = _skill_text()
    assert re.search(r"nunca emite, interpreta ni anticipa[^.\n]*veredicto", text), (
        "the verdict is exclusively human; the skill only observes"
    )
    for conclusion in ("lista para revisión", "no recomendable avanzar"):
        assert conclusion in text, f"readiness conclusion {conclusion!r} must be a named outcome"
    assert re.search(r"nunca un veredicto", text), "readiness is never a verdict"


def test_reviews_registry_is_proposal_only_with_stable_ids() -> None:
    text = _skill_text()
    assert "proyecto/registros/reviews.md" in text, "the future reviews registry is named"
    assert "REV-<TYPE>-<PHASE>-<NNN>" in text, "review entries carry stable unique ids"
    assert re.search(r"nunca la escribe|nunca escribe[^.\n]*entrada|solo propone", text), (
        "the skill proposes the verdict entry; the parent persists it"
    )
    assert re.search(r"veredicto[^.\n]*exclusivamente humana|exclusivamente humanos", text), (
        "the verdict field is exclusively human"
    )
    assert "paquete_docs_review" in text, "phases with a package cycle bind the verdict to the frozen package"


def test_baseline_mapping_distinguishes_exactly_three_classes() -> None:
    text = _skill_text()
    for klass in BASELINE_CLASSES:
        assert klass in text, f"baseline relation class {klass!r} must be in the embedded map"
    assert re.search(r"nunca crea, congela, aprueba ni registra baselines", text), (
        "the skill never creates, freezes, approves or registers baselines"
    )
    assert "configuracion.md" in text, "the skill never writes the configuration register"


def test_frozen_sequence_and_conditioned_verdict_block_are_reflected() -> None:
    text = _skill_text()
    assert re.search(r"precede[^.\n]*sometimiento|dossier precede", text), "the dossier precedes the submission"
    assert re.search(r"revisión congelada|revisión exacta congelada", text), (
        "the review is conducted against the exact frozen revision"
    )
    assert re.search(r"Prepare", text) and re.search(r"Submit", text), (
        "pre-review operations are human-authorized"
    )
    assert re.search(r"RecordDecision", text) and re.search(r"Promote", text), (
        "post-verdict operations are separated and explicit"
    )
    assert re.search(r"condición abierta[^.\n]*bloquea|bloqueadores abiertos", text), (
        "an open condition blocks the phase closure conjunction"
    )
    assert "r<NNN+1>" in text, "resubmissions create a traceable next revision"
    assert re.search(r"repiten?[^.\n]*preparaci[oó]n", text) or re.search(r"preparaci[oó]n[^.\n]*review", text), (
        "a resubmission repeats preparation and review"
    )
    assert re.search(r"nunca declara cerradas las condiciones", text), (
        "the skill never declares verdict conditions closed"
    )


def test_selection_fails_closed_on_unknown_type_or_inconsistent_phase() -> None:
    text = _skill_text()
    assert "fail-closed" in text.lower(), "selection validation is fail-closed"
    assert re.search(r"tipo desconocido", text), "an unknown review type must be reported"
    assert re.search(r"fase inconsistente|incoherente", text), "an inconsistent phase must be reported"
    assert re.search(r"informa(?:r)? el conflicto[^.\n]*sin elaborar el dossier|no elabora(?:r)? el dossier", text), (
        "on conflict the skill reports it and does not elaborate the dossier"
    )


def test_all_outputs_declare_the_four_evidence_classes() -> None:
    text = _skill_text()
    for klass in ("hechos verificados", "supuestos", "vacíos", "contradicciones"):
        assert klass in text, f"output evidence class {klass!r} must be explicit"


def _load_registry_check():
    script = REPO_ROOT / "tests" / "helpers" / "registry_check.py"
    spec = importlib.util.spec_from_file_location("registry_check_for_preparacion", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_registry_and_payload_mirrors_are_byte_coherent() -> None:
    registry_check = _load_registry_check()
    registry_text = REGISTRY.read_text(encoding="utf-8")
    assert registry_check.registry_mentions_skill(registry_text, "preparacion-de-review"), (
        "canonical registry must mention the exact preparacion-de-review id"
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


def test_catalog_maps_preparacion_de_review_to_the_implemented_skill() -> None:
    """The conceptual catalog ficha must carry the same `mapeada` + `Bindings` convention as implemented peers."""
    text = GUIA.read_text(encoding="utf-8")
    ficha = _ficha_section(text, "preparacion_de_review")
    assert "**Estado de implementación**: `mapeada`" in ficha, (
        "ficha must override the default `definida` maturity with `mapeada`"
    )
    assert (
        "**Bindings**: `preparacion_de_review` → skill `preparacion-de-review` "
        "(`runtime/skills/preparacion-de-review/SKILL.md`; "
        "instalada como `.agents/skills/preparacion-de-review/SKILL.md`)"
    ) in ficha, "ficha must bind to the implemented skill via the canonical Bindings convention"
    assert SKILL.is_file(), "the bound skill must exist in runtime"
    summary = re.search(r"^Estado por defecto:.*$", text, re.MULTILINE)
    assert summary is not None, "mapped-skill summary line must exist"
    assert "`preparacion_de_review`" in summary.group(0), (
        "mapped-skill summary must list preparacion_de_review among the capabilities with bindings"
    )
