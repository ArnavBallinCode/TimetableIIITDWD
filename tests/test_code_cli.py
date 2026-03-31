import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CODE_PATH = REPO_ROOT / "code.py"


@pytest.fixture
def code_module():
    spec = importlib.util.spec_from_file_location("exam_code_under_test", CODE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_resolve_date_range_uses_cli_args(code_module):
    start, end = code_module.resolve_date_range(["--start", "01-11-2025", "--end", "30-11-2025"])
    assert str(start) == "2025-11-01"
    assert str(end) == "2025-11-30"


def test_resolve_date_range_falls_back_to_input(code_module, monkeypatch):
    answers = iter(["01-11-2025", "05-11-2025"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    start, end = code_module.resolve_date_range([])
    assert str(start) == "2025-11-01"
    assert str(end) == "2025-11-05"


def test_resolve_date_range_rejects_end_before_start(code_module):
    with pytest.raises(SystemExit):
        code_module.resolve_date_range(["--start", "30-11-2025", "--end", "01-11-2025"])
