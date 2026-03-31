# Timetable Generation Logic (Full Repository Walkthrough)

This document explains, in plain English, **how timetable generation works end-to-end** in this repository.

---

## 1) Big Picture: There Are Two Timetable Engines

The repository contains **two separate timetable workflows**:

1. **Class Timetable Engine (weekly academic timetable)**
   - Main file: `timetable_automation/timetable.py`
   - Output: `Balanced_Timetable_latest.xlsx`
   - This is the primary “teaching timetable” generator.

2. **Exam Timetable Engine (dated exam schedule)**
   - Main files: `timetable_generator.py` and `code.py`
   - Outputs: `Exam_Timetable.xlsx`, `Exam_Timetable_Final.xlsx`
   - This handles exam dates/slots, including morning/evening shift logic.

So if you are asking “how classes are arranged Monday–Friday by hour”, use `timetable_automation/timetable.py`. If you are asking “which exam happens on which calendar date and shift”, use `timetable_generator.py` / `code.py`.

---

## 2) Class Timetable Lifecycle (`timetable_automation/timetable.py`)

## Phase A — Configuration + Input Loading

At startup, the script loads:
- **Fixed weekdays** (`Monday` to `Friday`)
- **Excluded slots** (usually break-like windows)
- **Time slots** from JSON (`data/time_slots.json`)
- **Course CSVs** for each branch/semester group
- **Room inventory** (`data/rooms.csv`) split into classrooms vs labs

### Code callout
```python
# timetable_automation/timetable.py

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
excluded = ["07:30-09:00", "10:30-10:45", "13:15-14:00","17:30-18:30"]

with open("data/time_slots.json") as f:
    slots = json.load(f)["time_slots"]
```

**Plain English:**
The engine only schedules on weekdays, and it avoids listed excluded slots unless it reaches fallback behavior.

---

## Phase B — Time Slot Normalization

Each slot like `09:00-10:30` is converted into:
- machine-friendly key
- start/end minutes
- duration in hours

This allows the allocator to ask practical questions like: “Do we already have at least 1.5 hours in this contiguous block?”

### Code callout
```python
# timetable_automation/timetable.py

slot_keys = [s["key"] for s in slots_norm]
slot_dur = {s["key"]: s["dur"] for s in slots_norm}
```

**Plain English:**
`slot_keys` preserves column order; `slot_dur` is the duration lookup table used for lecture/tutorial/lab chunk fitting.

---

## Phase C — In-Memory Timetable Grid + Conflict Maps

Inside `generate(...)`, the scheduler creates a working model:

- `tt`: Pandas DataFrame (rows=days, cols=slot_keys, value=scheduled text)
- `busy[day][faculty] -> set(slots)` to stop faculty clashes
- `room_busy[day][room] -> set(slots)` to stop room clashes
- `rm[(course_code, type)] -> room` for stable room mapping per course component
- `course_usage[day][code] -> {L,T,P counts}` to prevent over-placing same component in same day

### Code callout
```python
# timetable_automation/timetable.py

tt = pd.DataFrame("", index=days, columns=slot_keys)
busy = {d:{} for d in days}
room_busy = room_busy_global if room_busy_global is not None else {d:{} for d in days}
rm = {}
course_usage = {d:{} for d in days}
```

**Plain English:**
Before writing anything to Excel, everything is first attempted in memory with strict conflict tracking.

---

## Phase D — Course Categorization

Each input course is split into one of three buckets:
- **Elective** (`Elective == "1"`)
- **Combined core** (`Is_Combined == "1"` and not elective)
- **Regular core** (all remaining non-elective, non-combined)

### Code callout
```python
elec = [x for x in courses if s(x.get("Elective","")) == "1"]
combined_core = [x for x in courses if s(x.get("Elective","")) != "1" and s(x.get("Is_Combined","0")) == "1"]
regular_core = [x for x in courses if s(x.get("Elective","")) != "1" and s(x.get("Is_Combined","0")) != "1"]
```

**Plain English:**
The algorithm does **not** schedule all subjects the same way. Electives and combined courses get custom treatment.

---

## Phase E — Elective Basket Handling + Syncing

Electives in the same basket are represented with a shared sync identifier so they can align in the same day/time pattern.

### Code callout
```python
if sync_name and sync_name in elective_sync:
    pref = elective_sync[sync_name]
    alloc(... preferred_slots=(pref["day"], pref["slots"]))
```

**Plain English:**
If one elective in a basket got a slot, related electives reuse that slot logic. This keeps elective coordination predictable.

---

## Phase F — Combined Courses (C004-centric logic)

Combined courses are hard-bound to `C004` and handled by `assign_combined_precise_durations(...)`.

Key behaviors:
- `L/T/P` of combined courses are room-pinned to `C004`
- Lectures are chunked (prefer 1.5h, else 1.0h)
- The same lecture course tries to spread across different days
- Global C004 occupancy map prevents overlap with other branches

### Code callout
```python
rm[(code, "L")] = "C004"
rm[(code, "T")] = "C004"
rm[(code, "P")] = "C004"

if r == "C004":
    occ = c004_occupancy.get(day, {}).get(s_)
    if occ and occ != code:
        return False
```

**Plain English:**
C004 is treated as a globally protected shared resource. If another course already owns that slot in C004, allocation is rejected.

---

## Phase G — Regular Allocation + Fallback Strategy

For each chunk requirement (`L`, `T`, `P`):
1. Try preferred/synced slot if available.
2. Try normal allowed slots with day-order balancing.
3. If still not possible, fall back to excluded-slot mode.

### Code callout
```python
if not placed:
    for d in days:
        if alloc(..., ex=True, ...):
            h -= a; placed = True; break
```

**Plain English:**
Excluded slots are not first choice. They are safety-valve fallback to maximize completeness.

---

## Phase H — DataFrame to Worksheet + Formatting

After scheduling, the DataFrame is written row by row to worksheet, then:
- contiguous identical cells are merged
- color coding is applied per course
- legend blocks are appended from CSV metadata

### Code callout
```python
ws.append(["Day"] + slot_keys)
for d in days:
    ws.append([d] + [tt.at[d, s] for s in slot_keys])
```

**Plain English:**
Scheduling is solved first; styling/presentation is done later.

---

## Phase I — Orchestration Across Branches/Semesters

The `__main__` block calls `generate(...)` repeatedly for:
- CSE-I (A/B)
- DSAI-I
- ECE-I
- CSE-III (A/B)
- DSAI-III
- ECE-III
- CSE-V
- DSAI-V
- ECE-V
- Common 7th Sem

Each group is split into **First Half** and **Second Half** using `Semester_Half`.

---

## 3) Core Business Rules (Explicit)

## A) Morning vs Evening Shift Rules

This is implemented in the **exam timetable** flow (not in class timetable).

### Code callout
```python
# timetable_generator.py

def get_shift(batch_name: str):
    if "1ST" in batch_name or "3RD" in batch_name:
        return "Morning (10:00 AM – 11:30 AM)"
    else:
        return "Evening (03:00 PM – 04:30 PM)"
```

**Plain English:**
- 1st-year and 3rd-year batches are assigned **morning** exams.
- Other batches are assigned **evening** exams.

> Important: `timetable_automation/timetable.py` (class timetable) does **not** apply this year-based shift rule; it uses the common slot grid for all.

---

## B) Date Calculation + Weekend/Holiday Skipping

Again this is exam-side logic.

### Code callout
```python
# timetable_generator.py

def generate_exam_dates(num_days, start_date):
    dates = []
    d = start_date
    while len(dates) < num_days:
        if d.weekday() < 5:  # Monday–Friday only
            dates.append(d)
        d += dt.timedelta(days=1)
    return dates
```

**Plain English:**
Only weekdays are generated. Saturday/Sunday are skipped.

In `code.py`, weekdays are similarly built from a start/end range:
```python
def generate_weekdays(start, end):
    ...
    if d.weekday() < 5:
        res.append(d)
```

**Holiday note:**
There is **no dedicated holiday calendar file/integration** in current code. “Holiday skipping” is currently equivalent to “skip weekends only,” unless users externally adjust date ranges.

---

## C) Normal Courses vs Elective Courses

### In class timetable (`timetable_automation/timetable.py`)

- **Normal (regular core):** scheduled with rotating day order and room/faculty conflict checks.
- **Electives:** basket-aware syncing (`elective_sync`) to preserve aligned slots among related electives.
- **Combined:** special C004 pipeline (`assign_combined_precise_durations`).

### In exam timetable (`timetable_generator.py`)

- **Normal courses:** each gets next available date per batch sequence.
- **Electives:** all elective subjects for a batch are pushed to one common elective day.

### Code callout
```python
# timetable_generator.py
normal_courses = [(code, name) for code, name in clist if "ELECTIVE" not in code.upper()]
elective_courses = [(code, name) for code, name in clist if "ELECTIVE" in code.upper()]

# normal first, elective day grouped later
```

**Plain English:**
Electives are intentionally grouped together, while normal courses are distributed sequentially.

---

## 4) Important In-Memory Data Structures (Before Excel)

## Class timetable engine

- `tt` (DataFrame): the master weekly grid
- `busy`: faculty occupancy map
- `room_busy`: room occupancy map
- `c004_occupancy`: global lock map for C004 across generated sheets
- `elective_sync`: remembers chosen day/slots for elective sync names
- `combined_sync`: mirrors combined-course slot structures between related groups
- `elective_room_map`: stable elective room assignment map

## Exam timetable engine

- `courses` / `courses_by_batch`: batch -> list of course tuples/objects
- `dates` or `date_slots`: generated calendar candidates
- `records`: row-wise output list, later converted to DataFrame
- `room_availability` (`code.py`): per `(date,slot)` room quota and assignment counters

**Why this design matters:**
The code does heavy decision-making in Python dictionaries/lists first, then does a clean final conversion to Pandas and finally Excel.

---

## 5) End-to-End Flow Summary (Manager-Friendly)

1. **Read configuration and source data** (courses, rooms, slots).
2. **Build internal scheduling state** (free/busy for faculty, rooms, and special resources like C004).
3. **Split courses by type** (regular, elective, combined).
4. **Allocate sessions in chunks** with constraints (durations, clashes, preferred patterns, fallbacks).
5. **Persist result into DataFrame** (for class/exam rows).
6. **Export to Excel** with merged cells, styling, and legends.

In short: **the scheduler is constraint-first, output-second**.

---

## 6) Practical Caveats to Know

- The class timetable uses weekdays + slot grid, not real calendar dates.
- Exam date logic skips weekends but has no separate holiday calendar integration.
- Excluded class slots are soft-avoided but can be used as fallback.
- Combined courses rely heavily on C004 availability, making C004 the key bottleneck resource.

---

## 7) File Index (Where to Read What)

- `timetable_automation/timetable.py` → core class timetable generation logic
- `timetable_generator.py` → exam timetable with year-based shift assignment
- `code.py` → exam timetable variant with interactive date range + room quota splitting
- `timetable_automation/faculty_timetable_from_balanced.py` → derives faculty-centric views from generated class timetable

