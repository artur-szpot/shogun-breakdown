from typing import Optional

from compare.compare_battle import battle_finished
from data.snapshot.snapshot import Snapshot
from history.history import History
from logger import logger


def entered_reward(history: History, previous_snapshot: Optional[Snapshot], new_snapshot: Snapshot
                   ) -> History:
    if previous_snapshot is not None:
        battle_finished(history, previous_snapshot)

    if previous_snapshot is not None:
        logger.detail_info("== ENTERED REWARD ROOM ==")
    else:
        logger.detail_info("== IN A REWARD ROOM ==")
    logger.detail_info(f"== {new_snapshot.get_room()} ==")
    logger.detail_text(new_snapshot.reward.pretty_print_reward())
    logger.detail_text(f"Current reroll price: {new_snapshot.reward.current_reroll_price}")
    logger.line()

    return history


def reward_update(history: History, previous_snapshot: Snapshot, new_snapshot: Snapshot) -> History:
    old_reward = previous_snapshot.reward
    new_reward = new_snapshot.reward

    # New tile taken.
    if len(previous_snapshot.hero_deck) < len(new_snapshot.hero_deck):
        logger.detail_success(f"Taken new tile: {new_snapshot.hero_deck[-1].pretty_print()}")
        return history

    # Upgrade rewards taken.
    for index, weapon in enumerate(previous_snapshot.hero_deck):
        if not weapon.is_equal(new_snapshot.hero_deck[index]):
            # TODO handle adding slots etc. more gracefully
            logger.detail_success(
                f"Upgraded {weapon.pretty_print()} into {new_snapshot.hero_deck[index].pretty_print()}")
            return history

    # Was the reward rerolled?
    if old_reward.current_reroll_price != new_reward.current_reroll_price:
        logger.detail_info(f"Rerolled the rewards. New reroll price: {new_reward.current_reroll_price}")
        logger.detail_info(f"New reward: {new_snapshot.reward.pretty_print_reward()}")
        return history
    # Was it rerolled using Lucky Die?
    elif old_reward.available_upgrade != new_reward.available_upgrade \
            or False in [old_weapon.is_equal(new_snapshot.reward.available_tiles[index]) for index, old_weapon in
                         enumerate(previous_snapshot.reward.available_tiles)]:
        # TODO mark that the hero has used the potion
        logger.detail_info(f"Rerolled the rewards using Lucky Die.")
        logger.detail_info(f"New reward: {new_snapshot.reward.pretty_print_reward()}")
        return history

    return history
