from dataclasses import replace

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label

from controllers import CourseError, get_course, update_course


class UpdateCourseView(Screen):
    CSS_PATH = "update_course_view.tcss"
    BINDINGS = [Binding("escape", "app.pop_screen")]

    def __init__(self, course_code: str) -> None:
        super().__init__()
        self._og_course = get_course(course_code)      # reset target, never mutated
        self._course = replace(self._og_course)        # working copy = form state

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="form-card"):
            yield Label(f"Course code: {self._course.code}", id="course-code")
            yield Label(f"Department: {self._course.department.name}", id="department")
            yield Input(value=self._course.name, placeholder="Course name", id="name")
            yield Input(value=self._course.lecturer, placeholder="Lecturer name", id="lecturer")
            yield Input(value=str(self._course.semester), placeholder="Semester (1-8)", id="semester")
            with Horizontal(id="buttons"):
                yield Button("Reset", id="reset")
                yield Button("Submit", id="submit", variant="primary")
            yield Label(id="error")
        yield Footer()

    def _show_error(self, message: str) -> None:
        error_label = self.query_one("#error", Label)
        error_label.update(message)
        error_label.add_class("-visible")

    @on(Input.Changed, "#name")
    def _name_changed(self, event: Input.Changed) -> None:
        self._course.name = event.value

    @on(Input.Changed, "#lecturer")
    def _lecturer_changed(self, event: Input.Changed) -> None:
        self._course.lecturer = event.value

    @on(Input.Changed, "#semester")
    def _semester_changed(self, event: Input.Changed) -> None:
        try:
            self._course.semester = int(event.value)
        except ValueError:
            self._course.semester = 0  # invalid sentinel; update_course rejects it

    @on(Button.Pressed, "#reset")
    def _reset(self) -> None:
        self._course = replace(self._og_course)
        self.query_one("#name", Input).value = self._course.name
        self.query_one("#lecturer", Input).value = self._course.lecturer
        self.query_one("#semester", Input).value = str(self._course.semester)
        self.query_one("#error", Label).remove_class("-visible")

    @on(Button.Pressed, "#submit")
    def _submit(self) -> None:
        self.query_one("#error", Label).remove_class("-visible")
        try:
            update_course(self._course)
        except CourseError as e:
            self._show_error(str(e))
            return
        self.app.notify(f"Course {self._course.code} updated.")
        while len(self.app.screen_stack) > 3:
            self.app.pop_screen()
