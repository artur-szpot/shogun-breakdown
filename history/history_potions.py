from typing import Dict, List, Optional

from data.mappers import pickup_name_mapper
from data.other_enums import GamePhase
from data.room.room_enums import PickupEnum
from data.snapshot.snapshot import Snapshot
from logger import logger


class Potion:
    potion_types: List[PickupEnum]
    entangled_id: Optional[int]

    def __init__(self, possible_types: List[PickupEnum], entangled_id: Optional[int] = None):
        self.potion_types = possible_types
        self.entangled_id = entangled_id


class PotionHistory:
    potions: Dict[int, Potion]
    potion_queue: List[Potion]
    last_entanglement_id: int

    def __init__(self, first_snapshot: Snapshot):
        potion_ids = first_snapshot.hero_potion_ids
        all_types = [
            PickupEnum.EDAMAME_BREW,
            PickupEnum.COOL_UP,
            PickupEnum.KAMI_BREW,
            PickupEnum.LUCKY_DIE,
            PickupEnum.MASS_CURSE,
            PickupEnum.MASS_ICE,
            PickupEnum.MASS_POISON,
            PickupEnum.RAIN_OF_MIRRORS,
        ]
        self.potions = {p_id: Potion(possible_types=all_types, entangled_id=0) for p_id in potion_ids}
        self.potion_queue = []
        self.last_entanglement_id = 0

    def battle_update(self, previous_snapshot: Snapshot, new_snapshot: Snapshot):
        old_ids = previous_snapshot.hero_potion_ids
        new_ids = new_snapshot.hero_potion_ids
        added_ids = []
        for old_id in old_ids:
            if old_id not in new_ids:
                self.use_potion(old_id)  # TODO: or sell with rogue retail!
        for new_id in new_ids:
            if new_id not in old_ids:
                added_ids.append(new_id)
        could_have_been_picked_up = (previous_snapshot.room.pickups or {}).get(
            previous_snapshot.room.hero.position.cell, {})
        not_picked_up = (new_snapshot.room.pickups or {}).get(
            previous_snapshot.room.hero.position.cell, {})
        for potion_type, total in could_have_been_picked_up:
            new_total = not_picked_up.get(potion_type, 0)
            total_picked_up = total - new_total
            for i in range(total_picked_up):
                self.potion_queue.append(Potion([potion_type]))
        self.process_queue(added_ids)

    def shop_update(self, previous_snapshot: Snapshot, new_snapshot: Snapshot) -> List[int]:
        old_ids = previous_snapshot.hero_potion_ids
        new_ids = new_snapshot.hero_potion_ids
        added_ids = []
        for old_id in old_ids:
            if old_id not in new_ids:
                self.use_or_sell_potion(old_id)
        for new_id in new_ids:
            if new_id not in old_ids:
                added_ids.append(new_id)
        if previous_snapshot.game_phase != GamePhase.SHOP or previous_snapshot.shop.free_potion != new_snapshot.shop.free_potion:
            self.potion_queue.append(Potion([PickupEnum.EDAMAME_BREW, PickupEnum.KAMI_BREW]))
        # self.process_queue(added_ids)
        if new_snapshot.game_phase != GamePhase.SHOP:
            self.potion_queue = []
        return added_ids

    def process_queue(self, added_ids: List[int]):
        if len(self.potion_queue) != len(added_ids):
            raise ValueError(f"Wrong number of new potions appeared. Expected {len(self.potion_queue)}, "
                             f"got {len(added_ids)}")
        all_types = []
        for potion in self.potion_queue:
            for p_type in potion.potion_types:
                if p_type not in all_types:
                    all_types.append(p_type)
        self.add_entangled(all_types, added_ids)

    def queue_potion(self, potion_types: List[PickupEnum]):
        self.potion_queue.append(Potion(potion_types))

    def use_potion(self, potion_id):
        # apply effects, where and how?
        possible_types = [pickup_name_mapper[p] for p in self.potions[potion_id].potion_types]
        logger.debug_info(f"Used potion. Possible types: {', '.join(possible_types)}")
        del self.potions[potion_id]

    def use_or_sell_potion(self, potion_id):
        # apply effects, where and how?
        # not working yet
        return
        # possible_types = [pickup_name_mapper[p] for p in self.potions[potion_id].potion_types]
        # logger.debug_info(f"Used or sold potion. Possible types: {', '.join(possible_types)}")
        # del self.potions[potion_id]

    def get_entangled_id(self):
        self.last_entanglement_id += 1
        return self.last_entanglement_id

    # def add_certain(self, potion_type: PickupEnum, potion_id: int):
    #     self.potions[potion_id] = Potion([potion_type])
    #
    # def add_uncertain(self, potion_types: List[PickupEnum], potion_id: int):
    #     self.potions[potion_id] = Potion(potion_types)
    #
    # def queue_uncertain(self, potion_types: List[PickupEnum], potion_ids: List[int]):
    #     new_potion = Potion(potion_types)
    #     for p_id in potion_ids:
    #         if p_id not in self.potions:
    #             self.potions[p_id] = new_potion
    #             return
    #     self.potion_queue.append(new_potion)

    def add_entangled(self, potion_types: List[PickupEnum], potion_ids: List[int]):
        e_id = self.get_entangled_id()
        possible_types = [pickup_name_mapper[p] for p in potion_types]
        logger.debug_success(f"Got potion. Possible types: {', '.join(possible_types)}")
        for p_id in potion_ids:
            self.potions[p_id] = Potion(potion_types, e_id)

    # def potion_used(self, potion_id: int, possible_types: List[PickupEnum]) -> List[PickupEnum]:
    #     potion = self.potions[potion_id]
    #     overlapping_types = []
    #     for p_type in potion.potion_types:
    #         if p_type in possible_types:
    #             overlapping_types.append(p_type)
    #     if not len(overlapping_types):
    #         raise ValueError(
    #             f"None of the types of this potion was deemed possible to have been used. "
    #             f"Recorded types: {', '.join(pickup_name_mapper(x) for x in potion.potion_types)}, "
    #             f"types deemed possible: {', '.join(pickup_name_mapper(x) for x in possible_types)}")
    #     self.unentangle(potion_id, potion, overlapping_types)
    #     del self.potions[potion_id]
    #     return overlapping_types

    # def unentangle(self, potion_id: int, potion: Potion, overlapping_types: List[PickupEnum]):
    #     if potion.entangled_id is None:
    #         return
    #     other_entangled_potions = {}
    #     for index, pot in self.potions.items():
    #         if index != potion_id and pot.entangled_id == potion.entangled_id:
    #             other_entangled_potions[index] = pot
    #     for index, pot in other_entangled_potions.items():
    #         if len(overlapping_types) == 1:
    #             pot.potion_types.remove(overlapping_types[0])
    #         if len(other_entangled_potions) == 1:
    #             pot.entangled_id = None
