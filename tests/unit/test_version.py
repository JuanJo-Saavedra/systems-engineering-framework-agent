"""REQ-V1 — `se-agent --version` prints the installed package SemVer.

D2: the version comes from installed package metadata (`importlib.metadata`),
never from a fallback dev string, so printed version == installed metadata ==
`pyproject.toml` by construction.
"""

from __future__ import annotations

import importlib.metadata
import tomllib
from pathlib import Path

import pytest

from se_agent import cli

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"


def _declared_version() -> str:
    with PYPROJECT.open("rb") as fh:
        return tomllib.load(fh)["project"]["version"]


def test_version_prints_declared_semver_without_prefix(capsys: pytest.CaptureFixture[str]) -> None:
    """REQ-V1: stdout contains exactly `X.Y.Z\\n`; the `v` prefix is NOT printed."""
    # The console script runs `sys.exit(main())`: success is main() returning 0.
    assert cli.main(["--version"]) == 0
    captured = capsys.readouterr()
    assert captured.out == f"{_declared_version()}\n"
    assert captured.err == ""


def test_version_without_installed_metadata_fails_explicitly(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """D2: PackageNotFoundError -> exit 1 with an explicit message; never a fallback."""

    def _raise_missing(distribution: str) -> str:
        raise importlib.metadata.PackageNotFoundError(distribution)

    monkeypatch.setattr(importlib.metadata, "version", _raise_missing)
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--version"])
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "se-agent" in captured.err
    # No fallback dev string may leak into the message.
    assert _declared_version() not in captured.err
