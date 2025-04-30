from typing import Dict, List, Optional

from data.mappers import pickup_name_mapper
from data.snapshot import Snapshot
from enums import PickupEnum


class Potion:
    potion_types: List[PickupEnum]
    entangled_id: Optional[int]

    def __init__(self, possible_types: List[PickupEnum], entangled_id: Optional[int] = None):
        self.potion_types = possible_types
        self.entangled_id = entangled_id


class PotionHistory:
    potions: Dict[int, Potion]
    last_e_id: int

    def __init__(self, first_snapshot: Snapshot):
        potion_ids = first_snapshot.hero_potion_ids
        all_types = [
            PickupEnum.EDAMAME_BREW,
            PickupEnum.COOL_UP,
            PickupEnum.KAMI_BREW,
            PickupEnum.MASS_CURSE,
            PickupEnum.MASS_ICE,
            PickupEnum.MASS_POISON,
            PickupEnum.RAIN_OF_MIRRORS,
        ]
        self.potions = {p_id: Potion(possible_types=all_types, entangled_id=0) for p_id in potion_ids}
        self.last_e_id = 0

    def get_entangled_id(self):
        self.last_e_id += 1
        return self.last_e_id

    def add_certain(self, potion_type: PickupEnum, potion_id: int):
        self.potions[potion_id] = Potion([potion_type])

    def add_entangled(self, potion_types: List[PickupEnum], potion_ids: List[int]):
        e_id = self.get_entangled_id()
        for p_id in potion_ids:
            self.potions[p_id] = Potion(potion_types, e_id)

    def potion_used(self, potion_id: int, possible_types: List[PickupEnum]) -> List[PickupEnum]:
        potion = self.potions[potion_id]
        overlapping_types = []
        for p_type in potion.potion_types:
            if p_type in possible_types:
                overlapping_types.append(p_type)
        if not len(overlapping_types):
            raise ValueError(
                f"None of the types of this potion was deemed possible to have been used. "
                f"Recorded types: {', '.join(pickup_name_mapper(x) for x in potion.potion_types)}, "
                f"types deemed possible: {', '.join(pickup_name_mapper(x) for x in possible_types)}")
        self.unentangle(potion_id, potion, overlapping_types)
        del self.potions[potion_id]
        return overlapping_types

    def unentangle(self, potion_id: int, potion: Potion, overlapping_types: List[PickupEnum]):
        if potion.entangled_id is None:
            return
        other_entangled_potions = {}
        for index, pot in self.potions.items():
            if index != potion_id and pot.entangled_id == potion.entangled_id:
                other_entangled_potions[index] = pot
        for index, pot in other_entangled_potions.items():
            if len(overlapping_types) == 1:
                pot.potion_types.remove(overlapping_types[0])
            if len(other_entangled_potions) == 1:
                pot.entangled_id = None
