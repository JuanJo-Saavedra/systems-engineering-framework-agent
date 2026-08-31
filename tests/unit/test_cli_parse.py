"""REQ-V2 — `init` command surface and harness constraint (parse half).

D3: stdlib argparse; parse errors exit 2 and precede every filesystem access.
"""

from __future__ import annotations

import builtins
import contextlib
import os
from collections.abc import Iterator

import pytest

from se_agent import cli

_SENTINELLED_OS_ATTRS = (
    "stat",
    "lstat",
    "mkdir",
    "makedirs",
    "scandir",
    "listdir",
    "remove",
    "unlink",
    "rmdir",
    "rename",
)
_MUTATING_OS_ATTRS = frozenset({"mkdir", "makedirs", "remove", "unlink", "rmdir", "rename"})


@contextlib.contextmanager
def fs_sentinel(forbidden_paths: tuple[str, ...] = ()) -> Iterator[list[str]]:
    """Prove the block performs zero writes and never touches `forbidden_paths`.

    Scoped to the `cli.main()` invocation only (never active during pytest's
    own reporting/teardown). Mutating os calls hard-fail immediately. Read
    calls (os.stat/builtins.open) pass through — the stdlib itself reads
    locale data while constructing the parser — but any read whose path
    contains a `forbidden_paths` entry (e.g. the user-supplied --target) is
    recorded and raises, naming the entry point. REQ-V2's contract is zero
    writes and zero access to the destination filesystem on parse errors.
    """
    attempted: list[str] = []

    def _mutator_boom(name: str):
        def handler(*args: object, **kwargs: object) -> object:
            attempted.append(name)
            raise AssertionError(f"filesystem mutation attempted via {name}")

        return handler

    def _reader_guard(name: str, original):
        def handler(path: object, *args: object, **kwargs: object) -> object:
            s = str(path)
            if any(forbidden in s for forbidden in forbidden_paths):
                attempted.append(f"{name}:{s}")
                raise AssertionError(f"filesystem access to forbidden path via {name}: {s}")
            return original(path, *args, **kwargs)

        return handler

    saved_os = {attr: getattr(os, attr) for attr in _SENTINELLED_OS_ATTRS if hasattr(os, attr)}
    saved_open = builtins.open
    try:
        for attr in _SENTINELLED_OS_ATTRS:
            if attr not in saved_os:
                continue
            if attr in _MUTATING_OS_ATTRS:
                setattr(os, attr, _mutator_boom(f"os.{attr}"))
            else:
                setattr(os, attr, _reader_guard(f"os.{attr}", saved_os[attr]))
        builtins.open = _reader_guard("builtins.open", saved_open)  # type: ignore[assignment]
        yield attempted
    finally:
        for attr, fn in saved_os.items():
            setattr(os, attr, fn)
        builtins.open = saved_open  # type: ignore[assignment]


def test_invalid_harness_value_exits_2_naming_value(capsys: pytest.CaptureFixture[str]) -> None:
    """REQ-V2: harness other than `codex` -> exit 2 with a message naming the value."""
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["init", "--harness", "gradle", "--target", "some/dir"])
    assert excinfo.value.code == 2
    captured = capsys.readouterr()
    assert "gradle" in captured.err
    assert "codex" in captured.err


def test_missing_target_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    """REQ-V2: `--target` is required for `init`."""
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["init", "--harness", "codex"])
    assert excinfo.value.code == 2
    assert "--target" in capsys.readouterr().err


def test_unknown_top_level_flag_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    """D3/D5: unknown flags are usage errors (exit 2)."""
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--bogus"])
    assert excinfo.value.code == 2
    assert "--bogus" in capsys.readouterr().err


def test_invalid_harness_performs_zero_filesystem_access() -> None:
    """REQ-V2/D3: parse errors perform zero writes and never touch the target path."""
    with fs_sentinel(forbidden_paths=("some/dir",)) as attempted, pytest.raises(SystemExit) as excinfo:
        cli.main(["init", "--harness", "gradle", "--target", "some/dir"])
    assert excinfo.value.code == 2
    assert attempted == []


def test_missing_target_performs_zero_filesystem_access() -> None:
    """REQ-V2/D3: parse errors perform zero writes and never touch the target path."""
    with fs_sentinel() as attempted, pytest.raises(SystemExit) as excinfo:
        cli.main(["init", "--harness", "codex"])
    assert excinfo.value.code == 2
    assert attempted == []
