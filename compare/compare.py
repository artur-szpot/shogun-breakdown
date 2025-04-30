from typing import Optional

from compare.compare_battle import battle_update, battle_started, run_started
from compare.compare_map import entered_map
from compare.compare_reward import reward_update, entered_reward
from compare.compare_shop import shop_update, entered_shop
from data.snapshot import Snapshot
from enums import GamePhase, LogLevel
from history.history import History


def compare_snapshots(history: History, previous_snapshot: Optional[Snapshot], new_snapshot: Snapshot,
                      log_level: LogLevel) -> History:
    if new_snapshot.game_stats.turns == 0:
        return run_started(history, new_snapshot, log_level)
    elif previous_snapshot is None:
        if log_level == LogLevel.DEBUG:
            print('== Logging started in the middle of a run lacks many features. ==')
            print()

    if previous_snapshot is None or previous_snapshot.game_phase != new_snapshot.game_phase:
        if new_snapshot.game_phase == GamePhase.BATTLE:
            return battle_started(history, previous_snapshot, new_snapshot, log_level)
        if new_snapshot.game_phase == GamePhase.BATTLE_REWARDS:
            if previous_snapshot is not None:
                history = battle_update(history, previous_snapshot, new_snapshot, log_level)
            return entered_reward(history, previous_snapshot, new_snapshot, log_level)
        if new_snapshot.game_phase == GamePhase.MAP_JOURNEY:
            return entered_map(history, log_level)
        if new_snapshot.game_phase == GamePhase.SHOP:
            return entered_shop(history, previous_snapshot, new_snapshot, log_level)

    if previous_snapshot is None:
        return history

    if new_snapshot.game_phase == GamePhase.BATTLE:
        return battle_update(history, previous_snapshot, new_snapshot, log_level)
    if new_snapshot.game_phase == GamePhase.BATTLE_REWARDS:
        return reward_update(history, previous_snapshot, new_snapshot, log_level)
    if new_snapshot.game_phase == GamePhase.MAP_JOURNEY:
        # Should never happen, map only has one possible action
        return history
    if new_snapshot.game_phase == GamePhase.SHOP:
        return shop_update(history, previous_snapshot, new_snapshot, log_level)

    raise ValueError("Unknown game state!")
