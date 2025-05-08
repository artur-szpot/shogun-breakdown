from typing import Dict

from constants import RUN_STATS, HITS, FRIENDLY_KILLS, HEAL_PICKUPS, POTION_PICKUPS, SCROLL_PICKUPS, \
    COMBAT_ROOMS_CLEARED, COMBOS, TURN_AROUNDS, TIME, COINS, TURNS, NEW_TILES_PICKED, CONSUMABLES_USED, DAY, VERSION
from data.snapshot.prediction_error import PredictionError
from data.snapshot.predictions import Predictions
from logger import logger


class GameStats:
    version: str
    turn_arounds: int
    coins: int
    combos: int
    turns: int
    time: int
    combat_rooms_cleared: int
    scroll_pickups: int
    potion_pickups: int
    heal_pickups: int
    friendly_kills: int
    hits: int
    day: int
    consumables_used: int
    new_tiles_picked: int

    def __init__(self,
                 version: str,
                 turn_arounds: int,
                 coins: int,
                 combos: int,
                 turns: int,
                 time: int,
                 combat_rooms_cleared: int,
                 scroll_pickups: int,
                 potion_pickups: int,
                 heal_pickups: int,
                 friendly_kills: int,
                 hits: int,
                 day: int,
                 consumables_used: int,
                 new_tiles_picked: int,
                 ):
        self.version = version
        self.turn_arounds = turn_arounds
        self.coins = coins
        self.combos = combos
        self.turns = turns
        self.time = time
        self.combat_rooms_cleared = combat_rooms_cleared
        self.scroll_pickups = scroll_pickups
        self.potion_pickups = potion_pickups
        self.heal_pickups = heal_pickups
        self.friendly_kills = friendly_kills
        self.hits = hits
        self.day = day
        self.consumables_used = consumables_used
        self.new_tiles_picked = new_tiles_picked

    @staticmethod
    def from_dict(source: Dict):
        version = source[VERSION]
        turn_arounds = source[RUN_STATS].get(TURN_AROUNDS, 0)
        coins = source[RUN_STATS].get(COINS, 0)
        combos = source[RUN_STATS].get(COMBOS, 0)
        turns = source[RUN_STATS][TURNS]
        time = source[RUN_STATS][TIME]
        combat_rooms_cleared = source[RUN_STATS][COMBAT_ROOMS_CLEARED]
        scroll_pickups = source[RUN_STATS][SCROLL_PICKUPS]
        potion_pickups = source[RUN_STATS][POTION_PICKUPS]
        heal_pickups = source[RUN_STATS][HEAL_PICKUPS]
        friendly_kills = source[RUN_STATS][FRIENDLY_KILLS]
        hits = source[RUN_STATS][HITS]
        day = source[RUN_STATS][DAY]
        consumables_used = source[RUN_STATS][CONSUMABLES_USED]
        new_tiles_picked = source[RUN_STATS][NEW_TILES_PICKED]
        return GameStats(
            version=version,
            turn_arounds=turn_arounds,
            coins=coins,
            combos=combos,
            turns=turns,
            time=time,
            combat_rooms_cleared=combat_rooms_cleared,
            scroll_pickups=scroll_pickups,
            potion_pickups=potion_pickups,
            heal_pickups=heal_pickups,
            friendly_kills=friendly_kills,
            hits=hits,
            day=day,
            consumables_used=consumables_used,
            new_tiles_picked=new_tiles_picked
        )

    def clone(self):
        return GameStats(
            version=self.version,
            turn_arounds=self.turn_arounds,
            coins=self.coins,
            combos=self.combos,
            turns=self.turns,
            time=self.time,
            combat_rooms_cleared=self.combat_rooms_cleared,
            scroll_pickups=self.scroll_pickups,
            potion_pickups=self.potion_pickups,
            heal_pickups=self.heal_pickups,
            friendly_kills=self.friendly_kills,
            hits=self.hits,
            day=self.day,
            consumables_used=self.consumables_used,
            new_tiles_picked=self.new_tiles_picked
        )

    def debug_print(self) -> str:
        return f"ta {self.turn_arounds} $ {self.coins} cmb {self.combos} scr {self.scroll_pickups} " \
               f"pot {self.potion_pickups} heal {self.heal_pickups} fk {self.friendly_kills} ht {self.hits}" \
               f"cu {self.consumables_used}"

    def is_equal(self, other, debug: bool = False):
        if not debug:
            return self.turn_arounds == other.turn_arounds \
                   and self.coins == other.coins \
                   and self.combos == other.combos \
                   and self.turns == other.turns \
                   and self.combat_rooms_cleared == other.combat_rooms_cleared \
                   and self.scroll_pickups == other.scroll_pickups \
                   and self.potion_pickups == other.potion_pickups \
                   and self.heal_pickups == other.heal_pickups \
                   and self.friendly_kills == other.friendly_kills \
                   and self.hits == other.hits \
                   and self.consumables_used == other.consumables_used
        if self.turn_arounds != other.turn_arounds:
            raise PredictionError(f"wrong number of turn arounds")
        if self.coins != other.coins:
            raise PredictionError(f"wrong number of coins")
        if self.combos != other.combos:
            raise PredictionError(f"wrong number of combos self {self.combos} other {other.combos}")
        if self.turns != other.turns:
            raise PredictionError(f"wrong number of turns")
        if self.combat_rooms_cleared != other.combat_rooms_cleared:
            raise PredictionError(f"wrong number of rooms cleared")
        if self.scroll_pickups != other.scroll_pickups:
            raise PredictionError(
                f"wrong number of equal scroll pickups self {self.scroll_pickups} other {other.scroll_pickups}")
        if self.potion_pickups != other.potion_pickups:
            raise PredictionError(
                f"wrong number of potion pickups self {self.potion_pickups} other {other.potion_pickups}")
        if self.heal_pickups != other.heal_pickups:
            raise PredictionError(f"wrong number of heal pickups self {self.heal_pickups} other {other.heal_pickups}")
        if self.friendly_kills != other.friendly_kills:
            raise PredictionError(f"wrong number of friendly kills")
        if self.hits != other.hits:
            raise PredictionError(f"wrong number of hits self {self.hits} other {other.hits}")
        if self.consumables_used != other.consumables_used:
            raise PredictionError(f"wrong number of consumables used")
        return True

    def is_good_prediction(self, other, predictions: Predictions, debug: bool = False):
        new_potions = predictions.new_potions

        if predictions.allow_more_coins:
            coins_good = self.coins >= other.coins
        else:
            coins_good = self.coins == other.coins

        if predictions.allow_more_turn_arounds:
            turn_arounds_good = self.turn_arounds >= other.turn_arounds
        else:
            turn_arounds_good = self.turn_arounds == other.turn_arounds

        result = turn_arounds_good and coins_good \
                 and self.combos == other.combos \
                 and self.turns == other.turns \
                 and self.combat_rooms_cleared == other.combat_rooms_cleared \
                 and self.scroll_pickups <= other.scroll_pickups + new_potions \
                 and self.potion_pickups <= other.potion_pickups + new_potions \
                 and self.heal_pickups <= other.heal_pickups + new_potions \
                 and self.scroll_pickups + self.potion_pickups + self.heal_pickups <= \
                 other.scroll_pickups + other.potion_pickups + other.heal_pickups + new_potions \
                 and self.friendly_kills == other.friendly_kills \
                 and self.hits == other.hits \
                 and self.consumables_used == other.consumables_used
        if not debug:
            return result
        if not turn_arounds_good:
            raise PredictionError(f"wrong number of turn arounds self {self.turn_arounds} other {other.turn_arounds}")
        if not coins_good:
            raise PredictionError(f"wrong number of coins self {self.coins} other {other.coins}")
        if self.combos != other.combos:
            raise PredictionError(f"wrong number of combos self {self.combos} other {other.combos}")
        if self.turns != other.turns:
            raise PredictionError(f"wrong number of turns self {self.turns} other {other.turns}")
        if self.combat_rooms_cleared != other.combat_rooms_cleared:
            raise PredictionError(
                f"wrong number of rooms cleared self {self.combat_rooms_cleared} other {other.combat_rooms_cleared}")
        if self.scroll_pickups > other.scroll_pickups + new_potions:
            raise PredictionError(
                f"wrong number of scroll pickups self {self.scroll_pickups} other {other.scroll_pickups} new pots {new_potions}")
        if self.potion_pickups > other.potion_pickups + new_potions:
            raise PredictionError(
                f"wrong number of potion pickups self {self.potion_pickups} other {other.potion_pickups}")
        if self.heal_pickups > other.heal_pickups + new_potions:
            raise PredictionError(f"wrong number of heal pickups self {self.heal_pickups} other {other.heal_pickups}")
        if self.scroll_pickups + self.potion_pickups + self.heal_pickups > \
                other.scroll_pickups + other.potion_pickups + other.heal_pickups + new_potions:
            raise PredictionError(f"wrong number of total pickups "
                                  f"self {self.scroll_pickups + self.potion_pickups + self.heal_pickups} "
                                  f"other {other.scroll_pickups + other.potion_pickups + other.heal_pickups + new_potions}")
        if self.friendly_kills != other.friendly_kills:
            raise PredictionError(
                f"wrong number of friendly kills self {self.friendly_kills} other {other.friendly_kills}")
        if self.hits != other.hits:
            raise PredictionError(f"wrong number of hits self {self.hits} other {other.hits}")
        if self.consumables_used != other.consumables_used:
            raise PredictionError(
                f"wrong number of consumables used self {self.consumables_used} other {other.consumables_used}")
        if not result:
            raise PredictionError("Unchecked value is still wrong")
        return result

    def diff(self, other, new_potions: int):
        if self.turn_arounds != other.turn_arounds:
            logger.queue_debug_error(
                f"wrong number of turn arounds self {self.turn_arounds} other {other.turn_arounds}")
        if self.coins != other.coins:
            logger.queue_debug_error(f"wrong number of coins")
        if self.combos != other.combos:
            logger.queue_debug_error(f"wrong number of combos self {self.combos} other {other.combos}")
        if self.turns != other.turns:
            logger.queue_debug_error(f"wrong number of turns")
        if self.combat_rooms_cleared != other.combat_rooms_cleared:
            logger.queue_debug_error(f"wrong number of rooms cleared")
        if self.scroll_pickups > other.scroll_pickups + new_potions:
            logger.queue_debug_error(
                f"wrong number of scroll pickups self {self.scroll_pickups} other {other.scroll_pickups} np {new_potions}")
        if self.potion_pickups > other.potion_pickups + new_potions:
            logger.queue_debug_error(
                f"wrong number of potion pickups self {self.potion_pickups} other {other.potion_pickups}")
        if self.heal_pickups > other.heal_pickups + new_potions:
            logger.queue_debug_error(
                f"wrong number of heal pickups self {self.heal_pickups} other {other.heal_pickups}")
        if self.scroll_pickups + self.potion_pickups + self.heal_pickups > \
                other.scroll_pickups + other.potion_pickups + other.heal_pickups + new_potions:
            logger.queue_debug_error(f"wrong number of total pickups "
                                     f"self {self.scroll_pickups + self.potion_pickups + self.heal_pickups} "
                                     f"other {other.scroll_pickups + other.potion_pickups + other.heal_pickups + new_potions}")
        if self.friendly_kills != other.friendly_kills:
            logger.queue_debug_error(f"wrong number of friendly kills")
        if self.hits != other.hits:
            logger.queue_debug_error(f"wrong number of hits self {self.hits} other {other.hits}")
        if self.consumables_used != other.consumables_used:
            logger.queue_debug_error(f"wrong number of consumables used")
