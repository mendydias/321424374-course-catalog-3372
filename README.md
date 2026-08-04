# ECE Course Catalog Manager

A command-line application for managing the Open University ECE department's course catalog. Course metadata is derived automatically from structured course codes, reducing redundant manual entry and input error.

## Overview

Course codes follow a fixed format — 3 letters + 4 digits (e.g., `EEI3372`). Entering only the code lets the system derive:

- **Department** — first 2 letters (currently only `EE` → Electrical and Computer Engineering)
- **Academic Level** — 1st digit (1–4)
- **Credit Count** — 2nd digit (1–6)

The user is then prompted for the remaining descriptive fields: course name, semester number (1–8), and lecturer's name.

## Features

- **Add** a course from its code, with full validation and duplicate prevention — *implemented (UI + controller + data)*
- **View** all courses in a formatted list — *data layer only*
- **Search** for a course by exact code — *data layer only*
- **Filter** courses by academic level and/or semester — *not started*
- **Update** a course's lecturer or semester — *data layer only*
- **Delete** a course from the catalog — *data layer only*
- Robust input validation at every step (format, department, ranges, uniqueness, semester enum)

All data is held in memory and resets on each run — no database or file persistence.

## Architecture

Built as **MVC with a repository abstraction**, so the storage layer can later be swapped for a SQL backend without changing business logic or the UI.

```
project/
├── main.py                  # Textual app entry point (CourseApp + AppState)
├── models/
│   ├── __init__.py          # Facade — re-exports public API
│   ├── course.py            # Course entity
│   └── department.py        # Department entity
├── data/
│   ├── __init__.py          # Facade — re-exports public API
│   ├── course_repository.py     # Function-based course repo (add/get/update/remove/list/exists)
│   └── department_repository.py # Function-based department repo
├── controllers/
│   ├── __init__.py          # Facade — re-exports public API
│   └── course_controller.py # Parsing, validation, use-case orchestration
├── views/
│   ├── __init__.py          # Facade — re-exports public API
│   ├── course_view.py       # Textual screen (code entry)
│   ├── course_view.tcss     # Stylesheet
│   ├── course_name_lecturer_semester_view.py  # Textual screen (descriptive fields)
│   └── course_name_lecturer_semester_view.tcss
└── tests/
    ├── conftest.py          # Shared fixtures (async Textual pilot, AppState)
    ├── test_controller.py
    ├── test_course_repository.py
    ├── test_fuzz.py          # Hypothesis property-based tests (pending)
    └── test_views.py
```

- **Model** — `Course` and `Department` dataclasses; `Course` derives department, level, and credits from its code.
- **Data** — Module-level function repositories (`data/`), not classes or interfaces. Courses are keyed by uppercase code in a module-level dict for O(1) lookup and natural uniqueness enforcement; `clear_courses()` exists for test isolation.
- **View** — Textual `Screen` subclasses own all UI and formatting; no business logic, no `print()`.
- **Controller** — Owns parsing and validation rules; reaches storage only through the `data` facade.
- **Facade convention** — Every package (`models`, `controllers`, `views`, `data`) re-exports its public symbols from `__init__.py`. Import from the package namespace: `from models import Course`, never `from models.course import Course`. When adding a new module, update the `__init__.py` in the same change.

## Getting Started

```bash
# Clone and enter the project
git clone <repo-url>
cd project

# Install dependencies (uses uv — no manual venv needed)
uv sync

# Run the application
uv run python main.py

# Run tests
uv run pytest
```

## Validation Rules

| Rule | Behavior |
| --- | --- |
| Code format | Must match `[A-Za-z]{3}\d{4}`; rejected otherwise |
| Code casing | Auto-normalized to uppercase |
| Department | Only `EE` recognized; others rejected with a clear message |
| Academic Level | Must be 1–4 |
| Credit Count | Must be 1–6 |
| Semester | Must be an integer 1–8; rejected otherwise |
| Uniqueness | Duplicate course codes rejected on add |
| Existence checks | Search/Update/Delete confirm the course exists before proceeding |
