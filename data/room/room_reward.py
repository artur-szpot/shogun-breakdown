from typing import List, Dict

from constants import REWARD, REWARD_ROOM, TILE_UPGRADE, TILE_REWARDS, EXHAUSTED, REROLL_PRICE, IN_PROGRESS
from data.mappers import upgrade_name_mapper
from data.room.room_enums import WeaponUpgradesEnum
from data.weapon.weapon import Weapon


class RewardRoom:
    current_reroll_price: int
    exhausted: bool
    available_tiles: List[Weapon]
    available_upgrade: int

    def __init__(self,
                 current_reroll_price: int,
                 exhausted: bool,
                 available_tiles: List[Weapon],
                 available_upgrade: int,
                 ):
        self.current_reroll_price = current_reroll_price
        self.exhausted = exhausted
        self.available_tiles = available_tiles
        self.available_upgrade = available_upgrade

    @staticmethod
    def from_dict(source: Dict):
        if not source[REWARD_ROOM][REWARD][IN_PROGRESS]:
            return None
        current_reroll_price = source[REWARD_ROOM][REROLL_PRICE]
        exhausted = source[REWARD_ROOM][REWARD][EXHAUSTED]
        available_tiles = [Weapon.from_dict(x) for x in source[REWARD_ROOM][REWARD][TILE_REWARDS]]
        available_upgrade = source[REWARD_ROOM][REWARD][TILE_UPGRADE]
        return RewardRoom(
            current_reroll_price=current_reroll_price,
            exhausted=exhausted,
            available_tiles=available_tiles,
            available_upgrade=available_upgrade,
        )

    def pretty_print_reward(self):
        if self.available_upgrade == 0:
            return ' or '.join(w.pretty_print() for w in self.available_tiles)
        return f"Upgrade {upgrade_name_mapper[WeaponUpgradesEnum(self.available_upgrade)]}"
