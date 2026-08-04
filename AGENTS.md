# AGENTS.md

## Commands

- Setup: `uv sync` (creates/uses `.venv/`). No requirements.txt — this is a uv project.
- Run app: `uv run python main.py`
- Tests: `uv run pytest` (all), `uv run pytest tests/test_controller.py` (file),
  `uv run pytest -k <name>` (single test)
- Python >= 3.11 required.
- View tests are async (Textual `pilot` fixtures) and require the `pytest-asyncio`
  dev dependency.

## Project state

- App is a Textual TUI, not a plain CLI. `main.py` runs `CourseApp`, which pushes
  screens and shares state via the `AppState` dataclass. On submit it exits with
  the `Course` result and prints it to stdout.
- Structure:
  - `models/` — `Course` and `Department` dataclasses. `Course` carries code,
    department, level, credits, name, semester, lecturer.
  - `data/` — module-level function repositories (no classes/interfaces):
    `course_repository.py` (add/get/update/remove/list/exists + `CourseRepoError`)
    and `department_repository.py` (add/get/update/remove/list). Courses are keyed
    by uppercase code in a module-level dict (O(1) lookup, natural uniqueness).
    `clear_courses()` exists for test isolation.
  - `controllers/` — `create_course(code)` parses/validates the code into a
    `Course`; `register_course(course)` validates name/semester/lecturer and adds
    it via the `data` facade. Raises `CourseError` on any invalid input.
  - `views/` — Textual `Screen` subclasses (`CourseView`,
    `CourseNameLecturerSemesterView`) with `.tcss` stylesheets. Own ALL UI — no
    business logic, no `print()`.
- MVC + repository design: views own all UI, controllers do parsing/validation and
  reach storage only through the `data` facade, storage is swappable behind it.
- Scope: the UI currently exposes only the Add flow. View/Search/Update/Delete
  exist at the data layer but are not wired to screens; Filter is not started.

## Facade convention

- Every package (`models`, `controllers`, `views`, `data`) re-exports its public
  API from `__init__.py`.
- Consumers import from the package, not the module: `from models import Course`,
  never `from models.course import Course`. When adding a new module, update the
  package's `__init__.py` in the same change.
- Only `__init__.py` files and intra-package imports (e.g. `models/course.py`
  importing `models.department`) may reference modules directly.

## Documentation

- Textual API docs fetched and saved in `.docs/` as markdown.
  Reference these for widget usage, screen patterns, and app lifecycle.

## Quirks

- The UI is a Textual TUI (`views/` screens + `.tcss`); use the `.docs/` Textual
  reference when touching it.
- Tests are expected to include Hypothesis property-based tests
  (`tests/test_fuzz.py`). This is a pending requirement — not yet implemented.
- Devcontainer shell is fish, user `dev`; commits use Conventional Commits (see `git log`).
