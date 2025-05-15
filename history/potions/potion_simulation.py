from typing import Dict, List, Optional

from data.mappers import pickup_name_mapper
from data.room.room_enums import PickupEnum


class PotionSimulation:
    sold: List[PickupEnum]
    used: List[PickupEnum]
    guesses: Dict[int, PickupEnum]
    potion_description: Optional[str]

    def __init__(self, sold_ids: List[int] = None, sold: List[PickupEnum] = None,
                 used_ids: List[int] = None, used: List[PickupEnum] = None):
        self.sold = sold or []
        self.used = used or []
        _sold_ids = sold_ids or []
        _used_ids = used_ids or []
        if len(_sold_ids) != len(self.sold) or len(_used_ids) != len(self.used):
            raise ValueError("Wrong initialization of potion simulation")
        guesses = {}
        for index, sold_id in enumerate(_sold_ids):
            guesses[sold_id] = self.sold[index]
        for index, used_id in enumerate(_used_ids):
            guesses[used_id] = self.used[index]
        self.guesses = guesses
        if not sold and not used:
            self.potion_description = None
        elif sold and not used:
            self.potion_description = f"Sold {', '.join(pickup_name_mapper[t] for t in sold)}"
        elif not sold and used:
            self.potion_description = f"Used {', '.join(pickup_name_mapper[t] for t in used)}"
        else:
            self.potion_description = f"Sold {', '.join(pickup_name_mapper[t] for t in sold)} " \
                                      f"and used {', '.join(pickup_name_mapper[t] for t in used)}"
