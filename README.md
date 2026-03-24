
# Automated Timetable Scheduling – IIIT Dharwad

This project automates the generation of clash-free timetables for IIIT Dharwad using institute data such as courses, batches, rooms, and student counts.  
It reads structured input files (CSV/Excel), applies scheduling constraints, and produces a final timetable in Excel/CSV format that can be shared with faculty and students.

---

## Features

-  Automatic timetable generation
-  Clash detection to avoid overlapping exams or room conflicts
-  Batch-aware scheduling
-  Room capacity handling (full & half seating modes)
-  Excel and CSV outputs

---

## Repository Structure

```
.
├── timetable_automation/
├── data/
├── docs/
├── tests/
├── CourseCode&Name.csv
├── batch_student_counts.csv
├── student_roll_numbers.csv
├── rooms.csv
├── room_half_capacity.csv
├── Exam_Timetable_Final.xlsx
├── FINAL_EXCEL.csv
├── timetable_generator.py
├── code.py
└── README.md
```

---

## Requirements

- Python 3.8+
- pip

Required libraries:

```
pandas
openpyxl
```

---

## Installation

Clone the repository:

```
git clone https://github.com/MayankBSahu/Automated-Timetable-scheduling-IIIT-Dharwad.git
cd Automated-Timetable-scheduling-IIIT-Dharwad
```

Create and activate virtual environment (optional):

```
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt

# or manually
pip install pandas openpyxl
```

---

## Input Data

Place or update the following CSV files in the project root or `data/` directory:

- CourseCode&Name.csv – course code to name mapping
- batch_student_counts.csv – student count per batch
- student_roll_numbers.csv – roll numbers mapped to batch
- rooms.csv – room capacities
- room_half_capacity.csv – reduced room capacity seating

Ensure columns match expected format in scripts.

---

## Usage

Run the timetable generator:

```
python timetable_generator.py
```

Outputs:

- `Exam_Timetable_Final.xlsx`
- `FINAL_EXCEL.csv`

Alternative:

```
python code.py
```

---

## Troubleshooting

**FileNotFoundError**  
➡ Ensure all CSV files are located correctly and script paths match the data location.

**Import Errors**  
➡ Run scripts from the project root directory.

**Empty Outputs**  
➡ Check for missing CSV values or formatting mismatches.

---

## Future Improvements

- Web interface visualization
- Advanced constraint engine
- Multi-session scheduling
- PDF timetable export

---

## Contributing

1. Fork the repository.
2. Create feature branch:

```
git checkout -b feature/new-feature
```

3. Commit and push changes, open a pull request.

---

## License

Add your preferred license file (e.g., MIT License).

---

## Acknowledgements

IIIT Dharwad faculty & project contributors.
