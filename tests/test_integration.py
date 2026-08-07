import subprocess
import sys
from pathlib import Path

import pytest
from textual.widgets import DataTable, Input, Label

from controllers import list_courses as controller_list_courses
from data import get_course, list_courses
from views import (
    CourseActionModal,
    CourseDeleteConfirmModal,
    CourseListView,
    CreateCourseDepartmentView,
    CreateCourseNameLecturerSemesterView,
    HomeView,
    UpdateCourseView,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

ROW_3372 = [
    "EEI3372", "Digital systems", "Electrical and Computer Engineering", "3", "3", "2", "John Smith"
]
ROW_2262 = [
    "EEI2262", "Circuit theory", "Electrical and Computer Engineering", "2", "2", "1", "Jane Doe"
]


async def _add_course_via_ui(pilot, code, name, lecturer, semester) -> None:
    await pilot.click("#add-course")
    await pilot.pause()
    await pilot.press(*code)
    await pilot.press("enter")
    await pilot.pause()
    await pilot.press(*name)
    await pilot.press("tab")
    await pilot.press(*lecturer)
    await pilot.press("tab")
    await pilot.press(*semester)
    await pilot.press("enter")
    await pilot.pause()


async def _select_row(pilot) -> None:
    await pilot.click("#courses-table")
    await pilot.press("enter")
    await pilot.pause()


class TestInt1AddThenView:
    @pytest.mark.asyncio
    async def test_two_courses_added_show_formatted_in_view_all(self, pilot):
        await _add_course_via_ui(pilot, "EEI3372", "Digital Systems", "John Smith", "2")
        assert isinstance(pilot.app.screen, HomeView)
        await _add_course_via_ui(pilot, "EEI2262", "Circuit Theory", "Jane Doe", "1")
        await pilot.click("#view-courses")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 2
        assert {rk.value for rk in table.rows} == {"EEI3372", "EEI2262"}
        assert table.get_row("EEI3372") == ROW_3372
        assert table.get_row("EEI2262") == ROW_2262


class TestInt2AddRejectionLoop:
    @pytest.mark.asyncio
    async def test_invalid_then_corrected_entry_added_exactly_once(self, pilot):
        await pilot.click("#add-course")
        await pilot.pause()
        await pilot.press(*"bads")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CreateCourseDepartmentView)
        errors = list(pilot.app.screen.query("#error"))
        assert len(errors) == 1
        assert "-visible" in errors[0].classes
        assert pilot.app.screen.query_one(Input).value == ""
        assert list_courses() == {}

        await pilot.press(*"EEI3372")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press(*"Digital Systems")
        await pilot.press("tab")
        await pilot.press(*"John Smith")
        await pilot.press("tab")
        await pilot.press(*"2")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, HomeView)
        assert len(list_courses()) == 1


class TestInt3DuplicateRejection:
    @pytest.mark.asyncio
    async def test_duplicate_code_rejected_catalog_holds_one(self, pilot):
        await _add_course_via_ui(pilot, "EEI3372", "Digital Systems", "John Smith", "2")

        await pilot.click("#add-course")
        await pilot.pause()
        await pilot.press(*"EEI3372")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CreateCourseNameLecturerSemesterView)
        await pilot.press(*"Systems Design")
        await pilot.press("tab")
        await pilot.press(*"Jane Doe")
        await pilot.press("tab")
        await pilot.press(*"3")
        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(pilot.app.screen, CreateCourseNameLecturerSemesterView)
        error = pilot.app.screen.query_one("#error", Label)
        assert "-visible" in error.classes
        assert "already exists" in str(error.content).lower()
        assert len(list_courses()) == 1
        stored = get_course("EEI3372")
        assert stored is not None
        assert stored.name == "Digital systems"
        assert stored.lecturer == "John Smith"
        assert stored.semester == 2


class TestInt4SearchUpdateSearch:
    @pytest.mark.asyncio
    async def test_update_reflects_in_filtered_and_unfiltered_list(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#search")
        await pilot.press(*"3372")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 1
        assert {rk.value for rk in table.rows} == {"EEI3372"}

        await _select_row(pilot)
        assert isinstance(pilot.app.screen, CourseActionModal)
        await pilot.click("#update")
        await pilot.pause()
        assert isinstance(pilot.app.screen, UpdateCourseView)
        pilot.app.screen.query_one("#lecturer", Input).value = "Alice Ray"
        await pilot.pause()
        await pilot.click("#submit")
        await pilot.pause()

        assert isinstance(pilot.app.screen, CourseListView)
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 1
        assert {rk.value for rk in table.rows} == {"EEI3372"}
        assert table.get_row("EEI3372")[6] == "Alice Ray"

        search = pilot.app.screen.query_one("#search", Input)
        search.value = ""
        await pilot.pause()
        assert table.row_count == 2
        assert table.get_row("EEI2262") == ROW_2262
        assert table.get_row("EEI3372") == [*ROW_3372[:6], "Alice Ray"]

        stored = get_course("EEI3372")
        assert stored is not None
        assert stored.lecturer == "Alice Ray"
        assert stored.name == "Digital systems"
        assert stored.semester == 2
        assert stored.level == 3
        assert stored.credits == 3


class TestInt5SearchDeleteView:
    @pytest.mark.asyncio
    async def test_deleted_course_removed_remaining_unchanged(self, seeded_pilot):
        pilot = seeded_pilot
        await pilot.click("#view-courses")
        await pilot.pause()
        await pilot.click("#search")
        await pilot.press(*"3372")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 1
        assert {rk.value for rk in table.rows} == {"EEI3372"}

        await _select_row(pilot)
        assert isinstance(pilot.app.screen, CourseActionModal)
        await pilot.click("#delete")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CourseDeleteConfirmModal)
        await pilot.click("#yes")
        await pilot.pause()

        assert isinstance(pilot.app.screen, CourseListView)
        assert get_course("EEI3372") is None
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 0

        search = pilot.app.screen.query_one("#search", Input)
        search.value = ""
        await pilot.pause()
        assert {rk.value for rk in table.rows} == {"EEI2262"}
        assert table.get_row("EEI2262") == ROW_2262


class TestInt8MultiCourseSession:
    @pytest.mark.asyncio
    async def test_courses_queryable_within_session(self, pilot):
        await _add_course_via_ui(pilot, "EEI3372", "Digital Systems", "John Smith", "2")
        await _add_course_via_ui(pilot, "EEI2262", "Circuit Theory", "Jane Doe", "1")
        assert set(controller_list_courses()) == {"EEI3372", "EEI2262"}

        await pilot.click("#view-courses")
        await pilot.pause()
        table = pilot.app.screen.query_one("#courses-table", DataTable)
        assert table.row_count == 2

        await pilot.click("#search")
        await pilot.press(*"2262")
        await pilot.pause()
        assert table.row_count == 1
        assert {rk.value for rk in table.rows} == {"EEI2262"}

    @pytest.mark.asyncio
    async def test_catalog_empty_on_restart(self, pilot):
        await _add_course_via_ui(pilot, "EEI3372", "Digital Systems", "John Smith", "2")
        assert len(list_courses()) == 1
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from data import list_courses; assert list_courses() == {}",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, result.stderr
