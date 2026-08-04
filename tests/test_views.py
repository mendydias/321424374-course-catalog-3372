import pytest

from data import course_exists


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
