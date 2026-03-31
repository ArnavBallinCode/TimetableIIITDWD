from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_FILE = REPO_ROOT / "requirements.txt"


def test_requirements_txt_includes_runtime_dependencies():
    assert REQUIREMENTS_FILE.exists(), "requirements.txt is missing"

    lines = [
        line.strip()
        for line in REQUIREMENTS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    assert "pandas>=1.3" in lines
    assert "openpyxl>=3.0" in lines
