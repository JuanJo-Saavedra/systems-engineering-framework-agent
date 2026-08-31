"""Shared path-reference extraction for artifact/skill reference-integrity tests.

Single implementation of the backtick path-reference extraction used by the WU5
registry/skill test (AC-12) and the WU6 Codex artifacts test (REQ-A1): promoted
during the WU6 refactor instead of duplicating the logic per test module.

Pure, stdlib-only, read-only: operates on text, never touches the filesystem.
"""

from __future__ import annotations

import re

_BACKTICK_RE = re.compile(r"`([^`]+)`")


def extract_path_references(text: str) -> list[str]:
    """Backticked tokens that look like paths: contain `/` or end in `.md`
    (order-preserving dedup)."""
    refs: list[str] = []
    for candidate in _BACKTICK_RE.findall(text):
        if ("/" in candidate or candidate.endswith(".md")) and candidate not in refs:
            refs.append(candidate)
    return refs
