#!/usr/bin/env python3
"""
Script to create GitHub issues for the TimetableIIITDWD repository.

Usage:
    python docs/create_github_issues.py --token <your_github_pat>

Requires a GitHub Personal Access Token (PAT) with `repo` scope
(which includes issues:write permission).

Get a token at: https://github.com/settings/tokens
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

REPO = "ArnavBallinCode/TimetableIIITDWD"
API_BASE = "https://api.github.com"

# ---------------------------------------------------------------------------
# Issue definitions – each entry matches the default bug_report.md template:
#
#   **Describe the bug**
#   **Expected behavior**
#   **Steps to Reproduce**
#   **Additional context**
# ---------------------------------------------------------------------------
ISSUES = [
    {
        "title": "Tests fail to import: functions missing from timetable_automation package __init__",
        "body": (
            "**Describe the bug**\n"
            "`tests/test_timetable.py` (line 5) and `tests/test_faculty.py` (line 6) import "
            "symbols directly from the `timetable_automation` package:\n\n"
            "```python\n"
            "from timetable_automation import parse_time, slot_duration_from_bounds, parse_ltp, "
            "safe_str, get_free_blocks, allocate_session, merge_and_style_cells, "
            "generate_timetable, split_by_half\n"
            "```\n\n"
            "However `timetable_automation/_init_.py` is completely empty, so none of these "
            "symbols are exported. Running `pytest tests/` fails immediately with an "
            "`ImportError` before any test logic executes.\n\n"
            "**Expected behavior**\n"
            "Running `pytest tests/` should execute all tests without import errors.\n\n"
            "**Steps to Reproduce**\n"
            "1. Clone the repository.\n"
            "2. Install dependencies (`pip install pandas openpyxl`).\n"
            "3. Run `pytest tests/`.\n"
            "4. Observe `ImportError: cannot import name 'parse_time' from 'timetable_automation'`.\n\n"
            "**Additional context**\n"
            "The functions exist in `timetable_automation/timetable.py` and "
            "`timetable_automation/draft.py` but are never re-exported from `__init__.py`. "
            "Fix: populate `timetable_automation/__init__.py` with the required imports, "
            "or update the test files to import from the specific submodules."
        ),
    },
    {
        "title": "No requirements.txt / setup.py – pip dependencies undocumented, scripts fail on fresh clone",
        "body": (
            "**Describe the bug**\n"
            "The repository has no `requirements.txt`, `setup.py`, or `pyproject.toml`. "
            "Every Python script (`code.py`, `timetable_generator.py`, "
            "`timetable_automation/timetable.py`, etc.) imports third-party libraries "
            "(`pandas`, `openpyxl`) that are not pinned anywhere.\n\n"
            "**Expected behavior**\n"
            "A user should be able to run `pip install -r requirements.txt` to install "
            "all dependencies and then immediately use any script.\n\n"
            "**Steps to Reproduce**\n"
            "1. Clone the repository on a fresh Python environment.\n"
            "2. Run `python code.py`.\n"
            "3. Observe `ModuleNotFoundError: No module named 'pandas'`.\n\n"
            "**Additional context**\n"
            "At minimum a `requirements.txt` with the following content is needed:\n"
            "```\n"
            "pandas>=1.3\n"
            "openpyxl>=3.0\n"
            "```\n"
            "A `pyproject.toml` or `setup.cfg` would be even better for proper packaging."
        ),
    },
    {
        "title": "Hardcoded file paths throughout codebase make scripts non-portable",
        "body": (
            "**Describe the bug**\n"
            "Critical input/output file paths are hardcoded in multiple scripts:\n\n"
            "```python\n"
            "# code.py (lines 30-32)\n"
            "COURSE_FILE = \"FINAL_EXCEL.csv\"\n"
            "ROOM_FILE = \"rooms.csv\"\n"
            "OUTPUT_FILE = \"Exam_Timetable_Final.xlsx\"\n\n"
            "# timetable_automation/faculty.py (line 104)\n"
            "wb_in = openpyxl.load_workbook(\"Balanced_Timetable_latest.xlsx\")\n\n"
            "# timetable_automation/timetable.py (lines 51-64)\n"
            "coursesAI = pd.read_csv(\"data/coursesCSEA-I.csv\")...\n"
            "# ... 10+ more hardcoded paths\n"
            "```\n\n"
            "**Expected behavior**\n"
            "Scripts should accept file paths via command-line arguments or a configuration "
            "file, and fail with a clear error message if required files are missing.\n\n"
            "**Steps to Reproduce**\n"
            "1. Copy `code.py` to a different working directory.\n"
            "2. Run `python code.py`.\n"
            "3. Observe a `FileNotFoundError` with no indication of which file is missing "
            "or where it should be placed.\n\n"
            "**Additional context**\n"
            "Suggested fix: use `argparse` or a JSON/YAML config file to specify input/output "
            "paths. This also enables CI/CD automation."
        ),
    },
    {
        "title": "Bare `except:` clauses silently swallow errors and hide bugs",
        "body": (
            "**Describe the bug**\n"
            "Multiple locations use bare `except:` (or overly broad `except Exception:`) "
            "with silent recovery:\n\n"
            "```python\n"
            "# code.py line 43\n"
            "try:\n"
            "    ...\n"
            "except:          # catches SystemExit, KeyboardInterrupt, etc.\n"
            "    return None\n\n"
            "# code.py line 361\n"
            "except:\n"
            "    pass\n\n"
            "# timetable_automation/faculty.py lines 45, 67\n"
            "except:\n"
            "    continue  # silently skips a CSV file on any error\n"
            "except:\n"
            "    P = 0.0   # silently defaults enrollment to 0\n"
            "```\n\n"
            "**Expected behavior**\n"
            "Exceptions should be caught by the narrowest applicable type "
            "(e.g., `except (ValueError, TypeError):`), logged with a meaningful message, "
            "and re-raised or handled explicitly.\n\n"
            "**Steps to Reproduce**\n"
            "1. Corrupt a CSV file (e.g., introduce invalid bytes).\n"
            "2. Run `python timetable_automation/faculty.py`.\n"
            "3. Observe that the script completes with no error — the bad file is silently "
            "skipped, producing an incorrect timetable.\n\n"
            "**Additional context**\n"
            "Bare `except:` also catches `KeyboardInterrupt` and `SystemExit`, making it "
            "impossible to stop the script normally. This is a Python anti-pattern (PEP 8)."
        ),
    },
    {
        "title": "code.py requires interactive terminal input – cannot run in CI/CD or batch mode",
        "body": (
            "**Describe the bug**\n"
            "`code.py` calls `input()` at module level (lines 14–22) to ask for exam "
            "start/end dates before any other code runs:\n\n"
            "```python\n"
            "START_DATE = get_user_date(\"Enter exam START date\")\n"
            "END_DATE   = get_user_date(\"Enter exam END date\")\n"
            "```\n\n"
            "This makes the script impossible to automate. There is also no validation "
            "that `END_DATE >= START_DATE` until after both values are collected.\n\n"
            "**Expected behavior**\n"
            "Dates should be passable as command-line arguments (e.g., `--start 01-11-2025 "
            "--end 30-11-2025`) with the interactive prompt as a fallback.\n\n"
            "**Steps to Reproduce**\n"
            "1. Try to run `python code.py < /dev/null` (non-interactive).\n"
            "2. Observe `EOFError` or the script hanging indefinitely.\n\n"
            "**Additional context**\n"
            "Suggested fix: use `argparse` with optional `--start` / `--end` flags; "
            "fall back to `input()` only when those flags are absent."
        ),
    },
    {
        "title": "timetable_generator.py uses hardcoded start date – stale schedule every semester",
        "body": (
            "**Describe the bug**\n"
            "`timetable_generator.py` (line 9) has the exam start date hardcoded:\n\n"
            "```python\n"
            "START_DATE = dt.date(2025, 11, 20)\n"
            "```\n\n"
            "Every new semester the script must be manually edited to update this date. "
            "There is no warning or error if the date is in the past.\n\n"
            "**Expected behavior**\n"
            "The start date should be passed as a command-line argument or read from a "
            "configuration file so the script can be reused without code changes.\n\n"
            "**Steps to Reproduce**\n"
            "1. Run `python timetable_generator.py` without editing the file.\n"
            "2. Observe that the generated timetable uses dates from November 2025, "
            "regardless of the actual current date.\n\n"
            "**Additional context**\n"
            "Both `code.py` and `timetable_generator.py` solve the same problem with "
            "different approaches, creating confusion about which script to use. "
            "They should be consolidated into a single script."
        ),
    },
    {
        "title": "No validation of generated timetable – room/faculty conflicts can go undetected",
        "body": (
            "**Describe the bug**\n"
            "After the scheduling algorithm runs, neither `code.py`, `timetable_generator.py`, "
            "nor `timetable_automation/timetable.py` validates the output for constraint "
            "violations. The only signal of a problem is the string `\"(PARTIAL)\"` appended "
            "to a room cell in the Excel file (e.g., `code.py` line 245).\n\n"
            "**Expected behavior**\n"
            "Before saving, the script should assert:\n"
            "- No room is double-booked in the same slot.\n"
            "- No faculty member teaches two sessions simultaneously.\n"
            "- Every required course has a complete room assignment (no `PARTIAL` slots).\n"
            "If any constraint is violated, the script should print a clear error and "
            "optionally refuse to save the file.\n\n"
            "**Steps to Reproduce**\n"
            "1. Reduce room capacity values to force a shortage.\n"
            "2. Run `python code.py`.\n"
            "3. Open the generated `Exam_Timetable_Final.xlsx`.\n"
            "4. Observe `(PARTIAL)` entries with no error printed to the terminal.\n\n"
            "**Additional context**\n"
            "The existing `check_room_clashes.py` script performs post-hoc clash detection "
            "on an Excel file but is never called automatically. It should be integrated "
            "as a mandatory validation step before the output file is written."
        ),
    },
    {
        "title": "Missing file existence check before openpyxl.load_workbook – cryptic crash",
        "body": (
            "**Describe the bug**\n"
            "`timetable_automation/faculty.py` (line 104) opens an Excel workbook with no "
            "prior existence check:\n\n"
            "```python\n"
            "wb_in = openpyxl.load_workbook(\"Balanced_Timetable_latest.xlsx\")\n"
            "```\n\n"
            "If the file is missing, the user sees:\n"
            "```\n"
            "FileNotFoundError: [Errno 2] No such file or directory: "
            "'Balanced_Timetable_latest.xlsx'\n"
            "```\n"
            "with no guidance on how to generate or obtain the file.\n\n"
            "**Expected behavior**\n"
            "The script should check whether the file exists and, if not, print a helpful "
            "message such as:\n"
            "```\n"
            "ERROR: 'Balanced_Timetable_latest.xlsx' not found.\n"
            "Please run timetable_automation/timetable.py first to generate this file.\n"
            "```\n\n"
            "**Steps to Reproduce**\n"
            "1. Delete or rename `Balanced_Timetable_latest.xlsx`.\n"
            "2. Run `python timetable_automation/faculty.py`.\n"
            "3. Observe the cryptic `FileNotFoundError` traceback.\n\n"
            "**Additional context**\n"
            "The same issue applies to every `pd.read_csv(...)` call in "
            "`timetable_automation/timetable.py` (lines 51–73) – none of them check that "
            "the CSV files exist before opening."
        ),
    },
    {
        "title": "Room C004 is special-cased 47+ times in timetable.py – not configurable",
        "body": (
            "**Describe the bug**\n"
            "`timetable_automation/timetable.py` contains 47 references to the string "
            "`\"C004\"` (confirmed by `grep`). The room is given unique scheduling rules "
            "(dedicated `c004_occupancy` dict, special slot exclusions) that are baked "
            "directly into the code:\n\n"
            "```python\n"
            "c004_occupancy = {d: {} for d in days}\n"
            "excluded = [\"07:30-09:00\", \"10:30-10:45\", \"13:15-14:00\", \"17:30-18:30\"]\n"
            "ABSOLUTELY_FORBIDDEN_SLOTS = {\"07:30-09:00\"}\n"
            "```\n\n"
            "**Expected behavior**\n"
            "Special room rules should be defined in an external configuration file "
            "(e.g., `rooms.csv` or a `room_rules.json`), not scattered as magic strings "
            "throughout the scheduling engine.\n\n"
            "**Steps to Reproduce**\n"
            "1. Rename room C004 to a different room identifier in `rooms.csv`.\n"
            "2. Run `python timetable_automation/timetable.py`.\n"
            "3. Observe that the special rules are silently not applied to the renamed room, "
            "producing an incorrect schedule.\n\n"
            "**Additional context**\n"
            "The excluded time slots are also hardcoded. If the institute changes its daily "
            "schedule, every hardcoded string must be found and updated manually."
        ),
    },
    {
        "title": "Duplicate scheduling scripts (code.py, timetable_generator.py, timetable.py, draft.py) – no single source of truth",
        "body": (
            "**Describe the bug**\n"
            "The repository contains four separate exam/timetable generation scripts with "
            "overlapping functionality:\n\n"
            "| Script | Lines | Notes |\n"
            "|--------|-------|-------|\n"
            "| `code.py` | 382 | Exam scheduler, interactive date input |\n"
            "| `timetable_generator.py` | 183 | Exam scheduler, hardcoded date |\n"
            "| `timetable_automation/timetable.py` | 1 175 | Seminar scheduler |\n"
            "| `timetable_automation/draft.py` | ~900 | Variant of timetable.py |\n\n"
            "Because the same logic is duplicated, a bug fix in one file is never "
            "propagated to the others. For example, bare `except:` clauses and missing "
            "input validation exist in all four files independently.\n\n"
            "**Expected behavior**\n"
            "Common scheduling logic (slot parsing, room allocation, Excel generation) "
            "should live in a shared module (e.g., `timetable_automation/core.py`) and "
            "be imported by thin entry-point scripts.\n\n"
            "**Steps to Reproduce**\n"
            "1. Fix a bug in `code.py` (e.g., add missing `END_DATE >= START_DATE` check).\n"
            "2. Notice that `timetable_generator.py` has the same bug and was not fixed.\n\n"
            "**Additional context**\n"
            "The presence of `draft.py` alongside `timetable.py` suggests the codebase has "
            "grown organically without a clear refactoring step. "
            "`draft.py` should either be removed or documented as to how it differs from "
            "`timetable.py`."
        ),
    },
]


def create_issue(token: str, title: str, body: str) -> dict:
    """POST a new issue to the GitHub REST API and return the response JSON."""
    url = f"{API_BASE}/repos/{REPO}/issues"
    payload = json.dumps({"title": title, "body": body}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API error {exc.code} {exc.reason}: {body_text}"
        ) from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create pre-defined bug-report issues on the TimetableIIITDWD repository."
    )
    parser.add_argument(
        "--token",
        required=True,
        help=(
            "GitHub Personal Access Token with 'repo' scope. "
            "Generate one at https://github.com/settings/tokens"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the issues that would be created without actually creating them.",
    )
    args = parser.parse_args()

    print(f"Repository : {REPO}")
    print(f"Issues to create: {len(ISSUES)}")
    if args.dry_run:
        print("DRY-RUN mode – no API calls will be made.\n")

    created = []
    for i, issue in enumerate(ISSUES, start=1):
        print(f"\n[{i}/{len(ISSUES)}] {issue['title']}")
        if args.dry_run:
            print("  (skipped – dry run)")
            continue
        try:
            result = create_issue(args.token, issue["title"], issue["body"])
            url = result.get("html_url", "(unknown URL)")
            number = result.get("number", "?")
            print(f"  Created: #{number} – {url}")
            created.append(url)
        except RuntimeError as exc:
            print(f"  ERROR: {exc}", file=sys.stderr)

    if not args.dry_run:
        print(f"\n✓ Successfully created {len(created)}/{len(ISSUES)} issues.")
        for url in created:
            print(f"  {url}")


if __name__ == "__main__":
    main()
