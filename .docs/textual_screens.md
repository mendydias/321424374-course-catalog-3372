# Textual Screens

Fetched from https://textual.textualize.io/guide/screens/

Screens are containers for widgets that occupy the full terminal dimensions.

## Creating a screen
```
from textual.screen import Screen

class MyScreen(Screen):
    def compose(self):
        yield Input(placeholder="Enter code")
        yield Button("Submit")
```

## Screen stack
- push_screen / pop_screen / switch_screen
- Only top screen is visible/active

## Screen events
- Mount, Resume, Suspend, etc.
