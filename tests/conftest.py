import pytest
import pytest_asyncio

from data import clear_courses
from main import AppState, CourseApp


@pytest.fixture(autouse=True)
def clean_repo():
    clear_courses()
    # yield
    # clear_courses()


@pytest.fixture
def state() -> AppState:
    return AppState()


@pytest.fixture
def app(state) -> CourseApp:
    return CourseApp(state)


@pytest_asyncio.fixture
async def pilot(app):
    async with app.run_test(size=(80, 24)) as p:
        yield p


@pytest_asyncio.fixture
async def screen2_pilot(pilot):
    await pilot.press(*"EEI3372")
    await pilot.press("enter")
    await pilot.pause()
    return pilot
