from dataclasses import dataclass, field

from textual.app import App

from models import Course
from views import CourseView


@dataclass
class AppState:
    course: Course | None = field(default=None)


_state = AppState()


def set_course(course: Course) -> None:
    _state.course = course


class CourseApp(App):
    TITLE = "ECE Course Catalog Manager"
    ENABLE_COMMAND_PALETTE = False

    def on_mount(self) -> None:
        self.push_screen(CourseView(set_course))


if __name__ == "__main__":
    app = CourseApp()
    app.run()
