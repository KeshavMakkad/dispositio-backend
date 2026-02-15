from pathlib import Path

from fastapi import Request
from utils.csv import read_csv


def create_seating(request: Request):
    """
    Create a new seating arrangement.
    """
    data_dir = Path(__file__).resolve().parents[2] / "data"
    student_list_one = read_csv(data_dir / "student_list_one.csv")
    student_list_two = read_csv(data_dir / "student_list_two.csv")
    
    print(student_list_one)
    print(student_list_two)
    
    # Logic to create seating arrangement based on the two student lists
    