"""Contract for the pure phase skill ``f0-factibilidad``.

Static/packaging test: the skill has no scripts, so this pins its identity, the
exact 12-section phase template (with ``## Cambio atómico de apertura`` as a main
section placed after ``## Artefactos obligatorios`` and before ``## Review y
baseline``), the verification-only atomic opening (the initial opening was already
materialized by project initialization: the skill verifies it fail-closed and never
invents a previous phase, a transition, or artifact routes), the ``ubicación
pendiente`` policy, the MCR readiness boundary (never auto-approved), allowed
transversal records, and the registry/payload/catalog coherence.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL = REPO_ROOT / "runtime" / "skills" / "f0-factibilidad" / "SKILL.md"
GUIA = REPO_ROOT / "framework" / "guias" / "skill-architecture.md"
REGISTRY = REPO_ROOT / "runtime" / "catalogo" / "skill-registry.md"
PAYLOAD_SKILL = (
    REPO_ROOT / "src" / "se_agent" / "_payload" / ".agents" / "skills" / "f0-factibilidad" / "SKILL.md"
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

MUTABLE_RECORDS = ("riesgos.md", "requisitos.md", "decisiones_tecnicas.md")


def _skill_text() -> str:
    assert SKILL.is_file(), f"skill missing: {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _frontmatter_name(text: str) -> str | None:
    match = re.match(r"\A---\n(?P<header>.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    name = re.search(r"^name:\s*([^\s#]+)\s*$", match.group("header"), re.MULTILINE)
    return name.group(1) if name else None


def test_f0_factibilidad_surfaces_exist() -> None:
    """Grouped packaging gate: skill, both registries, and the payload skill mirror."""
    surfaces = (SKILL, REGISTRY, PAYLOAD_SKILL, PAYLOAD_REGISTRY)
    missing = [str(path.relative_to(REPO_ROOT)) for path in surfaces if not path.is_file()]
    assert missing == [], f"f0-factibilidad surfaces missing: {missing}"


def test_skill_declares_the_exact_phase_identity_and_trigger() -> None:
    text = _skill_text()
    assert _frontmatter_name(text) == "f0-factibilidad", "SKILL.md must publish the exact phase skill id"
    description = re.search(r'^description:\s*"(?P<text>.*)"\s*$', text, re.MULTILINE)
    assert description is not None, "frontmatter must carry a quoted selection description"
    for trigger in ("preproyecto_presupuesto", "F0", "MCR", "Go/No-Go"):
        assert trigger in description.group("text"), f"description must name trigger {trigger!r}"


def test_skill_follows_the_twelve_section_phase_template() -> None:
    headings = re.findall(r"^##\s+(.+?)\s*$", _skill_text(), re.MULTILINE)
    assert headings == list(PHASE_SECTIONS), f"expected the 12-section phase template, got: {headings}"


def _section_body(text: str, heading: str) -> str:
    """Return the body of a ``## heading`` section, up to the next ``##`` heading."""
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE)
    assert match, f"section heading missing: {heading!r}"
    next_heading = re.search(r"^##\s+", text[match.end():], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end():end]


def test_atomic_first_opening_is_verification_only_and_in_position() -> None:
    """F0's initial opening was already materialized by project initialization:
    the section verifies the initial state fail-closed and never invents a previous
    phase, a transition, or artifact routes. It is a main ``##`` section placed
    exactly after ``## Artefactos obligatorios`` and before ``## Review y baseline``."""
    text = _skill_text()
    match = re.search(rf"^##\s+{re.escape(ATOMIC_OPENING_HEADING)}\s*$", text, re.MULTILINE)
    assert match, "the atomic opening must be a dedicated ## main section"
    assert f"**{ATOMIC_OPENING_HEADING}**" not in text, "the bold inline label must not be used"
    headings = [(m.group(0), m.start()) for m in re.finditer(r"^##\s+.+$", text, re.MULTILINE)]
    position = headings.index((f"## {ATOMIC_OPENING_HEADING}", match.start()))
    assert headings[position - 1][0].startswith("## Artefactos obligatorios"), (
        "the atomic opening section must come immediately after Artefactos obligatorios"
    )
    assert headings[position + 1][0].startswith("## Review y baseline"), (
        "the atomic opening section must come immediately before Review y baseline"
    )
    section = _section_body(text, ATOMIC_OPENING_HEADING)
    for marker in (
        "preproyecto_presupuesto",
        "`active_phase: F0`",
        "`active_maturity: preliminar`",
        "`F0: en_progreso`",
        "fail-closed",
    ):
        assert marker in section, f"the atomic opening must verify {marker!r}"
    assert re.search(r"inicializaci[oó]n del proyecto", section), (
        "the initial opening must be attributed to project initialization, not to this skill"
    )
    assert re.search(r"no inventas? fase previa|no inventa fase previa", section), (
        "the skill must never invent a previous phase"
    )
    assert re.search(r"no propones? transici[oó]n|sin transici[oó]n", section), (
        "the skill must not propose an opening transition for F0"
    )
    assert "ubicación pendiente" in section, "the skill must not invent routes for ubicación pendiente artifacts"


def test_skill_keeps_the_ubicacion_pendiente_policy() -> None:
    text = _skill_text()
    assert re.search(r"ubicación pendiente", text), "artifacts without an authoritative route stay ubicación pendiente"
    assert re.search(r"[Nn]unca se inventan rutas", text), "routes are never invented"


def test_skill_evaluates_mcr_readiness_only() -> None:
    text = _skill_text()
    assert "MCR" in text and "readiness" in text.lower(), "the dossier readiness against the MCR is evaluated"
    assert re.search(r"[Nn]unca te autoapruebes", text), "the skill never self-approves closure, budget or MCR"
    assert "Go" in text and "No-Go" in text, "the technical Go/No-Go recommendation stays separated"
    assert re.search(r"apertura de .F1 preliminar.", text), "the F1 preliminar opening is a human decision"


def test_skill_scopes_mutations_to_allowed_records_only() -> None:
    text = _skill_text()
    for record in MUTABLE_RECORDS:
        assert record in text, f"mutable record {record!r} must be in scope"
    assert "trazabilidad de evidencia" in text, "datos_y_documentacion is treated as evidence traceability only"
    assert re.search(r"[Ss]obrescribir evidencia en silencio", text), "silent evidence overwrite stays forbidden"


def test_skill_declares_the_evidence_model() -> None:
    text = _skill_text()
    for marker in ("Hechos verificados", "Supuestos", "Vacíos", "Contradicciones"):
        assert marker in text, f"the evidence model must include {marker!r}"


def _load_registry_check():
    script = REPO_ROOT / "tests" / "helpers" / "registry_check.py"
    spec = importlib.util.spec_from_file_location("registry_check_for_f0", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_registry_and_payload_mirrors_are_byte_coherent() -> None:
    registry_check = _load_registry_check()
    registry_text = REGISTRY.read_text(encoding="utf-8")
    assert registry_check.registry_mentions_skill(registry_text, "f0-factibilidad"), (
        "canonical registry must mention the exact f0-factibilidad id"
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


def test_catalog_maps_f0_factibilidad_to_the_implemented_skill() -> None:
    """The conceptual catalog ficha must carry the same `mapeada` + `Bindings` convention as implemented peers."""
    text = GUIA.read_text(encoding="utf-8")
    ficha = _ficha_section(text, "f0_factibilidad")
    assert "**Estado de implementación**: `mapeada`" in ficha, (
        "ficha must override the default `definida` maturity with `mapeada`"
    )
    assert (
        "**Bindings**: `f0_factibilidad` → skill `f0-factibilidad` "
        "(`runtime/skills/f0-factibilidad/SKILL.md`; "
        "instalada como `.agents/skills/f0-factibilidad/SKILL.md`)"
    ) in ficha, "ficha must bind to the implemented skill via the canonical Bindings convention"
    assert SKILL.is_file(), "the bound skill must exist in runtime"
    summary = re.search(r"^Estado por defecto:.*$", text, re.MULTILINE)
    assert summary is not None, "mapped-skill summary line must exist"
    assert "`f0_factibilidad`" in summary.group(0), (
        "mapped-skill summary must list f0_factibilidad among the capabilities with bindings"
    )
