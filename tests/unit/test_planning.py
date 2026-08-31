"""WU3 unit tests: plan model, static expansion, deterministic ordering (design D4/D11).

`build_plan()` is a pure static expansion of a payload root: no user input ever
contributes a plan path, the result is a tuple of frozen `PlannedFile`s sorted
by the tuple of `dest_rel.parts`, and the write-set is asserted sanitary.
"""

from __future__ import annotations

import dataclasses
from pathlib import PurePosixPath

from se_agent.payload import PAYLOAD_ROOT, enumerate_payload
from se_agent.planning import PlannedFile, build_plan


def test_build_plan_expands_static_payload():
    plan = build_plan(PAYLOAD_ROOT)
    assert isinstance(plan, tuple)
    expected = {dest for dest, _ in enumerate_payload()}
    assert {item.dest_rel for item in plan} == expected


def test_build_plan_pairs_dest_with_payload_paths():
    for item in build_plan(PAYLOAD_ROOT):
        assert isinstance(item.dest_rel, PurePosixPath)
        assert isinstance(item.payload_rel, PurePosixPath)
        assert item.dest_rel == item.payload_rel


def test_build_plan_deterministic_sort_key():
    keys = [tuple(item.dest_rel.parts) for item in build_plan(PAYLOAD_ROOT)]
    assert keys == sorted(keys)
    assert len(set(keys)) == len(keys)


def test_build_plan_deterministic_across_calls():
    assert build_plan(PAYLOAD_ROOT) == build_plan(PAYLOAD_ROOT)


def test_planned_file_is_frozen():
    item = PlannedFile(PurePosixPath("a/b.md"), PurePosixPath("a/b.md"))
    assert item.dest_rel == PurePosixPath("a/b.md")
    assert item.payload_rel == PurePosixPath("a/b.md")
    try:
        setattr(item, "dest_rel", PurePosixPath("c/d.md"))
    except dataclasses.FrozenInstanceError:
        pass
    else:
        raise AssertionError("PlannedFile must be frozen")


def test_build_plan_synthetic_tree_ordering(tmp_path):
    (tmp_path / "b_dir").mkdir()
    (tmp_path / "b_dir" / "z.md").write_bytes(b"z")
    (tmp_path / "a.txt").write_bytes(b"a")
    (tmp_path / "b_dir" / "a.md").write_bytes(b"b")
    plan = build_plan(tmp_path)
    assert [tuple(item.dest_rel.parts) for item in plan] == [
        ("a.txt",),
        ("b_dir", "a.md"),
        ("b_dir", "z.md"),
    ]


def test_build_plan_empty_root(tmp_path):
    assert build_plan(tmp_path) == ()
