from typing import Optional

from compare.compare_battle import battle_update, battle_started, run_started, battle_ended
from compare.compare_map import entered_map
from compare.compare_reward import reward_update, entered_reward
from compare.compare_shop import shop_update, entered_shop
from data.other_enums import GamePhase
from data.snapshot.snapshot import Snapshot
from history.history import History
from logger import logger


def compare_snapshots(previous_snapshot: Optional[Snapshot], new_snapshot: Snapshot) -> History:
    if new_snapshot.game_stats.turns == 0:
        return run_started(new_snapshot)
    elif previous_snapshot is None:
        logger.detail_info('== Logging started in the middle of a run lacks many features. ==')
        logger.detail_info("")

    if previous_snapshot is None or previous_snapshot.game_phase != new_snapshot.game_phase:
        if previous_snapshot is not None:
            if previous_snapshot.game_phase == GamePhase.BATTLE:
                history = battle_ended(previous_snapshot, new_snapshot)
            if previous_snapshot.game_phase == GamePhase.BATTLE_REWARDS:
                # history = reward_update(previous_snapshot, new_snapshot)
                # Nothing here either # TODO unless potions...?
                pass
            if previous_snapshot.game_phase == GamePhase.MAP_JOURNEY:
                # Nothing to get from here
                pass
            if previous_snapshot.game_phase == GamePhase.SHOP:
                history = shop_update(previous_snapshot, new_snapshot)

        if new_snapshot.game_phase == GamePhase.BATTLE:
            return battle_started(previous_snapshot, new_snapshot)
        if new_snapshot.game_phase == GamePhase.BATTLE_REWARDS:
            # if previous_snapshot is not None:
            #     history = battle_ended(previous_snapshot, new_snapshot)
            return entered_reward(previous_snapshot, new_snapshot)
        if new_snapshot.game_phase == GamePhase.MAP_JOURNEY:
            entered_map()
            if previous_snapshot is not None:
                return previous_snapshot.history
            else:
                return new_snapshot.history
        if new_snapshot.game_phase == GamePhase.SHOP:
            return entered_shop(previous_snapshot, new_snapshot)

    if previous_snapshot is None:
        return new_snapshot.history

    if new_snapshot.game_phase == GamePhase.BATTLE:
        return battle_update(previous_snapshot, new_snapshot)
    if new_snapshot.game_phase == GamePhase.BATTLE_REWARDS:
        return reward_update(previous_snapshot, new_snapshot)
    if new_snapshot.game_phase == GamePhase.MAP_JOURNEY:
        # Should never happen, map only has one possible action
        return previous_snapshot.history
    if new_snapshot.game_phase == GamePhase.SHOP:
        return shop_update(previous_snapshot, new_snapshot)

    raise ValueError("Unknown game state!")
