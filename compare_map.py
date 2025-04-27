from enums import LogLevel
from history import History


def entered_map(history: History, log_level: LogLevel) -> History:
    if log_level == LogLevel.DEBUG:
        print("== ENTERED MAP JOURNEY ==")
        print()
    return history
