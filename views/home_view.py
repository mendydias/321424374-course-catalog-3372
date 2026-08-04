from collections.abc import Callable

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from models import Course

from views.create_course_department_view import CreateCourseDepartmentView


class HomeView(Screen):
    CSS_PATH = "home_view.tcss"
    BINDINGS = [Binding("escape", "app.quit")]

    def __init__(self, on_submit: Callable[[Course], None]) -> None:
        super().__init__()
        self._on_submit = on_submit

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="menu"):
            yield Button("Add Course", id="add-course", variant="primary")
            yield Button("View Courses", id="view-courses")
        yield Footer()

    @on(Button.Pressed, "#add-course")
    def _add_course(self) -> None:
        self.app.push_screen(CreateCourseDepartmentView(self._on_submit))
