"""Compatibility shim providing a small facultyTT API used by tests."""
import random
from timetable_automation import get_free_blocks, allocate_session, split_by_half

# Expose a `random` attribute so tests can patch `facultyTT.random.choice`.
__all__ = ["get_free_blocks", "allocate_session", "split_by_half", "random"]

# re-export random module for patching
random = random
