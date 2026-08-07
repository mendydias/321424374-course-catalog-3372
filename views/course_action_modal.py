from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button

from controllers import CourseError, delete_course
from views.course_delete_confirm_modal import CourseDeleteConfirmModal
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

    @on(Button.Pressed, "#cancel")
    def _close(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#delete")
    @work
    async def _delete(self) -> None:
        delete_course_confirmed = await self.app.push_screen_wait(
            CourseDeleteConfirmModal(self._course_code)
        )
        if not delete_course_confirmed:
            return
        try:
            delete_course(self._course_code)
        except CourseError as e:
            self.app.notify(str(e), severity="error")
            return
        self.app.notify(f"Course {self._course_code} deleted.")
        self.app.pop_screen()
