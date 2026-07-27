# Textual Input Widget

Fetched from https://textual.textualize.io/widgets/input/

A single-line text input widget. Focusable, Container.

## Key features
- Input types: "integer", "number", "text"
- Restrict with regex
- Max length
- Validators (built-in and custom)
- Messages: Changed, Submitted, Blurred
- Reactive attributes: value, cursor_position, placeholder, etc.

## Handling submit
The Input.Submitted message has a `value` attribute. Handle with `@on(Input.Submitted)` or `def on_input_submitted(self, event: Input.Submitted)`.

```
from textual.widgets import Input

def compose(self):
    yield Input(placeholder="Enter code")

@on(Input.Submitted)
def handle_submit(self, event: Input.Submitted):
    code = event.value
```
