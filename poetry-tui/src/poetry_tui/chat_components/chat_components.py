from typing import List, Tuple

from textual.app import ComposeResult, App
from textual.containers import VerticalGroup, VerticalScroll
from textual.reactive import Reactive, reactive
from textual.widgets import Label, Input

from .utility import MessageTypeEnum


class _MessageContainer(VerticalGroup):
    def __init__(self, message_type: MessageTypeEnum, message: str):
        super().__init__()
        self.message = message
        self.border_title = "Künstliche Intelligenz" if message_type == MessageTypeEnum.AIMessage else "Sie"
        self.styles.border_title_align = "center"
        if message_type == MessageTypeEnum.AIMessage:
            self.styles.border = ("heavy", "pink")
        else:
            self.styles.border = ("heavy", "purple")

    def compose(self) -> ComposeResult:
        yield Label(self.message)

class ChatHistory(VerticalScroll):
    messages: Reactive[List[Tuple[MessageTypeEnum, str]]] = reactive([
        (MessageTypeEnum.AIMessage, "Hey! Im your assistant"),
    ], init=False)

    def compose(self) -> ComposeResult:
        for message_type, message in self.messages:
            yield _MessageContainer(message_type, message)

    def watch_messages(self, old, new) -> None:
        # Nur die zuletzt hinzugefügte Message mounten
        kind, text = new[-1]
        self.mount(_MessageContainer(kind, text))
        self.scroll_end(animate=False)

# ---- Input Section ----

class InputContainer(VerticalGroup):
    def __init__(self):
        super().__init__()
        self.border_title = "Ihre Eingabe"
        self.styles.border_title_align = "left"
        self.styles.border = ("round", "white")

    def compose(self) -> ComposeResult:
        # Safe Guard could be added via custom validator!
        yield Input(type="text")
