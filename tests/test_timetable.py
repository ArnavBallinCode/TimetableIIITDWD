import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from timetable_automation import parse_time, slot_duration_from_bounds, parse_ltp, safe_str, get_free_blocks, allocate_session, merge_and_style_cells, generate_timetable, split_by_half
import timetable_automation.timetable as timetable_mod

# Example functions extracted for testing
def parse_time(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

def slot_duration_from_bounds(start, end):
    return (parse_time(end) - parse_time(start)) / 60.0

def safe_str(val):
    if val is None:
        return ""
    if isinstance(val, float) and pd.isna(val):
        return ""
    return str(val).strip()

def parse_ltp(sc_string):
    try:
        parts = [x.strip() for x in sc_string.split("-")]
        while len(parts) < 5:
            parts.append("0")
        return list(map(int, parts[:5]))
    except:
        return [0, 0, 0, 0, 0]

class TestTimetableFunctions(unittest.TestCase):
    def setUp(self):
        for d in timetable_mod.days:
            timetable_mod.c004_occupancy[d] = {}

    def test_parse_time(self):
        self.assertEqual(parse_time("07:30"), 450)
        self.assertEqual(parse_time("00:00"), 0)
        self.assertEqual(parse_time("23:59"), 1439)

    def test_slot_duration_from_bounds(self):
        self.assertAlmostEqual(slot_duration_from_bounds("07:30", "09:00"), 1.5)
        self.assertAlmostEqual(slot_duration_from_bounds("13:15", "14:00"), 0.75)

    def test_safe_str(self):
        self.assertEqual(safe_str(None), "")
        self.assertEqual(safe_str(float('nan')), "")
        self.assertEqual(safe_str("  test  "), "test")
        self.assertEqual(safe_str(123), "123")

    def test_parse_ltp(self):
        self.assertEqual(parse_ltp("3-0-2"), [3, 0, 2, 0, 0])
        self.assertEqual(parse_ltp("1-1-1-1-1"), [1, 1, 1, 1, 1])
        self.assertEqual(parse_ltp(""), [0, 0, 0, 0, 0])
        self.assertEqual(parse_ltp("invalid"), [0, 0, 0, 0, 0])

    # Example of get_free_blocks test
    def test_get_free_blocks(self):
        slot_keys = ["07:30-09:00", "09:00-10:30", "10:30-12:00"]
        excluded_slots = ["07:30-09:00"]
        df = pd.DataFrame("", index=["Monday"], columns=slot_keys)
        df.at["Monday", "09:00-10:30"] = "SomeClass"
        
        from facultyTT import get_free_blocks  # Import actual function
        free_blocks = get_free_blocks(df, "Monday")
        self.assertEqual(free_blocks, [["10:30-12:00"]])

    # Placeholder for allocate_session, merge_and_style_cells, generate_timetable tests
    # These can be tested using mocks because they depend on files, randomness, and Excel
    @patch("facultyTT.random.choice")
    def test_allocate_session_mocked(self, mock_choice):
        mock_choice.return_value = "Lab1"
        timetable = pd.DataFrame("", index=["Monday"], columns=["09:00-10:30", "10:30-12:00"])
        lecturer_busy = {"Monday": {}}
        course_room_map = {}
        labs_on_days = set()
        
        from facultyTT import allocate_session
        result = allocate_session(timetable, lecturer_busy, course_room_map, "Monday", "Prof A", "CS101", 1.0, "L", False, labs_on_days)
        self.assertTrue(result)
        self.assertIn("CS101", timetable.values)

    def test_split_by_half(self):
        courses_list = [
            {"Semester_Half": "1", "Course_Code": "C1"},
            {"Semester_Half": "2", "Course_Code": "C2"},
            {"Semester_Half": "0", "Course_Code": "C0"}
        ]
        from facultyTT import split_by_half
        first, second = split_by_half(courses_list)
        self.assertEqual(len(first), 2)
        self.assertEqual(len(second), 2)

    def test_c004_conflict_logs_and_blocks_different_course(self):
        day = "Monday"
        slot = "09:00-10:00"
        tt1 = pd.DataFrame("", index=timetable_mod.days, columns=timetable_mod.slot_keys)
        tt2 = pd.DataFrame("", index=timetable_mod.days, columns=timetable_mod.slot_keys)
        busy = {d: {} for d in timetable_mod.days}
        room_busy = {d: {} for d in timetable_mod.days}
        course_usage_1 = {d: {} for d in timetable_mod.days}
        course_usage_2 = {d: {} for d in timetable_mod.days}
        labsd = set()
        rm = {
            ("CS101", "L"): "C004",
            ("CS101", "_COMBINED"): True,
            ("CS102", "L"): "C004",
            ("CS102", "_COMBINED"): True,
        }

        ok1 = timetable_mod.alloc_specific(
            tt1, busy, rm, room_busy, day, [slot], "Prof A", "CS101", "L", False, labsd, course_usage_1
        )
        self.assertTrue(ok1)

        with patch("builtins.print") as mocked_print:
            ok2 = timetable_mod.alloc_specific(
                tt2, busy, rm, room_busy, day, [slot], "Prof B", "CS102", "L", False, labsd, course_usage_2
            )
        self.assertFalse(ok2)
        mocked_print.assert_called_once()
        self.assertIn("C004-REJECTED", mocked_print.call_args[0][0])
        self.assertIn("request=CS102", mocked_print.call_args[0][0])
        self.assertIn("occupied_by=CS101", mocked_print.call_args[0][0])

    def test_c004_allows_same_code_overlap_across_branches(self):
        day = "Tuesday"
        slot = "09:00-10:00"
        tt1 = pd.DataFrame("", index=timetable_mod.days, columns=timetable_mod.slot_keys)
        tt2 = pd.DataFrame("", index=timetable_mod.days, columns=timetable_mod.slot_keys)
        busy = {d: {} for d in timetable_mod.days}
        room_busy = {d: {} for d in timetable_mod.days}
        course_usage_1 = {d: {} for d in timetable_mod.days}
        course_usage_2 = {d: {} for d in timetable_mod.days}
        labsd = set()
        rm = {
            ("MA161", "L"): "C004",
            ("MA161", "_COMBINED"): True,
        }

        ok1 = timetable_mod.alloc_specific(
            tt1, busy, rm, room_busy, day, [slot], "Prof X", "MA161", "L", False, labsd, course_usage_1
        )
        ok2 = timetable_mod.alloc_specific(
            tt2, busy, rm, room_busy, day, [slot], "Prof Y", "MA161", "L", False, labsd, course_usage_2
        )

        self.assertTrue(ok1)
        self.assertTrue(ok2)

    def test_hide_c004_respects_explicit_combined_flag(self):
        day = "Wednesday"
        slot_a = "09:00-10:00"
        slot_b = "10:00-10:30"
        tt = pd.DataFrame("", index=timetable_mod.days, columns=timetable_mod.slot_keys)
        busy = {d: {} for d in timetable_mod.days}
        room_busy = {d: {} for d in timetable_mod.days}
        course_usage = {d: {} for d in timetable_mod.days}
        labsd = set()
        rm = {
            ("NC004", "L"): "C004",
            ("NC004", "_COMBINED"): False,
            ("CC004", "L"): "C004",
            ("CC004", "_COMBINED"): True,
        }

        ok_non_combined = timetable_mod.alloc_specific(
            tt, busy, rm, room_busy, day, [slot_a], "Prof N", "NC004", "L", False, labsd, course_usage, hide_c004=True
        )
        ok_combined = timetable_mod.alloc_specific(
            tt, busy, rm, room_busy, day, [slot_b], "Prof C", "CC004", "L", False, labsd, course_usage, hide_c004=True
        )

        self.assertTrue(ok_non_combined)
        self.assertTrue(ok_combined)
        self.assertEqual(tt.at[day, slot_a], "NC004 (C004)")
        self.assertEqual(tt.at[day, slot_b], "CC004")

if __name__ == "__main__":
    unittest.main()
