import importlib.util
from pathlib import Path

import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "timetable_automation" / "timetable.py"


def _load_scheduler_module():
    spec = importlib.util.spec_from_file_location("scheduler_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.c004_occupancy = {d: {} for d in module.days}
    return module


@pytest.fixture
def tm():
    return _load_scheduler_module()


def _blank_timetable(tm):
    return pd.DataFrame("", index=tm.days, columns=tm.slot_keys)


def _empty_state_maps(tm):
    busy = {d: {} for d in tm.days}
    room_busy = {d: {} for d in tm.days}
    course_usage = {d: {} for d in tm.days}
    return busy, room_busy, course_usage


def _first_and_last_usable_slot(tm):
    usable = [s for s in tm.slot_keys if s not in tm.excluded]
    assert usable, "Expected at least one usable time slot"
    return usable[0], usable[-1]


@pytest.mark.blackbox
def test_bva_first_and_last_usable_slots_can_be_allocated(tm):
    first_slot, last_slot = _first_and_last_usable_slot(tm)
    tt = _blank_timetable(tm)
    busy, room_busy, course_usage = _empty_state_maps(tm)
    rm = {}
    labsd = set()
    rr_state = {}

    first_ok = tm.alloc_specific(
        tt,
        busy,
        rm,
        room_busy,
        tm.days[0],
        [first_slot],
        "Prof Boundary A",
        "CSBVA1",
        "L",
        False,
        labsd,
        course_usage,
        class_prefix="C1",
        rr_state=rr_state,
    )

    last_ok = tm.alloc_specific(
        tt,
        busy,
        rm,
        room_busy,
        tm.days[-1],
        [last_slot],
        "Prof Boundary B",
        "CSBVA2",
        "L",
        False,
        labsd,
        course_usage,
        class_prefix="C1",
        rr_state=rr_state,
    )

    assert first_ok
    assert last_ok


@pytest.mark.blackbox
def test_equivalence_partition_valid_and_double_booked_room(tm):
    slot, _ = _first_and_last_usable_slot(tm)
    day = tm.days[1]

    tt_valid = _blank_timetable(tm)
    busy_valid, room_busy_valid, course_usage_valid = _empty_state_maps(tm)
    rm_valid = {("CSVALID", "L"): "C101"}
    valid_ok = tm.alloc_specific(
        tt_valid,
        busy_valid,
        rm_valid,
        room_busy_valid,
        day,
        [slot],
        "Prof Valid",
        "CSVALID",
        "L",
        False,
        set(),
        course_usage_valid,
        class_prefix="C1",
        rr_state={},
    )

    tt_invalid = _blank_timetable(tm)
    busy_invalid, room_busy_invalid, course_usage_invalid = _empty_state_maps(tm)
    room_busy_invalid[day] = {"C101": {slot}}
    rm_invalid = {("CSINVALID", "L"): "C101"}
    invalid_ok = tm.alloc_specific(
        tt_invalid,
        busy_invalid,
        rm_invalid,
        room_busy_invalid,
        day,
        [slot],
        "Prof Invalid",
        "CSINVALID",
        "L",
        False,
        set(),
        course_usage_invalid,
        class_prefix="C1",
        rr_state={},
    )

    assert valid_ok
    assert not invalid_ok


@pytest.mark.blackbox
def test_equivalence_partition_invalid_c004_conflict(tm):
    slot, _ = _first_and_last_usable_slot(tm)
    day = tm.days[2]
    tm.c004_occupancy[day][slot] = "OTHER101"

    tt = _blank_timetable(tm)
    busy, room_busy, course_usage = _empty_state_maps(tm)
    rm = {("CSC004", "L"): "C004"}

    ok = tm.alloc_specific(
        tt,
        busy,
        rm,
        room_busy,
        day,
        [slot],
        "Prof C004",
        "CSC004",
        "L",
        False,
        set(),
        course_usage,
        class_prefix="C1",
        rr_state={},
    )

    assert not ok


@pytest.mark.whitebox
def test_alloc_specific_rejects_invalid_slot_key(tm):
    tt = _blank_timetable(tm)
    busy, room_busy, course_usage = _empty_state_maps(tm)
    ok = tm.alloc_specific(
        tt,
        busy,
        {},
        room_busy,
        tm.days[0],
        ["BAD-SLOT-KEY"],
        "Prof Invalid Slot",
        "CSWB1",
        "L",
        False,
        set(),
        course_usage,
        class_prefix="C1",
        rr_state={},
    )
    assert not ok


@pytest.mark.whitebox
def test_alloc_specific_blocks_second_theory_placement_same_day(tm):
    first_slot, last_slot = _first_and_last_usable_slot(tm)
    day = tm.days[3]

    tt = _blank_timetable(tm)
    busy, room_busy, course_usage = _empty_state_maps(tm)
    rm = {}

    first_ok = tm.alloc_specific(
        tt,
        busy,
        rm,
        room_busy,
        day,
        [first_slot],
        "Prof Whitebox",
        "CSWB2",
        "L",
        False,
        set(),
        course_usage,
        class_prefix="C1",
        rr_state={},
    )

    second_ok = tm.alloc_specific(
        tt,
        busy,
        rm,
        room_busy,
        day,
        [last_slot],
        "Prof Whitebox",
        "CSWB2",
        "T",
        False,
        set(),
        course_usage,
        class_prefix="C1",
        rr_state={},
    )

    assert first_ok
    assert not second_ok


@pytest.mark.whitebox
def test_alloc_specific_success_updates_state_maps(tm):
    slot, _ = _first_and_last_usable_slot(tm)
    day = tm.days[4]

    tt = _blank_timetable(tm)
    busy, room_busy, course_usage = _empty_state_maps(tm)
    rm = {}
    labsd = set()

    ok = tm.alloc_specific(
        tt,
        busy,
        rm,
        room_busy,
        day,
        [slot],
        "Prof Success",
        "CSWB3",
        "L",
        False,
        labsd,
        course_usage,
        class_prefix="C1",
        rr_state={},
    )

    assert ok
    assert tt.at[day, slot] != ""
    assert ("CSWB3", "L") in rm
    assigned_room = rm[("CSWB3", "L")]
    assert slot in busy[day]["Prof Success"]
    assert slot in room_busy[day][assigned_room]
    assert course_usage[day]["CSWB3"]["L"] == 1
