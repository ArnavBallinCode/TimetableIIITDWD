import pandas as pd
import pytest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from timetable_automation.validation import (
    validate_batch_slot_uniqueness,
    validate_exam_output,
    validate_slot_allocations,
)


@pytest.mark.whitebox
def test_validate_exam_output_rejects_partial_rows():
    df = pd.DataFrame(
        [
            {
                "Batch": "1CSEA",
                "Date_str": "01-Apr-2026",
                "Slot": "Morning",
                "Course": "CS101",
                "Rooms": "C101 (30) (PARTIAL)",
            }
        ]
    )

    with pytest.raises(ValueError, match="Incomplete room assignment"):
        validate_exam_output(df, date_column="Date_str", slot_column="Slot", rooms_column="Rooms")


@pytest.mark.whitebox
def test_validate_exam_output_rejects_room_and_faculty_clashes():
    df = pd.DataFrame(
        [
            {
                "Date_str": "01-Apr-2026",
                "Slot": "Morning",
                "Course": "CS101",
                "Rooms": "C101 (30)",
                "Faculty": "Prof A",
            },
            {
                "Date_str": "01-Apr-2026",
                "Slot": "Morning",
                "Course": "CS102",
                "Rooms": "C101 (25)",
                "Faculty": "Prof A",
            },
        ]
    )

    with pytest.raises(ValueError, match="Room clash"):
        validate_exam_output(df, date_column="Date_str", slot_column="Slot", rooms_column="Rooms")


@pytest.mark.whitebox
def test_validate_batch_slot_uniqueness_rejects_overlap():
    df = pd.DataFrame(
        [
            {"Batch": "1CSEA", "Date_str": "01-Apr-2026", "Slot": "Morning", "Course": "CS101"},
            {"Batch": "1CSEA", "Date_str": "01-Apr-2026", "Slot": "Morning", "Course": "CS102"},
        ]
    )

    with pytest.raises(ValueError, match="overlapping exams"):
        validate_batch_slot_uniqueness(df, batch_column="Batch", date_column="Date_str", slot_column="Slot")


@pytest.mark.whitebox
def test_validate_slot_allocations_rejects_missing_room():
    with pytest.raises(ValueError, match="Incomplete room assignment"):
        validate_slot_allocations(
            [
                {
                    "day": "Monday",
                    "slot": "09:00-10:00",
                    "course": "CS101",
                    "room": "",
                    "faculty": "Prof A",
                    "requires_room": True,
                }
            ]
        )
