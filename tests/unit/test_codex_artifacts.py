"""WU6 — REQ-A1 — Codex adapter artifacts: mechanisms, not domain rules.

The Codex adapter (`adapters/codex/config.toml` + at least one
`adapters/codex/agents/*.toml`) must be installed as `.codex/config.toml` and
`.codex/agents/*.toml` by `se-agent init`. The artifacts expose Codex
MECHANISMS only: they must never redefine, duplicate, or contradict the domain
rules that live in `AGENTS.md` and `marco/` (design D8). The orchestrator agent
instantiates the runtime contract BY REFERENCE: `AGENTS.md` as the rules
source, `catalogo/skill-registry.md` for skill discovery, and `proyecto/estado/`
for state reading — with zero `proyecto/` write language and zero absolute
paths.

Installed-tree assertions run against the committed payload mirror
(`src/se_agent/_payload/`), which is the byte-exact oracle of what `init`
installs (D1); the mirror prefix `codex/` corresponds to the installed
`.codex/` (destination-preserving structure, D4). Triangulation negative cases
are pure functions over fixture strings — the canonical sources and the mirror
are never mutated by a test.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import tomllib
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTERS_ROOT = REPO_ROOT / "adapters" / "codex"
PAYLOAD_ROOT = REPO_ROOT / "src" / "se_agent" / "_payload"
#: Mirror prefix `.codex/` is DESTINATION-PRESERVING: installed `.codex/*` == mirror
#: `.codex/*` (spec REQ-P1 rows 5–6, design D4/D8 — same resolution as the WU5 `.agents`
#: prefix deviation, proven by the runtime harness).
CODEX_MIRROR = PAYLOAD_ROOT / ".codex"

#: Placeholder marker files are repo scaffolding, never adapter artifacts.
SKIP_NAMES = frozenset({".gitkeep"})


def _load_path_refs():
    """Import `tests/helpers/path_refs.py` (shared with the WU5 registry test — WU6 refactor)."""
    script = REPO_ROOT / "tests" / "helpers" / "path_refs.py"
    spec = importlib.util.spec_from_file_location("path_refs_under_test", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


path_refs = _load_path_refs()


# --- Reference extraction (shared with the WU5 registry test after REFACTOR) ----


def _toml_string_values(text: str) -> list[str]:
    """All string values of a TOML document, or [] when the text is not TOML
    (prose fixtures / free-text comments). Artifact parseability is asserted
    separately by test_every_payload_toml_parses_with_tomllib."""
    values: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, str):
            values.append(node)
        elif isinstance(node, dict):
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    try:
        document = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return []
    walk(document)
    return values


def _artifact_references(text: str) -> list[str]:
    """Path-like references in a Codex artifact: backticked mentions + TOML string values."""
    refs: list[str] = []
    for candidate in path_refs.extract_path_references(text):
        if candidate not in refs:
            refs.append(candidate)
    for value in _toml_string_values(text):
        if ("/" in value or value.endswith(".md")) and value not in refs:
            refs.append(value)
    return refs


# --- Pure validators (also exercised by the triangulation cases) -----------------

_ABSOLUTE_POSIX_RE = re.compile(r"(?:^|[\s\"'`(=:,])/[A-Za-z][A-Za-z0-9_./-]*")
_WINDOWS_DRIVE_RE = re.compile(r"\b[A-Za-z]:[\\/][A-Za-z0-9_\\/.-]+")

_WRITE_VERB_RE = re.compile(
    r"\b("
    r"escribe|escribir|escrito|crea|crear|creado|creada|modifica|modificar|modificado|modificada"
    r"|elimina|eliminar|eliminado|sobrescribe|sobrescribir|actualiza|actualizar|actualizado"
    r"|guarda|guardar|guardado"
    r"|write|writes|writing|written|create|creates|created|modify|modifies|modify"
    r"|delete|deletes|deleting|overwrite|overwrites|overwriting|update|updates|updating"
    r")\b",
    re.IGNORECASE,
)


def absolute_path_problems(text: str) -> list[str]:
    """Absolute filesystem paths (POSIX or Windows) that must never appear in an artifact."""
    problems = [f"absolute path in artifact: {match.group(0).strip()}" for match in _ABSOLUTE_POSIX_RE.finditer(text)]
    problems += [f"windows drive path in artifact: {match.group(0)}" for match in _WINDOWS_DRIVE_RE.finditer(text)]
    return problems


def write_language_problems(text: str) -> list[str]:
    """Lines that combine a `proyecto/` reference with write language: the adapter
    never instructs writes into the consumer's authoritative `proyecto/` tree
    (REQ-W2; the skill/orchestrator READS state, it never writes it)."""
    problems: list[str] = []
    for line in text.splitlines():
        if "proyecto/" in line and _WRITE_VERB_RE.search(line):
            problems.append(f"proyecto/ write language in artifact: {line.strip()}")
    return problems


def reference_problems(text: str, installed_root: Path) -> list[str]:
    """Reference integrity against the installed tree (mirror oracle):
    install-time references (`AGENTS.md`, `marco/**`, `catalogo/**`) must exist;
    `proyecto/…` references are FORM-CHECKED ONLY (relative, no `..`) because they
    denote runtime-authored consumer state that does not exist at install time
    (design D6/D8 rationale)."""
    problems: list[str] = []
    for ref in _artifact_references(text):
        parts = PurePosixPath(ref).parts
        if ref.startswith("proyecto/"):
            if PurePosixPath(ref).is_absolute() or ".." in parts:
                problems.append(f"malformed proyecto/ reference (must be relative, no '..'): {ref}")
            continue
        if PurePosixPath(ref).is_absolute() or ".." in parts or not parts:
            problems.append(f"non-relative install-time reference: {ref}")
            continue
        if not (installed_root / Path(*parts)).exists():
            problems.append(f"broken reference (not in installed tree): {ref}")
    return problems


# --- Loaders ----------------------------------------------------------------------


def _canonical_artifacts() -> dict[PurePosixPath, Path]:
    """Canonical adapter files: mirror-relative rel -> source path."""
    if not ADAPTERS_ROOT.is_dir():
        return {}
    return {
        PurePosixPath(*path.relative_to(ADAPTERS_ROOT).parts): path
        for path in sorted(ADAPTERS_ROOT.rglob("*"))
        if path.is_file() and path.name not in SKIP_NAMES
    }


def _mirror_artifacts() -> dict[PurePosixPath, Path]:
    """Installed codex artifacts: mirror-relative rel -> mirror path."""
    if not CODEX_MIRROR.is_dir():
        return {}
    return {
        PurePosixPath(*path.relative_to(CODEX_MIRROR).parts): path
        for path in sorted(CODEX_MIRROR.rglob("*"))
        if path.is_file() and path.name not in SKIP_NAMES
    }


def _artifact_texts() -> dict[PurePosixPath, str]:
    """Text of every installed artifact (mirror oracle of the post-init `.codex/` tree)."""
    return {rel: path.read_text(encoding="utf-8") for rel, path in _mirror_artifacts().items()}


# --- Structural presence (REQ-A1, design D8) --------------------------------------


def test_canonical_codex_sources_exist() -> None:
    """REQ-A1: `adapters/codex/config.toml` exists and at least one `agents/*.toml`."""
    canonical = _canonical_artifacts()
    assert PurePosixPath("config.toml") in canonical, f"missing canonical .codex config: {ADAPTERS_ROOT / 'config.toml'}"
    agents = [rel for rel in canonical if rel.parts[0] == "agents" and rel.suffix == ".toml"]
    assert agents, "at least one canonical agent artifact is required (REQ-P1 row 6)"


def test_mirror_installs_config_and_at_least_one_agent() -> None:
    """REQ-A1: post-init, `.codex/config.toml` is present and ≥1 `.codex/agents/*.toml` exists
    (destination-preserving mirror prefix `.codex/`, D4/REQ-P1 rows 5–6)."""
    installed = _mirror_artifacts()
    assert PurePosixPath("config.toml") in installed, f".codex/config.toml not installed; mirror has {sorted(installed)}"
    installed_agents = [rel for rel in installed if rel.parts[0] == "agents" and rel.suffix == ".toml"]
    assert installed_agents, f"no .codex/agents/*.toml installed; mirror has {sorted(installed)}"


def test_mirror_is_byte_identical_to_canonical_sources() -> None:
    """REQ-P2 rows 5–6: installed `.codex/*` are byte-for-byte copies of `adapters/codex/*`."""
    canonical = _canonical_artifacts()
    installed = _mirror_artifacts()
    assert set(canonical) == set(installed), (
        f"canonical-only: {sorted(set(canonical) - set(installed))}; "
        f"mirror-only: {sorted(set(installed) - set(canonical))}"
    )
    for rel, source in canonical.items():
        assert installed[rel].read_bytes() == source.read_bytes(), f"byte mismatch: {rel}"


def test_every_payload_toml_parses_with_tomllib() -> None:
    """REQ-A1: every `.toml` in the payload parses with the stdlib parser."""
    toml_files = [path for path in sorted(PAYLOAD_ROOT.rglob("*.toml")) if path.is_file()]
    assert toml_files, "no .toml artifacts in the payload mirror"
    for path in toml_files:
        with path.open("rb") as handle:
            tomllib.load(handle)  # tomllib.TOMLDecodeError propagates as the failure


# --- Boundary: mechanisms, not domain rules (REQ-A1, design D8) --------------------


def test_artifacts_contain_no_absolute_paths() -> None:
    """REQ-A1: no artifact contains an absolute filesystem path (repo-relative only)."""
    problems: list[str] = []
    for rel, text in _artifact_texts().items():
        problems += [f"{rel}: {problem}" for problem in absolute_path_problems(text)]
    assert problems == [], "\n".join(problems)


def test_artifacts_use_no_proyecto_write_language() -> None:
    """REQ-A1/REQ-W2: no artifact instructs writes into the consumer's `proyecto/` tree."""
    problems: list[str] = []
    for rel, text in _artifact_texts().items():
        problems += [f"{rel}: {problem}" for problem in write_language_problems(text)]
    assert problems == [], "\n".join(problems)


def test_artifact_references_resolve_in_installed_tree() -> None:
    """REQ-A1: every referenced `AGENTS.md`/`marco/`/`catalogo/` path exists in the
    installed tree; `proyecto/` references are form-checked only (D6/D8)."""
    problems: list[str] = []
    for rel, text in _artifact_texts().items():
        problems += [f"{rel}: {problem}" for problem in reference_problems(text, PAYLOAD_ROOT)]
    assert problems == [], "\n".join(problems)


def test_orchestrator_instantiates_runtime_contract_by_reference() -> None:
    """D8: the orchestrator agent points to `AGENTS.md` (rules source),
    `catalogo/skill-registry.md` (skill discovery) and `proyecto/estado/`
    (state reading) — it restates no domain rule itself."""
    installed = _mirror_artifacts()
    orchestrators = [rel for rel in installed if rel.parts[0] == "agents"]
    assert orchestrators, "no installed orchestrator agent"
    text = installed[orchestrators[0]].read_text(encoding="utf-8")
    refs = _artifact_references(text)
    for required in ("AGENTS.md", "catalogo/skill-registry.md", "proyecto/estado/"):
        assert required in refs, f"orchestrator must reference {required} by path; refs found: {refs}"
    assert any(ref == "marco/" or ref.startswith("marco/") for ref in refs), (
        f"orchestrator must reference the marco/ domain model; refs found: {refs}"
    )


# --- Triangulation: the validators must FAIL on every violation class --------------
# (fixture strings only — canonical sources and the mirror are never mutated).


def test_rejects_absolute_path_injected() -> None:
    """Triangulation: an injected absolute path is flagged, naming it."""
    text = 'trampa = "/etc/se-agent-no-debe-existir"\n'
    problems = absolute_path_problems(text)
    assert problems, "absolute path must be rejected"
    assert any("/etc/se-agent-no-debe-existir" in problem for problem in problems), "\n".join(problems)


def test_rejects_windows_drive_path_injected() -> None:
    """Triangulation: a Windows drive path is flagged, naming it."""
    problems = absolute_path_problems('trampa = "C:\\\\Users\\\\alguien"')
    assert problems, "windows drive path must be rejected"
    assert any("C:" in problem for problem in problems), "\n".join(problems)


def test_rejects_proyecto_write_language_injected() -> None:
    """Triangulation: an injected write instruction against `proyecto/` is flagged."""
    text = "# Instrucción inválida: escribe el resultado en proyecto/estado/\n"
    problems = write_language_problems(text)
    assert problems, "proyecto/ write language must be rejected"
    assert any("escribe" in problem.lower() for problem in problems), "\n".join(problems)


def test_reading_language_is_not_flagged() -> None:
    """Triangulation guard: read-only `proyecto/` language must NOT be flagged
    (the orchestrator legitimately reads `proyecto/estado/`)."""
    text = '# Lee el estado desde proyecto/estado/ antes de actuar.\nestado = "proyecto/estado/"\n'
    assert write_language_problems(text) == [], "read-only proyecto/ language must not be rejected"


def test_rejects_reference_to_nonexistent_marco_path_injected() -> None:
    """Triangulation: a reference to a nonexistent `marco/` path is flagged, naming it."""
    text = "Lee `marco/fases/fase_inexistente_para_triangulacion.md` antes de actuar.\n"
    problems = reference_problems(text, PAYLOAD_ROOT)
    assert problems, "broken marco/ reference must be rejected"
    assert any("marco/fases/fase_inexistente_para_triangulacion.md" in problem for problem in problems), "\n".join(
        problems
    )


def test_rejects_absolute_reference_injected() -> None:
    """Triangulation: a non-relative reference token is flagged by the reference checker too."""
    problems = reference_problems("Lee `/etc/passwd` antes de actuar.\n", PAYLOAD_ROOT)
    assert problems, "absolute reference token must be rejected"
    assert any("non-relative install-time reference" in problem for problem in problems), "\n".join(problems)


def test_negative_cases_never_touch_canonical_or_mirror() -> None:
    """REQ-R3 analog: triangulation runs on fixture strings; the canonical sources
    and the payload mirror stay byte-identical before and after."""
    snapshot = {p: p.read_bytes() for p in sorted(list(ADAPTERS_ROOT.rglob("*")) + list(CODEX_MIRROR.rglob("*"))) if p.is_file()}
    absolute_path_problems('x = "/tmp/trampa"')
    write_language_problems("# escribe en proyecto/estado/")
    reference_problems("Lee `marco/fases/inexistente.md`", PAYLOAD_ROOT)
    after = {p: p.read_bytes() for p in sorted(list(ADAPTERS_ROOT.rglob("*")) + list(CODEX_MIRROR.rglob("*"))) if p.is_file()}
    assert snapshot == after, "a triangulation case mutated canonical sources or the mirror"
