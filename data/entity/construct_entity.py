from typing import Dict

from constants import PATTERN_INDEX, ELITE_TYPE, FIRST_TURN, ENEMY_TILE_EFFECT, TILE_TO_PLAY, PREVIOUS_ACTION, ACTION, \
    ATTACK_QUEUE, ENEMY, SPECIAL_MOVE_COOLDOWN, HERO_ENUM, FACING, MAX_HP, HP, POISON, ICE, CURSE, SHIELD, ENTITY_STATE, \
    CELL
from data.entity.enemy import Enemy
from data.entity.entity_enums import EnemyActionEnum, HeroEnum, EnemyEnum, EnemyEliteEnum
from data.entity.entity_hp import EntityHp
from data.entity.entity_position import EntityPosition
from data.entity.entity_state import EntityState
from data.entity.hero import Hero
from data.weapon.weapon import Weapon
from data.weapon.weapon_enums import WeaponEnum, WeaponAttackEffectEnum


class EntityConstructor:
    @staticmethod
    def from_dict(source: Dict, hero: bool = False):
        entity_state = source.get(ENTITY_STATE, {})
        shield = entity_state.get(SHIELD, False)
        curse = entity_state.get(CURSE, False)
        ice = entity_state.get(ICE, 0)
        poison = entity_state.get(POISON, 0)
        _hp = entity_state.get(HP, 0)
        max_hp = entity_state.get(MAX_HP, 0)
        state = EntityState(shield=shield, curse=curse, ice=ice, poison=poison)
        hp = EntityHp(max_hp=max_hp, hp=_hp)

        facing = source.get(FACING, 0)
        cell = source.get(CELL, 0)
        position = EntityPosition(cell=cell, facing=facing)

        if hero:
            entity_id = source.get(HERO_ENUM)
            attack_queue = [Weapon.from_dict(x) for x in source.get(ATTACK_QUEUE, [])]
            special_move_cooldown = source.get(SPECIAL_MOVE_COOLDOWN, 0)

            return Hero(
                hero_id=HeroEnum(entity_id),
                state=state,
                position=position,
                hp=hp,
                attack_queue=attack_queue,
                special_move_cooldown=special_move_cooldown,
            )
        else:
            entity_id = source.get(ENEMY)
            attack_queue = [Weapon.from_dict(x) for x in source.get(ATTACK_QUEUE, [])]

            action = EnemyActionEnum(source.get(ACTION))
            previous_action = EnemyActionEnum(source.get(PREVIOUS_ACTION))
            tile_to_play = source.get(TILE_TO_PLAY)
            attack_effect = source.get(ENEMY_TILE_EFFECT)
            first_turn = source.get(FIRST_TURN)
            elite_type = EnemyEliteEnum(source.get(ELITE_TYPE))
            pattern_index = source.get(PATTERN_INDEX)

            return Enemy(
                enemy_id=EnemyEnum(entity_id),
                state=state,
                position=position,
                hp=hp,
                attack_queue=attack_queue,
                action=action,
                previous_action=previous_action,
                next_weapon=Weapon(
                    weapon_type=WeaponEnum(tile_to_play),
                    cooldown=0,
                    cooldown_charge=0,
                    strength=-1,
                    base_strength=-1,
                    level=0,
                    max_level=0,
                    attack_effect=WeaponAttackEffectEnum(attack_effect) if attack_effect != 0 else None,
                    tile_effect=None
                ),
                elite_type=elite_type,
                first_turn=first_turn,
                pattern_index=pattern_index
            )

    @staticmethod
    def thorns(cell):
        return Enemy(
            enemy_id=EnemyEnum.THORNS,
            state=EntityState.fresh(),
            position=EntityPosition(cell, 1),
            hp=EntityHp(hp=1, max_hp=1),
            action=EnemyActionEnum.WAIT,
            previous_action=EnemyActionEnum.WAIT,
            next_weapon=None,
            first_turn=True,
            elite_type=EnemyEliteEnum.NOT_ELITE,
            pattern_index=0,
            attack_queue=[],
        )

    @staticmethod
    def trap(cell):
        return Enemy(
            enemy_id=EnemyEnum.TRAP,
            state=EntityState.fresh(),
            position=EntityPosition(cell, 1),
            hp=EntityHp(hp=1, max_hp=1),
            action=EnemyActionEnum.WAIT,
            previous_action=EnemyActionEnum.WAIT,
            next_weapon=None,
            first_turn=True,
            elite_type=EnemyEliteEnum.NOT_ELITE,
            pattern_index=0,
            attack_queue=[],
        )
