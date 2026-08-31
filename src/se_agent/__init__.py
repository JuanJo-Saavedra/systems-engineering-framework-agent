"""se-agent: one-shot Codex scaffolder package (PRD 1).

The package exposes CLI `se-agent` with exactly two commands: `--version`
and `init --harness codex --target <dir>`. It has zero runtime dependencies
and performs a one-shot payload install; see `docs/prd/prd-001-one-shot-codex-scaffolder.md`.
"""

from __future__ import annotations

import importlib.metadata

__all__ = ["__version__"]


def __getattr__(name: str):
    """PEP 562 lazy attributes.

    `__version__` resolves from the installed distribution metadata at access
    time (D2): printed/queried version == installed metadata == `pyproject.toml`
    by construction. If the distribution is not installed, `PackageNotFoundError`
    propagates — there is deliberately NO fallback dev string (REQ-V1/D2).
    """
    if name == "__version__":
        return importlib.metadata.version("se-agent")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
