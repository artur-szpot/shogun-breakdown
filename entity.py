from typing import List, Dict

from constants import FACING, SPECIAL_MOVE_COOLDOWN, MAX_HP, HP, ICE, CURSE, SHIELD, ENTITY_STATE, HERO_ENUM, CELL, \
    POISON, ATTACK_QUEUE
from enums import EntityType
from weapon import Weapon


class Entity:
    entity_type: EntityType
    cell: int
    facing: int
    hp: int
    max_hp: int
    shield: bool
    curse: bool
    ice: int
    poison: int
    attack_queue: List[Weapon]
    will_attack: bool
    special_move_cooldown: int

    def __init__(self,
                 entity_type: EntityType,
                 cell: int,
                 facing: int,
                 hp: int,
                 max_hp: int,
                 shield: bool,
                 curse: bool,
                 ice: int,
                 poison: int,
                 attack_queue: List[Weapon],
                 will_attack: bool,
                 special_move_cooldown: int):
        self.entity_type = entity_type
        self.cell = cell
        self.facing = facing
        self.hp = hp
        self.max_hp = max_hp
        self.shield = shield
        self.curse = curse
        self.ice = ice
        self.poison = poison
        self.attack_queue = attack_queue
        self.will_attack = will_attack
        self.special_move_cooldown = special_move_cooldown

    @staticmethod
    def from_dict(source: Dict, hero: bool = False):
        entity_type = source.get(HERO_ENUM) if hero else EntityType.ENEMY
        entity_state = source.get(ENTITY_STATE, {})
        shield = entity_state.get(SHIELD, False)
        curse = entity_state.get(CURSE, False)
        ice = entity_state.get(ICE, 0)
        poison = entity_state.get(POISON, 0)
        hp = entity_state.get(HP, 0)
        max_hp = entity_state.get(MAX_HP, 0)
        attack_queue = [Weapon.from_dict(x) for x in source.get(ATTACK_QUEUE, [])]
        will_attack = False  # TODO!
        special_move_cooldown = source.get(SPECIAL_MOVE_COOLDOWN, 0)
        facing = source.get(FACING, 0)
        cell = source.get(CELL, 0)
        return Entity(
            entity_type=entity_type,
            cell=cell,
            facing=facing,
            hp=hp,
            max_hp=max_hp,
            shield=shield,
            curse=curse,
            ice=ice,
            poison=poison,
            attack_queue=attack_queue,
            will_attack=will_attack,
            special_move_cooldown=special_move_cooldown,
        )
