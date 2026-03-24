# Known Bugs & Failure Cases

This document catalogues **10 confirmed bugs and failure cases** found in the
TimetableIIITDWD repository. Each entry follows the default
[bug report template](./../.github/ISSUE_TEMPLATE/bug_report.md).

To open all of these as GitHub Issues automatically, run:

```bash
# Install no extra dependencies – uses Python's standard library only
python docs/create_github_issues.py --token <YOUR_GITHUB_PAT>
```

A GitHub Personal Access Token (PAT) with the **`repo`** scope is required.
Generate one at <https://github.com/settings/tokens>.

---

## Bug 1 – Tests fail to import: functions missing from `timetable_automation` package `__init__`

**Describe the bug**

`tests/test_timetable.py` (line 5) and `tests/test_faculty.py` (line 6) import
symbols directly from the `timetable_automation` package:

```python
from timetable_automation import parse_time, slot_duration_from_bounds, parse_ltp, \
    safe_str, get_free_blocks, allocate_session, merge_and_style_cells, \
    generate_timetable, split_by_half
```

However `timetable_automation/_init_.py` is completely empty, so none of these
symbols are exported. Running `pytest tests/` fails immediately with an
`ImportError` before any test logic executes.

**Expected behavior**

Running `pytest tests/` should execute all tests without import errors.

**Steps to Reproduce**

1. Clone the repository.
2. Install dependencies (`pip install pandas openpyxl`).
3. Run `pytest tests/`.
4. Observe `ImportError: cannot import name 'parse_time' from 'timetable_automation'`.

**Additional context**

The functions exist in `timetable_automation/timetable.py` and
`timetable_automation/draft.py` but are never re-exported from `__init__.py`.
Fix: populate `timetable_automation/__init__.py` with the required imports, or
update the test files to import from the specific submodules.

---

## Bug 2 – No `requirements.txt` / `setup.py` – pip dependencies undocumented, scripts fail on fresh clone

**Describe the bug**

The repository has no `requirements.txt`, `setup.py`, or `pyproject.toml`.
Every Python script imports third-party libraries (`pandas`, `openpyxl`) that
are not pinned anywhere.

**Expected behavior**

A user should be able to run `pip install -r requirements.txt` to install all
dependencies and then immediately use any script.

**Steps to Reproduce**

1. Clone the repository on a fresh Python environment.
2. Run `python code.py`.
3. Observe `ModuleNotFoundError: No module named 'pandas'`.

**Additional context**

At minimum a `requirements.txt` with the following content is needed:

```
pandas>=1.3
openpyxl>=3.0
```

A `pyproject.toml` or `setup.cfg` would be even better for proper packaging.

---

## Bug 3 – Hardcoded file paths throughout codebase make scripts non-portable

**Describe the bug**

Critical input/output file paths are hardcoded in multiple scripts:

```python
# code.py (lines 30-32)
COURSE_FILE = "FINAL_EXCEL.csv"
ROOM_FILE = "rooms.csv"
OUTPUT_FILE = "Exam_Timetable_Final.xlsx"

# timetable_automation/faculty.py (line 104)
wb_in = openpyxl.load_workbook("Balanced_Timetable_latest.xlsx")

# timetable_automation/timetable.py (lines 51-64)
coursesAI = pd.read_csv("data/coursesCSEA-I.csv")...
# ... 10+ more hardcoded paths
```

**Expected behavior**

Scripts should accept file paths via command-line arguments or a configuration
file, and fail with a clear error message if required files are missing.

**Steps to Reproduce**

1. Copy `code.py` to a different working directory.
2. Run `python code.py`.
3. Observe a `FileNotFoundError` with no indication of which file is missing or
   where it should be placed.

**Additional context**

Suggested fix: use `argparse` or a JSON/YAML config file to specify
input/output paths. This also enables CI/CD automation.

---

## Bug 4 – Bare `except:` clauses silently swallow errors and hide bugs

**Describe the bug**

Multiple locations use bare `except:` (or overly broad `except Exception:`)
with silent recovery:

```python
# code.py line 43
try:
    ...
except:          # catches SystemExit, KeyboardInterrupt, etc.
    return None

# code.py line 361
except:
    pass

# timetable_automation/faculty.py lines 45, 67
except:
    continue  # silently skips a CSV file on any error
except:
    P = 0.0   # silently defaults enrollment to 0
```

**Expected behavior**

Exceptions should be caught by the narrowest applicable type
(e.g., `except (ValueError, TypeError):`), logged with a meaningful message,
and re-raised or handled explicitly.

**Steps to Reproduce**

1. Corrupt a CSV file (e.g., introduce invalid bytes).
2. Run `python timetable_automation/faculty.py`.
3. Observe that the script completes with no error — the bad file is silently
   skipped, producing an incorrect timetable.

**Additional context**

Bare `except:` also catches `KeyboardInterrupt` and `SystemExit`, making it
impossible to stop the script normally. This is a Python anti-pattern (PEP 8).

---

## Bug 5 – `code.py` requires interactive terminal input – cannot run in CI/CD or batch mode

**Describe the bug**

`code.py` calls `input()` at module level (lines 14–22) to ask for exam
start/end dates before any other code runs:

```python
START_DATE = get_user_date("Enter exam START date")
END_DATE   = get_user_date("Enter exam END date")
```

This makes the script impossible to automate. There is also no validation that
`END_DATE >= START_DATE` until after both values are collected.

**Expected behavior**

Dates should be passable as command-line arguments (e.g.,
`--start 01-11-2025 --end 30-11-2025`) with the interactive prompt as a
fallback.

**Steps to Reproduce**

1. Try to run `python code.py < /dev/null` (non-interactive).
2. Observe `EOFError` or the script hanging indefinitely.

**Additional context**

Suggested fix: use `argparse` with optional `--start` / `--end` flags; fall
back to `input()` only when those flags are absent.

---

## Bug 6 – `timetable_generator.py` uses hardcoded start date – stale schedule every semester

**Describe the bug**

`timetable_generator.py` (line 9) has the exam start date hardcoded:

```python
START_DATE = dt.date(2025, 11, 20)
```

Every new semester the script must be manually edited to update this date.
There is no warning or error if the date is in the past.

**Expected behavior**

The start date should be passed as a command-line argument or read from a
configuration file so the script can be reused without code changes.

**Steps to Reproduce**

1. Run `python timetable_generator.py` without editing the file.
2. Observe that the generated timetable uses dates from November 2025,
   regardless of the actual current date.

**Additional context**

Both `code.py` and `timetable_generator.py` solve the same problem with
different approaches, creating confusion about which script to use.
They should be consolidated into a single script.

---

## Bug 7 – No validation of generated timetable – room/faculty conflicts can go undetected

**Describe the bug**

After the scheduling algorithm runs, neither `code.py`, `timetable_generator.py`,
nor `timetable_automation/timetable.py` validates the output for constraint
violations. The only signal of a problem is the string `"(PARTIAL)"` appended
to a room cell in the Excel file (e.g., `code.py` line 245).

**Expected behavior**

Before saving, the script should assert:
- No room is double-booked in the same slot.
- No faculty member teaches two sessions simultaneously.
- Every required course has a complete room assignment (no `PARTIAL` slots).

If any constraint is violated, the script should print a clear error and
optionally refuse to save the file.

**Steps to Reproduce**

1. Reduce room capacity values to force a shortage.
2. Run `python code.py`.
3. Open the generated `Exam_Timetable_Final.xlsx`.
4. Observe `(PARTIAL)` entries with no error printed to the terminal.

**Additional context**

The existing `check_room_clashes.py` script performs post-hoc clash detection
on an Excel file but is never called automatically. It should be integrated as
a mandatory validation step before the output file is written.

---

## Bug 8 – Missing file existence check before `openpyxl.load_workbook` – cryptic crash

**Describe the bug**

`timetable_automation/faculty.py` (line 104) opens an Excel workbook with no
prior existence check:

```python
wb_in = openpyxl.load_workbook("Balanced_Timetable_latest.xlsx")
```

If the file is missing, the user sees:

```
FileNotFoundError: [Errno 2] No such file or directory: 'Balanced_Timetable_latest.xlsx'
```

with no guidance on how to generate or obtain the file.

**Expected behavior**

The script should check whether the file exists and, if not, print a helpful
message such as:

```
ERROR: 'Balanced_Timetable_latest.xlsx' not found.
Please run timetable_automation/timetable.py first to generate this file.
```

**Steps to Reproduce**

1. Delete or rename `Balanced_Timetable_latest.xlsx`.
2. Run `python timetable_automation/faculty.py`.
3. Observe the cryptic `FileNotFoundError` traceback.

**Additional context**

The same issue applies to every `pd.read_csv(...)` call in
`timetable_automation/timetable.py` (lines 51–73) – none of them check that
the CSV files exist before opening.

---

## Bug 9 – Room C004 is special-cased 47+ times in `timetable.py` – not configurable

**Describe the bug**

`timetable_automation/timetable.py` contains 47 references to the string
`"C004"`. The room is given unique scheduling rules (dedicated
`c004_occupancy` dict, special slot exclusions) that are baked directly into
the code:

```python
c004_occupancy = {d: {} for d in days}
excluded = ["07:30-09:00", "10:30-10:45", "13:15-14:00", "17:30-18:30"]
ABSOLUTELY_FORBIDDEN_SLOTS = {"07:30-09:00"}
```

**Expected behavior**

Special room rules should be defined in an external configuration file
(e.g., `rooms.csv` or a `room_rules.json`), not scattered as magic strings
throughout the scheduling engine.

**Steps to Reproduce**

1. Rename room C004 to a different room identifier in `rooms.csv`.
2. Run `python timetable_automation/timetable.py`.
3. Observe that the special rules are silently not applied to the renamed room,
   producing an incorrect schedule.

**Additional context**

The excluded time slots are also hardcoded. If the institute changes its daily
schedule, every hardcoded string must be found and updated manually.

---

## Bug 10 – Duplicate scheduling scripts – no single source of truth

**Describe the bug**

The repository contains four separate exam/timetable generation scripts with
overlapping functionality:

| Script | Lines | Notes |
|--------|-------|-------|
| `code.py` | 382 | Exam scheduler, interactive date input |
| `timetable_generator.py` | 183 | Exam scheduler, hardcoded date |
| `timetable_automation/timetable.py` | 1 175 | Seminar scheduler |
| `timetable_automation/draft.py` | ~900 | Variant of `timetable.py` |

Because the same logic is duplicated, a bug fix in one file is never
propagated to the others. For example, bare `except:` clauses and missing
input validation exist in all four files independently.

**Expected behavior**

Common scheduling logic (slot parsing, room allocation, Excel generation)
should live in a shared module (e.g., `timetable_automation/core.py`) and be
imported by thin entry-point scripts.

**Steps to Reproduce**

1. Fix a bug in `code.py` (e.g., add the missing `END_DATE >= START_DATE`
   check).
2. Notice that `timetable_generator.py` has the same bug and was not fixed.

**Additional context**

The presence of `draft.py` alongside `timetable.py` suggests the codebase has
grown organically without a clear refactoring step. `draft.py` should either
be removed or documented as to how it differs from `timetable.py`.
