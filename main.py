from dataclasses import dataclass, field

from textual.app import App

from models import Course
from views import HomeView


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
        self.push_screen(HomeView(self.set_course))


if __name__ == "__main__":
    app = CourseApp()
    app.run()
