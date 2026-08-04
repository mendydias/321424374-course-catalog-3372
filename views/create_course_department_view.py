from collections.abc import Callable

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label

from controllers import CourseError, create_course
from models import Course

from views.create_course_name_lecturer_semester_view import (
    CreateCourseNameLecturerSemesterView,
)


class CreateCourseDepartmentView(Screen):
    CSS_PATH = "create_course_department_view.tcss"
    BINDINGS = [Binding("escape", "app.pop_screen")]

    def __init__(self, on_submit: Callable[[Course], None]) -> None:
        super().__init__()
        self._on_submit = on_submit

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="form-card"):
            yield Input(placeholder="Course code (e.g. EEI3372)")
            with Horizontal(id="buttons"):
                yield Button("Back", id="back")
                yield Button("Submit", id="submit", variant="primary")
            yield Label(id="error")
        yield Footer()

    @on(Input.Submitted)
    @on(Button.Pressed, "#submit")
    def _submit(self) -> None:
        code = self.query_one(Input).value.strip()
        try:
            course = create_course(code)
        except CourseError as e:
            error_label = self.query_one("#error", Label)
            error_label.update(str(e))
            error_label.add_class("-visible")
            inp = self.query_one(Input)
            inp.clear()
            inp.focus()
            return
        self._on_submit(course)
        self.app.push_screen(CreateCourseNameLecturerSemesterView(course, self._on_submit))

    @on(Button.Pressed, "#back")
    def _back(self) -> None:
        self.app.pop_screen()
