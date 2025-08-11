from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Button
from textual import on

from poetry_tui.chat_components import *


class PoetryAI(Screen):
    """A Textual app to create a chat interface for the poetry ai.."""
    session_id = 0
    _debounce = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield ChatHistory()
        yield InputContainer()

    def on_mount(self) -> None:
        # Autofokus beim Start
        self.query_one("#prompt", Input).focus()
        self._debounce = None

    @on(Input.Changed)
    def on_prompt_changed(self, ev: Input.Changed) -> None:
        text = ev.value

        # TODO: Show timer on display!
        if self._debounce:
            self._debounce.stop()
        self._debounce = self.set_timer(5, lambda: self._reset_chat())

    @on(Input.Submitted)
    def handle_submit(self, event: Input.Submitted) -> None:
        """Also there for the api call handling"""
        if event.input.value != "":
            history = self.query_one(ChatHistory)
            history.messages = [*history.messages, (MessageTypeEnum.HumanMessage, event.input.value)]
            event.input.value = ""
            self.query_one("#prompt", Input).focus()

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Propagates buttons on poetry-tui.chat_components.chat_components.InputContainer"""
        if event.button.id == "btn_new_chat":
            self._reset_chat()
        if event.button.id == "btn_print":
            #TODO: Implement print!
            pass

    def _reset_chat(self):
        history = self.query_one(ChatHistory)
        history.messages = [history.messages[0]]
        self.query_one("#prompt", Input).value = ""
        self.session_id += 1


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