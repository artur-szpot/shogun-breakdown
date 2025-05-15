from typing import List

from constants import SPECIAL_MOVE_COOLDOWN, ATTACK_QUEUE, FACING, MAX_HP, HP, POISON, ICE, CURSE, SHIELD, ENTITY_STATE, \
    HERO_ENUM, CELL, NAME
from data.entity.entity import Entity
from data.entity.entity_enums import EntityType, HeroEnum
from data.entity.entity_hp import EntityHp
from data.entity.entity_mappers import hero_name_mapper
from data.entity.entity_position import EntityPosition
from data.entity.entity_state import EntityState
from data.snapshot.prediction_error import PredictionError
from data.weapon.weapon import Weapon


class Hero(Entity):
    hero_id: HeroEnum
    special_move_cooldown: int
    has_reactive_shield: bool

    def __init__(self,
                 hero_id: HeroEnum,
                 state: EntityState,
                 position: EntityPosition,
                 hp: EntityHp,
                 attack_queue: List[Weapon],
                 special_move_cooldown: int,
                 has_reactive_shield: bool,
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
        self.has_reactive_shield = has_reactive_shield

    def clone(self):
        return Hero(
            hero_id=self.hero_id,
            state=self.state.clone(),
            position=self.position.clone(),
            hp=self.hp.clone(),
            attack_queue=[weapon.clone() for weapon in self.attack_queue],
            special_move_cooldown=self.special_move_cooldown,
            has_reactive_shield=self.has_reactive_shield,
        )

    def to_dict(self):
        return {
            HERO_ENUM: self.hero_id.value,
            NAME: hero_name_mapper[self.hero_id],
            ENTITY_STATE: {
                SHIELD: self.state.shield,
                CURSE: self.state.curse,
                ICE: self.state.ice,
                POISON: self.state.poison,
                HP: self.hp.hp,
                MAX_HP: self.hp.max_hp,
            },
            FACING: self.position.facing,
            CELL: self.position.cell,
            ATTACK_QUEUE: [weapon.to_dict() for weapon in self.attack_queue],
            SPECIAL_MOVE_COOLDOWN: self.special_move_cooldown,
        }

    def is_equal(self, other, debug: bool = False):
        if not debug:
            # predicted special cooldown can be higher by one (no easy way to check the current max)
            # TODO fix this - it CAN be predicted by hero + skills
            return self.entity_type == other.entity_type and \
                   self.hero_id == other.hero_id and \
                   self.state.is_equal(other.state) and \
                   self.position.is_equal(other.position) and \
                   self.hp.is_equal(other.hp) and \
                   Weapon.is_list_equal(self.attack_queue, other.attack_queue) and \
                   self.special_move_cooldown in [other.special_move_cooldown, other.special_move_cooldown - 1]

        name = hero_name_mapper.get(self.hero_id, f"Unknown hero #{self.hero_id.value}")
        if self.entity_type != other.entity_type:
            raise PredictionError(f"wrong entity type ({name})")
        if self.hero_id != other.hero_id:
            raise PredictionError(f"wrong hero id ({name})")
        if self.special_move_cooldown not in [other.special_move_cooldown, other.special_move_cooldown - 1]:
            raise PredictionError(
                f"wrong special move cooldown ({name}) self {self.special_move_cooldown} other {other.special_move_cooldown}")
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

    def is_reactive(self) -> bool:
        return self.has_reactive_shield
