# Exam Timetable Generator Walkthrough (Beginner-First)

File covered: `timetable_generator.py`

This document explains the script as if you are starting from zero.
If you do not know Python, CSV, Pandas, or Excel automation yet, that is okay.

## 0. What This Script Actually Does

In one sentence:

- It reads a custom text/CSV file of batches and courses, creates exam dates, assigns dates to courses using simple rules, and writes a formatted Excel timetable.

Think of it as a small factory:

```text
Raw Course File -> Parse -> Schedule -> Build Table -> Write Excel
```

No advanced AI. No optimization engine. Mostly rule-based assignment.

## 1. Before You Run Anything (Absolute Basics)

### 1.1 Files needed

| Item | Why needed | Example |
|---|---|---|
| `timetable_generator.py` | Main program | This script |
| `CourseCode&Name.csv` | Input data | Batch + course list |
| Python + packages | Runtime | `pandas`, `openpyxl` |

### 1.2 What is a CSV?

- CSV means **Comma Separated Values**.
- Usually one line is one row.
- But this script uses a **custom block format**, not a normal clean table.

### 1.3 What is generated?

- `Exam_Timetable.xlsx`
  - `Master_Timetable` sheet (all batches together)
  - One sheet per batch

## 2. Input Format (Very Important)

This script expects a custom structure like this:

```text
BATCH CSE 1ST:
CS101,Data Structures
CS102,Discrete Mathematics
ELECTIVE-AI,Introduction to AI

BATCH CSE 3RD:
CS201,DBMS
CS202,Operating Systems
```

Rules:

1. A batch starts with `BATCH ...:`
2. Course line format is `CourseCode,CourseName`
3. Blank line means “batch ended”
4. If file ends suddenly, script still saves last batch

If you break these rules, parser may silently skip lines or produce bad output.

## 3. High-Level Pipeline

This is the exact runtime flow from top to bottom:

```text
Step A: Load constants (input path, start date, output path)
Step B: Parse custom file into Python dictionary
Step C: Generate weekday-only dates
Step D: For each batch, schedule normal courses first, electives later
Step E: Convert records -> DataFrame
Step F: Create Excel workbook (master + batch sheets)
Step G: Save Exam_Timetable.xlsx
```

No special rendering required: this chart is plain text.

## 4. Data Structures Used (What lives in memory)

| Variable | Type | Meaning |
|---|---|---|
| `courses` | `dict[str, list[tuple[str, str]]]` | Batch name -> list of `(code, name)` |
| `dates` | `list[date]` | Candidate exam dates (weekdays only) |
| `records` | `list[dict]` | Flat schedule rows before DataFrame |
| `df` | `pandas.DataFrame` | Sorted tabular data for Excel writing |

## 5. Detailed Execution (Chronological)

### Phase 1: Custom Parsing Logic (State-machine style)

Core parser:

```python
courses = {}
current_batch = None
current_courses = []

with open(FILE_PATH, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if line.startswith("BATCH"):
            if current_batch and current_courses:
                courses[current_batch] = current_courses
            current_batch = line.replace("BATCH", "").replace(":", "").strip()
            current_courses = []

        elif line and "," in line:
            code, name = [x.strip() for x in line.split(",", 1)]
            current_courses.append((code, name))

        elif not line:
            if current_batch and current_courses:
                courses[current_batch] = current_courses
                current_batch, current_courses = None, []

if current_batch and current_courses:
    courses[current_batch] = current_courses
```

What this means in simple words:

- `current_batch` = “which batch I am currently reading”
- `current_courses` = “courses collected for that batch so far”
- On new `BATCH` line:
  - push old batch to dictionary
  - start fresh list for new batch
- On `code,name` line:
  - add tuple `(code, name)`
- On blank line:
  - batch complete -> save and reset
- End of file safety flush:
  - saves last batch if file has no blank final line

Why `split(",", 1)` matters:

- If course title has commas, only first comma splits code and title.

Trace example:

| Read line | `current_batch` after line | `current_courses` size | `courses` size |
|---|---|---:|---:|
| `BATCH CSE 1ST:` | `CSE 1ST` | 0 | 0 |
| `CS101,Data Structures` | `CSE 1ST` | 1 | 0 |
| blank line | `None` | 0 | 1 |

### Phase 2: Date Generation

Function:

```python
def generate_exam_dates(num_days, start_date):
    dates = []
    d = start_date
    while len(dates) < num_days:
        if d.weekday() < 5:
            dates.append(d)
        d += dt.timedelta(days=1)
    return dates
```

Beginner explanation:

- `weekday()` returns number for day of week
  - Monday = 0 ... Sunday = 6
- Condition `< 5` means Monday to Friday only
- Saturday and Sunday are skipped
- Loop continues until enough working days are collected

### Phase 3: Core Scheduling Engine

Main loop:

```python
for batch_name, clist in courses.items():
```

This means: process one batch at a time.

#### 3.1 Shift logic

```python
def get_shift(batch_name: str):
    b = batch_name.upper()
    if "1ST" in b or "3RD" in b:
        return "Morning (10:00 AM – 11:30 AM)"
    else:
        return "Evening (03:00 PM – 04:30 PM)"
```

Simple interpretation:

- 1st/3rd semester batches get morning shift
- others get evening shift

#### 3.2 Split normal vs elective courses

```python
normal_courses = [(code, name) for code, name in clist if "ELECTIVE" not in code.upper()]
elective_courses = [(code, name) for code, name in clist if "ELECTIVE" in code.upper()]
```

Why split?

- Normal courses: one-by-one sequential dates
- Electives: grouped on same date for that batch

#### 3.3 `date_idx` and `used_dates` (most important)

Initialization per batch:

```python
date_idx = 0
used_dates = set()
```

- `date_idx` points into `dates` list
- `used_dates` remembers dates already assigned in this batch

Normal scheduling:

```python
for code, name in normal_courses:
    while date_idx < len(dates) and dates[date_idx].weekday() >= 5:
        date_idx += 1

    exam_date = dates[date_idx]
    used_dates.add(exam_date)
    # append record
    date_idx += 1
```

Meaning:

- pick next available date
- assign it to this normal course
- move pointer forward

Elective grouping:

```python
if elective_courses:
    while date_idx < len(dates) and (dates[date_idx] in used_dates or dates[date_idx].weekday() >= 5):
        date_idx += 1

    elective_date = dates[date_idx]

    for code, name in elective_courses:
        # all electives get elective_date
```

Meaning:

- find a date not already used by normal courses in same batch
- assign **that one date** to all electives of that batch

Mini simulation:

Assume `dates = [Mon, Tue, Wed, Thu, Fri]`

- Batch has normal courses: N1, N2, N3
- electives: E1, E2

Result:

- N1 -> Mon
- N2 -> Tue
- N3 -> Wed
- E1 -> Thu
- E2 -> Thu

That is the grouped elective behavior.

### Phase 4: DataFrame Transformation

Each scheduled course adds one dict to `records`:

```python
records.append({
    "Batch": batch_name,
    "Date": exam_date,
    "Day": exam_date.strftime("%A"),
    "Shift": SHIFT,
    "CourseCode": code,
    "CourseName": name
})
```

Then:

```python
df = pd.DataFrame(records)
df = df.sort_values(by=["Batch", "Date"]).reset_index(drop=True)
df["Date"] = pd.to_datetime(df["Date"])
df["Date_str"] = df["Date"].dt.strftime("%d-%b-%Y")
```

Why DataFrame here?

- easy sorting
- easy filtering per batch
- easy iteration for Excel output

### Phase 5: Excel Generation with `openpyxl`

Workbook steps:

1. Create workbook
2. Rename active sheet to `Master_Timetable`
3. Write headers
4. Write all rows from DataFrame
5. For each batch, make one dedicated sheet
6. Apply styling (bold, alignment, borders)
7. Auto-adjust column widths
8. Save output file

Per-batch writer pattern:

```python
for batch in df["Batch"].unique():
    sub_df = df[df["Batch"] == batch].sort_values(by="Date")
    ws = wb.create_sheet(title=batch[:30])
    # write title, headers, data
    # apply borders
    # set width based on longest text
```

Why `batch[:30]`?

- Excel sheet name limit is 31 chars.
- Truncation prevents runtime errors for long batch labels.

## 6. End-to-End Flow (No special renderer needed)

```text
Input file lines
  -> parser state variables update
  -> courses dictionary formed
  -> weekday date pool created
  -> per-batch scheduler assigns dates
  -> records list built
  -> records converted to DataFrame
  -> master sheet + batch sheets written
  -> formatted Excel file saved
```

## 7. Common Failure Points (Very Practical)

| Problem | Why it happens | What you see |
|---|---|---|
| Wrong input format | Missing `BATCH` markers or commas | Missing courses/batches in output |
| Not enough generated days | `max_exams + 5` heuristic too small | Index error near date assignment |
| Shift rule mismatch | Batch naming doesn't contain expected tokens | Unexpected morning/evening mapping |
| Elective naming mismatch | No `ELECTIVE` substring in code | Elective grouped logic not applied |

## 8. If You Want To Improve This Script Next

Suggested upgrades in order:

1. Add input validation with clear error messages.
2. Add safe guard for `date_idx >= len(dates)`.
3. Move shift rules and elective detection into configuration.
4. Replace custom parser with structured schema (if data source can be changed).
5. Add tests for parser and scheduler edge cases.

## 9. Final Beginner Summary

If you remember only five things, remember these:

1. The file is parsed as text blocks, not a normal table.
2. Dates are weekdays only.
3. Normal courses get sequential days.
4. Electives for a batch are grouped on one day.
5. Everything is exported to one Excel with master + per-batch sheets.