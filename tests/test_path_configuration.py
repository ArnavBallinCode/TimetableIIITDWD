from pathlib import Path
import subprocess
import sys
import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CODE_SCRIPT = REPO_ROOT / "code.py"
TIMETABLE_SCRIPT = REPO_ROOT / "timetable_automation" / "timetable.py"
FACULTY_SCRIPT = REPO_ROOT / "timetable_automation" / "faculty.py"


def _run(cmd, cwd=None, timeout=180):
    return subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        text=True,
        capture_output=True,
        timeout=timeout,
    )


@pytest.mark.integration
def test_code_py_accepts_explicit_paths_and_generates_output(tmp_path):
    output_file = tmp_path / "exam.xlsx"
    result = _run(
        [
            sys.executable,
            str(CODE_SCRIPT),
            "--course-file",
            str(REPO_ROOT / "FINAL_EXCEL.csv"),
            "--room-file",
            str(REPO_ROOT / "rooms.csv"),
            "--output-file",
            str(output_file),
            "--start-date",
            "01-04-2026",
            "--end-date",
            "10-04-2026",
        ]
    )

    assert result.returncode == 0, (
        "code.py failed with explicit file path arguments\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
    assert output_file.exists(), "Expected exam timetable workbook to be generated at --output-file"


@pytest.mark.integration
def test_code_py_reports_missing_course_file_clearly(tmp_path):
    missing_course = tmp_path / "missing_course.csv"
    result = _run(
        [
            sys.executable,
            str(CODE_SCRIPT),
            "--course-file",
            str(missing_course),
            "--room-file",
            str(REPO_ROOT / "rooms.csv"),
            "--output-file",
            str(tmp_path / "unused.xlsx"),
            "--start-date",
            "01-04-2026",
            "--end-date",
            "10-04-2026",
        ]
    )

    assert result.returncode != 0
    assert "Missing required course_file:" in result.stdout
    assert str(missing_course.resolve()) in result.stdout


@pytest.mark.integration
def test_timetable_py_reports_missing_data_dir_paths(tmp_path):
    missing_dir = tmp_path / "missing_data"
    result = _run(
        [
            sys.executable,
            str(TIMETABLE_SCRIPT),
            "--data-dir",
            str(missing_dir),
            "--output",
            str(tmp_path / "balanced.xlsx"),
        ]
    )

    assert result.returncode != 0
    combined = f"{result.stdout}\n{result.stderr}"
    assert "Missing required time slots file" in combined or "None of the required data files were found" in combined
    assert str(missing_dir.resolve()) in combined


@pytest.mark.integration
def test_faculty_py_reports_missing_balanced_input(tmp_path):
    missing_balanced = tmp_path / "missing_balanced.xlsx"
    result = _run(
        [
            sys.executable,
            str(FACULTY_SCRIPT),
            "--data-dir",
            str(REPO_ROOT / "data"),
            "--balanced-input",
            str(missing_balanced),
            "--output",
            str(tmp_path / "faculty.xlsx"),
        ]
    )

    assert result.returncode != 0
    assert "Missing required balanced timetable workbook:" in result.stdout
    assert str(missing_balanced.resolve()) in result.stdout
