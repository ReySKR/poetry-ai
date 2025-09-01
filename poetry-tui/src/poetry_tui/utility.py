import logging
from enum import Enum

from textual.screen import Screen


class LogSeverityEnum(Enum):
    """Enumeration for log severity levels."""
    INFO = 0
    WARNING = 1
    ERROR = 2

def log_message(screen_instance: Screen, message, severity: LogSeverityEnum):
    """Logs a message via notify on screen. And via logging."""
    match severity:
        case LogSeverityEnum.INFO:
            screen_instance.notify(message, severity="information")
        case LogSeverityEnum.WARNING:
            screen_instance.notify(message, severity="warning")

        case LogSeverityEnum.ERROR:
            screen_instance.notify(message, severity="error")
        case _:
            screen_instance.notify(message + "(Severity unspecified)", severity="information")