"""REQ-M1/M2 — partial write failure: stop, report, never roll back.

Failure is injected through the `copy_file` seam (design D9 seams; the task
mandates injection rather than permission assumptions, since running as root
or on ACL-less filesystems makes permission-based injection unreliable). The
writer must stop at the first OSError, keep every already-written file (they
belong to the consumer), report `written:`/`pending:` blocks on stderr, and
exit non-zero — never claiming success with pending writes.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from se_agent.init_flow import run_init
from se_agent.payload import PAYLOAD_ROOT
from se_agent.planning import PlannedFile, build_plan


def _failing_copy(fail_on_index: int, calls: list[str]):
    """Inject an OSError on the Nth write; record every attempted destination."""

    def copy(payload_root, item: PlannedFile, destination: Path) -> None:
        calls.append(item.dest_rel.as_posix())
        if len(calls) - 1 == fail_on_index:
            raise OSError("injected: disk full")  # failure before any byte lands
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(
            payload_root.joinpath(*item.payload_rel.parts).read_bytes()  # type: ignore[attr-defined]
        )

    return copy


def _plan() -> tuple[PlannedFile, ...]:
    return build_plan(PAYLOAD_ROOT)


def test_failure_on_third_file_stops_reports_and_never_rolls_back(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    plan = _plan()
    calls: list[str] = []
    rc = run_init(
        str(target), copy_file=_failing_copy(fail_on_index=2, calls=calls)
    )
    assert rc == 1

    err = capsys.readouterr().err
    assert "written:" in err and "pending:" in err
    written = [line.strip() for line in err.splitlines()[
        err.splitlines().index("written:") + 1:
        err.splitlines().index("pending:")
    ] if line.strip()]

    def _looks_like_path(line: str) -> bool:
        """Destination-path line: plan paths never contain spaces, which excludes
        the trailing guidance sentence (paths may start uppercase — WU6 added
        AGENTS.md — or with a dot: .agents/.codex)."""
        return bool(line) and " " not in line

    pending = [line.strip() for line in err.splitlines()[
        err.splitlines().index("pending:") + 1:
    ] if _looks_like_path(line.strip())]

    assert written == [item.dest_rel.as_posix() for item in plan[:2]]
    assert pending == [item.dest_rel.as_posix() for item in plan[2:]]
    assert calls == [item.dest_rel.as_posix() for item in plan[:3]]

    # No rollback: written files keep payload bytes; pending files absent.
    for item in plan[:2]:
        dest = target.joinpath(*item.dest_rel.parts)
        expected = PAYLOAD_ROOT.joinpath(*item.payload_rel.parts).read_bytes()
        assert dest.read_bytes() == expected
    for item in plan[2:]:
        assert not target.joinpath(*item.dest_rel.parts).exists()

    # REQ-M2: success is never claimed.
    assert "Installed" not in capsys.readouterr().out


def test_failure_on_first_file_reports_everything_pending(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    plan = _plan()
    rc = run_init(str(target), copy_file=_failing_copy(0, []))
    assert rc == 1
    err = capsys.readouterr().err
    assert "pending:" in err
    for item in plan:
        assert item.dest_rel.as_posix() in err
    assert not (target / "AGENTS.md").exists()


def test_injected_seam_success_still_writes_everything(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Control: the same seam with no failure behaves like a normal run."""
    target = tmp_path / "target"
    target.mkdir()
    plan = _plan()
    recorded: list[str] = []

    def recording_copy(
        payload_root: object, item: PlannedFile, destination: Path
    ) -> None:
        recorded.append(item.dest_rel.as_posix())
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(
            payload_root.joinpath(*item.payload_rel.parts).read_bytes()  # type: ignore[attr-defined]
        )

    rc = run_init(str(target), copy_file=recording_copy)
    assert rc == 0
    assert recorded == [item.dest_rel.as_posix() for item in plan]
    out = capsys.readouterr().out
    assert f"Installed {len(plan)} file(s):" in out
