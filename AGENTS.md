# AGENTS.md

## Commands

- Setup: `uv sync` (creates/uses `.venv/`). No requirements.txt — this is a uv project.
- Run app: `uv run python main.py`
- Tests: `uv run pytest` (all), `uv run pytest tests/test_models.py` (file),
  `uv run pytest -k <name>` (single test)
- Python >= 3.11 required.

## Project state

- Scaffold in progress: `models/course.py`, `models/department.py`, and
  `controllers/course_controller.py` exist. Repository and views still
  unimplemented. `README.md` is the authoritative spec — implement to it
  (features list + validation rules table are normative).
- MVC + repository design per README:
  - `views/` owns ALL `input()`/`print()` — no business logic there.
  - `controllers/` does parsing/validation; touches storage only via `ICourseRepository`.
  - `InMemoryCourseRepository` keys courses by code (O(1) lookup, natural uniqueness).

## Facade convention

- Every package (`models`, `controllers`, `views`) re-exports its public API from
  `__init__.py`.
- Import from the package, not the module: `from models import Course`, never
  `from models.course import Course`. When adding a new module, update the
  package's `__init__.py` in the same change.

## Quirks

- `textual` is a dependency even though the README describes a plain CLI view;
  confirm with the user before building a TUI.
- Tests are expected to include Hypothesis property-based tests (`tests/test_fuzz.py`).
- Devcontainer shell is fish, user `dev`; commits use Conventional Commits (see `git log`).
