This project is a updated copy of https://github.com/MayankBSahu/Automated-Timetable-scheduling-IIIT-Dharwad.git  made for project presentation for the CS265 SE   


# Automated Timetable Scheduling – IIIT Dharwad (Semicolons)

This project automates the generation of clash-free timetables for IIIT Dharwad using institute data such as courses, batches, rooms, and student counts.  
It reads structured input files (CSV/Excel), applies scheduling constraints, and produces a final timetable in Excel/CSV format that can be shared with faculty and students.

## Scheduling scripts and shared core

- Shared reusable scheduling utilities now live in `timetable_automation/core.py`.
- Active seminar scheduler: `timetable_automation/timetable.py`.
- `timetable_automation/draft.py` is a legacy variant kept for comparison/tuning and is not the primary entrypoint.
- Exam scripts (`code.py`, `timetable_generator.py`) reuse core helpers to avoid duplicated date/slot/save logic.

 

