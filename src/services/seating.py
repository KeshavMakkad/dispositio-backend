import random
from dataclasses import dataclass, field
from fastapi import Request

from schemas.classroom import ClassLayoutItem
from schemas.seating import ClassroomLayouts
from schemas.seating import CreateSeatingRequest
from services.classroom import get_default_class_details


@dataclass
class ClassStudentAssignment:
    classroom_name: str
    layout: list[ClassLayoutItem]
    set_one_capacity: int
    set_two_capacity: int
    set_one_assigned_students: list[str] = field(default_factory=list)
    set_two_assigned_students: list[str] = field(default_factory=list)


def _to_assignment(layout: ClassroomLayouts) -> ClassStudentAssignment:
    return ClassStudentAssignment(
        classroom_name=layout.classroom_name,
        layout=layout.layout,
        set_one_capacity=layout.set_one_capacity,
        set_two_capacity=layout.set_two_capacity,
    )


def prepare_class_layouts(args: CreateSeatingRequest) -> dict[str, ClassStudentAssignment]:
    """
    Load layouts for classrooms.
    If a custom layout exists use it, otherwise load default layout.
    """
    class_layouts: dict[str, ClassStudentAssignment] = {}
    custom_layouts = {
        detail.classroom_name: detail for detail in (args.classroom_details or [])
    }

    for classroom in args.classrooms_list:
        if classroom in custom_layouts:
            class_layouts[classroom] = _to_assignment(custom_layouts[classroom])
        else:
            class_layouts[classroom] = _to_assignment(get_default_class_details(classroom))

    return class_layouts


def validate_capacity(args: CreateSeatingRequest, class_layouts: dict):
    """
    Ensure classrooms have enough capacity for students.
    """

    set_one_student_count = len(args.student_list_one)
    set_two_student_count = len(args.student_list_two)

    set_one_capacity = sum(layout.set_one_capacity for layout in class_layouts.values())
    set_two_capacity = sum(layout.set_two_capacity for layout in class_layouts.values())

    if set_one_student_count <= 0 and set_two_student_count <= 0:
        raise Exception("No students to seat.")

    if (
        set_two_student_count == 0 and set_one_student_count > set_one_capacity
        or set_one_student_count == 0 and set_two_student_count > set_two_capacity
        or set_one_student_count > set_one_capacity and set_two_student_count > set_two_capacity
    ):
        raise Exception("Total students exceed total classroom capacity.")


def shuffle_students(args: CreateSeatingRequest):
    """
    Shuffle students randomly before assigning.
    """
    student_list_one = args.student_list_one.copy()
    student_list_two = args.student_list_two.copy()

    random.shuffle(student_list_one)
    random.shuffle(student_list_two)

    return student_list_one, student_list_two


def assign_students_to_classrooms(
    class_layouts: dict[str, ClassStudentAssignment],
    student_list_one: list,
    student_list_two: list
):
    """
    Evenly and randomly assign students to classrooms.
    """

    set_one_index = 0
    set_two_index = 0

    total_classes = len(class_layouts)

    set_one_total = len(student_list_one)
    set_two_total = len(student_list_two)

    for classroom in class_layouts:

        layout = class_layouts[classroom]

        layout.set_one_assigned_students = []
        layout.set_two_assigned_students = []

        remaining_classes = total_classes

        remaining_set_one = set_one_total - set_one_index
        remaining_set_two = set_two_total - set_two_index

        if remaining_classes > 0:

            set_one_target = min(
                layout.set_one_capacity,
                (remaining_set_one + remaining_classes - 1) // remaining_classes
            )

            set_two_target = min(
                layout.set_two_capacity,
                (remaining_set_two + remaining_classes - 1) // remaining_classes
            )

        else:
            set_one_target = 0
            set_two_target = 0

        layout.set_one_assigned_students = student_list_one[
            set_one_index:set_one_index + set_one_target
        ]

        layout.set_two_assigned_students = student_list_two[
            set_two_index:set_two_index + set_two_target
        ]

        set_one_index += set_one_target
        set_two_index += set_two_target

        total_classes -= 1

def generate_seating_for_classroom(classroom: str, layout: ClassStudentAssignment):
    _ = classroom
    class_seating = []

    for col in layout.layout:
        seating = [col.column_name]

        try:
            column_capacity = int(col.column_capacity)
        except (TypeError, ValueError):
            column_capacity = 0

        for _ in range(column_capacity):
            if col.column_set == "Set 1" and layout.set_one_assigned_students:
                seating.append(layout.set_one_assigned_students.pop())
            elif col.column_set == "Set 2" and layout.set_two_assigned_students:
                seating.append(layout.set_two_assigned_students.pop())
            else:
                seating.append("")

        class_seating.append(seating)

    return class_seating

def generate_seating(class_layouts: dict[str, ClassStudentAssignment]):
    seating_plan = {}
    for classroom, layout in class_layouts.items():
        class_seating = generate_seating_for_classroom(classroom, layout)
        seating_plan[classroom] = class_seating
    return seating_plan



def create_seating_service(request: Request, args: CreateSeatingRequest):
    """
    Main orchestration function
    """
    class_layouts = prepare_class_layouts(args)

    validate_capacity(args, class_layouts)

    set_one_students, set_two_students = shuffle_students(args)

    assign_students_to_classrooms(
        class_layouts,
        set_one_students,
        set_two_students
    )

    seating_plan = generate_seating(class_layouts)

    return seating_plan