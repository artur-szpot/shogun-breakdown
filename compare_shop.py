from typing import Optional

from enums import LogLevel
from history import History
from snapshot import Snapshot


def entered_shop(history: History, previous_snapshot: Optional[Snapshot], new_snapshot: Snapshot,
                 log_level: LogLevel) -> History:
    if log_level == LogLevel.DEBUG:
        if previous_snapshot is None:
            print("== IN A SHOP ==")
        else:
            print("== ENTERED A SHOP ==")
        print(f"== {new_snapshot.get_room()} ==")
        print()
    return history


def shop_update(history: History, previous_snapshot: Snapshot, new_snapshot: Snapshot, log_level: LogLevel) -> History:
    return history
