import datetime as dt
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "timetable_generator.py"
WRAPPER = REPO_ROOT / "code.py"


@pytest.mark.whitebox
def test_parse_start_date_and_weekdays():
    sys.path.insert(0, str(REPO_ROOT))
    import timetable_generator as tg

    parsed = tg.parse_start_date("2026-04-03")
    assert parsed == dt.date(2026, 4, 3)

    dates = tg.generate_exam_dates(3, dt.date(2026, 4, 3))  # Friday start
    assert [d.strftime("%Y-%m-%d") for d in dates] == ["2026-04-03", "2026-04-06", "2026-04-07"]


@pytest.mark.integration
def test_timetable_generator_cli_start_date_and_wrapper(tmp_path):
    input_file = tmp_path / "CourseCode&Name.csv"
    output_main = tmp_path / "main_output.xlsx"
    output_wrapper = tmp_path / "wrapper_output.xlsx"
    input_file.write_text(
        "BATCH 1ST CSE:\n"
        "CS101, Intro to CS\n"
        "CS102, Data Structures\n"
        "\n",
        encoding="utf-8",
    )

    run_main = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input-file",
            str(input_file),
            "--output-file",
            str(output_main),
            "--start-date",
            "2026-04-03",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert run_main.returncode == 0, run_main.stderr
    assert output_main.exists()

    run_wrapper = subprocess.run(
        [
            sys.executable,
            str(WRAPPER),
            "--input-file",
            str(input_file),
            "--output-file",
            str(output_wrapper),
            "--start-date",
            "2026-04-03",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert run_wrapper.returncode == 0, run_wrapper.stderr
    assert output_wrapper.exists()


@pytest.mark.integration
def test_timetable_generator_warns_for_past_start_date(tmp_path):
    input_file = tmp_path / "CourseCode&Name.csv"
    output_file = tmp_path / "past_output.xlsx"
    input_file.write_text(
        "BATCH 1ST CSE:\n"
        "CS101, Intro to CS\n"
        "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input-file",
            str(input_file),
            "--output-file",
            str(output_file),
            "--start-date",
            "2020-01-06",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "is in the past" in result.stdout
    assert output_file.exists()
