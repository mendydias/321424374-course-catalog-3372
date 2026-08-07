# AGENTS.md

## Commands

- Setup: `uv sync` (creates/uses `.venv/`). No requirements.txt — this is a uv project.
- Run app: `uv run python main.py`
- Tests: `uv run pytest` (all), `uv run pytest tests/test_controller.py` (file),
  `uv run pytest -k <name>` (single test)
- Python >= 3.11 required.
- View tests are async (Textual `pilot` fixtures) and require the `pytest-asyncio`
  dev dependency.

## Workflow

Work proceeds in three phases, with artifacts stored per feature under
`.plans/<feature>/` at the repo root (gitignored, so plans never enter version
control). Directory names follow the format `Date-feature-short-summary`
(e.g. `2026-08-04-ac2.4-retrieval`):

1. **Research** — explore the codebase and write findings to
   `.plans/<feature>/research.md`. Output exact line numbers, filenames, and
   exact code snippets.
2. **Plan** — based on the research, suggest a preliminary plan when asked and
   write it to `.plans/<feature>/plan.md`.
3. **Implement** — when given the go-ahead, implement `plan.md` and write the
   summary to `.plans/<feature>/implementation.md`.

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
- Tests include Hypothesis property-based tests
  (`tests/test_fuzz.py`).
- Devcontainer shell is fish, user `dev`; commits use Conventional Commits (see `git log`).

## UI design system

- Palette tokens (single source of truth in `views/app.tcss`):
  - screen bg: `#14161c`
  - chrome bg: `#0e0f13`
  - card bg: `#1c1f28`
  - input bg: `#22252f` (focus `#262a35`)
  - border: `#363c4c`
  - text: `#e6e6ea`
  - muted: `#b9bfcc`
  - accent: `#5b8cff`, hover `#7aa2ff`
  - on-accent: `#0e0f13`
  - error: `#ff5c5c`
- Shared styles live in `views/app.tcss`; screen `.tcss` files hold only
  screen-specific rules.
- Every interactive widget must declare explicit `background` + `color` for
  default/hover/focus; never rely on Textual theme defaults.
- Button convention: default buttons use `#343a4a` bg / `#e6e6ea` text;
  `-primary` buttons use accent bg + on-accent text.
- DataTable baseline: header `#0e0f13`, zebra rows (`#22252f` odd / `#1c1f28`
  even), hover `#343a4a`, cursor accent bg (`#5b8cff`) + on-accent text + bold.
- Table containers use `width: 1fr` (no max-width cap) and the table itself
  uses `width: 100%; height: auto`.
- Error-label convention: `id="error"`, hidden by default, shown via
  `.-visible` toggle.
