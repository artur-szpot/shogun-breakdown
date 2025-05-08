from typing import Dict, Optional

from constants import WEAPON_TYPE, MAX_LEVEL, LEVEL, BASE_STRENGTH, STRENGTH, COOLDOWN_CHARGE, COOLDOWN, \
    WEAPON_TILE_EFFECT, WEAPON_ATTACK_EFFECT
from data.mappers import weapon_mapper, weapon_attack_effect_mapper
from data.snapshot.prediction_error import PredictionError
from data.weapon.weapon_enums import WeaponAttackEffectEnum, WeaponTileEffectEnum, WeaponEnum


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
                 attack_effect: Optional[WeaponAttackEffectEnum] = None,
                 tile_effect: Optional[WeaponTileEffectEnum] = None):
        self.weapon_type = weapon_type
        self.cooldown = cooldown
        self.cooldown_charge = cooldown_charge
        self.strength = strength
        self.base_strength = base_strength
        self.level = level
        self.max_level = max_level
        self.attack_effect = attack_effect
        self.tile_effect = tile_effect

    @staticmethod
    def signature_move():
        return Weapon(
            weapon_type=WeaponEnum.SIGNATURE_MOVE,
            cooldown=0,
            cooldown_charge=0,
            strength=1,
            base_strength=1,
            level=0,
            max_level=0,
        )

    @staticmethod
    def corrupted_explosion():
        return Weapon(
            weapon_type=WeaponEnum.CORRUPTED_EXPLOSION,
            cooldown=0,
            cooldown_charge=0,
            strength=1,
            base_strength=1,
            level=0,
            max_level=0,
        )

    @staticmethod
    def corrupted_wave(strength: int):
        return Weapon(
            weapon_type=WeaponEnum.CORRUPTED_WAVE,
            cooldown=0,
            cooldown_charge=0,
            strength=strength,
            base_strength=strength,
            level=0,
            max_level=0,
        )

    @staticmethod
    def trap(stength: int):
        return Weapon(
            weapon_type=WeaponEnum.TRAP,
            cooldown=0,
            cooldown_charge=0,
            strength=stength,
            base_strength=stength,
            level=0,
            max_level=0,
        )

    @staticmethod
    def shock():
        return Weapon(
            weapon_type=WeaponEnum.SHOCK,
            cooldown=0,
            cooldown_charge=0,
            strength=1,
            base_strength=1,
            level=0,
            max_level=0,
        )

    @staticmethod
    def poison_tick():
        return Weapon(
            weapon_type=WeaponEnum.POISON_TICK,
            cooldown=0,
            cooldown_charge=0,
            strength=1,
            base_strength=1,
            level=0,
            max_level=0,
        )

    @staticmethod
    def push():
        return Weapon(
            weapon_type=WeaponEnum.PUSH,
            cooldown=0,
            cooldown_charge=0,
            strength=0,
            base_strength=0,
            level=0,
            max_level=0,
        )

    @staticmethod
    def stop():
        return Weapon(
            weapon_type=WeaponEnum.STOP,
            cooldown=0,
            cooldown_charge=0,
            strength=1,
            base_strength=1,
            level=0,
            max_level=0,
        )

    @staticmethod
    def kunai():
        return Weapon(
            weapon_type=WeaponEnum.KUNAI,
            cooldown=0,
            cooldown_charge=0,
            strength=1,
            base_strength=1,
            level=0,
            max_level=0,
        )

    @staticmethod
    def explosion(strength: int):
        return Weapon(
            weapon_type=WeaponEnum.EXPLOSION,
            cooldown=0,
            cooldown_charge=0,
            strength=strength,
            base_strength=strength,
            level=0,
            max_level=0,
        )

    @staticmethod
    def any():
        return Weapon(
            weapon_type=WeaponEnum.ANY,
            cooldown=0,
            cooldown_charge=0,
            strength=1,
            base_strength=1,
            level=0,
            max_level=0,
        )

    def print_name(self) -> str:
        name = weapon_mapper.get(self.weapon_type, f"Unkown weapon {self.weapon_type}")
        prefix = ""
        if self.attack_effect is not None:
            prefix = weapon_attack_effect_mapper[self.attack_effect]
        if self.tile_effect is not None:
            if self.attack_effect is not None:
                raise ValueError("Both attack effect and tile effect set on a weapon shouldn't be possible")
        return prefix + (" " if prefix else "") + name

    def short_print(self) -> str:
        if self.strength == -1:
            return self.print_name() + f" ({self.cooldown})"
        return self.print_name() + f" ({self.strength},{self.cooldown})"

    def pretty_print(self) -> str:
        if self.strength == -1:
            return self.print_name() + f" (cooldown {self.cooldown})"
        return self.print_name() + f" (power {self.strength}, cooldown {self.cooldown})"

    def debug_print(self) -> str:
        if self.strength == -1:
            return self.print_name() + f"{self.cooldown_charge}/{self.cooldown}, " \
                                       f"{self.level}/{self.max_level})"
        return self.print_name() + f" ({self.strength}({self.base_strength}), " \
                                   f"{self.cooldown_charge}/{self.cooldown}, " \
                                   f"{self.level}/{self.max_level})"
        # return self.print_name() + f" (pwr {self.strength}({self.base_strength}), " \
        #                            f"cd {self.cooldown_charge}/{self.cooldown}, " \
        #                            f"lvl {self.level}/{self.max_level})"

    @staticmethod
    def short_print_list(weapon_list) -> str:
        return ", ".join(x.short_print() for x in weapon_list)

    @staticmethod
    def pretty_print_list(weapon_list) -> str:
        return ", ".join(x.pretty_print() for x in weapon_list)

    @staticmethod
    def debug_print_list(weapon_list) -> str:
        return ", ".join(x.debug_print() for x in weapon_list)

    def is_equal(self, other, debug=False) -> bool:
        if not debug:
            return self.weapon_type == other.weapon_type and \
                   self.cooldown == other.cooldown and \
                   self.cooldown_charge == other.cooldown_charge and \
                   self.strength == other.strength and \
                   self.base_strength == other.base_strength and \
                   self.level == other.level and \
                   self.max_level == other.max_level and \
                   self.attack_effect == other.attack_effect and \
                   self.tile_effect == other.tile_effect
        if self.weapon_type != other.weapon_type:
            raise PredictionError(f"Wrong weapon type")
        if self.cooldown != other.cooldown:
            raise PredictionError(f"Wrong cooldown")
        if self.cooldown_charge != other.cooldown_charge:
            raise PredictionError(f"Wrong cooldown charge self: {self.cooldown_charge} other: {other.cooldown_charge}")
        if self.strength != other.strength:
            raise PredictionError(f"Wrong strength")
        if self.base_strength != other.base_strength:
            raise PredictionError(f"Wrong base strength")
        if self.level != other.level:
            raise PredictionError(f"Wrong level")
        if self.max_level != other.max_level:
            raise PredictionError(f"Wrong max level")
        if self.attack_effect != other.attack_effect:
            raise PredictionError(f"Wrong attack effect")
        if self.tile_effect != other.tile_effect:
            raise PredictionError(f"Wrong tile effect")
        return True

    def is_same_tile(self, other) -> bool:
        return self.weapon_type == other.weapon_type and \
               self.cooldown == other.cooldown and \
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

    def clone(self):
        return Weapon(
            weapon_type=self.weapon_type,
            attack_effect=self.attack_effect,
            tile_effect=self.tile_effect,
            cooldown=self.cooldown,
            cooldown_charge=self.cooldown_charge,
            strength=self.strength,
            base_strength=self.base_strength,
            level=self.level,
            max_level=self.max_level)

    def use(self):
        self.cooldown_charge = 0

    def is_shocking(self):
        return self.attack_effect is not None and self.attack_effect == WeaponAttackEffectEnum.SHOCKWAVE

    def is_immediate(self):
        return self.tile_effect is not None and self.tile_effect == WeaponTileEffectEnum.IMMEDIATE

    def is_double_strike(self):
        return self.attack_effect is not None and self.attack_effect == WeaponAttackEffectEnum.DOUBLE_STRIKE
