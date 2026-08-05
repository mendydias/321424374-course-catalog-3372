from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label

from controllers import list_courses

COLUMNS = ("Code", "Name", "Department", "Level", "Credits", "Semester", "Lecturer")


class CourseListView(Screen):
    CSS_PATH = "course_list_view.tcss"
    BINDINGS = [Binding("escape", "app.pop_screen")]

    def __init__(self) -> None:
        super().__init__()
        self._courses = list_courses()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="table-card"):
            if self._courses:
                yield DataTable(id="courses-table", cursor_type="row", zebra_stripes=True)
            else:
                yield Label("Courses table is empty.", id="empty")
        yield Footer()

    def on_mount(self) -> None:
        if not self._courses:
            return
        table = self.query_one("#courses-table", DataTable)
        table.add_columns(*COLUMNS)
        for code, course in self._courses.items():
            table.add_row(
                course.code,
                course.name,
                course.department.name,
                course.level,
                course.credits,
                course.semester,
                course.lecturer,
                key=code,
            )
