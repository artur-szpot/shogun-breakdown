from typing import Dict

from constants import RUN_STATS, HITS, FRIENDLY_KILLS, HEAL_PICKUPS, POTION_PICKUPS, SCROLL_PICKUPS, \
    COMBAT_ROOMS_CLEARED, COMBOS, TURN_AROUNDS, TIME, COINS, TURNS, NEW_TILES_PICKED, CONSUMABLES_USED, DAY, VERSION


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
    consumabled_used: int
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
                 consumabled_used: int,
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
        self.consumabled_used = consumabled_used
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
        consumabled_used = source[RUN_STATS][CONSUMABLES_USED]
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
            consumabled_used=consumabled_used,
            new_tiles_picked=new_tiles_picked
        )
