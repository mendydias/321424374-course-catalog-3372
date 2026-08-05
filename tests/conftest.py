import pytest
import pytest_asyncio

from data import add_course, clear_courses, get_department
from main import CourseApp
from models import Course


@pytest.fixture(autouse=True)
def clean_repo():
    clear_courses()
    # yield
    # clear_courses()


@pytest.fixture
def app() -> CourseApp:
    return CourseApp()


@pytest_asyncio.fixture
async def pilot(app):
    async with app.run_test(size=(80, 24)) as p:
        yield p


@pytest_asyncio.fixture
async def screen2_pilot(pilot):
    await pilot.click("#add-course")
    await pilot.pause()
    await pilot.press(*"EEI3372")
    await pilot.press("enter")
    await pilot.pause()
    return pilot


@pytest_asyncio.fixture
async def seeded_pilot(pilot):
    dept = get_department("EE")
    assert dept is not None
    add_course(Course(code="EEI3372", department=dept, level=3, credits=3,
                      name="Digital systems", semester=2, lecturer="John Smith"))
    add_course(Course(code="EEI2262", department=dept, level=2, credits=2,
                      name="Circuit theory", semester=1, lecturer="Jane Doe"))
    return pilot
