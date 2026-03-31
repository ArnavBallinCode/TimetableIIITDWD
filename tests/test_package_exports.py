from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_timetable_automation_package_exports():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from timetable_automation import "
                "parse_time, slot_duration_from_bounds, parse_ltp, safe_str, "
                "get_free_blocks, allocate_session, merge_and_style_cells, "
                "generate_timetable, split_by_half"
            ),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
