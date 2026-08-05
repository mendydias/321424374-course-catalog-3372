import re

from data import (
    CourseRepoError,
    add_course,
    get_department,
    list_courses as _repo_list_courses,
    list_departments,
)
from models import Course

CODE_PATTERN = re.compile(r"[A-Za-z]{3}\d{4}")
LEVEL_RANGE = range(1, 5)
CREDIT_RANGE = range(1, 7)


class CourseError(ValueError):
    pass


def create_course(code: str) -> Course:
    raw = code.strip().upper()
    if not CODE_PATTERN.fullmatch(raw):
        raise CourseError(
            f"Invalid course code format: '{code}'. "
            f"Expected 3 letters followed by 4 digits (e.g. EEI3372)."
        )

    dept_code = raw[:2]
    department = get_department(dept_code)
    if department is None:
        supported = ", ".join(sorted(list_departments()))
        raise CourseError(
            f"Unknown department code '{dept_code}'. Supported codes: {supported}."
        )

    level = int(raw[3])
    if level not in LEVEL_RANGE:
        raise CourseError(
            f"Academic level {level} is out of range. Must be between "
            f"{LEVEL_RANGE.start} and {LEVEL_RANGE.stop - 1}."
        )

    credits = int(raw[4])
    if credits not in CREDIT_RANGE:
        raise CourseError(
            f"Credit count {credits} is out of range. Must be between "
            f"{CREDIT_RANGE.start} and {CREDIT_RANGE.stop - 1}."
        )

    return Course(code=raw, department=department, level=level, credits=credits)


def _parse_name_semester_lecturer(
    course: Course, name: str, semester: int, lecturer: str,
) -> Course:
    name = name.strip()
    if not name:
        raise CourseError("Course name cannot be empty.")
    if len(name) <= 3:
        raise CourseError(
            f"Course name must be longer than 3 characters, got {len(name)}."
        )
    course.name = name[0].upper() + name[1:].lower()

    if semester <= 0 or semester >= 9:
        raise CourseError(
            f"Semester must be between 1 and 8, got {semester}."
        )
    course.semester = semester

    lecturer = lecturer.strip()
    if not lecturer:
        raise CourseError("Lecturer name cannot be empty.")
    if len(lecturer) <= 3:
        raise CourseError(
            f"Lecturer name must be longer than 3 characters, got {len(lecturer)}."
        )
    course.lecturer = lecturer.title()

    return course


def register_course(course: Course) -> Course:
    _parse_name_semester_lecturer(course, course.name, course.semester, course.lecturer)
    try:
        add_course(course)
    except CourseRepoError as e:
        raise CourseError(str(e)) from e
    return course


def list_courses() -> dict[str, Course]:
    return _repo_list_courses()
