Issue summaries (plain English) — TimetableIIITDWD

Purpose
- This document explains each open issue in plain English for non-technical readers (administrators, faculty, or stakeholders).
- For each issue: What the problem is, what happens in real life because of it, who it affects, and simple suggested next steps.

---

1) #25 — C004 special-casing: combined occupancy hides cross-branch conflict risk

What is the problem?
- The scheduling code treats one particular room (called "C004") as special. It lets the same course appear in that room across different departments without checking properly for conflicts.

What happens in real life?
- If two different departments claim the same time in C004, the system might not notice and could assign overlapping sessions.
- If course names are slightly different (typos, spacing), the system may fail to recognize the conflict and still schedule both classes in the same room.

Who is affected?
- Students and faculty who expect exclusive use of a room during an exam or class.
- Administrators who rely on the timetable to coordinate room usage.

Why it matters
- Double-booking a room causes confusion, stressful last-minute relocations, and can disrupt exams or classes.

Simple next steps
- Stop hardcoding special rules for one room; keep room rules in a regular configuration file.
- Make course identifiers consistent so the system can reliably detect duplicates.

---

2) #24 — Ambiguous placeholder room 'Lab' used across multiple sheets

What is the problem?
- Some entries in the timetable use the word "Lab" instead of a specific room name (like "L1" or "C101").

What happens in real life?
- The timetable can't tell which lab is actually meant. Multiple courses might appear to use "Lab" at the same time, but that may or may not be a real conflict depending on which physical lab is intended.

Who is affected?
- Lab technicians, students, and faculty who need to know the exact room to attend.
- Timetable managers who must verify and publish accurate room assignments.

Why it matters
- Ambiguous room names lead to uncertainty, wasted time finding rooms, or accidental overcrowding if many groups go to the same lab.

Simple next steps
- Replace "Lab" placeholders with specific room identifiers in the input data.
- If a course can go to any lab, specify a small list of candidate labs and pick one deterministically.

---

3) #23 — Duplicate scheduling scripts — no single source of truth

What is the problem?
- There are multiple scripts that do the same or very similar scheduling work.

What happens in real life?
- Fixes or improvements applied in one script are not carried over to others. This causes inconsistent behavior and makes maintenance harder.

Who is affected?
- Developers and maintainers who have to update multiple files.
- End users who might run different scripts and get different timetables.

Why it matters
- Wastes maintenance time and increases the chance of bugs.

Simple next steps
- Consolidate common logic into a single shared module and use small wrapper scripts for different entry points.

---

4) #22 — Room C004 is special-cased 47+ times in timetable.py — not configurable

What is the problem?
- The code contains many hardcoded references and special rules for room C004.

What happens in real life?
- If the room's name changes or its schedule rules change, the code must be updated in many places; otherwise the timetable will be incorrect.

Who is affected?
- Administrators when room policies change.

Why it matters
- Hard-to-change code means errors and extra work when a simple administrative change occurs.

Simple next steps
- Move room-specific rules into a configuration file that staff can edit without touching code.

---

5) #20 — No validation of generated timetable — room/faculty conflicts can go undetected

What is the problem?
- After generating the timetable, the system does not automatically check for mistakes like the same room booked twice or a teacher scheduled in two places at once.

What happens in real life?
- Conflicts are only found later (manually or by users), leading to last-minute fixes that confuse students and staff.

Who is affected?
- Everyone using the timetable: students, faculty, and scheduling staff.

Why it matters
- Undetected conflicts can lead to exam delays, lack of space, and disrupted classes.

Simple next steps
- Run an automatic clash-check after timetabling that reports any room or faculty overlaps and refuses to publish the timetable until cleared.

---

6) #19 — timetable_generator.py uses hardcoded start date — stale schedule every semester

What is the problem?
- The timetable generator has a fixed start date coded into it, so it won't automatically use the current semester dates.

What happens in real life?
- The generated timetable may have dates from a past semester instead of the correct upcoming dates.

Who is affected?
- Timetable creators and anyone relying on the script for current schedules.

Why it matters
- Publishing an incorrect dated timetable is misleading and could cause people to miss exams.

Simple next steps
- Allow the user to pass the start date as an option or read it from a small config file.

---

7) #18 — code.py requires interactive terminal input — cannot run in CI/CD or batch mode

What is the problem?
- One script asks for input interactively (typing in dates) and cannot run automatically.

What happens in real life?
- The script can’t be scheduled to run by an automated system (e.g., overnight updates), and it will hang waiting for input if run non-interactively.

Who is affected?
- Administrators who want to automate timetable generation.

Why it matters
- Prevents automation and increases manual steps, causing delays and potential human error.

Simple next steps
- Change scripts to accept command-line options and only fall back to asking users interactively if options aren’t provided.

---

8) #17 — Bare `except:` clauses silently swallow errors and hide bugs

What is the problem?
- The code catches errors too broadly and then ignores them without clear messages.

What happens in real life?
- When something goes wrong (bad CSV file, misformatted data), the script may continue silently and produce an incorrect timetable without informing anyone.

Who is affected?
- Those who rely on correct outputs — staff and students — and developers who must debug the system.

Why it matters
- Hidden errors reduce trust in the system and make debugging difficult.

Simple next steps
- Catch specific error types and log helpful messages if something goes wrong.

---

9) #16 — Hardcoded file paths throughout codebase make scripts non-portable

What is the problem?
- Scripts assume input and output files are in fixed locations instead of accepting file paths.

What happens in real life?
- Moving files or running scripts from a different folder causes errors, making the system fragile and harder to run in different environments.

Who is affected?
- Anyone trying to run the scripts on a different computer or as part of automation.

Why it matters
- Reduces flexibility and increases setup time.

Simple next steps
- Accept file paths via options or a config file, and display clear error messages if files are missing.

---

10) #15 — No requirements.txt / setup.py — pip dependencies undocumented

What is the problem?
- The code uses external Python libraries but does not provide a simple list of required packages.

What happens in real life?
- When someone tries to run the code on a fresh machine, it immediately fails with missing-library errors.

Who is affected?
- New developers or admins trying to deploy the system.

Why it matters
- Wastes time installing packages manually and increases friction for adoption.

Simple next steps
- Add a small `requirements.txt` listing needed packages (for example `pandas`, `openpyxl`) and a short README step to install them.

---

11) #14 — Tests fail to import: package initializer misnamed and empty

What is the problem?
- The test code expects a package initializer file, but the repository has a misnamed and empty file, causing automated tests to fail immediately.

What happens in real life?
- Tests cannot run, and automated checks (CI) fail early.

Who is affected?
- Developers who rely on tests to validate changes.

Why it matters
- Prevents automated testing and reduces confidence in code changes.

Simple next steps
- Rename the file to the correct name and export the necessary functions so tests can import them.

---

12) #8 — Performance and scalability issues under large inputs

What is the problem?
- The scheduling code may be slow or memory-hungry with large datasets.

What happens in real life?
- On big semesters or campus-wide schedules, timetabling may take too long or fail.

Who is affected?
- Administrators who need to run schedules for many courses, and any automated systems with time limits.

Why it matters
- Delays in producing timetables and increased operational cost.

Simple next steps
- Add performance tests, measure common cases, and optimize hot spots.

---

13) #7 — C004 occupancy/blocking logic unintentionally prevents valid placements

What is the problem?
- The logic that prevents conflicts for C004 is sometimes too aggressive and rejects valid placements.

What happens in real life?
- Legitimate room assignments may fail, making the scheduler leave classes unplaced when there was actually a valid option.

Who is affected?
- Scheduling staff and classes that become unscheduled.

Why it matters
- Leads to unnecessary manual fixes and a less complete timetable.

Simple next steps
- Log when placements are blocked and add unit tests for these cases.

---

14) #6 — Room capacity enforcement causes silent omissions / incorrect allocation

What is the problem?
- When rooms are too small for the number of students, the system either allows oversubscription or silently drops the class.

What happens in real life?
- Students may be placed in rooms that are too small, or classes might disappear from the schedule.

Who is affected?
- Students (safety and comfort), faculty, and administrators.

Why it matters
- Overcrowding is a safety and logistics issue; missing classes cause confusion.

Simple next steps
- Ensure the scheduler refuses to place classes in rooms that are too small and reports any unscheduled classes with reasons.

---

15) #4 — Class scheduled multiple times disappears from final timetable

What is the problem?
- If the same course is accidentally scheduled more than once, it may be removed entirely from the output.

What happens in real life?
- Students and faculty cannot find their class in the published timetable even though the scheduler ran.

Who is affected?
- Everyone relying on the final published timetable.

Why it matters
- Makes the timetable unreliable and forces manual audits.

Simple next steps
- Detect duplicate placements and either keep the first placement or report duplicates clearly so an administrator can resolve them.

---

16) #3 — Scheduled course(s) not appearing in generated timetable — final output empty

What is the problem?
- The scheduler may report that courses were placed, but the final published file ends up empty.

What happens in real life?
- The published timetable appears blank, causing panic and manual intervention.

Who is affected?
- Everyone; especially immediate when exams or classes approach.

Why it matters
- Produces major operational disruption and loss of trust.

Simple next steps
- Add end-to-end checks ensuring any scheduled course appears in the final output and report mismatches.

---

17) #2 — New classes not scheduled when rooms reach capacity — no warning

What is the problem?
- When rooms are already full, new classes are silently omitted and no warning is shown.

What happens in real life?
- Classes are missing without explanation; staff must manually discover and fix the gaps.

Who is affected?
- Organizers, faculty, and students expecting those classes to appear.

Why it matters
- Missing schedule entries break planning and communication.

Simple next steps
- Record unscheduled classes in a clear report with reasons (capacity, conflicts) and present it after scheduling.

---

Document created in the repository at: `docs/issue-summaries-for-nontech.md`

If you want, I can:
- Add this summary to a GitHub issue or PR, or
- Convert it into a nicely formatted PDF for circulation, or
- Start implementing one suggested fix (e.g., add `requirements.txt` or a simple validation step).
