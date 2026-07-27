from collections.abc import Callable

from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input, Label

from controllers import CourseCodeError, parse_course_code
from models import Course


class CourseView(Screen):
    def __init__(self, on_submit: Callable[[Course], None]) -> None:
        super().__init__()
        self._on_submit = on_submit

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Course code (e.g. EEI3372)")
        yield Button("Submit", variant="primary")
        yield Label(id="error")

    @on(Input.Submitted)
    @on(Button.Pressed)
    def _submit(self) -> None:
        code = self.query_one(Input).value.strip()
        try:
            course = parse_course_code(code)
        except CourseCodeError as e:
            error_label = self.query_one("#error", Label)
            error_label.update(str(e))
            inp = self.query_one(Input)
            inp.clear()
            inp.focus()
            return
        self._on_submit(course)
        self.app.exit()
