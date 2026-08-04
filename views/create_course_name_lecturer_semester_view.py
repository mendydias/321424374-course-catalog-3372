from collections.abc import Callable

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label

from controllers import CourseError, register_course
from models import Course


class CreateCourseNameLecturerSemesterView(Screen):
    CSS_PATH = "create_course_name_lecturer_semester_view.tcss"
    BINDINGS = [Binding("escape", "app.pop_screen")]

    def __init__(self, course: Course, on_submit: Callable[[Course], None]) -> None:
        super().__init__()
        self._course = course
        self._on_submit = on_submit

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="form-card"):
            yield Label(f"Course code: {self._course.code}", id="course-code")
            yield Label(f"Department: {self._course.department.name}", id="department")
            yield Input(placeholder="Course name", id="name")
            yield Input(placeholder="Lecturer name", id="lecturer")
            yield Input(placeholder="Semester (1-8)", id="semester")
            with Horizontal(id="buttons"):
                yield Button("Back", id="back")
                yield Button("Next", id="next", variant="primary")
            yield Label(id="error")
        yield Footer()

    def _show_error(self, message: str) -> None:
        error_label = self.query_one("#error", Label)
        error_label.update(message)
        error_label.add_class("-visible")

    @on(Input.Submitted)
    @on(Button.Pressed, "#next")
    def _submit(self) -> None:
        name = self.query_one("#name", Input).value.strip()
        lecturer = self.query_one("#lecturer", Input).value.strip()
        raw_semester = self.query_one("#semester", Input).value.strip()

        error_label = self.query_one("#error", Label)
        error_label.remove_class("-visible")

        try:
            semester = int(raw_semester)
        except ValueError:
            self._show_error(f"Semester must be a number between 1 and 8, got '{raw_semester}'.")
            self.query_one("#semester", Input).focus()
            return

        self._course.name = name
        self._course.semester = semester
        self._course.lecturer = lecturer

        try:
            register_course(self._course)
        except CourseError as e:
            self._show_error(str(e))
            return

        self._on_submit(self._course)
        self.app.notify(f"Course {self._course.code} registered.")
        while len(self.app.screen_stack) > 2:
            self.app.pop_screen()

    @on(Button.Pressed, "#back")
    def _back(self) -> None:
        self.app.pop_screen()
