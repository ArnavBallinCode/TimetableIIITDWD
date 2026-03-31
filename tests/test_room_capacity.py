import unittest
import pandas as pd
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from timetable_automation.timetable import room_candidates, room_capacity


class TestRoomCapacityEnforcement(unittest.TestCase):
    """Test that room capacity is properly enforced during scheduling."""

    def test_room_capacity_loaded(self):
        """Verify room capacity data is loaded."""
        self.assertIsInstance(room_capacity, dict)
        self.assertGreater(len(room_capacity), 0)
        # Check specific rooms have capacity
        self.assertIn("C101", room_capacity)
        self.assertEqual(room_capacity["C101"], 48)
        self.assertIn("C004", room_capacity)
        self.assertEqual(room_capacity["C004"], 240)

    def test_room_candidates_no_capacity_filter(self):
        """Test room_candidates returns all matching rooms when no capacity specified."""
        candidates = room_candidates(lab=False, prefix="C1", min_capacity=0)
        self.assertIsInstance(candidates, list)
        # Should return rooms starting with C1
        for room in candidates:
            self.assertTrue(room.startswith("C1"))

    def test_room_candidates_with_exact_capacity(self):
        """Test room_candidates filters by exact capacity match."""
        # Request rooms with capacity >= 48 (most standard rooms)
        candidates = room_candidates(lab=False, prefix="C1", min_capacity=48)
        self.assertIsInstance(candidates, list)
        # All returned rooms should have capacity >= 48
        for room in candidates:
            self.assertGreaterEqual(room_capacity.get(room, 0), 48)

    def test_room_candidates_capacity_slightly_above(self):
        """Test room_candidates with capacity slightly above standard rooms."""
        # Request rooms with capacity >= 50 (should exclude 48-capacity rooms)
        candidates = room_candidates(lab=False, prefix="C", min_capacity=50)
        self.assertIsInstance(candidates, list)
        # All returned rooms should have capacity >= 50
        for room in candidates:
            self.assertGreaterEqual(room_capacity.get(room, 0), 50)
        # Should include larger halls but not standard classrooms
        if candidates:
            # C004 has 240 capacity, should be included
            # C002, C003 have 120 capacity, should be included
            self.assertTrue(
                any(room_capacity.get(room, 0) >= 100 for room in candidates),
                "Should include at least one large room"
            )

    def test_room_candidates_capacity_significantly_below(self):
        """Test room_candidates when no room meets high capacity requirement."""
        # Request rooms with capacity >= 300 (exceeds all room capacities)
        candidates = room_candidates(lab=False, prefix="C", min_capacity=300)
        # Should return empty list
        self.assertEqual(len(candidates), 0)

    def test_room_candidates_sorted_by_capacity(self):
        """Test that rooms are sorted by capacity (largest first) when capacity filtering is used."""
        candidates = room_candidates(lab=False, prefix="C", min_capacity=100)
        if len(candidates) > 1:
            # Verify descending order by capacity
            capacities = [room_capacity.get(room, 0) for room in candidates]
            self.assertEqual(capacities, sorted(capacities, reverse=True))

    def test_room_candidates_lab_rooms(self):
        """Test room_candidates for lab rooms with capacity."""
        candidates = room_candidates(lab=True, lab_prefix="L1", min_capacity=40)
        self.assertIsInstance(candidates, list)
        # All returned rooms should be labs with sufficient capacity
        for room in candidates:
            self.assertTrue(room.startswith("L"))
            self.assertGreaterEqual(room_capacity.get(room, 0), 40)

    def test_large_class_gets_large_room(self):
        """Test that requesting capacity for large classes returns appropriate rooms."""
        # Simulate a course with 200 students
        candidates = room_candidates(lab=False, prefix="C", min_capacity=200)
        self.assertIsInstance(candidates, list)
        # Should only return C004 (240 capacity)
        self.assertIn("C004", candidates)
        # All rooms should have capacity >= 200
        for room in candidates:
            self.assertGreaterEqual(room_capacity.get(room, 0), 200)

    def test_small_class_gets_any_room(self):
        """Test that small classes can use any available room."""
        # Simulate a course with 30 students
        candidates = room_candidates(lab=False, prefix="C1", min_capacity=30)
        self.assertIsInstance(candidates, list)
        # Should return multiple rooms
        self.assertGreater(len(candidates), 0)
        # All rooms should have capacity >= 30
        for room in candidates:
            self.assertGreaterEqual(room_capacity.get(room, 0), 30)


if __name__ == "__main__":
    unittest.main()
