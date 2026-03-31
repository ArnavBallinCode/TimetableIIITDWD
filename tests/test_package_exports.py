import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_timetable_automation_package_exports():
    from timetable_automation import (
        allocate_session,
        generate_timetable,
        get_free_blocks,
        merge_and_style_cells,
        parse_ltp,
        parse_time,
        safe_str,
        slot_duration_from_bounds,
        split_by_half,
    )

    assert callable(parse_time)
    assert callable(slot_duration_from_bounds)
    assert callable(parse_ltp)
    assert callable(safe_str)
    assert callable(get_free_blocks)
    assert callable(allocate_session)
    assert callable(merge_and_style_cells)
    assert callable(generate_timetable)
    assert callable(split_by_half)
