# ECE Course Catalog Manager

A command-line application for managing the Open University ECE department's course catalog. Course metadata is derived automatically from structured course codes, reducing redundant manual entry and input error.

## Overview

Course codes follow a fixed format — 3 letters + 4 digits (e.g., `EEI3372`). Entering only the code lets the system derive:

- **Department** — first 2 letters (currently only `EE` → Electrical and Computer Engineering)
- **Academic Level** — 1st digit (1–4)
- **Credit Count** — 2nd digit (1–6)

The user is then prompted for the remaining descriptive fields: course name, semester number (1–8), and lecturer's name.

## Features

- **Add** a course from its code, with full validation and duplicate prevention
- **View** all courses in a formatted list
- **Search** for a course by exact code
- **Filter** courses by academic level and/or semester
- **Update** a course's lecturer or semester
- **Delete** a course from the catalog
- Robust input validation at every step (format, department, ranges, uniqueness, semester enum)

All data is held in memory and resets on each run — no database or file persistence.

## Architecture

Built as **MVC with a repository abstraction**, so the storage layer can later be swapped for a SQL backend without changing business logic or the CLI.

```
project/
├── main.py                  # Entry point
├── models/
│   ├── __init__.py          # Facade — re-exports public API
│   ├── course.py            # Course entity + validation rules
│   └── repository.py        # ICourseRepository interface + in-memory implementation
├── controllers/
│   ├── __init__.py          # Facade — re-exports public API
│   └── course_controller.py # Parsing, validation, use-case orchestration
├── views/
│   ├── __init__.py          # Facade — re-exports public API
│   └── cli_view.py          # CLI input/output, formatting
└── tests/
    ├── test_models.py
    ├── test_controller.py
    ├── test_fuzz.py          # Hypothesis property-based tests
    └── test_integration.py
```

- **Model** — `Course` entity plus `ICourseRepository`; `InMemoryCourseRepository` keys courses by code for O(1) lookup and natural uniqueness enforcement.
- **View** — Owns all `input()`/`print()`; no business logic.
- **Controller** — Owns parsing and validation rules; talks to the repository only through its interface.
- **Facade convention** — Every package (`models`, `controllers`, `views`) re-exports its public symbols from `__init__.py`. Import from the package namespace: `from models import Course`, never `from models.course import Course`. When adding a new module, update the `__init__.py` in the same change.

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
