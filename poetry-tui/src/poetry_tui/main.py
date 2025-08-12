from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Button, Static
from textual import on
from dotenv import load_dotenv

from poetry_tui.chat_components import *
# noinspection PyUnresolvedReferences
from poetry_tui.api import APIHandler
load_dotenv()

CHAT_TIMEOUT = 120

class PoetryAI(Screen):
    """A Textual app to create a chat interface for the poetry ai.."""
    session_id = 0
    was_resetted = True
    api_handler = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ChatHistory()
        yield InputContainer()
        yield Static("", id="label_timeout")

    def on_mount(self) -> None:
        self.query_one("#prompt", Input).focus()
        self._label: Static = self.query_one("#label_timeout", Static)
        self._debounce_count: int = CHAT_TIMEOUT
        self._label.update(f"{self._debounce_count}s bis zur Zurücksetzung des Chats")
        self._ticker: Timer = self.set_interval(1.0, self._second_step, pause=True)
        self.api_handler = APIHandler(self.session_id)


    @on(Input.Changed)
    def on_prompt_changed(self, ev: Input.Changed) -> None:
        self._debounce_count = CHAT_TIMEOUT
        self._label.update(f"{self._debounce_count}s bis zur Zurücksetzung des Chats")
        if self.was_resetted:
            return
        self._ticker.resume()


    def _second_step(self) -> None:
        if self._debounce_count <= 0:
            self._ticker.pause()
            self._label.update("0s bis zur Zurücksetzung des Chats")
            self._reset_chat()  # deine Funktion
            return
        self._debounce_count -= 1
        self._label.update(f"{self._debounce_count}s bis zur Zurücksetzung des Chats")


    @on(Input.Submitted)
    def handle_submit(self, event: Input.Submitted) -> None:
        """Also there for the api call handling"""
        if event.input.value != "":
            history = self.query_one(ChatHistory)
            history.messages = [*history.messages]
            self.recompose()
            if self.was_resetted:
                for message in self.api_handler.start_session(event.input.value):
                    history.messages.append(message)
            else:
                response = self.api_handler.resume_chat(event.input.value)
                for message in response[0]:
                    history.messages.append(message)
                if response[1]:
                    #TODO: Add Print handler!
                    pass
            event.input.value = ""
            self.was_resetted = False
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
        self.was_resetted = True
        history = self.query_one(ChatHistory)
        history.messages = [history.messages[0]]
        self.query_one("#prompt", Input).value = ""
        self.session_id += 1
        self.api_handler = APIHandler(self.session_id)



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