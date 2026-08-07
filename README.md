# ECE Course Catalog Manager

A terminal app for managing the Open University ECE department's course catalog. Enter a course code (e.g. `EEI3372`) and the app derives the department, academic level, and credit count automatically — you only fill in the name, semester, and lecturer.

## Features

- Add, list, search, update, and delete courses
- Validation on every input (code format, department, ranges, duplicates)
- Data held in memory; resets on each run

## Usage

```bash
uv sync
uv run python main.py
```

## Tests

```bash
uv run pytest
```

## Project Layout

```
main.py                # App entry point
models/                # Course and Department entities
data/                  # In-memory repositories
controllers/           # Parsing and validation logic
views/                 # Textual UI screens
tests/                 # Unit, integration, and fuzz tests
```
