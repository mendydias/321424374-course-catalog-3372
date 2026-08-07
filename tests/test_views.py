import pytest
from textual.widgets import Button, DataTable, Input, Label

from controllers import CourseDTO
from data import course_exists, get_course, remove_course
from views import (
    CourseActionModal,
    CourseDeleteConfirmModal,
    CourseListView,
    HomeView,
    UpdateCourseView,
    filter_courses,
)


class TestHomeView:
    @pytest.mark.asyncio
    async def test_launch_shows_home_view(self, pilot):
        assert type(pilot.app.screen).__name__ == "HomeView"

    @pytest.mark.asyncio
    async def test_add_course_button_pushes_department_view(self, pilot):
        await pilot.click("#add-course")
        await pilot.pause()
        assert type(pilot.app.screen).__name__ == "CreateCourseDepartmentView"


class TestCreateCourseDepartmentView:
    @pytest.mark.asyncio
    async def test_invalid_code_shows_error(self, pilot):
        await pilot.click("#add-course")
        await pilot.pause()
        await pilot.press(*"bads")
        await pilot.press("enter")
        await pilot.pause()
        error = pilot.app.screen.query_one("#error")
        assert "-visible" in error.classes

    @pytest.mark.asyncio
    async def test_valid_code_navigates_to_screen2(self, screen2_pilot):
        assert "CreateCourseNameLecturerSemesterView" in type(screen2_pilot.app.screen).__name__

    @pytest.mark.asyncio
    async def test_back_button_returns_to_home(self, pilot):
        await pilot.click("#add-course")
        await pilot.pause()
        await pilot.click("#back")
        await pilot.pause()
        assert type(pilot.app.screen).__name__ == "HomeView"

    @pytest.mark.asyncio
    async def test_escape_returns_to_home(self, pilot):
        await pilot.click("#add-course")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert type(pilot.app.screen).__name__ == "HomeView"

    @pytest.mark.asyncio
    async def test_back_button_does_not_trigger_submit(self, pilot):
        await pilot.click("#add-course")
        await pilot.pause()
        await pilot.press(*"bads")
        await pilot.click("#back")
        await pilot.pause()
        assert type(pilot.app.screen).__name__ == "HomeView"


class TestCreateCourseNameLecturerSemesterView:
    @pytest.mark.asyncio
    async def test_displays_code_and_department(self, screen2_pilot):
        assert "EEI3372" in screen2_pilot.app.screen.query_one("#course-code").content
        assert "Electrical" in screen2_pilot.app.screen.query_one("#department").content

    @pytest.mark.asyncio
    async def test_rejects_empty_name(self, screen2_pilot):
        await screen2_pilot.press("enter")
        await screen2_pilot.pause()
        error = screen2_pilot.app.screen.query_one("#error")
        assert "-visible" in error.classes

    @pytest.mark.asyncio
    async def test_rejects_invalid_semester_string(self, screen2_pilot):
        await screen2_pilot.press(*"Digital Systems")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"John Smith")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"abc")
        await screen2_pilot.press("enter")
        await screen2_pilot.pause()
        error = screen2_pilot.app.screen.query_one("#error")
        assert "-visible" in error.classes
        assert "number" in error.content.lower()

    @pytest.mark.asyncio
    async def test_successful_submission(self, screen2_pilot, app):
        await screen2_pilot.press(*"Digital Systems")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"John Smith")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"2")
        await screen2_pilot.press("enter")
        await screen2_pilot.pause()
        course = app.state()
        assert course.code == "EEI3372"
        assert course.name == "Digital systems"
        assert course.semester == 2
        assert course.lecturer == "John Smith"
        course.name = "X"
        assert app.state().name == "Digital systems"

    @pytest.mark.asyncio
    async def test_submission_returns_to_home_view(self, screen2_pilot):
        await screen2_pilot.press(*"Digital Systems")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"John Smith")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"2")
        await screen2_pilot.press("enter")
        await screen2_pilot.pause()
        assert type(screen2_pilot.app.screen).__name__ == "HomeView"
        assert course_exists("EEI3372")

    @pytest.mark.asyncio
    async def test_semester_upper_boundary_accepted(self, screen2_pilot):
        await screen2_pilot.press(*"Digital Systems")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"John Smith")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"8")
        await screen2_pilot.press("enter")
        await screen2_pilot.pause()
        assert type(screen2_pilot.app.screen).__name__ == "HomeView"
        stored = get_course("EEI3372")
        assert stored is not None
        assert stored.semester == 8

    @pytest.mark.asyncio
    async def test_re_add_resets_course_state(self, screen2_pilot, app):
        await screen2_pilot.press(*"Digital Systems")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"John Smith")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"2")
        await screen2_pilot.press("enter")
        await screen2_pilot.pause()
        await screen2_pilot.click("#add-course")
        await screen2_pilot.pause()
        assert app.state().code == ""

    @pytest.mark.asyncio
    async def test_back_button_returns_to_department(self, screen2_pilot):
        await screen2_pilot.click("#back")
        await screen2_pilot.pause()
        assert type(screen2_pilot.app.screen).__name__ == "CreateCourseDepartmentView"

    @pytest.mark.asyncio
    async def test_escape_returns_to_department(self, screen2_pilot):
        await screen2_pilot.press("escape")
        await screen2_pilot.pause()
        assert type(screen2_pilot.app.screen).__name__ == "CreateCourseDepartmentView"


class TestCourseListView:
    @pytest.mark.asyncio
    async def test_empty_repo_shows_empty_label(self, pilot):
        await pilot.click("#view-courses")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseListView)
        label = pilot.app.screen.query_one("#empty", Label)
        assert str(label.content) == "Courses table is empty."

    @pytest.mark.asyncio
    async def test_empty_repo_has_no_table(self, pilot):
        await pilot.click("#view-courses")
        await pilot.pause()
        assert len(list(pilot.app.screen.query(DataTable))) == 0

    @pytest.mark.asyncio
    async def test_seeded_repo_shows_table_not_label(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseListView)
        pilot.app.screen.query_one("#courses-table", DataTable)
        assert len(list(pilot.app.screen.query("#empty"))) == 0

    @pytest.mark.asyncio
    async def test_table_cursor_type_is_row(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.cursor_type == "row"

    @pytest.mark.asyncio
    async def test_table_zebra_stripes_enabled(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.zebra_stripes is True

    @pytest.mark.asyncio
    async def test_table_columns(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert [str(c.label) for c in table.ordered_columns] == [
            "Code", "Name", "Department", "Level", "Credits", "Semester", "Lecturer"
        ]

    @pytest.mark.asyncio
    async def test_table_rows_keyed_by_code(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert {rk.value for rk in table.rows} == {"EEI3372", "EEI2262"}
        assert table.row_count == 2

    @pytest.mark.asyncio
    async def test_table_row_content(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.get_row("EEI3372") == [
            "EEI3372", "Digital systems", "Electrical and Computer Engineering", "3", "3", "2", "John Smith"
        ]

    @pytest.mark.asyncio
    async def test_escape_returns_to_home(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(pilot.app.screen, HomeView)

    @pytest.mark.asyncio
    async def test_courses_added_via_add_flow_appear(self, screen2_pilot):
        pilot = screen2_pilot
        await pilot.press(*"Digital Systems")
        await pilot.press("tab")
        await pilot.press(*"John Smith")
        await pilot.press("tab")
        await pilot.press(*"2")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.click("#view-courses")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 1
        assert "EEI3372" in {rk.value for rk in table.rows}


class TestFilterCourses:
    @staticmethod
    def _seed() -> dict[str, CourseDTO]:
        return {
            "EEI3372": CourseDTO(code="EEI3372", department="Electrical and Computer Engineering",
                                 level="3", credits="3",
                                 name="Digital systems", semester="2", lecturer="John Smith"),
            "EEI2262": CourseDTO(code="EEI2262", department="Electrical and Computer Engineering",
                                 level="2", credits="2",
                                 name="Circuit theory", semester="1", lecturer="Jane Doe"),
        }

    def test_empty_key_returns_full_dict_unchanged(self):
        courses = self._seed()
        assert filter_courses(courses, "") is courses

    def test_code_substring_matches_both(self):
        assert set(filter_courses(self._seed(), "EEI")) == {"EEI3372", "EEI2262"}

    def test_numeric_substring_matches_one(self):
        assert set(filter_courses(self._seed(), "3372")) == {"EEI3372"}

    def test_filter_is_case_insensitive(self):
        assert set(filter_courses(self._seed(), "eei2262")) == {"EEI2262"}

    def test_no_match_returns_empty_dict(self):
        assert filter_courses(self._seed(), "XYZ") == {}

    def test_field_value_matches_by_field(self):
        assert set(filter_courses(self._seed(), "name:circuit")) == {"EEI2262"}

    def test_field_search_is_case_insensitive(self):
        assert set(filter_courses(self._seed(), "Name:CIRCUIT")) == {"EEI2262"}

    def test_numeric_field_matches_via_str_coercion(self):
        assert set(filter_courses(self._seed(), "level:3")) == {"EEI3372"}
        assert set(filter_courses(self._seed(), "semester:1")) == {"EEI2262"}

    def test_code_field_matches(self):
        assert set(filter_courses(self._seed(), "code:2262")) == {"EEI2262"}

    def test_field_mode_does_not_fall_back_to_code(self):
        assert filter_courses(self._seed(), "name:eei") == {}

    def test_value_with_colon_does_not_raise(self):
        assert filter_courses(self._seed(), "name:a:b") == {}

    def test_unknown_field_returns_empty(self):
        assert filter_courses(self._seed(), "bogus:x") == {}

    def test_empty_value_after_colon_matches_all(self):
        assert set(filter_courses(self._seed(), "name:")) == {"EEI3372", "EEI2262"}

    def test_department_name_matches(self):
        assert set(filter_courses(self._seed(), "department:electrical")) == {
            "EEI3372",
            "EEI2262",
        }


class TestCourseListViewSearch:
    @pytest.mark.asyncio
    async def test_search_input_shown_when_seeded(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        pilot.app.screen.query_one("#search", Input)

    @pytest.mark.asyncio
    async def test_search_input_hidden_when_empty(self, pilot):
        await pilot.click("#view-courses")
        await pilot.pause()
        assert list(pilot.app.screen.query("#search")) == []

    @pytest.mark.asyncio
    async def test_typing_filters_rows(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#search")
        await pilot.press(*"3372")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 1
        assert {rk.value for rk in table.rows} == {"EEI3372"}

    @pytest.mark.asyncio
    async def test_filter_case_insensitive(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#search")
        await pilot.press(*"eei2262")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 1
        assert {rk.value for rk in table.rows} == {"EEI2262"}

    @pytest.mark.asyncio
    async def test_no_match_shows_zero_rows(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#search")
        await pilot.press(*"XYZ")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 0
        assert len(table.ordered_columns) == 7

    @pytest.mark.asyncio
    async def test_clearing_input_restores_rows(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#search")
        await pilot.press(*"3372")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 1
        search = pilot.app.screen.query_one("#search", Input)
        search.value = ""
        await pilot.pause()
        assert table.row_count == 2

    @pytest.mark.asyncio
    async def test_typing_field_value_filters_rows(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#search")
        await pilot.press(*"name:circuit")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 1
        assert {rk.value for rk in table.rows} == {"EEI2262"}

    @pytest.mark.asyncio
    async def test_numeric_field_search_filters_rows(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#search")
        await pilot.press(*"level:2")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 1
        assert {rk.value for rk in table.rows} == {"EEI2262"}

    @pytest.mark.asyncio
    async def test_unknown_field_shows_zero_rows(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#search")
        await pilot.press(*"bogus:x")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 0
        assert len(table.ordered_columns) == 7

    @pytest.mark.asyncio
    async def test_colon_in_value_does_not_crash(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#search")
        await pilot.press(*"name:a:b")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 0


class TestCourseActionModal:
    @pytest.mark.asyncio
    async def test_row_selection_opens_modal_with_three_buttons(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#courses-table")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseActionModal)
        for button_id in ("update", "delete", "cancel"):
            pilot.app.screen.query_one(f"#{button_id}", Button)

    @pytest.mark.asyncio
    async def test_cancel_returns_to_list(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#courses-table")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.click("#cancel")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseListView)

    @pytest.mark.asyncio
    async def test_escape_closes_modal(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#courses-table")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseListView)

    @pytest.mark.asyncio
    async def test_selecting_second_row_targets_that_course_not_the_first(
        self, seeded_pilot
    ):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#courses-table")
        await pilot.press("down")  # move cursor off row 0 (EEI3372) onto row 1 (EEI2262)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseActionModal)
        await pilot.click("#delete")
        await pilot.pause()
        await pilot.click("#yes")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseListView)
        assert get_course("EEI2262") is None
        assert get_course("EEI3372") is not None
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert {rk.value for rk in table.rows} == {"EEI3372"}


class TestCourseDeleteConfirmModal:
    @staticmethod
    async def _open_confirm_modal(pilot) -> None:
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#courses-table")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.click("#delete")
        await pilot.pause()

    @pytest.mark.asyncio
    async def test_delete_button_opens_confirm_modal(self, seeded_pilot):
        pilot = seeded_pilot
        await self._open_confirm_modal(pilot)
        assert isinstance(pilot.app.screen, CourseDeleteConfirmModal)
        pilot.app.screen.query_one("#yes", Button)
        pilot.app.screen.query_one("#no", Button)

    @pytest.mark.asyncio
    async def test_no_keeps_course_and_returns_to_action_modal(self, seeded_pilot):
        pilot = seeded_pilot
        await self._open_confirm_modal(pilot)
        await pilot.click("#no")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseActionModal)
        assert get_course("EEI3372") is not None

    @pytest.mark.asyncio
    async def test_escape_keeps_course_and_returns_to_action_modal(self, seeded_pilot):
        pilot = seeded_pilot
        await self._open_confirm_modal(pilot)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseActionModal)
        assert get_course("EEI3372") is not None

    @pytest.mark.asyncio
    async def test_yes_deletes_course_and_returns_to_list(self, seeded_pilot):
        pilot = seeded_pilot
        await self._open_confirm_modal(pilot)
        await pilot.click("#yes")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseListView)
        assert get_course("EEI3372") is None
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert {rk.value for rk in table.rows} == {"EEI2262"}

    @pytest.mark.asyncio
    async def test_yes_after_course_already_removed_notifies_and_stays_on_action_modal(
        self, seeded_pilot
    ):
        pilot = seeded_pilot
        await self._open_confirm_modal(pilot)
        remove_course("EEI3372")  # simulate concurrent removal before confirming
        await pilot.click("#yes")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseActionModal)


class TestUpdateCourseView:
    @staticmethod
    async def _open_form(pilot) -> None:
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#courses-table")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.click("#update")
        await pilot.pause()

    @pytest.mark.asyncio
    async def test_update_form_shows_current_values(self, seeded_pilot):
        pilot = seeded_pilot
        await self._open_form(pilot)
        assert isinstance(pilot.app.screen, UpdateCourseView)
        assert pilot.app.screen.query_one("#name", Input).value == "Digital systems"
        assert pilot.app.screen.query_one("#lecturer", Input).value == "John Smith"
        assert pilot.app.screen.query_one("#semester", Input).value == "2"

    @pytest.mark.asyncio
    async def test_submit_updates_course_and_returns_to_list(self, seeded_pilot):
        pilot = seeded_pilot
        await self._open_form(pilot)
        pilot.app.screen.query_one("#lecturer", Input).value = "Alice Ray"
        await pilot.pause()
        await pilot.click("#submit")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseListView)
        stored = get_course("EEI3372")
        assert stored is not None
        assert stored.lecturer == "Alice Ray"
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.get_row("EEI3372")[6] == "Alice Ray"

    @pytest.mark.asyncio
    async def test_invalid_submit_shows_error_and_keeps_course(self, seeded_pilot):
        pilot = seeded_pilot
        await self._open_form(pilot)
        pilot.app.screen.query_one("#name", Input).value = ""
        await pilot.pause()
        await pilot.click("#submit")
        await pilot.pause()
        error = pilot.app.screen.query_one("#error", Label)
        assert "-visible" in error.classes
        stored = get_course("EEI3372")
        assert stored is not None
        assert stored.name == "Digital systems"

    @pytest.mark.asyncio
    async def test_invalid_semester_text_shows_error_and_keeps_course(self, seeded_pilot):
        pilot = seeded_pilot
        await self._open_form(pilot)
        pilot.app.screen.query_one("#semester", Input).value = "abc"
        await pilot.pause()
        await pilot.click("#submit")
        await pilot.pause()
        error = pilot.app.screen.query_one("#error", Label)
        assert "-visible" in error.classes
        assert "between 1 and 8" in str(error.content)
        stored = get_course("EEI3372")
        assert stored is not None
        assert stored.semester == 2

    @pytest.mark.asyncio
    async def test_reset_restores_original_values(self, seeded_pilot):
        pilot = seeded_pilot
        await self._open_form(pilot)
        pilot.app.screen.query_one("#name", Input).value = "Changed name"
        pilot.app.screen.query_one("#lecturer", Input).value = "Someone Else"
        pilot.app.screen.query_one("#semester", Input).value = "5"
        await pilot.pause()
        await pilot.click("#reset")
        await pilot.pause()
        screen = pilot.app.screen
        assert screen.query_one("#name", Input).value == "Digital systems"
        assert screen.query_one("#lecturer", Input).value == "John Smith"
        assert screen.query_one("#semester", Input).value == "2"
