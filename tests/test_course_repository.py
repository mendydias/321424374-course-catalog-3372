import pytest

from data import (
    CourseRepoError,
    add_course,
    clear_courses,
    course_exists,
    get_course,
    list_courses,
    remove_course,
    update_course,
)
from models import Course
from models.department import Department

_DEPT = Department(code="EE", name="Electrical and Computer Engineering")


class TestCourseRepository:
    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def _clear_repo(cls) -> None:
        clear_courses()

    def test_add_and_get(self) -> None:
        course = Course(code="EEI1172", department=_DEPT, level=3, credits=3, name="Digital Systems", semester=1, lecturer="John Smith")
        add_course(course)
        assert get_course("EEI1172") is course

    def test_get_nonexistent(self) -> None:
        assert get_course("XXXXXXXX") is None

    def test_add_duplicate_raises_error(self) -> None:
        course = Course(code="EEI2172", department=_DEPT, level=3, credits=3)
        add_course(course)
        dup = Course(code="EEI2172", department=_DEPT, level=3, credits=3)
        with pytest.raises(CourseRepoError, match="already exists"):
            add_course(dup)

    def test_add_duplicate_case_insensitive(self) -> None:
        course = Course(code="EEI3172", department=_DEPT, level=3, credits=3)
        add_course(course)
        dup = Course(code="eei3172", department=_DEPT, level=3, credits=3)
        with pytest.raises(CourseRepoError, match="already exists"):
            add_course(dup)

    def test_update_existing(self) -> None:
        original = Course(code="EEI4172", department=_DEPT, level=3, credits=3, name="Old", semester=1, lecturer="A")
        add_course(original)
        updated = Course(code="EEI4172", department=_DEPT, level=3, credits=3, name="New", semester=2, lecturer="B")
        update_course(updated)
        stored = get_course("EEI4172")
        assert stored is updated
        assert stored.name == "New"

    def test_update_nonexistent_raises_error(self) -> None:
        course = Course(code="EEI5172", department=_DEPT, level=3, credits=3)
        with pytest.raises(CourseRepoError, match="not found"):
            update_course(course)

    def test_remove_existing(self) -> None:
        course = Course(code="EEI6172", department=_DEPT, level=3, credits=3)
        add_course(course)
        remove_course("EEI6172")
        assert get_course("EEI6172") is None

    def test_remove_nonexistent_raises_error(self) -> None:
        with pytest.raises(CourseRepoError, match="not found"):
            remove_course("XXXXXXXX")

    def test_list_courses_snapshot(self) -> None:
        c1 = Course(code="EEI7172", department=_DEPT, level=3, credits=3)
        c2 = Course(code="EEI8172", department=_DEPT, level=3, credits=3)
        add_course(c1)
        add_course(c2)
        snapshot = list_courses()
        assert "EEI7172" in snapshot
        assert "EEI8172" in snapshot
        assert len(snapshot) >= 2
        assert snapshot is not list_courses()

    def test_course_exists(self) -> None:
        course = Course(code="EEI9172", department=_DEPT, level=3, credits=3)
        assert not course_exists("EEI9172")
        add_course(course)
        assert course_exists("EEI9172")
