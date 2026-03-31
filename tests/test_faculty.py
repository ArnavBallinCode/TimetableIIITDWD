from pathlib import Path
import subprocess
import sys
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
TIMETABLE_SCRIPT = REPO_ROOT / "timetable_automation" / "timetable.py"
FACULTY_SCRIPT = REPO_ROOT / "timetable_automation" / "faculty_timetable_from_balanced.py"
BALANCED_OUTPUT = REPO_ROOT / "Balanced_Timetable_latest.xlsx"
FACULTY_OUTPUT = REPO_ROOT / "Faculty_Timetable_from_Balanced.xlsx"


def _run(cmd, timeout=300):
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def _ensure_balanced_output():
    if BALANCED_OUTPUT.exists():
        return
    result = _run([sys.executable, str(TIMETABLE_SCRIPT)], timeout=360)
    assert result.returncode == 0, (
        "Failed to generate balanced timetable prerequisite\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


@pytest.mark.integration
@pytest.mark.regression
def test_faculty_timetable_generation_smoke():
    _ensure_balanced_output()
    if FACULTY_OUTPUT.exists():
        FACULTY_OUTPUT.unlink()

    result = _run(
        [
            sys.executable,
            str(FACULTY_SCRIPT),
            "--input",
            str(BALANCED_OUTPUT),
            "--faculty-csv",
            str(REPO_ROOT / "data" / "Faculty.csv"),
            "--slots-json",
            str(REPO_ROOT / "data" / "time_slots.json"),
            "--output",
            str(FACULTY_OUTPUT),
        ],
        timeout=360,
    )

    assert result.returncode == 0, (
        "faculty_timetable_from_balanced.py failed\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
    assert FACULTY_OUTPUT.exists(), "Faculty_Timetable_from_Balanced.xlsx was not generated"