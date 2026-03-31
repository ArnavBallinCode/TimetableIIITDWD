import datetime as dt
import json
from pathlib import Path

import pandas as pd


def safe_int(value):
    """Best-effort conversion for numeric values from CSV inputs."""
    try:
        if pd.isna(value):
            return None
        text = str(value).replace(",", "").strip()
        if text in ("", "-", "NA", "N/A", "nan"):
            return None
        return int(float(text))
    except (TypeError, ValueError):
        return None


def generate_weekdays(start_date, end_date):
    """Return all Monday-Friday dates in [start_date, end_date]."""
    if end_date < start_date:
        raise ValueError("end_date must be greater than or equal to start_date")

    current = start_date
    result = []
    while current <= end_date:
        if current.weekday() < 5:
            result.append(current)
        current += dt.timedelta(days=1)
    return result


def generate_exam_dates(num_days, start_date):
    """Return the next `num_days` weekdays beginning at `start_date`."""
    if num_days < 0:
        raise ValueError("num_days must be non-negative")

    current = start_date
    result = []
    while len(result) < num_days:
        if current.weekday() < 5:
            result.append(current)
        current += dt.timedelta(days=1)
    return result


def t2m(time_text):
    """Convert HH:MM text to minutes from midnight."""
    hour, minute = map(int, time_text.split(":"))
    return hour * 60 + minute


def load_time_slots(time_slots_path):
    """Load and normalize time-slot metadata from JSON."""
    with open(time_slots_path, encoding="utf-8") as stream:
        slots = json.load(stream)["time_slots"]

    slots_norm = [
        {
            "key": f"{item['start']}-{item['end']}",
            "start": item["start"],
            "end": item["end"],
            "dur": (t2m(item["end"]) - t2m(item["start"])) / 60.0,
        }
        for item in slots
    ]
    slots_norm.sort(key=lambda item: t2m(item["start"]))
    slot_keys = [item["key"] for item in slots_norm]
    slot_dur = {item["key"]: item["dur"] for item in slots_norm}
    return slots_norm, slot_keys, slot_dur


def save_workbook_with_fallback(workbook, output_file):
    """
    Save workbook to `output_file`. If the file is locked, append `_N`.
    Returns the final saved Path.
    """
    out_path = Path(output_file)
    i = 1
    base = out_path.stem
    ext = out_path.suffix or ".xlsx"
    while True:
        try:
            workbook.save(out_path)
            return out_path
        except PermissionError:
            out_path = Path(f"{base}_{i}{ext}")
            i += 1
