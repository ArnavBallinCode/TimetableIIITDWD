from collections import defaultdict
import re


PARTIAL_TAG = "(PARTIAL)"


def _normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _parse_exam_rooms(rooms_text):
    cleaned = _normalize_text(rooms_text).replace(PARTIAL_TAG, "").strip()
    if not cleaned:
        return []
    rooms = []
    for chunk in cleaned.split(";"):
        token = chunk.strip()
        if not token:
            continue
        match = re.match(r"^(.*?)\s*\(\s*\d+\s*\)\s*$", token)
        room = (match.group(1) if match else token).strip()
        if room:
            rooms.append(room)
    return rooms


def validate_exam_output(df, date_column, slot_column, rooms_column="Rooms", faculty_column="Faculty"):
    errors = []

    if date_column not in df.columns or slot_column not in df.columns:
        missing = [c for c in (date_column, slot_column) if c not in df.columns]
        raise ValueError(f"Timetable validation failed: missing required columns {missing}")

    if rooms_column in df.columns:
        partial_rows = []
        room_usage = defaultdict(list)
        for idx, row in df.iterrows():
            date_value = _normalize_text(row.get(date_column))
            slot_value = _normalize_text(row.get(slot_column))
            course_value = _normalize_text(row.get("Course")) or _normalize_text(row.get("CourseCode"))
            room_text = _normalize_text(row.get(rooms_column))
            room_names = _parse_exam_rooms(room_text)

            if PARTIAL_TAG in room_text or not room_names:
                partial_rows.append((idx + 2, course_value or "<unknown course>"))

            for room_name in room_names:
                room_usage[(date_value, slot_value, room_name)].append((idx + 2, course_value))

        for (date_value, slot_value, room_name), hits in room_usage.items():
            unique_courses = {course for _, course in hits if course}
            if len(unique_courses) > 1:
                lines = ", ".join(f"row {line}" for line, _ in hits)
                errors.append(
                    f"Room clash at {date_value} | {slot_value} | {room_name} ({lines})"
                )

        if partial_rows:
            lines = ", ".join(f"row {line} ({course})" for line, course in partial_rows)
            errors.append(f"Incomplete room assignment detected: {lines}")

    if faculty_column in df.columns:
        has_faculty = df[faculty_column].fillna("").astype(str).str.strip().ne("").any()
        if has_faculty:
            faculty_usage = defaultdict(list)
            for idx, row in df.iterrows():
                faculty = _normalize_text(row.get(faculty_column))
                if not faculty:
                    continue
                date_value = _normalize_text(row.get(date_column))
                slot_value = _normalize_text(row.get(slot_column))
                course_value = _normalize_text(row.get("Course")) or _normalize_text(row.get("CourseCode"))
                faculty_usage[(date_value, slot_value, faculty.lower())].append((idx + 2, course_value, faculty))

            for (date_value, slot_value, _), hits in faculty_usage.items():
                unique_courses = {course for _, course, _ in hits if course}
                if len(unique_courses) > 1:
                    label = hits[0][2]
                    lines = ", ".join(f"row {line}" for line, _, _ in hits)
                    errors.append(
                        f"Faculty clash at {date_value} | {slot_value} | {label} ({lines})"
                    )

    if errors:
        raise ValueError("Timetable validation failed:\n- " + "\n- ".join(errors))


def validate_batch_slot_uniqueness(df, batch_column, date_column, slot_column):
    if any(col not in df.columns for col in (batch_column, date_column, slot_column)):
        return

    duplicates = (
        df.groupby([batch_column, date_column, slot_column], dropna=False)
        .size()
        .reset_index(name="count")
    )
    clashes = duplicates[duplicates["count"] > 1]
    if clashes.empty:
        return

    formatted = []
    for _, row in clashes.iterrows():
        formatted.append(
            f"{_normalize_text(row[batch_column])} | {_normalize_text(row[date_column])} | {_normalize_text(row[slot_column])}"
        )
    raise ValueError(
        "Timetable validation failed:\n- Batch has overlapping exams in same slot: "
        + "; ".join(formatted)
    )


def validate_slot_allocations(allocation_events, check_faculty_conflicts=True):
    room_usage = defaultdict(set)
    faculty_usage = defaultdict(set)
    missing_rooms = []

    for event in allocation_events:
        day = _normalize_text(event.get("day"))
        slot = _normalize_text(event.get("slot"))
        course = _normalize_text(event.get("course"))
        room = _normalize_text(event.get("room"))
        faculty = _normalize_text(event.get("faculty"))
        needs_room = bool(event.get("requires_room", False))

        if needs_room and not room:
            missing_rooms.append((day, slot, course))
        if room:
            room_usage[(day, slot, room)].add(course or "<unknown course>")
        if check_faculty_conflicts and faculty:
            faculty_usage[(day, slot, faculty.lower())].add(course or "<unknown course>")

    errors = []

    if missing_rooms:
        text = ", ".join(f"{day} | {slot} | {course}" for day, slot, course in missing_rooms[:10])
        errors.append(f"Incomplete room assignment detected: {text}")

    for (day, slot, room), courses in room_usage.items():
        if len(courses) > 1:
            errors.append(f"Room clash at {day} | {slot} | {room}: {sorted(courses)}")

    if check_faculty_conflicts:
        for (day, slot, faculty_key), courses in faculty_usage.items():
            if len(courses) > 1:
                errors.append(f"Faculty clash at {day} | {slot} | {faculty_key}: {sorted(courses)}")

    if errors:
        raise ValueError("Timetable validation failed:\n- " + "\n- ".join(errors))
