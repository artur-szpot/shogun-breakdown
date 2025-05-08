import json
from typing import Dict, Tuple, List

from constants import SKILLS, HERO, FACING, SPECIAL_MOVE_COOLDOWN, MAX_HP, ENTITY_STATE, HP, POISON, ICE, CURSE, SHIELD, \
    HERO_ENUM, HITS, RUN_STATS, FRIENDLY_KILLS, HEAL_PICKUPS, POTION_PICKUPS, SCROLL_PICKUPS, COMBAT_ROOMS_CLEARED, \
    TURNS, COMBOS, COINS, TURN_AROUNDS, SKILL_LEVELS, TIME, CELL, NEW_TILES_PICKED, CONSUMABLES_USED, DAY, PRICE, \
    REWARD, REWARD_ROOM, TILE_UPGRADE, TILE_REWARDS, EXHAUSTED, REROLL_PRICE, IN_PROGRESS, FREE_POTION_ALREADY_GIVEN, \
    SHOP_DATA, SHOP_ROOM, RIGHT_SHOP_TYPE, LEFT_SHOP_TYPE, FREE_POTION, ALREADY_UPGRADED, SHOP_ITEMS_SALE, \
    SHOP_ITEM_NAMES, MAP_SELECTION, VERSION, RUN_NUMBER, RUN_IN_PROGRESS, NAME, ATTACK_QUEUE, DECK, POTIONS, \
    COMBAT_ROOM, ENEMIES, PICKUP_LOCATIONS, PICKUPS, UNTIL_NEXT_WAVE, WAVE_NUMBER, PATTERN_INDEX, ELITE_TYPE, \
    FIRST_TURN, ENEMY_TILE_EFFECT, TILE_TO_PLAY, PREVIOUS_ACTION, ACTION, ENEMY, CURRENT_LOCATION, MAP_SAVE, \
    CURRENT_LOCATION_NAME, UNCOVERED_LOCATIONS, PROGRESSION_DATA, PROGRESSION, CORRUPTED_BOSS_SECTORS, ROOM_VARIANT, \
    SHOP_COMPONENT
from logger import logger


def is_empty_dict(source: Dict) -> Tuple[bool, Dict]:
    whats_left = {}
    for key, value in source.items():
        if isinstance(value, Dict):
            is_empty, sub_value = is_empty_dict(value)
            if not is_empty:
                whats_left[key] = sub_value
        elif isinstance(value, List):
            sub_values = []
            for item in value:
                sub_empty, sub_value = is_empty_dict(item)
                if not sub_empty:
                    sub_values.append(sub_value)
            if len(sub_values):
                whats_left[key] = sub_values
        else:
            whats_left[key] = value
    return not bool(whats_left), whats_left


def test_data(raw_data: Dict) -> None:
    # Test that all data is being recorded.
    # Remove skills' data
    del raw_data[SKILLS]
    del raw_data[SKILL_LEVELS]

    # Remove game stats' data
    del raw_data[VERSION]
    del raw_data[RUN_STATS][TURN_AROUNDS]
    del raw_data[RUN_STATS][COINS]
    del raw_data[RUN_STATS][COMBOS]
    del raw_data[RUN_STATS][TURNS]
    del raw_data[RUN_STATS][TIME]
    del raw_data[RUN_STATS][COMBAT_ROOMS_CLEARED]
    del raw_data[RUN_STATS][SCROLL_PICKUPS]
    del raw_data[RUN_STATS][POTION_PICKUPS]
    del raw_data[RUN_STATS][HEAL_PICKUPS]
    del raw_data[RUN_STATS][FRIENDLY_KILLS]
    del raw_data[RUN_STATS][HITS]
    del raw_data[RUN_STATS][DAY]
    del raw_data[RUN_STATS][CONSUMABLES_USED]
    del raw_data[RUN_STATS][NEW_TILES_PICKED]

    # Remove hero data
    del raw_data[HERO][HERO_ENUM]
    del raw_data[HERO][ENTITY_STATE][SHIELD]
    del raw_data[HERO][ENTITY_STATE][CURSE]
    del raw_data[HERO][ENTITY_STATE][ICE]
    del raw_data[HERO][ENTITY_STATE][POISON]
    del raw_data[HERO][ENTITY_STATE][HP]
    del raw_data[HERO][ENTITY_STATE][MAX_HP]
    del raw_data[HERO][SPECIAL_MOVE_COOLDOWN]
    del raw_data[HERO][FACING]
    del raw_data[HERO][CELL]
    del raw_data[HERO][ATTACK_QUEUE]
    del raw_data[DECK]
    del raw_data[POTIONS]

    # Remove reward data
    del raw_data[REWARD_ROOM][REWARD][IN_PROGRESS]
    del raw_data[REWARD_ROOM][REROLL_PRICE]
    del raw_data[REWARD_ROOM][REWARD][EXHAUSTED]
    del raw_data[REWARD_ROOM][REWARD][TILE_REWARDS]
    del raw_data[REWARD_ROOM][REWARD][TILE_UPGRADE]

    # Remove shop data
    del raw_data[SHOP_ROOM][REWARD][IN_PROGRESS]
    del raw_data[SHOP_ROOM][REWARD][TILE_UPGRADE]
    del raw_data[SHOP_ROOM][REWARD][PRICE]
    del raw_data[SHOP_ROOM][SHOP_DATA][SHOP_ITEM_NAMES]
    del raw_data[SHOP_ROOM][SHOP_DATA][SHOP_ITEMS_SALE]
    del raw_data[SHOP_ROOM][SHOP_DATA][ALREADY_UPGRADED]
    del raw_data[SHOP_ROOM][SHOP_DATA][FREE_POTION]
    del raw_data[SHOP_ROOM][LEFT_SHOP_TYPE]
    del raw_data[SHOP_ROOM][RIGHT_SHOP_TYPE]

    # Remove battle room state data
    for i in range(len(raw_data[COMBAT_ROOM][ENEMIES])):
        del raw_data[COMBAT_ROOM][ENEMIES][i][ENTITY_STATE][SHIELD]
        del raw_data[COMBAT_ROOM][ENEMIES][i][ENTITY_STATE][CURSE]
        del raw_data[COMBAT_ROOM][ENEMIES][i][ENTITY_STATE][ICE]
        del raw_data[COMBAT_ROOM][ENEMIES][i][ENTITY_STATE][POISON]
        del raw_data[COMBAT_ROOM][ENEMIES][i][ENTITY_STATE][HP]
        del raw_data[COMBAT_ROOM][ENEMIES][i][ENTITY_STATE][MAX_HP]
        del raw_data[COMBAT_ROOM][ENEMIES][i][FACING]
        del raw_data[COMBAT_ROOM][ENEMIES][i][CELL]
        del raw_data[COMBAT_ROOM][ENEMIES][i][ATTACK_QUEUE]
        del raw_data[COMBAT_ROOM][ENEMIES][i][ENEMY]
        del raw_data[COMBAT_ROOM][ENEMIES][i][ACTION]
        del raw_data[COMBAT_ROOM][ENEMIES][i][PREVIOUS_ACTION]
        del raw_data[COMBAT_ROOM][ENEMIES][i][TILE_TO_PLAY]
        del raw_data[COMBAT_ROOM][ENEMIES][i][ENEMY_TILE_EFFECT]
        del raw_data[COMBAT_ROOM][ENEMIES][i][FIRST_TURN]
        del raw_data[COMBAT_ROOM][ENEMIES][i][ELITE_TYPE]
        del raw_data[COMBAT_ROOM][ENEMIES][i][PATTERN_INDEX]
    del raw_data[COMBAT_ROOM][WAVE_NUMBER]
    del raw_data[COMBAT_ROOM][UNTIL_NEXT_WAVE]
    del raw_data[PICKUPS]
    del raw_data[PICKUP_LOCATIONS]
    del raw_data[PROGRESSION_DATA][PROGRESSION]
    del raw_data[PROGRESSION_DATA][ROOM_VARIANT]
    del raw_data[PROGRESSION_DATA][CORRUPTED_BOSS_SECTORS]

    # Other
    del raw_data[MAP_SELECTION]  # which game phase it is
    del raw_data[MAP_SAVE][CURRENT_LOCATION]  # where we are
    del raw_data[MAP_SAVE][SHOP_COMPONENT]  # used to constrcut whole map in history

    # Remove purposely ignored data
    del raw_data[HERO][NAME]  # taken from enum
    del raw_data[RUN_IN_PROGRESS]  # why would it not be true?
    del raw_data[RUN_NUMBER]  # how to get it above 0?
    del raw_data[REWARD_ROOM][REWARD][PRICE]  # always 0
    del raw_data[SHOP_ROOM][REWARD][EXHAUSTED]  # doesn't happen
    del raw_data[SHOP_ROOM][REWARD][TILE_REWARDS]  # never offered
    del raw_data[SHOP_ROOM][SHOP_DATA][FREE_POTION_ALREADY_GIVEN]  # not interesting
    del raw_data[MAP_SAVE][CURRENT_LOCATION_NAME]  # mapped from other values
    del raw_data[MAP_SAVE][UNCOVERED_LOCATIONS]  # not needed

    # Print what's left
    is_empty, whats_left = is_empty_dict(raw_data)
    if not is_empty:
        logger.debug_error(json.dumps(whats_left, indent=2))
        raise ValueError("Unused data detected in the save file")
