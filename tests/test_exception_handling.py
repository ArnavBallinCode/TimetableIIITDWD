from pathlib import Path
import re

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.whitebox
@pytest.mark.regression
@pytest.mark.parametrize(
    "relative_path",
    [
        "code.py",
        "timetable_automation/faculty.py",
    ],
)
def test_target_files_do_not_use_bare_or_broad_exception_handlers(relative_path):
    source = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
    assert not re.search(r"except\s*:", source), f"Found bare except in {relative_path}"
    assert not re.search(
        r"except\s+Exception\s*:", source
    ), f"Found broad except Exception in {relative_path}"
