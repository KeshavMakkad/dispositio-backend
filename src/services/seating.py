from fastapi import Request


def create_seating(request: Request):
    """
    Create a new seating arrangement.
    """
    student_list_one = request.json().get("student_list_one")
    student_list_two = request.json().get("student_list_two")
    
    # Logic to create seating arrangement based on the two student lists
    