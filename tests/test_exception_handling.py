from pathlib import Path
import ast

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
    tree = ast.parse(source, filename=relative_path)
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        assert node.type is not None, f"Found bare except in {relative_path}"
        if isinstance(node.type, ast.Name):
            assert node.type.id != "Exception", f"Found broad except Exception in {relative_path}"
