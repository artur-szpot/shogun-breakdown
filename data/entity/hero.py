from typing import List

from data.entity.entity import Entity
from data.entity.entity_enums import EntityType, HeroEnum
from data.entity.entity_hp import EntityHp
from data.entity.entity_mappers import hero_name_mapper
from data.entity.entity_position import EntityPosition
from data.entity.entity_state import EntityState
from data.snapshot.prediction_error import PredictionError
from data.weapon.weapon import Weapon
from logger import logger


class Hero(Entity):
    hero_id: HeroEnum
    special_move_cooldown: int

    def __init__(self,
                 hero_id: HeroEnum,
                 state: EntityState,
                 position: EntityPosition,
                 hp: EntityHp,
                 attack_queue: List[Weapon],
                 special_move_cooldown: int
                 ):
        super().__init__(
            entity_type=EntityType.HERO,
            state=state,
            position=position,
            hp=hp,
            attack_queue=attack_queue,
        )
        self.hero_id = hero_id
        self.special_move_cooldown = special_move_cooldown

    def clone(self):
        return Hero(
            hero_id=self.hero_id,
            state=self.state.clone(),
            position=self.position.clone(),
            hp=self.hp.clone(),
            attack_queue=[weapon.clone() for weapon in self.attack_queue],
            special_move_cooldown=self.special_move_cooldown,
        )

    def is_equal(self, other, debug: bool = False):
        if not debug:
            # predicted cooldown can be higher by one (no easy way to check the current max)
            return self.entity_type == other.entity_type and \
                   self.hero_id == other.hero_id and \
                   self.state.is_equal(other.state) and \
                   self.position.is_equal(other.position) and \
                   self.hp.is_equal(other.hp) and \
                   Weapon.is_list_equal(self.attack_queue, other.attack_queue) and \
                   self.special_move_cooldown == other.special_move_cooldown

        name = hero_name_mapper.get(self.hero_id, f"Unknown hero #{self.hero_id.value}")
        if self.entity_type != other.entity_type:
            raise PredictionError(f"wrong entity type ({name})")
        if self.hero_id != other.hero_id:
            raise PredictionError(f"wrong hero id ({name})")
        if len(self.attack_queue) != len(other.attack_queue):
            raise PredictionError(
                f"wrong attack queue length ({name}) self: {Weapon.pretty_print_list(self.attack_queue)} other: {Weapon.pretty_print_list(other.attack_queue)}")
        for i in range(len(self.attack_queue)):
            if not self.attack_queue[i].is_equal(other.attack_queue[i]):
                raise PredictionError(f"wrong weapon in attack queue in position {i} ({name})")
        return self.state.is_equal(other.state, debug=name) and \
               self.position.is_equal(other.position, debug=name) and \
               self.hp.is_equal(other.hp, debug=name)

    def get_name(self) -> str:
        hero_name = f"{hero_name_mapper.get(self.hero_id, f'Unknown hero {self.hero_id.value}')}"
        return f"{hero_name}"

    def short_print(self) -> str:
        return self.get_name()

    def pretty_print(self) -> str:
        position = f"cell {self.position.cell}, facing {'right' if self.position.facing == 1 else 'left'}"
        return f"{self.get_name()} {position}"
