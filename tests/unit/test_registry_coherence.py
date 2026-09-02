"""Registry↔skills coherence as a general, schema-agnostic distribution contract.

The hand-maintained registry (`runtime/catalogo/skill-registry.md`) is free-form
documentation with NO frozen internal contract: these tests never assert its
body structure, sections, columns, table rows, frontmatter keys, backticks, or
installed ruta forms. The asserted invariant is purely distribution-level:
every real skill directory under `runtime/skills/` that contains a `SKILL.md`
must appear in the registry body as its complete id (matched with safe
boundaries), skill directory names follow the stable kebab-case convention,
and the registry exists and is non-empty.

Everything is dynamic: skill ids are discovered from the filesystem, never
encoded, so the checks keep working as skills are added or removed. The same
holds for the skill side: `SKILL.md` frontmatter and body content are never
inspected. The verifier (`tests/helpers/registry_check.py`) is pure,
stdlib-only, and read-only: the canonical registry and skill sources must stay
byte-identical before and after every verification run, and every rejection
fixture runs on temporary copies.
"""

from __future__ import annotations

import importlib.util
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


# --- Canonical sources: general distribution invariants -------------------------


def _canonical_skill_ids() -> set[str]:
    """Skill ids discovered dynamically from the canonical runtime tree."""
    ids = registry_check.skill_directories(SKILLS_ROOT)
    assert ids, "expected at least one skill directory with a SKILL.md under runtime/skills/"
    return ids


def test_canonical_registry_exists_and_is_non_empty() -> None:
    """The registry is a present, non-empty file (no structure asserted)."""
    assert REGISTRY_PATH.is_file(), f"registry missing: {REGISTRY_PATH}"
    assert REGISTRY_PATH.read_text(encoding="utf-8").strip(), "registry must not be empty"


def test_canonical_skill_directories_are_discovered_and_kebab_case() -> None:
    """Every canonical skill directory contains a `SKILL.md` and is kebab-case.

    Skill ids are discovered dynamically; nothing about the inventory, the
    SKILL.md frontmatter, or its body is asserted.
    """
    problems: list[str] = []
    for name in sorted(_canonical_skill_ids()):
        if not (SKILLS_ROOT / name / "SKILL.md").is_file():
            problems.append(f"skill directory {name!r} has no SKILL.md")
        if not registry_check.KEBAB_CASE_RE.fullmatch(name):
            problems.append(f"skill directory {name!r} must be kebab-case")
    assert problems == [], "\n".join(problems)


def test_canonical_skills_and_registry_are_coherent() -> None:
    """Every real runtime skill id appears in the registry body as a complete id,
    whatever the current set of skills is (no structure of the body asserted)."""
    assert SKILLS_ROOT.is_dir(), f"skills source directory missing: {SKILLS_ROOT}"
    problems = registry_check.check_coherence(SKILLS_ROOT, REGISTRY_PATH)
    assert problems == [], "\n".join(problems)


# --- Synthetic fixtures: generic registry + arbitrary skills (temp copies) ------


def _skill_text(name: str) -> str:
    """A minimal, generic SKILL.md fixture (content is never inspected)."""
    return f"cuerpo generico de la skill {name}\n"


def _write_skill_fixture(root: Path, name: str) -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(_skill_text(name), encoding="utf-8")


def _registry_fixture_text(mentioned_ids: list[str]) -> str:
    """A minimal free-form registry fixture mentioning each id as a complete id.

    Deliberately NOT a table: the verifier must not depend on any registry
    format, only on complete-id mentions in the body.
    """
    lines = ["# Registry de ejemplo", ""]
    lines += [f"- `{skill_id}`: skill de ejemplo." for skill_id in mentioned_ids]
    return "\n".join(lines) + "\n"


def _temp_registry(tmp_path: Path, text: str) -> Path:
    """Write a registry fixture copy to tmp_path; the canonical registry is never touched."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    fixture = tmp_path / "skill-registry.md"
    fixture.write_text(text, encoding="utf-8")
    return fixture


FIXTURE_SKILLS = ("alpha-skill", "beta-skill", "gamma-skill")


def _write_fixture_skills(root: Path) -> None:
    for skill_id in FIXTURE_SKILLS:
        _write_skill_fixture(root, skill_id)


def test_multiple_valid_synthetic_skills_are_coherent(tmp_path: Path) -> None:
    """Arbitrary valid skills with a registry mentioning each id pass the check."""
    skills_root = tmp_path / "skills"
    _write_fixture_skills(skills_root)
    registry = _temp_registry(tmp_path / "registry", _registry_fixture_text(list(FIXTURE_SKILLS)))
    problems = registry_check.check_coherence(skills_root, registry)
    assert problems == [], "\n".join(problems)


# --- Negative cases: general distribution properties only ------------------------


def test_skill_present_in_runtime_but_absent_from_registry_text_fails(tmp_path: Path) -> None:
    """A skill present in runtime but missing from the registry body fails, naming it."""
    missing_id = FIXTURE_SKILLS[-1]
    skills_root = tmp_path / "skills"
    _write_fixture_skills(skills_root)
    registry = _temp_registry(
        tmp_path / "registry", _registry_fixture_text([s for s in FIXTURE_SKILLS if s != missing_id])
    )
    problems = registry_check.check_coherence(skills_root, registry)
    assert problems, "skill absent from registry text must be rejected"
    assert any(missing_id in problem for problem in problems), "\n".join(problems)


def test_substring_mention_does_not_count_as_a_full_id(tmp_path: Path) -> None:
    """A longer identifier that merely contains the id (`<id>-v2`) must not satisfy
    the mention requirement: only complete-id matches with safe boundaries count."""
    contained_id = "alpha-skill"
    skills_root = tmp_path / "skills"
    _write_fixture_skills(skills_root)
    text = _registry_fixture_text(["beta-skill", "gamma-skill"]).replace(
        "beta-skill", f"{contained_id}-v2", 1
    )
    assert registry_check.registry_mentions_skill(text, f"{contained_id}-v2")
    assert not registry_check.registry_mentions_skill(text, contained_id)
    registry = _temp_registry(tmp_path / "registry", text)
    problems = registry_check.check_coherence(skills_root, registry)
    assert problems, "substring-only mention must be rejected"
    assert any(contained_id in problem for problem in problems), "\n".join(problems)


def test_missing_registry_file_fails(tmp_path: Path) -> None:
    """A nonexistent registry fails."""
    skills_root = tmp_path / "skills"
    _write_fixture_skills(skills_root)
    problems = registry_check.check_coherence(skills_root, tmp_path / "no-existe" / "skill-registry.md")
    assert problems, "missing registry must be rejected"
    assert any("does not exist" in problem for problem in problems), "\n".join(problems)


def test_empty_registry_fails(tmp_path: Path) -> None:
    """An empty (whitespace-only) registry fails."""
    skills_root = tmp_path / "skills"
    _write_fixture_skills(skills_root)
    registry = _temp_registry(tmp_path / "registry", "\n\n")
    problems = registry_check.check_coherence(skills_root, registry)
    assert problems, "empty registry must be rejected"
    assert any("empty" in problem for problem in problems), "\n".join(problems)


def test_non_kebab_directory_among_valid_peers_fails(tmp_path: Path) -> None:
    """One snake_case directory among valid peers fails, naming it."""
    bad_dir = "gamma_skill"
    skills_root = tmp_path / "skills"
    for skill_id in (*FIXTURE_SKILLS[:-1], bad_dir):
        _write_skill_fixture(skills_root, skill_id)
    registry = _temp_registry(
        tmp_path / "registry", _registry_fixture_text([*FIXTURE_SKILLS[:-1], bad_dir])
    )
    problems = registry_check.check_coherence(skills_root, registry)
    assert problems, "non-kebab skill directory must be rejected"
    assert any("kebab-case" in problem and bad_dir in problem for problem in problems), "\n".join(problems)


def test_canonical_skill_removed_from_registry_copy_fails(tmp_path: Path) -> None:
    """Dynamically: removing one real skill id from a temp copy of the canonical
    registry fails, naming that skill (no id or inventory is encoded here)."""
    removed_id = sorted(_canonical_skill_ids())[0]
    pattern = registry_check.id_boundary_pattern(removed_id)
    substituted, n = pattern.subn("id-eliminado", REGISTRY_PATH.read_text(encoding="utf-8"))
    assert n >= 1, "canonical registry must mention the skill id at least once"
    assert not registry_check.registry_mentions_skill(substituted, removed_id), "substitution must remove the mention"
    registry = _temp_registry(tmp_path, substituted)
    problems = registry_check.check_coherence(SKILLS_ROOT, registry)
    assert problems, "runtime skill absent from registry copy must be rejected"
    assert any(removed_id in problem for problem in problems), "\n".join(problems)


# --- Read-only behavior (canonical sources stay byte-identical) ------------------


def _canonical_snapshot() -> tuple[bytes, dict[Path, bytes]]:
    registry_bytes = REGISTRY_PATH.read_bytes()
    skills_bytes = {p: p.read_bytes() for p in sorted(SKILLS_ROOT.rglob("*")) if p.is_file()}
    return registry_bytes, skills_bytes


def _assert_snapshot_unchanged(snapshot: tuple[bytes, dict[Path, bytes]]) -> None:
    registry_before, skills_before = snapshot
    assert REGISTRY_PATH.read_bytes() == registry_before, "registry was modified by verification"
    after = {p: p.read_bytes() for p in sorted(SKILLS_ROOT.rglob("*")) if p.is_file()}
    assert after == skills_before, "skill sources were modified by verification"


def test_verification_is_read_only_canonical_registry_byte_invariant() -> None:
    """A verification run (pass) leaves the registry and skill sources byte-identical."""
    snapshot = _canonical_snapshot()
    for _ in range(2):
        problems = registry_check.check_coherence(SKILLS_ROOT, REGISTRY_PATH)
        assert problems == [], "\n".join(problems)
    _assert_snapshot_unchanged(snapshot)


def test_negative_fixtures_never_touch_canonical_sources(tmp_path: Path) -> None:
    """All rejection fixtures run on temp copies; the canonical registry and skill
    sources stay byte-identical across every negative scenario."""
    snapshot = _canonical_snapshot()
    test_skill_present_in_runtime_but_absent_from_registry_text_fails(tmp_path / "missing")
    test_substring_mention_does_not_count_as_a_full_id(tmp_path / "substring")
    test_missing_registry_file_fails(tmp_path / "no-file")
    test_empty_registry_fails(tmp_path / "empty")
    test_non_kebab_directory_among_valid_peers_fails(tmp_path / "kebab")
    test_canonical_skill_removed_from_registry_copy_fails(tmp_path / "canonical-missing")
    test_multiple_valid_synthetic_skills_are_coherent(tmp_path / "valid")
    _assert_snapshot_unchanged(snapshot)
