from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Input
from textual import on

from poetry_tui.chat_components import *


class PoetryAI(Screen):
    """A Textual app to create a chat interface for the poetry ai.."""
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield ChatHistory()
        yield InputContainer()
        yield Footer()

    @on(Input.Submitted)
    def handle_submit(self, event: Input.Submitted) -> None:
        history = self.query_one(ChatHistory)
        history.messages = [*history.messages, (MessageTypeEnum.HumanMessage, event.input.value)]
        event.input.value = ""

class PoetryTUI(App):
    """A Textual app for poetry ai"""
    SCREENS = { "poetry_ai": PoetryAI }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme = "nord"

    def on_mount(self) -> None:
        self.push_screen("poetry_ai")


if __name__ == "__main__":
    app = PoetryTUI()
    app.run()