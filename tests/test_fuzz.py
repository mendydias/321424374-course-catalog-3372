import re
from typing import Any

import pytest
from hypothesis import given, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

from controllers import (
    CourseDTO,
    CourseError,
    create_course,
    delete_course,
    list_courses,
    register_course,
    update_course,
)
from data import clear_courses, course_exists
from models import Course

SPEC_PATTERN = re.compile(r"[A-Za-z]{3}\d{4}")

arbitrary = st.text()

non_matching = st.text().filter(lambda s: not SPEC_PATTERN.fullmatch(s.strip().upper()))

valid_codes = st.from_regex(
    re.compile(r"[Ee]{2}[A-Za-z][1-4][1-6][0-9]{2}"), fullmatch=True
)

_padding = st.text(alphabet=" \t", max_size=3)
padded_valid_codes = st.tuples(_padding, valid_codes, _padding).map(
    lambda t: t[0] + t[1] + t[2]
)


def make_course(code: str) -> Course:
    course = create_course(code)
    course.name = "Fuzz course"
    course.semester = 1
    course.lecturer = "Dr Fuzz"
    return course


def recase(code: str) -> str:
    return "".join(c.lower() if i % 2 else c.upper() for i, c in enumerate(code))


class TestParserTotality:
    @given(arbitrary)
    def test_create_course_is_total(self, s: str) -> None:
        try:
            course = create_course(s)
        except CourseError:
            return
        assert course.code == s.strip().upper()
        assert SPEC_PATTERN.fullmatch(s.strip().upper())


class TestFormatErrorPrecedence:
    @given(non_matching)
    def test_format_error_precedes_others(self, s: str) -> None:
        with pytest.raises(CourseError) as exc:
            create_course(s)
        message = str(exc.value)
        assert "Invalid course code format" in message
        assert "Unknown department" not in message
        assert "out of range" not in message
        assert "Credit count" not in message


class TestCodeRoundTrip:
    @given(padded_valid_codes)
    def test_code_round_trips(self, raw: str) -> None:
        course = create_course(raw)
        normalized = raw.strip().upper()
        assert course.code == normalized
        assert CourseDTO.from_course(course).code == course.code
        assert course.level == int(normalized[3])
        assert course.credits == int(normalized[4])


class TestCaseNormalization:
    @given(valid_codes)
    def test_parse_layer_normalizes(self, v: str) -> None:
        assert create_course(v).code == v.strip().upper()

    @given(valid_codes)
    def test_repo_layer_case_insensitive(self, v: str) -> None:
        clear_courses()
        register_course(make_course(v))
        normalized = v.strip().upper()
        variants = {v, normalized, normalized.lower(), recase(normalized)}
        for variant in variants:
            assert course_exists(variant)
        with pytest.raises(CourseError, match="already exists"):
            register_course(make_course(recase(normalized)))
        assert len(list_courses()) == 1


from controllers.course_controller import validate_course

printable_text = st.text(
    alphabet=st.characters(blacklist_categories=("Cs", "Cc"), min_codepoint=32),
    min_size=4,
    max_size=40,
)
valid_field_text = printable_text.filter(lambda s: len(s.strip()) > 3)
valid_semesters = st.integers(min_value=1, max_value=8)


class TestValidateCourseFuzz:
    @given(name=valid_field_text, lecturer=valid_field_text, semester=valid_semesters)
    def test_sufficiently_long_fields_are_accepted_without_crashing(
        self, name: str, lecturer: str, semester: int
    ) -> None:
        course = create_course("EEI3372")
        course.name = name
        course.lecturer = lecturer
        course.semester = semester
        validated = validate_course(course)
        assert len(validated.name) > 3
        assert len(validated.lecturer) > 3
        assert validated.semester == semester
        assert validated.name == validated.name.strip()
        assert validated.lecturer == validated.lecturer.strip()

    @given(name=st.text(max_size=3))
    def test_name_at_or_under_three_chars_always_rejected(self, name: str) -> None:
        course = create_course("EEI3372")
        course.name = name
        course.lecturer = "Dr Fuzz"
        course.semester = 1
        with pytest.raises(CourseError):
            validate_course(course)

    @given(semester=st.integers().filter(lambda s: s <= 0 or s >= 9))
    def test_semester_outside_1_to_8_always_rejected(self, semester: int) -> None:
        course = create_course("EEI3372")
        course.name = "Fuzz course"
        course.lecturer = "Dr Fuzz"
        course.semester = semester
        with pytest.raises(CourseError, match="between 1 and 8"):
            validate_course(course)


CODE_POOL = [
    "EEI1172",
    "EEI2262",
    "EEI3372",
    "EEI4472",
    "EEI1272",
    "EEI1572",
    "EEI2272",
    "EEI3172",
    "EEI3672",
    "EEI4372",
]


@st.composite
def any_casing(draw: Any, code: str) -> str:
    chars = []
    for ch in code:
        if ch.isalpha():
            chars.append(draw(st.sampled_from([ch.lower(), ch.upper()])))
        else:
            chars.append(ch)
    return "".join(chars)


cased_code = st.sampled_from(CODE_POOL).flatmap(any_casing)


class CourseStateMachine(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        clear_courses()
        self.model: set[str] = set()
        self.successful_adds = 0
        self.successful_deletes = 0

    @rule(code=cased_code)
    def add(self, code: str) -> None:
        key = code.strip().upper()
        if key in self.model:
            with pytest.raises(CourseError):
                register_course(make_course(code))
        else:
            register_course(make_course(code))
            self.model.add(key)
            self.successful_adds += 1

    @rule(code=cased_code)
    def delete(self, code: str) -> None:
        key = code.strip().upper()
        if key in self.model:
            delete_course(code)
            self.model.discard(key)
            self.successful_deletes += 1
        else:
            with pytest.raises(CourseError):
                delete_course(code)

    @rule(code=cased_code)
    def update(self, code: str) -> None:
        key = code.strip().upper()
        if key in self.model:
            update_course(make_course(code))
        else:
            with pytest.raises(CourseError):
                update_course(make_course(code))

    @invariant()
    def repo_count_matches_model(self) -> None:
        assert len(list_courses()) == self.successful_adds - self.successful_deletes

    @invariant()
    def repo_keys_unique_uppercase(self) -> None:
        keys = list(list_courses())
        assert len(keys) == len(set(keys))
        assert all(key == key.upper() for key in keys)

    def teardown(self) -> None:
        clear_courses()


TestCourseSequences = CourseStateMachine.TestCase
