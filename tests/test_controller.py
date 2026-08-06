import pytest

from controllers import CourseDTO, CourseError, create_course, list_courses, register_course, update_course
from data import course_exists, get_course
from models import Course, Department


class TestParseCourseCode:
    def test_parse_valid_code(self) -> None:
        course = create_course("EEI3372")
        assert course == Course(
            code="EEI3372",
            department=Department(code="EE", name="Electrical and Computer Engineering"),
            level=3,
            credits=3,
        )

    @pytest.mark.parametrize(
        "raw",
        [
            "EEI3372",
            "eei3372",
            "Eei3372",
            "eEI3372",
        ],
    )
    def test_case_normalization(self, raw: str) -> None:
        course = create_course(raw)
        assert course.code == "EEI3372"

    @pytest.mark.parametrize(
        ("raw", "expected_level"),
        [
            ("EEI1372", 1),
            ("EEI4372", 4),
        ],
    )
    def test_level_boundaries_valid(self, raw: str, expected_level: int) -> None:
        course = create_course(raw)
        assert course.level == expected_level

    @pytest.mark.parametrize(
        ("raw", "expected_credits"),
        [
            ("EEI3172", 1),
            ("EEI3672", 6),
        ],
    )
    def test_credit_boundaries_valid(self, raw: str, expected_credits: int) -> None:
        course = create_course(raw)
        assert course.credits == expected_credits

    def test_unknown_department(self) -> None:
        with pytest.raises(CourseError) as exc:
            create_course("XXI3372")
        msg = str(exc.value)
        assert "Unknown department code 'XX'" in msg
        assert "EE" in msg

    @pytest.mark.parametrize(
        "raw",
        [
            "",
            "EE3372",
            "EEII3372",
            "12I3372",
            "EEI33A2",
            "EEI337",
        ],
    )
    def test_malformed_input(self, raw: str) -> None:
        with pytest.raises(CourseError, match="Invalid course code format"):
            create_course(raw)

    @pytest.mark.parametrize(
        ("raw", "level"),
        [
            ("EEI0372", 0),
            ("EEI5372", 5),
        ],
    )
    def test_level_out_of_range(self, raw: str, level: int) -> None:
        with pytest.raises(CourseError) as exc:
            create_course(raw)
        msg = str(exc.value)
        assert str(level) in msg
        assert "between 1 and 4" in msg

    @pytest.mark.parametrize(
        ("raw", "credits"),
        [
            ("EEI3072", 0),
            ("EEI3772", 7),
        ],
    )
    def test_credits_out_of_range(self, raw: str, credits: int) -> None:
        with pytest.raises(CourseError) as exc:
            create_course(raw)
        msg = str(exc.value)
        assert "Credit count" in msg
        assert str(credits) in msg
        assert "between 1 and 6" in msg


class TestRegisterCourse:
    @staticmethod
    def _make_course(code: str, name: str, semester: int, lecturer: str) -> Course:
        course = create_course(code)
        course.name = name
        course.semester = semester
        course.lecturer = lecturer
        return course

    def test_valid(self) -> None:
        course = self._make_course("EEI3372", "digital systems", 1, "john smith")
        register_course(course)
        assert get_course("EEI3372") == course
        assert course.code == "EEI3372"
        assert course.name == "Digital systems"
        assert course.semester == 1
        assert course.lecturer == "John Smith"
        assert course.department == Department(code="EE", name="Electrical and Computer Engineering")
        assert course.level == 3
        assert course.credits == 3

    @pytest.mark.parametrize(
        ("code", "raw_name", "expected"),
        [
            ("EEI2172", "digital systems", "Digital systems"),
            ("EEI3172", "DIGITAL SYSTEMS", "Digital systems"),
            ("EEI4172", "Digital Systems", "Digital systems"),
        ],
    )
    def test_name_sentence_case_normalization(self, code: str, raw_name: str, expected: str) -> None:
        course = self._make_course(code, raw_name, 1, "John Smith")
        register_course(course)
        assert course.name == expected

    @pytest.mark.parametrize(
        ("code", "raw_lecturer", "expected"),
        [
            ("EEI1272", "john smith", "John Smith"),
            ("EEI2272", "JOHN SMITH", "John Smith"),
            ("EEI3272", "john SMITH", "John Smith"),
        ],
    )
    def test_lecturer_title_case_normalization(self, code: str, raw_lecturer: str, expected: str) -> None:
        course = self._make_course(code, "Digital Systems", 1, raw_lecturer)
        register_course(course)
        assert course.lecturer == expected

    @pytest.mark.parametrize(
        ("name", "semester", "lecturer", "match"),
        [
            ("", 1, "John Smith", "cannot be empty"),
            ("AB", 1, "John Smith", "longer than 3"),
            ("Digital Systems", 0, "John Smith", "between 1 and 8"),
            ("Digital Systems", 9, "John Smith", "between 1 and 8"),
            ("Digital Systems", -1, "John Smith", "between 1 and 8"),
            ("Digital Systems", 1, "", "cannot be empty"),
            ("Digital Systems", 1, "AB", "longer than 3"),
        ],
    )
    def test_validation_errors(self, name: str, semester: int, lecturer: str, match: str) -> None:
        course = self._make_course("EEI3372", name, semester, lecturer)
        with pytest.raises(CourseError, match=match):
            register_course(course)
        assert not course_exists("EEI3372")

    def test_duplicate_code_raises_error(self) -> None:
        course1 = self._make_course("EEI1372", "Digital Systems", 2, "Jane Doe")
        register_course(course1)
        course2 = self._make_course("EEI1372", "Digital Systems", 2, "Jane Doe")
        with pytest.raises(CourseError, match="already exists"):
            register_course(course2)


class TestUpdateCourse:
    @staticmethod
    def _make_course(code: str, name: str, semester: int, lecturer: str) -> Course:
        course = create_course(code)
        course.name = name
        course.semester = semester
        course.lecturer = lecturer
        return course

    def _register_base(self, code: str = "EEI3372") -> Course:
        course = self._make_course(code, "Digital systems", 2, "John Smith")
        register_course(course)
        stored = get_course(code)
        assert stored is not None
        return stored

    def test_update_nonexistent_code_rejected(self) -> None:
        course = self._make_course("EEI3372", "Digital Systems", 1, "John Smith")
        with pytest.raises(CourseError, match="not found"):
            update_course(course)
        assert not course_exists("EEI3372")

    def test_existence_checked_before_field_validation(self) -> None:
        course = self._make_course("EEI3372", "", 1, "John Smith")
        with pytest.raises(CourseError, match="not found"):
            update_course(course)

    def test_update_lecturer_changes_only_that_field(self) -> None:
        original = self._register_base("EEI3372")
        updated = self._make_course("EEI3372", "Digital systems", 2, "Jane Doe")
        update_course(updated)
        stored = get_course("EEI3372")
        assert stored is not None
        assert stored.lecturer == "Jane Doe"
        assert stored.code == "EEI3372"
        assert stored.department == original.department
        assert stored.level == original.level
        assert stored.credits == original.credits
        assert stored.name == original.name
        assert stored.semester == original.semester

    @pytest.mark.parametrize(
        ("field", "raw", "expected"),
        [
            ("name", "CIRCUIT THEORY", "Circuit theory"),
            ("name", "digital systems", "Digital systems"),
            ("lecturer", "JANE DOE", "Jane Doe"),
            ("lecturer", "jane SMITH", "Jane Smith"),
        ],
    )
    def test_update_normalizes_casing(self, field: str, raw: str, expected: str) -> None:
        self._register_base("EEI3372")
        updated = self._make_course("EEI3372", "Digital systems", 2, "John Smith")
        if field == "name":
            updated.name = raw
        else:
            updated.lecturer = raw
        update_course(updated)
        stored = get_course("EEI3372")
        assert stored is not None
        assert getattr(stored, field) == expected

    @pytest.mark.parametrize(
        ("name", "semester", "lecturer", "match"),
        [
            ("", 1, "John Smith", "cannot be empty"),
            ("AB", 1, "John Smith", "longer than 3"),
            ("Digital Systems", 0, "John Smith", "between 1 and 8"),
            ("Digital Systems", 9, "John Smith", "between 1 and 8"),
            ("Digital Systems", -1, "John Smith", "between 1 and 8"),
            ("Digital Systems", 1, "", "cannot be empty"),
            ("Digital Systems", 1, "AB", "longer than 3"),
        ],
    )
    def test_update_validation_errors(self, name: str, semester: int, lecturer: str, match: str) -> None:
        original = self._register_base("EEI3372")
        updated = self._make_course("EEI3372", name, semester, lecturer)
        with pytest.raises(CourseError, match=match):
            update_course(updated)
        stored = get_course("EEI3372")
        assert stored is not None
        assert stored == original


class TestListCourses:
    def test_list_courses_empty(self) -> None:
        assert list_courses() == {}

    def test_list_courses_returns_all(self) -> None:
        course = create_course("EEI3372")
        course.name = "Digital Systems"
        course.semester = 2
        course.lecturer = "John Smith"
        register_course(course)

        result = list_courses()
        assert len(result) == 1
        assert "EEI3372" in result
        assert result["EEI3372"] == CourseDTO.from_course(course)

    def test_list_courses_returns_copy(self) -> None:
        course = create_course("EEI3372")
        course.name = "Digital Systems"
        course.semester = 2
        course.lecturer = "John Smith"
        register_course(course)

        list_courses().clear()
        assert len(list_courses()) == 1
