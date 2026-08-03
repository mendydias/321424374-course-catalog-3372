from dataclasses import dataclass, field

from textual.app import App

from models import Course
from views import CourseView


@dataclass
class AppState:
    course: Course | None = field(default=None)


class CourseApp(App):
    TITLE = "ECE Course Catalog Manager"
    ENABLE_COMMAND_PALETTE = False

    def __init__(self, state: AppState | None = None) -> None:
        super().__init__()
        self.state = state if state is not None else AppState()

    def set_course(self, course: Course) -> None:
        self.state.course = course

    def on_mount(self) -> None:
        self.push_screen(CourseView(self.set_course))


if __name__ == "__main__":
    app = CourseApp()
    course = app.run() or app.state.course
    if course:
        print(course)
