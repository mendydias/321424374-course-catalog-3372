import pytest

from controllers import CourseCodeError, parse_course_code
from models import Course


class TestParseCourseCode:
    def test_parse_valid_code(self) -> None:
        course = parse_course_code("EEI3372")
        assert course == Course(
            code="EEI3372",
            department="Electrical and Computer Engineering",
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
        course = parse_course_code(raw)
        assert course.code == "EEI3372"

    @pytest.mark.parametrize(
        ("raw", "expected_level"),
        [
            ("EEI1372", 1),
            ("EEI4372", 4),
        ],
    )
    def test_level_boundaries_valid(self, raw: str, expected_level: int) -> None:
        course = parse_course_code(raw)
        assert course.level == expected_level

    @pytest.mark.parametrize(
        ("raw", "expected_credits"),
        [
            ("EEI3172", 1),
            ("EEI3672", 6),
        ],
    )
    def test_credit_boundaries_valid(self, raw: str, expected_credits: int) -> None:
        course = parse_course_code(raw)
        assert course.credits == expected_credits

    def test_unknown_department(self) -> None:
        with pytest.raises(CourseCodeError) as exc:
            parse_course_code("XXI3372")
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
        with pytest.raises(CourseCodeError, match="Invalid course code format"):
            parse_course_code(raw)

    @pytest.mark.parametrize(
        ("raw", "level"),
        [
            ("EEI0372", 0),
            ("EEI5372", 5),
        ],
    )
    def test_level_out_of_range(self, raw: str, level: int) -> None:
        with pytest.raises(CourseCodeError) as exc:
            parse_course_code(raw)
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
        with pytest.raises(CourseCodeError) as exc:
            parse_course_code(raw)
        msg = str(exc.value)
        assert "Credit count" in msg
        assert str(credits) in msg
        assert "between 1 and 6" in msg
