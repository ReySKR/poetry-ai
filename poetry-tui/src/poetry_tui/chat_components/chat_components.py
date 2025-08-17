from typing import List, Tuple

from textual.app import ComposeResult, App
from textual.color import Color
from textual.containers import VerticalGroup, VerticalScroll, HorizontalGroup
from textual.reactive import Reactive, reactive
from textual.widgets import Label, Input, Button, LoadingIndicator
from textual.screen import ModalScreen

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
    messages: Reactive[List[Tuple[MessageTypeEnum, str]]] = reactive([], init=False, recompose=True)
    is_loading: Reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        yield _MessageContainer(MessageTypeEnum.AIMessage, "Hey! Ich bin dein Poesieassitent. Zusammen werden wir ein tolles Gedicht zaubern, beschreibe doch einfach eine Szenerie, oder gib mir ein paar Stichwörter und ich mache dir einen Vorschlag 😃")
        for message_type, message in self.messages:
            yield _MessageContainer(message_type, message)


# ---- Input Section ----

class InputContainer(VerticalGroup):

    DEFAULT_CSS = """
    HorizontalGroup { padding: 1 0 1 1; width: 100%; align-horizontal: center; }
    Button { width: 50%; border: tall $border-blurred; margin: 0 0 0 1; }
    """

    def __init__(self):
        super().__init__()
        self.border_title = "Ihre Eingabe"
        self.styles.border_title_align = "left"
        self.styles.border = ("round", "white")

    def compose(self) -> ComposeResult:
        # Safe Guard could be added via custom validator!
        yield Input(type="text", id="prompt", placeholder="Ihre einzigartige Antwort an die KI.")
        yield HorizontalGroup(
            Button("Neuer Chat", id="btn_new_chat"),
            Button("Drucken", id="btn_print")
        )

class LoadingOverlay(ModalScreen):
    def __init__(self):
        super().__init__()
        self.styles.background = Color.parse("rgba(255, 255, 255, 0.1)")

    def compose(self):
        yield LoadingIndicator()