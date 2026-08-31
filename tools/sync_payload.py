"""Dev-only payload sync tool (design D1).

Mirrors canonical product sources into the committed snapshot
`src/se_agent/_payload/`. The mirror is a packaging artifact: canonical
authority stays in `framework/`, `runtime/`, and `adapters/`, and
`tests/unit/test_payload_coherence.py` proves mirror == sources byte-for-byte.

NEVER run by CI (REQ-CI1): CI only verifies equality. Run manually after
editing any canonical payload source:

    python tools/sync_payload.py

The script is deterministic and idempotent: re-running it with unchanged
sources produces no file changes. Placeholder marker files (`.gitkeep`) are
repo scaffolding and are never mirrored.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_ROOT = REPO_ROOT / "src" / "se_agent" / "_payload"

#: Placeholder marker files are repo scaffolding, never payload.
SKIP_NAMES = frozenset({".gitkeep"})

#: Exact-file mappings: canonical source (repo-relative) -> mirror (payload-relative).
FILE_MAP: dict[str, str] = {
    "runtime/AGENTS.md": "AGENTS.md",
    "runtime/catalogo/skill-registry.md": "catalogo/skill-registry.md",
}

#: Recursive dir mappings: canonical source dir (repo-relative) -> mirror dir
#: prefix (payload-relative). Prefixes are DESTINATION-PRESERVING (design D4:
#: dest_rel == payload_rel): `runtime/skills/` installs as `.agents/skills/`
#: (spec REQ-P1 row 4, design D6), `adapters/codex/` installs as `.codex/`
#: (spec REQ-P1 rows 5–6, design D8), `framework/marco/` installs as `marco/`.
#: Optional sources (`runtime/skills/`, `adapters/codex/`, populated by later
#: work units) are mirrored when present and absent from the mirror otherwise
#: (enforced by prune + coherence test).
DIR_MAP: dict[str, tuple[str, ...]] = {
    "framework/marco": ("marco",),
    "runtime/skills": (".agents", "skills"),
    "adapters/codex": (".codex",),
}


def mapped_expansion() -> dict[PurePosixPath, Path]:
    """Single source->mirror table expansion: mirror rel -> canonical source path."""
    expansion: dict[PurePosixPath, Path] = {}
    for src_rel, mirror_rel in FILE_MAP.items():
        expansion[PurePosixPath(mirror_rel)] = REPO_ROOT / src_rel
    for src_dir, prefix in DIR_MAP.items():
        src_root = REPO_ROOT / src_dir
        if not src_root.is_dir():
            continue
        for path in sorted(src_root.rglob("*")):
            if path.is_file() and path.name not in SKIP_NAMES:
                rel = PurePosixPath(*path.relative_to(src_root).parts)
                expansion[PurePosixPath(*prefix) / rel] = path
    return expansion


def sync() -> int:
    """Make the mirror byte-identical to `mapped_expansion()`; prune stale files.

    Returns the number of mirror files created or updated. Never deletes
    files that are part of the mapped expansion.
    """
    expansion = mapped_expansion()
    changed = 0
    for rel in sorted(expansion, key=lambda p: p.parts):
        source = expansion[rel]
        destination = PAYLOAD_ROOT / Path(*rel.parts)
        data = source.read_bytes()
        if not destination.is_file() or destination.read_bytes() != data:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            changed += 1
    # Prune stale mirror files that are no longer (or never were) mapped.
    expected = set(expansion)
    for path in sorted(PAYLOAD_ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = PurePosixPath(*path.relative_to(PAYLOAD_ROOT).parts)
        if rel not in expected:
            path.unlink()
            changed += 1
    # Remove now-empty directories left behind by pruning.
    for path in sorted((p for p in PAYLOAD_ROOT.rglob("*") if p.is_dir()), reverse=True):
        if not any(path.iterdir()):
            path.rmdir()
    return changed


def main() -> int:
    changed = sync()
    print(f"synced payload mirror: {changed} file(s) created/updated under {PAYLOAD_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
