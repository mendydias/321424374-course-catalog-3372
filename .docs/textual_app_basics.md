# Textual App Basics

Fetched from https://textual.textualize.io/guide/app/

## The App class

The first step in building a Textual app is to import the App class and create a subclass.

```
from textual.app import App

class MyApp(App):
    pass
```

### The run method

To run an app we create an instance and call run().

Apps don't get much simpler than this.

When you call App.run() Textual puts the terminal into a special state called application mode. If you hit Ctrl+Q Textual will exit application mode and return you to the command prompt.

## Exiting

An app will run until you call App.exit() which will exit application mode and the run() method will return.

The exit method will also accept an optional positional value to be returned by run().

## Composing

To add widgets to your app implement a compose() method which should return an iterable of Widget instances.

```
def compose(self) -> ComposeResult:
    yield Button("Yes")
```

## CSS

Textual apps can reference CSS files via CSS_PATH class variable or inline CSS via CSS class variable.
