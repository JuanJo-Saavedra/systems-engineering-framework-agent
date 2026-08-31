"""Shared integration-test fixtures (design D9).

`make_target()` builds target trees programmatically under pytest's `tmp_path`
(never inside the checkout): `empty`, `populated_proyecto`, `collision_files`,
`symlink_escape`. `tree_snapshot()` returns a deterministic content snapshot
(sha256 per file, symlink targets, directory markers) used to prove
byte-invariance of untouched content (REQ-W2/W3, AC-4).
"""

from __future__ import annotations

import hashlib
import io
import itertools
import os
import stat
import sys
from collections.abc import Callable
from pathlib import Path

# pi-lens-ignore: Pyright:reportMissingImports
# pi-lens-ignore: reportMissingImports
import pytest  # pyright: ignore[reportMissingImports]

_TARGET_KINDS = ("empty", "populated_proyecto", "collision_files", "symlink_escape")


@pytest.fixture
def make_target(tmp_path: Path) -> Callable[[str], Path]:
    """Fixture factory: build a target directory of the requested kind.

    Repeated calls with the same kind yield distinct directories so a test can
    create several equivalent targets (e.g. determinism checks, REQ-P4).
    """
    counter = itertools.count()

    def _make(kind: str) -> Path:
        if kind not in _TARGET_KINDS:
            raise ValueError(f"unknown target kind: {kind!r}")
        target = tmp_path / f"{kind}-{next(counter)}"
        target.mkdir()
        if kind == "populated_proyecto":
            _populate_proyecto(target)
        elif kind == "collision_files":
            _add_collision_files(target)
        elif kind == "symlink_escape":
            _add_symlink_escape(tmp_path, next(counter), target)
        return target

    return _make


@pytest.fixture
def fake_stdin(monkeypatch: pytest.MonkeyPatch) -> Callable[..., io.StringIO]:
    """Install a fake `sys.stdin` with controlled TTY-ness and scripted input.

    `answer=None` means an exhausted stream (EOF at the prompt, REQ-C3).
    """

    def _install(is_tty: bool, answer: str | None) -> io.StringIO:
        class _FakeStdin(io.StringIO):
            def isatty(self) -> bool:
                return is_tty

        stream = _FakeStdin(answer if answer is not None else "")
        if answer is None:
            stream.seek(0, io.SEEK_END)  # nothing left to read: readline() == ""
        monkeypatch.setattr(sys, "stdin", stream)
        return stream

    return _install


@pytest.fixture
def tree_snapshot() -> Callable[[Path], dict[str, str]]:
    """Return a snapshot function: rel-path -> content descriptor, sorted.

    Files hash by sha256, symlinks record their target, directories are
    markers. Comparing before/after snapshots proves byte-invariance without
    assuming anything about mtimes or permissions.
    """
    return _snapshot


def _snapshot(root: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    if not root.exists():
        return entries

    def walk(directory: Path, prefix: str) -> None:
        for child in sorted(directory.iterdir(), key=lambda p: p.name):
            rel = f"{prefix}{child.name}"
            mode = child.lstat().st_mode
            if stat.S_ISLNK(mode):
                entries[rel] = f"link:{os.readlink(child)}"
            elif child.is_dir():
                entries[rel] = "dir"
                walk(child, f"{rel}/")
            else:
                digest = hashlib.sha256(child.read_bytes()).hexdigest()
                entries[rel] = f"sha256:{digest}"

    walk(root, "")
    return entries


def _populate_proyecto(target: Path) -> None:
    """Consumer-owned `proyecto/` state — untouchable in every mode (REQ-W2)."""
    registros = target / "proyecto" / "registros"
    estado = target / "proyecto" / "estado"
    registros.mkdir(parents=True)
    estado.mkdir(parents=True)
    (registros / "riesgos.md").write_text(
        "# Riesgos\n\nR-01 riesgo propio del consumidor.\n", encoding="utf-8"
    )
    (registros / "decisiones_tecnicas.md").write_text(
        "# Decisiones técnicas\n\nDT-01 decisión propia.\n", encoding="utf-8"
    )
    (estado / "fase_actual.md").write_text("fase: F0\n", encoding="utf-8")


def _add_collision_files(target: Path) -> None:
    """Pre-existing files that collide with write-set destinations (REQ-C1)."""
    marco = target / "marco"
    catalogo = target / "catalogo"
    marco.mkdir()
    catalogo.mkdir()
    (target / "AGENTS.md").write_bytes(b"stale AGENTS.md (consumer)\n")
    (marco / "README.md").write_bytes(b"stale marco README (consumer)\n")
    (catalogo / "skill-registry.md").write_bytes(b"stale registry (consumer)\n")


def _add_symlink_escape(tmp_path: Path, suffix: int, target: Path) -> None:
    """`marco` -> sibling directory outside the target (REQ-F2 escape)."""
    outside = tmp_path / f"outside-{suffix}"
    outside.mkdir()
    (outside / "secret.txt").write_bytes(b"outside the target\n")
    (target / "marco").symlink_to(outside, target_is_directory=True)
