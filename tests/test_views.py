import pytest

from main import CourseApp, _state
from data import clear_courses


@pytest.fixture(autouse=True)
def reset():
    _state.course = None
    clear_courses()


async def _navigate_to_screen2(pilot, app):
    await pilot.press(*"EEI3372")
    await pilot.press("enter")
    await pilot.pause()


class TestCourseView:
    @pytest.mark.asyncio
    async def test_invalid_code_shows_error(self):
        app = CourseApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.press(*"bads")
            await pilot.press("enter")
            await pilot.pause()
            error = app.screen.query_one("#error")
            assert "-visible" in error.classes

    @pytest.mark.asyncio
    async def test_valid_code_navigates_to_screen2(self):
        app = CourseApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await _navigate_to_screen2(pilot, app)
            assert "CourseNameLecturerSemesterView" in type(app.screen).__name__


class TestCourseNameLecturerSemesterView:
    @pytest.mark.asyncio
    async def test_displays_code_and_department(self):
        app = CourseApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await _navigate_to_screen2(pilot, app)
            assert "EEI3372" in app.screen.query_one("#course-code").content
            assert "Electrical" in app.screen.query_one("#department").content

    @pytest.mark.asyncio
    async def test_rejects_empty_name(self):
        app = CourseApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await _navigate_to_screen2(pilot, app)
            await pilot.press("enter")
            await pilot.pause()
            error = app.screen.query_one("#error")
            assert "-visible" in error.classes

    @pytest.mark.asyncio
    async def test_rejects_invalid_semester_string(self):
        app = CourseApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await _navigate_to_screen2(pilot, app)
            await pilot.press(*"Digital Systems")
            await pilot.press("tab")
            await pilot.press(*"John Smith")
            await pilot.press("tab")
            await pilot.press(*"abc")
            await pilot.press("enter")
            await pilot.pause()
            error = app.screen.query_one("#error")
            assert "-visible" in error.classes
            assert "number" in error.content.lower()

    @pytest.mark.asyncio
    async def test_successful_submission(self):
        app = CourseApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await _navigate_to_screen2(pilot, app)
            await pilot.press(*"Digital Systems")
            await pilot.press("tab")
            await pilot.press(*"John Smith")
            await pilot.press("tab")
            await pilot.press(*"2")
            await pilot.press("enter")
            await pilot.pause()
            assert _state.course is not None
            assert _state.course.code == "EEI3372"
            assert _state.course.name == "Digital systems"
            assert _state.course.semester == 2
            assert _state.course.lecturer == "John Smith"
