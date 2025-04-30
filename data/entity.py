from typing import List, Dict, Optional

from constants import FACING, SPECIAL_MOVE_COOLDOWN, MAX_HP, HP, ICE, CURSE, SHIELD, ENTITY_STATE, HERO_ENUM, CELL, \
    POISON, ATTACK_QUEUE, ENEMY, PATTERN_INDEX, ELITE_TYPE, FIRST_TURN, ENEMY_TILE_EFFECT, TILE_TO_PLAY, \
    PREVIOUS_ACTION, ACTION
from data.mappers import hero_name_mapper, enemy_name_mapper, weapon_mapper, enemy_elite_name_mapper
from data.prediction_error import PredictionError
from data.weapon import Weapon
from enums import EntityType, WeaponEnum, EnemyEliteEnum, EnemyEnum, EnemyActionEnum, WeaponAttackEffectEnum


class EntityState:
    shield: bool
    curse: bool
    ice: int
    poison: int

    def __init__(self,
                 shield: bool,
                 curse: bool,
                 ice: int,
                 poison: int):
        self.shield = shield
        self.curse = curse
        self.ice = ice
        self.poison = poison

    def clone(self):
        return EntityState(
            shield=self.shield,
            curse=self.curse,
            ice=self.ice,
            poison=self.poison,
        )

    def is_equal(self, other, debug: str = None):
        if not debug:
            return self.shield == other.shield and \
                   self.curse == other.curse and \
                   self.ice == other.ice and \
                   self.poison == other.poison
        if self.shield != other.shield:
            raise PredictionError(f"wrong shield state ({debug})")
        if self.curse != other.curse:
            raise PredictionError(f"wrong curse state ({debug})")
        if self.ice != other.ice:
            raise PredictionError(f"wrong ice state ({debug})")
        if self.poison != other.poison:
            raise PredictionError(f"wrong poison state ({debug})")
        return True


class EntityHp:
    hp: int
    max_hp: int

    def __init__(self,
                 hp: int,
                 max_hp: int):
        self.hp = hp
        self.max_hp = max_hp

    def clone(self):
        return EntityHp(
            hp=self.hp,
            max_hp=self.max_hp
        )

    def is_equal(self, other, debug: str = None):
        if not debug:
            return self.hp == other.hp and \
                   self.max_hp == other.max_hp
        if self.hp != other.hp:
            raise PredictionError(f"wrong hp ({debug}) self: {self.hp} other: {other.hp}")
        if self.max_hp != other.max_hp:
            raise PredictionError(f"wrong max_hp ({debug})")
        return True


class EntityPosition:
    cell: int
    facing: int

    def __init__(self,
                 cell: int,
                 facing: int):
        self.cell = cell
        self.facing = facing

    def clone(self):
        return EntityPosition(
            cell=self.cell,
            facing=self.facing
        )

    def is_equal(self, other, debug: str = None):
        if not debug:
            return self.cell == other.cell and \
                   self.facing == other.facing
        if self.cell != other.cell:
            raise PredictionError(f"wrong cell ({debug}) self: {self.cell} other: {other.cell}")
        if self.facing != other.facing:
            raise PredictionError(f"wrong facing ({debug})")
        return True

    def flip(self):
        self.facing = 1 if self.facing == 0 else 0


class EnemyIntent:
    action: EnemyActionEnum
    previous_action: EnemyActionEnum
    tile_to_play: int
    attack_effect: int
    first_turn: bool
    elite_type: int
    pattern_index: int  # dictates which order of actions will be taken

    def __init__(self,
                 action: EnemyActionEnum,
                 previous_action: EnemyActionEnum,
                 tile_to_play: int,
                 attack_effect: int,
                 first_turn: bool,
                 elite_type: int,
                 pattern_index: int):
        self.action = action
        self.previous_action = previous_action
        self.tile_to_play = tile_to_play
        self.attack_effect = attack_effect
        self.first_turn = first_turn
        self.elite_type = elite_type
        self.pattern_index = pattern_index

    def clone(self):
        return EnemyIntent(
            action=self.action,
            previous_action=self.previous_action,
            tile_to_play=self.tile_to_play,
            attack_effect=self.attack_effect,
            first_turn=self.first_turn,
            elite_type=self.elite_type,
            pattern_index=self.pattern_index,
        )


class Entity:
    entity_type: EntityType
    entity_id: int
    state: EntityState
    position: EntityPosition
    hp: EntityHp
    enemy_intent: Optional[EnemyIntent]
    attack_queue: List[Weapon]
    special_move_cooldown: Optional[int]

    def __init__(self,
                 entity_type: EntityType,
                 entity_id: int,
                 state: EntityState,
                 position: EntityPosition,
                 hp: EntityHp,
                 attack_queue: List[Weapon],
                 enemy_intent: Optional[EnemyIntent] = None,
                 special_move_cooldown: Optional[int] = None):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.state = state
        self.position = position
        self.hp = hp
        self.enemy_intent = enemy_intent
        self.attack_queue = attack_queue
        self.special_move_cooldown = special_move_cooldown

    @staticmethod
    def from_dict(source: Dict, hero: bool = False):
        if hero:
            entity_type = EntityType.HERO
            entity_id = source.get(HERO_ENUM)
            attack_queue = [Weapon.from_dict(x) for x in source.get(ATTACK_QUEUE, [])]
            special_move_cooldown = source.get(SPECIAL_MOVE_COOLDOWN, 0)
            enemy_intent = None
        else:
            entity_type = EntityType.ENEMY
            entity_id = source.get(ENEMY)
            attack_queue = [Weapon.from_dict(x) for x in source.get(ATTACK_QUEUE, [])]
            special_move_cooldown = None

            action = EnemyActionEnum(source.get(ACTION))
            previous_action = EnemyActionEnum(source.get(PREVIOUS_ACTION))
            tile_to_play = source.get(TILE_TO_PLAY)
            attack_effect = source.get(ENEMY_TILE_EFFECT)
            first_turn = source.get(FIRST_TURN)
            elite_type = source.get(ELITE_TYPE)
            pattern_index = source.get(PATTERN_INDEX)
            enemy_intent = EnemyIntent(
                action=action,
                previous_action=previous_action,
                tile_to_play=tile_to_play,
                attack_effect=attack_effect,
                first_turn=first_turn,
                elite_type=elite_type,
                pattern_index=pattern_index,
            )

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

        return Entity(
            entity_type=entity_type,
            entity_id=entity_id,
            state=state,
            position=position,
            hp=hp,
            attack_queue=attack_queue,
            special_move_cooldown=special_move_cooldown,
            enemy_intent=enemy_intent
        )

    def clone(self):
        return Entity(
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            state=self.state.clone(),
            position=self.position.clone(),
            hp=self.hp.clone(),
            enemy_intent=None if self.enemy_intent is None else self.enemy_intent.clone(),
            attack_queue=[weapon.clone() for weapon in self.attack_queue],
            special_move_cooldown=self.special_move_cooldown,
        )

    def is_equal(self, other, debug: bool = False):
        name = self.get_name()
        self_none = self.special_move_cooldown is None
        other_none = other.special_move_cooldown is None
        if self_none != other_none:
            if debug:
                raise PredictionError(f"special move cooldown charge is None in one of the cases ({name})")
            return False
        if not self_none and self.special_move_cooldown > other.special_move_cooldown:
            if debug:
                raise PredictionError(f"special move cooldown charge ({self.special_move_cooldown}) "
                                      f"is lower than expected ({other.special_move_cooldown}) ({name})")
            return False

        if not debug:
            # predicted cooldown can be higher by one (no easy way to check the current max)
            return self.entity_type == other.entity_type and \
                   self.entity_id == other.entity_id and \
                   self.state.is_equal(other.state) and \
                   self.position.is_equal(other.position) and \
                   self.hp.is_equal(other.hp) and \
                   len(self.attack_queue) == len(other.attack_queue) and \
                   False not in [self.attack_queue[i].is_equal(other.attack_queue[i]) for i in
                                 range(len(self.attack_queue))]
        if self.entity_type != other.entity_type:
            raise PredictionError(f"wrong entity type ({name})")
        if self.entity_id != other.entity_id:
            raise PredictionError(f"wrong entity id ({name})")
        if len(self.attack_queue) != len(other.attack_queue):
            raise PredictionError(
                f"wrong attack queue length ({name}) self: {Weapon.pretty_print_list(self.attack_queue)} other: {Weapon.pretty_print_list(other.attack_queue)}")
        for i in range(len(self.attack_queue)):
            if not self.attack_queue[i].is_equal(other.attack_queue[i]):
                raise PredictionError(f"wrong weapon in attack queue in position {i} ({name})")
        return self.state.is_equal(other.state, debug=name) and \
               self.position.is_equal(other.position, debug=name) and \
               self.hp.is_equal(other.hp, debug=name)

    def is_good_prediction(self, other, debug: bool = False):
        # The only difference from is_equal is that we don't care about enemies' attack queues.
        name = self.get_name()
        self_none = self.special_move_cooldown is None
        other_none = other.special_move_cooldown is None
        if self_none != other_none:
            if debug:
                raise PredictionError(f"special move cooldown charge is None in one of the cases ({name})")
            return False
        if not self_none and self.special_move_cooldown < other.special_move_cooldown:
            if debug:
                raise PredictionError(f"special move cooldown charge is lower than expected ({name})")
            return False

        if not debug:
            return self.entity_type == other.entity_type and \
                   self.entity_id == other.entity_id and \
                   self.state.is_equal(other.state) and \
                   self.position.is_equal(other.position) and \
                   self.hp.is_equal(other.hp)
        if self.entity_type != other.entity_type:
            raise PredictionError(f"wrong entity type ({name})")
        if self.entity_id != other.entity_id:
            raise PredictionError(f"wrong entity id ({name})")
        return self.state.is_equal(other.state, debug=name) and \
               self.position.is_equal(other.position, debug=name) and \
               self.hp.is_equal(other.hp, debug=name)

    def get_name(self) -> str:
        if self.entity_type == EntityType.HERO:
            hero_name = f"{hero_name_mapper.get(self.entity_id, f'Unknown hero {self.entity_id}')}"
            return f"{hero_name}"
        e = self.enemy_intent
        enemy_elite = enemy_elite_name_mapper[EnemyEliteEnum(e.elite_type)]
        return f"{f'{enemy_elite} ' if len(enemy_elite) else ''}{enemy_name_mapper[EnemyEnum(self.entity_id)]}"

    def pretty_print(self) -> str:
        position = f"cell {self.position.cell}, facing {'right' if self.position.facing == 1 else 'left'}"
        if self.entity_type == EntityType.HERO:
            return f"{self.get_name()} {position}"
        enemy_name = self.get_name()
        e = self.enemy_intent
        intended_weapon = weapon_mapper[WeaponEnum(e.tile_to_play)]
        if e.action == EnemyActionEnum.WAIT:
            action = f"waiting"
        elif e.action == EnemyActionEnum.MOVE_LEFT:
            action = f"moving left"
        elif e.action == EnemyActionEnum.MOVE_RIGHT:
            action = f"moving right"
        elif e.action == EnemyActionEnum.EXECUTE_QUEUE:
            action = f"about to execute"
        elif e.action == EnemyActionEnum.EXPAND_QUEUE:
            action = f"about to add {intended_weapon} to attack queue"
        elif e.action == EnemyActionEnum.TURN_AROUND:
            action = f"turning around"
        elif e.action == EnemyActionEnum.TURN_AROUND_BOSS:
            action = f"turning around"
        else:
            action = f"performing unknown action {e.action}"
        first_turn = "(first turn)" if e.first_turn else ""
        weird_pattern = f"pattern: {e.pattern_index}" if e.pattern_index != 0 else ""
        action_alert = f"({e.action}({e.previous_action}))" if e.action != e.previous_action else ""
        if len(self.attack_queue):
            attack_queue = f"attack queue: {Weapon.short_print_list(self.attack_queue)}"
        else:
            attack_queue = "empty attack queue "
        retval = []
        for value in [enemy_name, position, action, action_alert, first_turn, weird_pattern, attack_queue]:
            if len(value):
                retval.append(value)
        return ", ".join(retval)

    def get_spaces_in_front(self, weapon_range: int = 1) -> List[int]:
        if self.position.facing == 1:
            return [self.position.cell + i + 1 for i in range(weapon_range)]
        return [self.position.cell - i - 1 for i in range(weapon_range)]

    def get_space_away_in_front(self, weapon_range: int) -> int:
        if self.position.facing == 1:
            return self.position.cell + weapon_range
        return self.position.cell - weapon_range

    def get_space_in_the_back(self) -> int:
        if self.position.facing == 1:
            return self.position.cell - 1
        return self.position.cell + 1

    def get_spaces_around(self, weapon_range=1) -> List[int]:
        targets = []
        for i in range(weapon_range):
            targets.append(self.position.cell + i + 1)
            targets.append(self.position.cell - i - 1)
        return targets

    def get_spaces_away_around(self, weapon_range: int) -> List[int]:
        return [self.position.cell + weapon_range, self.position.cell - weapon_range]

    def actual_hit(self, weapon: Weapon) -> int:
        strength = weapon.strength
        hits = self.entity_type == EntityType.HERO
        if strength > 0:
            if self.state.shield:
                self.state.shield = False
                hits = 0
            else:
                if self.state.curse:
                    strength *= 2
                    self.state.curse = False
                if weapon.weapon_type == WeaponEnum.SAI \
                        and self.enemy_intent is not None \
                        and self.enemy_intent.action == EnemyActionEnum.EXECUTE_QUEUE:
                    strength *= 2
                self.hp.hp -= strength
                if weapon.weapon_type == WeaponEnum.NAGIBOKU and self.hp.hp < 1:
                    self.hp.hp = 1
                # TODO: does nagiboku activate reactive shield when no damage dealt
                if self.enemy_intent is not None:
                    if self.enemy_intent.elite_type == EnemyEliteEnum.REACTIVE_SHIELD:
                        self.state.shield = True
        return hits

    def hit(self, weapon: Weapon) -> int:
        hits = self.actual_hit(weapon)
        if weapon.attack_effect is not None:
            if weapon.attack_effect == WeaponAttackEffectEnum.POISON:
                self.state.poison = 3
            elif weapon.attack_effect == WeaponAttackEffectEnum.ICE:
                self.state.ice = 3
            elif weapon.attack_effect == WeaponAttackEffectEnum.CURSE:
                self.state.curse = True
            elif weapon.attack_effect == WeaponAttackEffectEnum.DOUBLE_STRIKE:
                # Double strike needs to be handled a level higher.
                pass
            elif weapon.attack_effect == WeaponAttackEffectEnum.SHOCKWAVE:
                # Shockwave needs to be handled a level higher.
                pass
            else:
                raise ValueError(f"Unhandled weapon attack effect: {weapon.attack_effect.value}")
        return hits

    def is_hero(self):
        return self.entity_type == EntityType.HERO
