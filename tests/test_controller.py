import pytest

from controllers import CourseError, save_course
from models import Course
from models.department import Department


def _parse_course_code(code: str) -> Course:
    from controllers.course_controller import _parse_course_code as _priv
    return _priv(code)


class TestParseCourseCode:
    def test_parse_valid_code(self) -> None:
        course = _parse_course_code("EEI3372")
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
        course = _parse_course_code(raw)
        assert course.code == "EEI3372"

    @pytest.mark.parametrize(
        ("raw", "expected_level"),
        [
            ("EEI1372", 1),
            ("EEI4372", 4),
        ],
    )
    def test_level_boundaries_valid(self, raw: str, expected_level: int) -> None:
        course = _parse_course_code(raw)
        assert course.level == expected_level

    @pytest.mark.parametrize(
        ("raw", "expected_credits"),
        [
            ("EEI3172", 1),
            ("EEI3672", 6),
        ],
    )
    def test_credit_boundaries_valid(self, raw: str, expected_credits: int) -> None:
        course = _parse_course_code(raw)
        assert course.credits == expected_credits

    def test_unknown_department(self) -> None:
        with pytest.raises(CourseError) as exc:
            _parse_course_code("XXI3372")
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
            _parse_course_code(raw)

    @pytest.mark.parametrize(
        ("raw", "level"),
        [
            ("EEI0372", 0),
            ("EEI5372", 5),
        ],
    )
    def test_level_out_of_range(self, raw: str, level: int) -> None:
        with pytest.raises(CourseError) as exc:
            _parse_course_code(raw)
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
            _parse_course_code(raw)
        msg = str(exc.value)
        assert "Credit count" in msg
        assert str(credits) in msg
        assert "between 1 and 6" in msg


class TestSaveCourse:
    def test_valid(self) -> None:
        course = save_course("EEI3372", "digital systems", 1, "john smith")
        assert course.code == "EEI3372"
        assert course.name == "Digital systems"
        assert course.semester == 1
        assert course.lecturer == "John Smith"
        assert course.department == Department(code="EE", name="Electrical and Computer Engineering")
        assert course.level == 3
        assert course.credits == 3

    @pytest.mark.parametrize(
        ("raw_name", "expected"),
        [
            ("digital systems", "Digital systems"),
            ("DIGITAL SYSTEMS", "Digital systems"),
            ("Digital Systems", "Digital systems"),
        ],
    )
    def test_name_sentence_case_normalization(self, raw_name: str, expected: str) -> None:
        course = save_course("EEI3372", raw_name, 1, "John Smith")
        assert course.name == expected

    @pytest.mark.parametrize(
        ("raw_lecturer", "expected"),
        [
            ("john smith", "John Smith"),
            ("JOHN SMITH", "John Smith"),
            ("john SMITH", "John Smith"),
        ],
    )
    def test_lecturer_title_case_normalization(self, raw_lecturer: str, expected: str) -> None:
        course = save_course("EEI3372", "Digital Systems", 1, raw_lecturer)
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
        with pytest.raises(CourseError, match=match):
            save_course("EEI3372", name, semester, lecturer)
