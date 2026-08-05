# Textual DataTable

Fetched from https://textual.textualize.io/widgets/data_table/

A widget to display text in a table: update data, navigate with a cursor, respond to mouse clicks, delete rows/columns, and render each cell as a Rich Text renderable. Focusable, container. Emits events for custom logic.

## Guide

### Adding data
```python
class TableApp(App):
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])
```
Use `add_row()` / `add_column()` for single additions.

#### Styling and justifying cells
Cells can be Rich renderables, e.g. `Text`:
```python
styled_row = [Text(str(cell), style="italic #03AC13", justify="right") for cell in row]
table.add_row(*styled_row)
```

### Keys
- `add_row(..., key=...)` and `add_column(..., key=...)` accept a unique key; if omitted Textual generates one and returns it from the call.
- Keys reference data regardless of current position (rows move on sort/deletion).
- `coordinate_to_cell_key()` converts a coordinate to a key.

### Cursors
- `cursor_type`: `"cell"` (default), `"row"`, `"column"`, `"none"`. Set via the reactive attribute.
- Cursor position exposed via `cursor_coordinate`; mouse hover via `hover_coordinate`.
- Arrow/PageUp/PageDown/Home/End move the cursor, emitting Highlighted messages; Enter selects, emitting Selected messages. Mouse click emits both Highlighted and Selected.

### Updating data
`update_cell()` and `update_cell_at()`.

### Removing data
- `clear()` removes all data; `clear(columns=True)` also removes columns.
- `remove_row(row_key)` removes a single row.
- Remove the row under the cursor:
```python
row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
table.remove_row(row_key)
```

### Removing columns
```python
_, column_key = table.coordinate_to_cell_key(table.cursor_coordinate)
table.remove_column(column_key)
```

### Fixed data
```python
table.fixed_rows = 2
table.fixed_columns = 1
```
Pins rows/columns so they don't scroll.

### Sorting
`sort(*columns, key=None, reverse=False)` — three modes:
1. By column(s): `sort("country", "region")`
2. By key function: `sort(key=lambda row: ...)` — called once per row with a tuple of all row values
3. Both: `sort("hours", "rate", key=lambda h, r: h * r)` — only those columns' data passed to the key function

Note: key function may need to undo formatting (e.g. `key=lambda country: country.plain` for Rich `Text` cells).

### Labeled rows
`add_row(*cells, label=...)` adds a label column on the left (like spreadsheet row numbers) that the cursor cannot interact with. `show_row_labels` controls visibility.
```python
table.add_row(*row, label=Text(str(number), style="#B0FC38 italic"))
```

## Reactive attributes

| Attribute | Type | Default | Description |
|---|---|---|---|
| `show_header` | bool | True | Show the table header |
| `show_row_labels` | bool | True | Show the row labels |
| `fixed_rows` | int | 0 | Number of rows that do not scroll |
| `fixed_columns` | int | 0 | Number of columns that do not scroll |
| `zebra_stripes` | bool | False | Alternating row colors |
| `header_height` | int | 1 | Height of header row |
| `show_cursor` | bool | True | Show both keyboard and hover cursor |
| `cursor_type` | CursorType | "cell" | "cell", "row", "column", or "none" |
| `cursor_coordinate` | Coordinate | (0, 0) | Current cursor coordinate |
| `hover_coordinate` | Coordinate | (0, 0) | Coordinate the mouse is above |
| `cell_padding` | int | 1 | Horizontal padding on each side of each cell |
| `cursor_foreground_priority` | Literal['renderable','css'] | 'css' | Prioritize renderable or CSS foreground under cursor |
| `cursor_background_priority` | Literal['renderable','css'] | 'renderable' | Prioritize renderable or CSS background under cursor |

Properties: `cursor_column`, `cursor_row`, `hover_column`, `hover_row` (int indices); `ordered_columns` (list[Column]), `ordered_rows` (list[Row]), `row_count` (int). Instance attrs: `columns: dict[ColumnKey, Column]`, `rows: dict[RowKey, Row]`.

## Messages

All nested in `DataTable`, all have `.data_table` and `.control`. Handlers: `on_data_table_<message>_selected/highlighted`.

- `CellHighlighted(data_table, value, coordinate, cell_key)` — cursor moved to a new cell (cursor_type "cell")
- `CellSelected(data_table, value, coordinate, cell_key)` — cell selected (cursor_type "cell")
- `RowHighlighted(data_table, cursor_row, row_key)` — row highlighted (cursor_type "row")
- `RowSelected(data_table, cursor_row, row_key)` — row selected (cursor_type "row")
- `ColumnHighlighted(data_table, cursor_column, column_key)` — column highlighted (cursor_type "column")
- `ColumnSelected(data_table, cursor_column, column_key)` — column selected (cursor_type "column")
- `HeaderSelected(data_table, column_key, column_index, label)` — column header clicked
- `RowLabelSelected(data_table, row_key, row_index, label)` — row label clicked

## Bindings

| Key | Action |
|---|---|
| enter | select_cursor |
| up/down/left/right | cursor_up/down/left/right |
| pageup / pagedown | page_up / page_down |
| ctrl+home / ctrl+end | scroll_top / scroll_bottom |
| home / end | scroll_home / scroll_end |

## Component classes

`datatable--cursor`, `datatable--hover`, `datatable--fixed`, `datatable--fixed-cursor`, `datatable--header`, `datatable--header-cursor`, `datatable--header-hover`, `datatable--odd-row`, `datatable--even-row` (zebra stripes).

## Methods

```python
add_column(label, *, width=None, key=None, default=None) -> ColumnKey
add_columns(*columns) -> list[ColumnKey]          # each: TextType or (label, key) tuple
add_row(*cells, height=1, key=None, label=None) -> RowKey
add_rows(rows) -> list[RowKey]                    # rows: Iterable[Iterable[CellType]]
clear(columns=False) -> Self
coordinate_to_cell_key(coordinate) -> CellKey     # raises CellDoesNotExist
get_cell(row_key, column_key) -> CellType
get_cell_at(coordinate) -> CellType               # raises CellDoesNotExist
get_cell_coordinate(row_key, column_key) -> Coordinate
get_column(column_key) -> Iterable[CellType]      # generator
get_column_at(column_index) -> Iterable[CellType]
get_column_index(column_key) -> int
get_row(row_key) -> list[CellType]
get_row_at(row_index) -> list[CellType]
get_row_height(row_key) -> int
get_row_index(row_key) -> int
is_valid_column_index(column_index) -> bool
is_valid_coordinate(coordinate) -> bool
is_valid_row_index(row_index) -> bool
move_cursor(*, row=None, column=None, animate=False, scroll=True)
refresh_column(column_index) -> Self
refresh_coordinate(coordinate) -> Self
refresh_row(row_index) -> Self
remove_column(column_key)                         # raises ColumnDoesNotExist
remove_row(row_key)                               # raises RowDoesNotExist
sort(*columns, key=None, reverse=False) -> Self
update_cell(row_key, column_key, value, *, update_width=False)
update_cell_at(coordinate, value, *, update_width=False)
```

Actions: `action_page_up/down/left/right()`, `action_scroll_top/bottom/home/end()`.

## data_table module types

- `CellType = TypeVar('CellType')`
- `CursorType = Literal['cell', 'row', 'column', 'none']`
- `CellKey` — NamedTuple `(row_key, column_key)`
- `RowKey`, `ColumnKey` — subclasses of `StringKey` (unique identifiers, stable across sort/delete)
- `StringKey(value=None)` — object used as a mapping key; wraps a string, lookups behave like the string itself
- `Row`, `Column` — dataclasses with column metadata (`Column.get_render_width(data_table) -> int`)
- Exceptions: `CellDoesNotExist`, `RowDoesNotExist`, `ColumnDoesNotExist`, `DuplicateKey`
