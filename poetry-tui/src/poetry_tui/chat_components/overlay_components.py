import time

from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Center, Middle, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


class LoadingIndicator(Static):
    """Animated loading indicator"""

    def __init__(self):
        super().__init__()
        self.animation_frames = [
            "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
        ]
        self.current_frame = 0
        self.timer = None

    def on_mount(self) -> None:
        """Init styles on mount"""
        self.styles.text_align = "center"
        self.styles.color = Color.parse("cyan")
        self.start_animation()

    def start_animation(self) -> None:
        """Start timer used to animate spinner"""
        self.timer = self.set_interval(0.1, self.update_spinner)

    def stop_animation(self) -> None:
        """Stop spinner animation"""
        if self.timer:
            self.timer.stop()

    def update_spinner(self) -> None:
        """Update sprinner animation frame"""
        frame = self.animation_frames[self.current_frame]
        self.update(f"{frame} LLM generiert Antwort... {frame}")
        self.current_frame = (self.current_frame + 1) % len(self.animation_frames)


class PulsingDot(Static):
    """Pulsating dot for loading indicator"""

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
    """Loading overlay"""

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
        """Styling of loading overlay"""
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

        # Timer for elapsed time
        self.elapsed_timer = self.set_interval(1.0, self.update_elapsed_time)

    def update_elapsed_time(self) -> None:
        """Update elapsed time"""
        elapsed = int(time.time() - self.start_time)
        elapsed_widget = self.query_one("#elapsed-time")
        elapsed_widget.update(f"Verstrichene Zeit: {elapsed}s")

    def on_unmount(self) -> None:
        """Stop timer when unmounting overlay"""
        if self.elapsed_timer:
            self.elapsed_timer.stop()

        for widget in [LoadingIndicator, PulsingDot]:
            for instance in self.query(widget):
                if hasattr(instance, 'stop_animation'):
                    instance.stop_animation()
                if hasattr(instance, 'stop_pulsing'):
                    instance.stop_pulsing()