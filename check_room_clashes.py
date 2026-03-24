import re
from collections import defaultdict

import pandas as pd

FILE = "Balanced_Timetable_latest.xlsx"
DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
HALF_LABEL_PATTERN = re.compile(r"^(.+?\s+(First|Second)\s+Half)\s*$", re.IGNORECASE)
ROOM_PATTERN = re.compile(r"\(([^)]+)\)")
COURSE_CODE_PATTERN = re.compile(r"([A-Z]{2,}\d{2,}[A-Z]?)", re.IGNORECASE)
PLACEHOLDER_ROOMS = {"LAB"}


def parse_cell(text):
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text:
        return None

    room_match = ROOM_PATTERN.search(text)
    room = None
    room_raw = None
    is_placeholder = False

    if room_match:
        room_raw = room_match.group(1).strip()
        room = room_raw
        if "-" in room:
            room = room.split("-")[-1].strip()
        if room.upper() in PLACEHOLDER_ROOMS:
            is_placeholder = True

    course_match = COURSE_CODE_PATTERN.search(text)
    course_code = course_match.group(1).upper() if course_match else None

    return {
        "text": text,
        "room": room,
        "room_raw": room_raw,
        "is_placeholder": is_placeholder,
        "course_code": course_code,
    }


def parse_timetable_blocks(file_path):
    xls = pd.ExcelFile(file_path)
    entries = []

    for sheet in xls.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet, header=None)
        rows, cols = df.shape

        for r in range(rows):
            label = df.iat[r, 0]
            if not isinstance(label, str):
                continue
            half_match = HALF_LABEL_PATTERN.match(label.strip())
            if not half_match:
                continue

            block_name = half_match.group(1).strip()
            if r + 1 >= rows:
                continue
            headers = [
                str(df.iat[r + 1, c]).strip() if pd.notna(df.iat[r + 1, c]) else ""
                for c in range(cols)
            ]

            rr = r + 2
            while rr < rows:
                next_label = df.iat[rr, 0]
                if isinstance(next_label, str) and HALF_LABEL_PATTERN.match(next_label.strip()):
                    break

                day = str(next_label).strip() if pd.notna(next_label) else ""
                if day in DAYS:
                    for c in range(1, cols):
                        slot = headers[c]
                        if not slot or slot.lower() == "nan":
                            continue
                        val = df.iat[rr, c]
                        if pd.isna(val):
                            continue
                        cell = parse_cell(str(val))
                        if not cell:
                            continue
                        entries.append(
                            {
                                "sheet": sheet,
                                "block": block_name,
                                "day": day,
                                "slot": slot,
                                **cell,
                            }
                        )
                rr += 1

    return entries


def classify(entries):
    concrete_occ = defaultdict(list)
    placeholder_occ = defaultdict(list)

    for e in entries:
        if e["room"] is None:
            continue
        key = (e["day"], e["slot"], e["room"])
        if e["is_placeholder"]:
            placeholder_occ[key].append(e)
        else:
            concrete_occ[key].append(e)

    real_clashes = []
    allowed_combined = []

    for (day, slot, room), occ in concrete_occ.items():
        if len(occ) <= 1:
            continue
        course_codes = {o["course_code"] for o in occ}
        if len(course_codes) == 1 and None not in course_codes:
            allowed_combined.append((day, slot, room, occ))
        else:
            real_clashes.append((day, slot, room, occ))

    ambiguous_placeholders = []
    for (day, slot, room), occ in placeholder_occ.items():
        if len(occ) > 1:
            ambiguous_placeholders.append((day, slot, room, occ))

    return real_clashes, allowed_combined, ambiguous_placeholders


def print_category(title, items):
    print(f"\n{title}: {len(items)}")
    if not items:
        print("  None")
        return
    for day, slot, room, occ in sorted(items):
        print(f"  {day} | {slot} | {room}")
        for o in occ:
            print(f"    - {o['sheet']} | {o['block']} | {o['text']}")


def main():
    entries = parse_timetable_blocks(FILE)
    real_clashes, allowed_combined, ambiguous_placeholders = classify(entries)

    print(f"Workbook: {FILE}")
    print(f"Parsed timetable entries: {len(entries)}")
    print_category("Real clashes", real_clashes)
    print_category("Allowed combined overlaps", allowed_combined)
    print_category("Ambiguous placeholders (plain Lab-like rooms)", ambiguous_placeholders)


if __name__ == "__main__":
    main()
