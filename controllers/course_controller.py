import re

from data import get_department, list_departments
from models import Course

CODE_PATTERN = re.compile(r"[A-Za-z]{3}\d{4}")
LEVEL_RANGE = range(1, 5)
CREDIT_RANGE = range(1, 7)


class CourseCodeError(ValueError):
    pass


def parse_course_code(code: str) -> Course:
    raw = code.strip().upper()
    if not CODE_PATTERN.fullmatch(raw):
        raise CourseCodeError(
            f"Invalid course code format: '{code}'. "
            f"Expected 3 letters followed by 4 digits (e.g. EEI3372)."
        )

    dept_code = raw[:2]
    department = get_department(dept_code)
    if department is None:
        supported = ", ".join(sorted(list_departments()))
        raise CourseCodeError(
            f"Unknown department code '{dept_code}'. Supported codes: {supported}."
        )

    level = int(raw[3])
    if level not in LEVEL_RANGE:
        raise CourseCodeError(
            f"Academic level {level} is out of range. Must be between "
            f"{LEVEL_RANGE.start} and {LEVEL_RANGE.stop - 1}."
        )

    credits = int(raw[4])
    if credits not in CREDIT_RANGE:
        raise CourseCodeError(
            f"Credit count {credits} is out of range. Must be between "
            f"{CREDIT_RANGE.start} and {CREDIT_RANGE.stop - 1}."
        )

    return Course(code=raw, department=department.name, level=level, credits=credits)
