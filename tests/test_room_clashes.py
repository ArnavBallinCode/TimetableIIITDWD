import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "check_room_clashes.py"


def _load_checker_module():
    spec = importlib.util.spec_from_file_location("room_clash_checker", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_classify_allows_same_course_id_overlap_for_configured_shared_room():
    checker = _load_checker_module()
    rules = checker.load_room_rules()
    entries = [
        {
            "day": "Monday",
            "slot": "10:45-11:45",
            "room": "C004",
            "is_placeholder": False,
            "course_code": "EC161",
            "course_id": "EC161",
            "sheet": "A",
            "block": "First Half",
            "text": "EC161 (C004)",
        },
        {
            "day": "Monday",
            "slot": "10:45-11:45",
            "room": "C004",
            "is_placeholder": False,
            "course_code": "ec-161",
            "course_id": "EC161",
            "sheet": "B",
            "block": "First Half",
            "text": "ec-161 (C004)",
        },
    ]

    real, allowed, placeholders = checker.classify(entries, rules)
    assert not real
    assert len(allowed) == 1
    assert not placeholders


def test_classify_flags_cross_course_overlap_for_configured_shared_room():
    checker = _load_checker_module()
    rules = checker.load_room_rules()
    entries = [
        {
            "day": "Tuesday",
            "slot": "14:30-15:30",
            "room": "C004",
            "is_placeholder": False,
            "course_code": "MA162",
            "course_id": "MA162",
            "sheet": "A",
            "block": "First Half",
            "text": "MA162 (C004)",
        },
        {
            "day": "Tuesday",
            "slot": "14:30-15:30",
            "room": "C004",
            "is_placeholder": False,
            "course_code": "MA163",
            "course_id": "MA163",
            "sheet": "B",
            "block": "First Half",
            "text": "MA163 (C004)",
        },
    ]

    real, allowed, placeholders = checker.classify(entries, rules)
    assert len(real) == 1
    assert not allowed
    assert not placeholders
