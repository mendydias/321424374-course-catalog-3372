from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label, Input

from controllers import CourseDTO, list_courses
from views.course_action_modal import CourseActionModal

COLUMNS = ("Code", "Name", "Department", "Level", "Credits", "Semester", "Lecturer")


def filter_courses(courses: dict[str, CourseDTO], key: str) -> dict[str, CourseDTO]:
    if not key:
        return courses
    needle = key.casefold()
    feature = None
    if ":" in needle:
        feature, needle = needle.split(":", 1)
    rows = {}
    for code, course in courses.items():
        if not feature and needle in code.casefold():
            rows[code] = course
        elif feature:
            property_value = getattr(course, feature, None)
            if property_value and needle in property_value.casefold():
                rows[code] = course
    return rows


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
                yield Input(id="search", placeholder="Search")
                yield DataTable(id="courses-table", cursor_type="row", zebra_stripes=True)
            else:
                yield Label("Courses table is empty.", id="empty")
        yield Footer()

    def on_mount(self) -> None:
        if not self._courses:
            return
        table = self.query_one("#courses-table", DataTable)
        table.add_columns(*COLUMNS)
        self.populate_table(self._courses.items())

    def populate_table(self, rows) -> None:
        table = self.query_one("#courses-table", DataTable)
        table.clear()
        if isinstance(rows, dict):
            rows = rows.items()
        for code, course in rows:
            table.add_row(
                course.code,
                course.name,
                course.department,
                course.level,
                course.credits,
                course.semester,
                course.lecturer,
                key=code,
            )

    @on(Input.Changed, "#search")
    def on_input_changed(self, event: Input.Changed) -> None:
        self.populate_table(filter_courses(self._courses, event.value))

    @on(DataTable.RowSelected, "#courses-table")
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        row = event.data_table.get_row(event.row_key)
        self.app.push_screen(CourseActionModal(row[0]))
