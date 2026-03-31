from pathlib import Path
import subprocess
import sys
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
TIMETABLE_SCRIPT = REPO_ROOT / "timetable_automation" / "timetable.py"
BALANCED_OUTPUT = REPO_ROOT / "Balanced_Timetable_latest.xlsx"


def _run(cmd, timeout=300):
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


@pytest.mark.integration
def test_jan_apr_data_files_are_present():
    expected = {
        "coursesCSEA-II.csv",
        "coursesCSEA-IV.csv",
        "coursesCSEA-VI.csv",
        "coursesCSEB-II.csv",
        "coursesCSEB-IV.csv",
        "coursesCSEB-VI.csv",
        "coursesDSAI-II.csv",
        "coursesDSAI-IV.csv",
        "coursesDSAI-VI.csv",
        "coursesECE-II.csv",
        "coursesECE-IV.csv",
        "coursesECE-VI.csv",
        "Faculty.csv",
        "rooms.csv",
        "time_slots.json",
    }
    available = {p.name for p in DATA_DIR.iterdir() if p.is_file()}
    missing = sorted(expected - available)
    assert not missing, f"Missing required Jan-Apr data files: {missing}"


@pytest.mark.integration
@pytest.mark.regression
def test_timetable_generation_smoke():
    if BALANCED_OUTPUT.exists():
        BALANCED_OUTPUT.unlink()

    result = _run([sys.executable, str(TIMETABLE_SCRIPT)], timeout=360)
    assert result.returncode == 0, (
        "timetable.py failed\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
    assert BALANCED_OUTPUT.exists(), "Balanced_Timetable_latest.xlsx was not generated"