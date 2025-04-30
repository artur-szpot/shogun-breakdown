from typing import Optional

from compare.compare_battle import battle_finished
from data.snapshot import Snapshot
from enums import LogLevel
from history.history import History


def entered_reward(history: History, previous_snapshot: Optional[Snapshot], new_snapshot: Snapshot,
                   log_level: LogLevel) -> History:
    if previous_snapshot is not None:
        battle_finished(history, previous_snapshot, log_level)

    if log_level == LogLevel.DEBUG:
        if previous_snapshot is not None:
            print("== ENTERED REWARD ROOM ==")
        else:
            print("== IN A REWARD ROOM ==")
        print(f"== {new_snapshot.get_room()} ==")
        print()

    return history


def reward_update(history: History, previous_snapshot: Snapshot, new_snapshot: Snapshot,
                  log_level: LogLevel) -> History:
    return history
