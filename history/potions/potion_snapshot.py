from typing import Dict, List

from data.room.room_enums import PickupEnum


class PotionSnapshot:
    coins: int
    potions_ids: List[int]
    ground_potions: Dict[int, Dict[PickupEnum, int]]
    total_used: int
    total_scrolls_dropped: int
    total_potions_dropped: int
    total_heals_dropped: int

    def __init__(
            self,
            coins: int,
            potions_ids: List[int],
            ground_potions: Dict[int, Dict[PickupEnum, int]],
            total_used: int,
            total_scrolls_dropped: int,
            total_potions_dropped: int,
            total_heals_dropped: int,
    ):
        self.coins = coins
        self.potions_ids = potions_ids
        self.ground_potions = ground_potions
        self.total_used = total_used
        self.total_scrolls_dropped = total_scrolls_dropped
        self.total_potions_dropped = total_potions_dropped
        self.total_heals_dropped = total_heals_dropped

    def id_totals(self) -> Dict[int, int]:
        retval = {}
        for pid in self.potions_ids:
            if pid not in retval:
                retval[pid] = 1
            else:
                retval[pid] += 1
        return retval

    def total_dropped(self) -> int:
        return self.total_scrolls_dropped + self.total_potions_dropped + self.total_heals_dropped
