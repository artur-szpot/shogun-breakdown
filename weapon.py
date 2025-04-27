from typing import Dict, Optional

from constants import WEAPON_TYPE, MAX_LEVEL, LEVEL, BASE_STRENGTH, STRENGTH, COOLDOWN_CHARGE, COOLDOWN, \
    WEAPON_TILE_EFFECT, WEAPON_ATTACK_EFFECT
from mappers import weapon_mapper, weapon_attack_effect_mapper, weapon_tile_effect_mapper
from enums import WeaponEnum, WeaponAttackEffectEnum, WeaponTileEffectEnum


class Weapon:
    weapon_type: WeaponEnum
    attack_effect: Optional[WeaponAttackEffectEnum]
    tile_effect: Optional[WeaponTileEffectEnum]
    cooldown: int
    cooldown_charge: int
    strength: int
    base_strength: int
    level: int
    max_level: int

    def __init__(self,
                 weapon_type: WeaponEnum,
                 cooldown: int,
                 cooldown_charge: int,
                 strength: int,
                 base_strength: int,
                 level: int,
                 max_level: int,
                 attack_effect: Optional[WeaponAttackEffectEnum],
                 tile_effect: Optional[WeaponTileEffectEnum]):
        self.weapon_type = weapon_type
        self.cooldown = cooldown
        self.cooldown_charge = cooldown_charge
        self.strength = strength
        self.base_strength = base_strength
        self.level = level
        self.max_level = max_level
        self.attack_effect = attack_effect
        self.tile_effect = tile_effect

    def pretty_print(self) -> str:
        name = weapon_mapper.get(self.weapon_type, f"Unkown weapon {self.weapon_type}")
        prefix = weapon_attack_effect_mapper.get(self.attack_effect,
                                                 weapon_tile_effect_mapper.get(self.tile_effect, ""))
        return prefix + (" " if prefix else "") + name + f" (power {self.strength}, cooldown {self.cooldown})"

    def debug_print(self) -> str:
        name = weapon_mapper.get(self.weapon_type, f"Unkown weapon {self.weapon_type}")
        prefix = weapon_attack_effect_mapper.get(self.attack_effect,
                                                 weapon_tile_effect_mapper.get(self.tile_effect, ""))
        return prefix + (" " if prefix else "") + name + f" (pwr {self.strength}({self.base_strength}), cd {self.cooldown_charge}/{self.cooldown}, lvl {self.level}/{self.max_level})"

    @staticmethod
    def pretty_print_list(weapon_list) -> str:
        return ", ".join(x.pretty_print() for x in weapon_list)

    @staticmethod
    def debug_print_list(weapon_list) -> str:
        return ", ".join(x.debug_print() for x in weapon_list)

    def is_equal(self, other) -> bool:
        return self.weapon_type == other.weapon_type and \
               self.cooldown == other.cooldown and \
               self.cooldown_charge == other.cooldown_charge and \
               self.strength == other.strength and \
               self.base_strength == other.base_strength and \
               self.level == other.level and \
               self.max_level == other.max_level and \
               self.attack_effect == other.attack_effect and \
               self.tile_effect == other.tile_effect

    @staticmethod
    def is_list_equal(first, other) -> bool:
        if len(first) != len(other):
            return False
        for i in range(len(first)):
            if not first[i].is_equal(other[i]):
                return False
        return True

    @staticmethod
    def is_list_reordered(first, other) -> bool:
        if len(first) != len(other):
            return False
        other_copy = other[:]
        for item in first:
            found = False
            for i in range(len(other_copy)):
                if not found and item.is_equal(other_copy[i]):
                    other_copy = other_copy[:i] + other_copy[i + 1:]
                    found = True
            if not found:
                return False
        return True

    @staticmethod
    def from_dict(value: Dict):
        _type = value[WEAPON_TYPE]
        weapon_type = WeaponEnum(_type)
        _attack_effect = value.get(WEAPON_ATTACK_EFFECT)
        attack_effect = WeaponAttackEffectEnum(_attack_effect) if _attack_effect else None
        _tile_effect = value.get(WEAPON_TILE_EFFECT)
        tile_effect = WeaponTileEffectEnum(_tile_effect) if _tile_effect else None
        # TODO: can it ever have both?
        cooldown = value[COOLDOWN]
        cooldown_charge = value[COOLDOWN_CHARGE]
        strength = value[STRENGTH]
        base_strength = value[BASE_STRENGTH]
        level = value[LEVEL]
        max_level = value[MAX_LEVEL]
        return Weapon(
            weapon_type=weapon_type,
            cooldown=cooldown,
            cooldown_charge=cooldown_charge,
            strength=strength,
            base_strength=base_strength,
            level=level,
            max_level=max_level,
            attack_effect=attack_effect,
            tile_effect=tile_effect,
        )
