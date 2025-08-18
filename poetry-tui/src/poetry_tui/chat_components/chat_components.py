from typing import List, Tuple
import time

from textual.app import ComposeResult, App
from textual.color import Color
from textual.containers import VerticalGroup, VerticalScroll, HorizontalGroup, Vertical, Center, Middle
from textual.reactive import Reactive, reactive
from textual.widgets import Label, Input, Button, LoadingIndicator, Static
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
        yield Label(self.message, markup=True, shrink=True)

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

class LoadingIndicator(Static):
    """Animierter Loading Indicator"""

    def __init__(self):
        super().__init__()
        self.animation_frames = [
            "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
        ]
        self.current_frame = 0
        self.timer = None

    def on_mount(self) -> None:
        """Startet die Animation"""
        self.styles.text_align = "center"
        self.styles.color = Color.parse("cyan")
        self.start_animation()

    def start_animation(self) -> None:
        """Startet die Spinner-Animation"""
        self.timer = self.set_interval(0.1, self.update_spinner)

    def stop_animation(self) -> None:
        """Stoppt die Animation"""
        if self.timer:
            self.timer.stop()

    def update_spinner(self) -> None:
        """Aktualisiert den Spinner-Frame"""
        frame = self.animation_frames[self.current_frame]
        self.update(f"{frame} LLM generiert Antwort... {frame}")
        self.current_frame = (self.current_frame + 1) % len(self.animation_frames)


class PulsingDot(Static):
    """Pulsierende Punkte Animation"""

    def __init__(self):
        super().__init__()
        self.dots = 0
        self.timer = None

    def on_mount(self) -> None:
        self.styles.text_align = "center"
        self.styles.color = Color.parse("yellow")
        self.start_pulsing()

    def start_pulsing(self) -> None:
        self.timer = self.set_interval(0.5, self.update_dots)

    def stop_pulsing(self) -> None:
        if self.timer:
            self.timer.stop()

    def update_dots(self) -> None:
        dots_str = "●" * (self.dots + 1) + "○" * (3 - self.dots)
        self.update(f"Bitte warten {dots_str}")
        self.dots = (self.dots + 1) % 4


class LoadingOverlay(ModalScreen):
    """Transparenter Loading Overlay Screen"""

    def __init__(self, message: str = "LLM generiert Antwort..."):
        super().__init__()
        self.message = message
        self.start_time = time.time()
        self.elapsed_timer = None

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Vertical(id="loading-container"):
                    yield Static("🤖", id="robot-icon")
                    yield LoadingIndicator()
                    yield PulsingDot()
                    yield Static("Verstanden! Einen Moment...", id="status-text")
                    yield Static("Verstrichene Zeit: 0s", id="elapsed-time")

    def on_mount(self) -> None:
        """Styling für den Loading Overlay"""
        # Loading Container
        container = self.query_one("#loading-container")
        container.styles.background = Color(0, 0, 0, 0)
        container.styles.border = ("thick", "pink")
        container.styles.padding = 3
        container.styles.width = 60
        container.styles.height = 20
        container.styles.text_align = "center"

        # Robot Icon
        robot = self.query_one("#robot-icon")
        robot.styles.text_align = "center"
        robot.styles.color = Color.parse("cyan")
        robot.styles.text_style = "bold"
        robot.styles.margin = (0, 0, 1, 0)

        # Status Text
        status = self.query_one("#status-text")
        status.styles.color = Color.parse("white")
        status.styles.text_align = "center"
        status.styles.margin = 1

        # Elapsed Time
        elapsed = self.query_one("#elapsed-time")
        elapsed.styles.color = Color.parse("gray")
        elapsed.styles.text_align = "center"
        elapsed.styles.margin = (1, 0)

        # Timer für verstrichene Zeit
        self.elapsed_timer = self.set_interval(1.0, self.update_elapsed_time)

    def update_elapsed_time(self) -> None:
        """Aktualisiert die verstrichene Zeit"""
        elapsed = int(time.time() - self.start_time)
        elapsed_widget = self.query_one("#elapsed-time")
        elapsed_widget.update(f"Verstrichene Zeit: {elapsed}s")

    def on_unmount(self) -> None:
        """Cleanup bei Schließung"""
        if self.elapsed_timer:
            self.elapsed_timer.stop()

        # Animationen stoppen
        for widget in [LoadingIndicator, PulsingDot]:
            for instance in self.query(widget):
                if hasattr(instance, 'stop_animation'):
                    instance.stop_animation()
                if hasattr(instance, 'stop_pulsing'):
                    instance.stop_pulsing()