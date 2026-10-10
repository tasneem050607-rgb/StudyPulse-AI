
import pandas as pd
from pathlib import Path

DATA_FILE = Path(__file__).with_name("student_subjects.csv")

COLUMNS = [
    "Subject",
    "Exam Date",
    "Quiz Score",
    "Previous Score",
    "Study Time",
    "Revision Count",
    "Difficulty",
    "Syllabus Completion",
]


def load_subjects():
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE)

    return pd.DataFrame(columns=COLUMNS)


def save_subjects(subjects):
    subjects.to_csv(DATA_FILE, index=False)