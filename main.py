import copy

from textual.app import App

from models import Course, Department
from views import HomeView


class CourseApp(App):
    TITLE = "ECE Course Catalog Manager"
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "views/app.tcss"

    def __init__(self) -> None:
        super().__init__()
        self._course = Course(
            code="",
            department=Department(code="", name=""),
            level=0,
            credits=0,
        )

    def state(self) -> Course:
        return copy.deepcopy(self._course)

    def set_course(self, course: Course) -> None:
        self._course = course

    def reset_course(self) -> None:
        self._course = Course(
            code="",
            department=Department(code="", name=""),
            level=0,
            credits=0,
        )

    def on_mount(self) -> None:
        self.push_screen(HomeView(self.set_course, self.reset_course))


if __name__ == "__main__":
    app = CourseApp()
    app.run()
