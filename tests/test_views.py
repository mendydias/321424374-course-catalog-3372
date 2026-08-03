import pytest


class TestCourseView:
    @pytest.mark.asyncio
    async def test_invalid_code_shows_error(self, pilot):
        await pilot.press(*"bads")
        await pilot.press("enter")
        await pilot.pause()
        error = pilot.app.screen.query_one("#error")
        assert "-visible" in error.classes

    @pytest.mark.asyncio
    async def test_valid_code_navigates_to_screen2(self, screen2_pilot):
        assert "CourseNameLecturerSemesterView" in type(screen2_pilot.app.screen).__name__


class TestCourseNameLecturerSemesterView:
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
    async def test_successful_submission(self, screen2_pilot, state):
        await screen2_pilot.press(*"Digital Systems")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"John Smith")
        await screen2_pilot.press("tab")
        await screen2_pilot.press(*"2")
        await screen2_pilot.press("enter")
        await screen2_pilot.pause()
        assert state.course is not None
        assert state.course.code == "EEI3372"
        assert state.course.name == "Digital systems"
        assert state.course.semester == 2
        assert state.course.lecturer == "John Smith"
