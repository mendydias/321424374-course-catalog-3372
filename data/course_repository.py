from models import Course


_COURSES: dict[str, Course] = {}


def clear_courses() -> None:
    _COURSES.clear()


class CourseRepoError(ValueError):
    pass


def add_course(course: Course) -> None:
    key = course.code.strip().upper()
    if key in _COURSES:
        raise CourseRepoError(
            f"Course with code '{course.code}' already exists."
        )
    _COURSES[key] = course


def get_course(code: str) -> Course | None:
    return _COURSES.get(code.strip().upper())


def update_course(course: Course) -> None:
    key = course.code.strip().upper()
    if key not in _COURSES:
        raise CourseRepoError(
            f"Course with code '{course.code}' not found."
        )
    _COURSES[key] = course


def remove_course(code: str) -> None:
    key = code.strip().upper()
    if key not in _COURSES:
        raise CourseRepoError(
            f"Course with code '{code}' not found."
        )
    del _COURSES[key]


def list_courses() -> dict[str, Course]:
    return dict(_COURSES)


def course_exists(code: str) -> bool:
    return code.strip().upper() in _COURSES
