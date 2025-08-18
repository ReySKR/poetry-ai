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
            logging.info(message)
            screen_instance.notify(message, severity="information")
        case LogSeverityEnum.WARNING:
            logging.warning(message)
            screen_instance.notify(message, severity="warning")

        case LogSeverityEnum.ERROR:
            logging.error(message)
            screen_instance.notify(message, severity="error")
        case _:
            logging.info(message + "(Severity unspecified)")
            screen_instance.notify(message + "(Severity unspecified)", severity="information")