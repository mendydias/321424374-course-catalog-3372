import re

from controllers.course_dto import CourseDTO
from data import (
    CourseRepoError,
    add_course,
    course_exists,
    get_course as _repo_get_course,
    get_department,
    list_courses as _repo_list_courses,
    list_departments,
    remove_course as _repo_remove_course,
    update_course as _repo_update_course,
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


def validate_course(course: Course) -> Course:
    name = course.name.strip()
    if not name:
        raise CourseError("Course name cannot be empty.")
    if len(name) <= 3:
        raise CourseError(
            f"Course name must be longer than 3 characters, got {len(name)}."
        )
    course.name = name[0].upper() + name[1:].lower()

    semester = course.semester
    if semester <= 0 or semester >= 9:
        raise CourseError(f"Semester must be between 1 and 8, got {semester}.")
    course.semester = semester

    lecturer = course.lecturer.strip()
    if not lecturer:
        raise CourseError("Lecturer name cannot be empty.")
    if len(lecturer) <= 3:
        raise CourseError(
            f"Lecturer name must be longer than 3 characters, got {len(lecturer)}."
        )
    course.lecturer = lecturer.title()

    return course


def register_course(course: Course) -> Course:
    validate_course(course)
    try:
        add_course(course)
    except CourseRepoError as e:
        raise CourseError(str(e)) from e
    return course


def update_course(course: Course) -> Course:
    if not course_exists(course.code):
        raise CourseError(f"Course with code '{course.code}' not found.")
    validate_course(course)
    try:
        _repo_update_course(course)
    except CourseRepoError as e:
        raise CourseError(str(e)) from e
    return course


def delete_course(code: str) -> None:
    if not course_exists(code):
        raise CourseError(f"Course with code '{code}' not found.")
    try:
        _repo_remove_course(code)
    except CourseRepoError as e:
        raise CourseError(str(e)) from e


def get_course(code: str) -> Course:
    course = _repo_get_course(code)
    if course is None:
        raise CourseError(f"Course with code '{code}' not found.")
    return course


def list_courses() -> dict[str, CourseDTO]:
    return {code: CourseDTO.from_course(c) for code, c in _repo_list_courses().items()}
