import datetime as dt
from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from timetable_automation.core import (
    generate_exam_dates,
    generate_weekdays,
    load_time_slots,
)


def test_generate_weekdays_inclusive_and_weekday_only():
    start = dt.date(2026, 3, 30)  # Monday
    end = dt.date(2026, 4, 5)  # Sunday
    dates = generate_weekdays(start, end)
    assert dates == [
        dt.date(2026, 3, 30),
        dt.date(2026, 3, 31),
        dt.date(2026, 4, 1),
        dt.date(2026, 4, 2),
        dt.date(2026, 4, 3),
    ]


def test_generate_weekdays_rejects_invalid_range():
    with pytest.raises(ValueError):
        generate_weekdays(dt.date(2026, 4, 2), dt.date(2026, 4, 1))


def test_generate_exam_dates_skips_weekends():
    start = dt.date(2026, 4, 3)  # Friday
    dates = generate_exam_dates(3, start)
    assert dates == [
        dt.date(2026, 4, 3),
        dt.date(2026, 4, 6),
        dt.date(2026, 4, 7),
    ]


def test_load_time_slots_normalizes_keys():
    slots_norm, slot_keys, slot_dur = load_time_slots(
        REPO_ROOT / "data" / "time_slots.json"
    )
    assert slots_norm
    assert slot_keys
    assert all("-" in key for key in slot_keys)
    assert set(slot_keys) == set(slot_dur.keys())
