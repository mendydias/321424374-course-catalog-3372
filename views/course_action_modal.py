from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button

from views.update_course_view import UpdateCourseView


class CourseActionModal(ModalScreen):
    CSS_PATH = "course_action_modal.tcss"
    BINDINGS = [Binding("escape", "app.pop_screen")]

    def __init__(self, course_code: str) -> None:
        super().__init__()
        self._course_code = course_code   # stored for the future Update/Delete flows

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Button("Update", id="update", variant="primary")
            yield Button("Delete", id="delete")
            yield Button("Cancel", id="cancel")

    @on(Button.Pressed, "#update")
    def _update(self) -> None:
        self.app.push_screen(UpdateCourseView(self._course_code))

    @on(Button.Pressed, "#delete")
    @on(Button.Pressed, "#cancel")
    def _close(self) -> None:
        self.app.pop_screen()
