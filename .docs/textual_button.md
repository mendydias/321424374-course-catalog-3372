# Textual Button Widget

Fetched from https://textual.textualize.io/widgets/button/

A simple clickable button. Focusable, Container.

## Key features
- Variants: default, primary, success, warning, error
- Compose: yield Button("Label")
- Message: Button.Pressed with `button` attribute
- Handle with `@on(Button.Pressed)` or `def on_button_pressed(self, event: Button.Pressed)`

```
from textual.widgets import Button

def compose(self):
    yield Button("Submit")

@on(Button.Pressed)
def handle_press(self):
    # handle press
```
