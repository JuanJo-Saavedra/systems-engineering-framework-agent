"""Regression: `_default_prompt` must flush its no-newline stderr prompt
before blocking on stdin.

On Windows PowerShell an unflushed partial stderr line is not visible while
the process blocks on input, so the user sees no prompt. The observable
contract under test: by the time `_default_prompt` reads stdin, the prompt
text is already *flushed* to stderr — not merely written into its buffer.
"""

from __future__ import annotations

import io
import sys

import pytest  # pyright: ignore[reportMissingImports]

from se_agent import collision


class _StderrRecorder(io.TextIOBase):
    """Stderr double that separates buffered writes from flushed output."""

    def __init__(self) -> None:
        self._pending = io.StringIO()
        self.flushed = io.StringIO()

    def write(self, s: str) -> int:
        self._pending.write(s)
        return len(s)

    def flush(self) -> None:
        self.flushed.write(self._pending.getvalue())
        self._pending.seek(0)
        self._pending.truncate(0)


def test_default_prompt_flushes_stderr_before_reading_stdin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompt = "Overwrite the listed path(s)? [y/N] "
    stderr = _StderrRecorder()

    class _StdinStub:
        def __init__(self) -> None:
            self.seen_at_read: str | None = None

        def readline(self) -> str:
            # Snapshot what a blocked reader would already SEE on stderr.
            self.seen_at_read = stderr.flushed.getvalue()
            return "y\n"

    stdin = _StdinStub()
    monkeypatch.setattr(sys, "stderr", stderr)
    monkeypatch.setattr(sys, "stdin", stdin)

    assert collision._default_prompt(prompt) == "y\n"
    assert stdin.seen_at_read == prompt
