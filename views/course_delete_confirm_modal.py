from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class CourseDeleteConfirmModal(ModalScreen[bool]):
    CSS_PATH = "course_delete_confirm_modal.tcss"
    BINDINGS = [Binding("escape", "cancel")]

    def __init__(self, course_code: str) -> None:
        super().__init__()
        self._course_code = course_code

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(f"Delete course {self._course_code}?", id="question")
            yield Button("Yes", id="yes", variant="error")
            yield Button("No", id="no", variant="primary")

    @on(Button.Pressed, "#yes")
    def _yes(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#no")
    def _no(self) -> None:
        self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)
