from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import Header, Input, Button, Static
from textual import on
from dotenv import load_dotenv
import os
from escpos.printer import File, Dummy
from uuid import uuid1

from poetry_tui.chat_components import *
# noinspection PyUnresolvedReferences
from poetry_tui.api import APIHandler
from poetry_tui.utility import log_message, LogSeverityEnum
from typing import Union
load_dotenv()

CHAT_TIMEOUT = 120

class PoetryAI(Screen):
    """A Textual app to create a chat interface for the poetry ai.."""
    session_id = uuid1().int
    was_resetted = True
    api_handler: Union[APIHandler, None] = None
    chat_history_container = ChatHistory()

    def compose(self) -> ComposeResult:
        yield self.chat_history_container
        yield InputContainer()
        yield Static("", id="label_timeout")

    def on_mount(self) -> None:
        """Initialize components on each mount: 1. Focus Prompt Interface, 2. Init Timer for auto timeout (clearing of chat history) 3. Init APIHandler"""
        self.query_one("#prompt", Input).focus()
        self._label: Static = self.query_one("#label_timeout", Static)
        self._debounce_count: int = CHAT_TIMEOUT
        self._label.update(f"{self._debounce_count}s bis zur Zurücksetzung des Chats")
        self._ticker: Timer = self.set_interval(1.0, self._second_step, pause=True)
        self.api_handler = APIHandler()


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
            self._reset_chat()
            return
        self._debounce_count -= 1
        self._label.update(f"{self._debounce_count}s bis zur Zurücksetzung des Chats")


    @on(Input.Submitted)
    async def handle_submit(self, event: Input.Submitted) -> None:
        """Also there for the api call handling"""
        if event.input.value != "":
            self.run_worker(self.call_api(event.input.value))
            event.input.value = ""
            self.query_one("#prompt", Input).focus()

    async def call_api(self, prompt: str) -> None:
        history = self.query_one(ChatHistory)
        history.messages = [*history.messages]
        await self.app.push_screen(LoadingOverlay())
        await self.recompose()
        try:
            if self.was_resetted:
                # start_session ist jetzt async → await nicht vergessen
                messages = await self.api_handler.start_session(prompt, self.session_id)
                history.messages = messages
            else:
                # resume_chat liefert (messages, ended)
                messages, ended = await self.api_handler.resume_chat(prompt, self.session_id)
                history.messages = messages
                # if ended:
                #     self._print_latest_poetry()
            # If chat api responded correctly set was_resetted to false in order to being able to resume chat
            self.was_resetted = False
        except Exception as e:
            log_message(self,str(e), LogSeverityEnum.ERROR)
        finally:
            self.chat_history_container.is_loading = False
            await self.app.pop_screen()
            await self.recompose()

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Propagates buttons on poetry-tui.chat_components.chat_components.InputContainer"""
        if event.button.id == "btn_new_chat":
            self._reset_chat()
        if event.button.id == "btn_print":
            # Print on button click
            self._print_latest_poetry()

    def _reset_chat(self):
        self.was_resetted = True
        history = self.query_one(ChatHistory)
        history.messages = []
        self.query_one("#prompt", Input).value = ""
        self.session_id = uuid1().int

    def _print_latest_poetry(self):
        device_path = os.getenv("PRINTER_DEVICE_PATH")
        last_poetry = self.api_handler.last_poetry
        try:
            f = File(device_path)
            d = Dummy()
            f.set_with_default(width=384)
            d.set(align="center", bold=True, height=3, width=384)
            d.text("AI Poetry")
            d.ln()
            d.ln()
            d.set(align="center", bold=True, height=2, width=384)

            d.ln()
            d.set(align="left", bold=False, height=1, width=384)
            d.text(last_poetry)

            d.image(img_source="./resources/vsh_logo.jpeg", center=True)
            d.set(align="center", bold=True, height=2, width=2)
            d.text("verschwörhaus.de")
            d.ln()
            d.ln()
            d.ln()
            d.ln()

            f._raw(d.output)
            f.close()
            self.api_handler.last_poetry = None
        except Exception as e:
            log_message(self, f"Es ist ein Druckfehler aufgetreten. Bitte kontaktiere uns einmal: {e}", LogSeverityEnum.ERROR)





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
