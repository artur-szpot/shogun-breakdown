from typing import List

from data.entity.entity_enums import EntityType
from data.entity.entity_hp import EntityHp
from data.entity.entity_position import EntityPosition
from data.entity.entity_state import EntityState
from data.weapon.weapon import Weapon
from data.weapon.weapon_enums import WeaponEnum, WeaponAttackEffectEnum
from logger import logger


class Entity:
    entity_type: EntityType
    state: EntityState
    position: EntityPosition
    hp: EntityHp
    attack_queue: List[Weapon]

    def __init__(self,
                 entity_type: EntityType,
                 state: EntityState,
                 position: EntityPosition,
                 hp: EntityHp,
                 attack_queue: List[Weapon]
                 ):
        self.entity_type = entity_type
        self.state = state
        self.position = position
        self.hp = hp
        self.attack_queue = attack_queue

    def clone(self):
        raise TypeError("Cloning not allowed on the base class")

    def is_equal(self, other, debug: bool = False):
        raise TypeError("Compoaring not allowed on the base class")

    def is_good_prediction(self, other, debug: bool = False):
        raise TypeError("Compoaring not allowed on the base class")

    def get_name(self) -> str:
        return "Unimplemented base Entity class"

    def short_print(self) -> str:
        return ""

    def pretty_print(self) -> str:
        return ""

    def is_hero(self) -> bool:
        return self.entity_type == EntityType.HERO

    def is_heavy(self) -> bool:
        return False

    def is_corrupted(self) -> bool:
        return False

    def is_reactive(self) -> bool:
        return False

    def will_attack(self) -> bool:
        return False

    def is_boss(self) -> bool:
        return False

    def actual_hit(self, weapon: Weapon) -> int:
        logger.queue_debug_text(f"{self.get_name()} getting hit with {weapon.pretty_print()}")
        strength = weapon.strength
        hits = 1 if self.is_hero() else 0
        if self.state.shield:
            if strength > 0:
                self.state.shield = False
            hits = 0
        else:
            if self.state.curse:
                strength *= 2
                self.state.curse = False
            if weapon.weapon_type == WeaponEnum.SAI and self.will_attack():
                strength *= 2
            self.hp.hp -= strength
            if weapon.weapon_type == WeaponEnum.NAGIBOKU and self.hp.hp < 1:
                self.hp.hp = 1
            # TODO: does nagiboku activate reactive shield when no damage dealt
            if strength > 0 and self.is_reactive():
                logger.queue_debug_text("reactive shield turned on")
                self.state.shield = True
        if self.hp.hp <= 0:
            self.position.died_in = self.position.cell
        return hits

    def hit(self, weapon: Weapon, twin_target) -> int:
        hits = self.actual_hit(weapon)
        if weapon.attack_effect is not None:
            if weapon.attack_effect == WeaponAttackEffectEnum.POISON:
                self.state.poison = 3
            elif weapon.attack_effect == WeaponAttackEffectEnum.ICE:
                self.state.ice = 4
            elif weapon.attack_effect == WeaponAttackEffectEnum.CURSE:
                self.state.curse = True
            elif weapon.attack_effect == WeaponAttackEffectEnum.DOUBLE_STRIKE:
                # Double strike handled elsewhere.
                pass
            elif weapon.attack_effect == WeaponAttackEffectEnum.SHOCKWAVE:
                # Shockwave handled elsewhere.
                pass
            elif weapon.attack_effect == WeaponAttackEffectEnum.PERFECT_STRIKE:
                # TODO WHAT DO?!?!
                pass
            else:
                raise ValueError(f"Unhandled weapon attack effect: {weapon.attack_effect.value}")

        hits2 = self.hit_clone(weapon, twin_target)
        hits += hits2
        return hits

    def hit_clone(self, weapon: Weapon, twin_target) -> int:
        return 0
