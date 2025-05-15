from typing import List, Optional

from constants import PATTERN_INDEX, ELITE_TYPE, FIRST_TURN, ENEMY_TILE_EFFECT, TILE_TO_PLAY, PREVIOUS_ACTION, ACTION, \
    ATTACK_QUEUE, FACING, MAX_HP, HP, POISON, ICE, CURSE, SHIELD, ENTITY_STATE, ENEMY, CELL
from data.entity.entity import Entity
from data.entity.entity_enums import EnemyEnum, EnemyEliteEnum, EnemyActionEnum, EntityType
from data.entity.entity_hp import EntityHp
from data.entity.entity_mappers import enemy_name_mapper, enemy_elite_name_mapper
from data.entity.entity_position import EntityPosition
from data.entity.entity_state import EntityState
from data.mappers import weapon_mapper
from data.snapshot.prediction_error import PredictionError
from data.weapon.weapon import Weapon
from data.weapon.weapon_enums import WeaponAttackEffectEnum
from logger import logger


class Enemy(Entity):
    enemy_id: EnemyEnum
    action: EnemyActionEnum
    previous_action: EnemyActionEnum
    next_weapon: Optional[Weapon]
    elite_type: EnemyEliteEnum
    first_turn: bool  # Probably useless here
    pattern_index: int  # Probably useless here; dictates which order of actions will be taken

    def __init__(self,
                 enemy_id: EnemyEnum,
                 state: EntityState,
                 position: EntityPosition,
                 hp: EntityHp,
                 attack_queue: List[Weapon],
                 action: EnemyActionEnum,
                 previous_action: EnemyActionEnum,
                 next_weapon: Optional[Weapon],
                 elite_type: EnemyEliteEnum,
                 first_turn: bool,
                 pattern_index: int
                 ):
        super().__init__(
            entity_type=EntityType.ENEMY,
            state=state,
            position=position,
            hp=hp,
            attack_queue=attack_queue,
        )
        self.enemy_id = enemy_id
        self.action = action
        self.previous_action = previous_action
        self.next_weapon = next_weapon
        self.elite_type = elite_type
        self.first_turn = first_turn
        self.pattern_index = pattern_index

    def corrupted_progeny(self):
        return Enemy(
            enemy_id=EnemyEnum.CORRUPTED_PROGENY,
            state=EntityState.fresh(),
            position=self.position.clone_on_death(),
            hp=EntityHp(hp=1, max_hp=1),
            action=EnemyActionEnum.WAIT,
            previous_action=EnemyActionEnum.WAIT,
            next_weapon=Weapon.corrupted_explosion(),
            first_turn=True,
            elite_type=EnemyEliteEnum.NOT_ELITE,
            pattern_index=0,
            attack_queue=[],
        )

    @staticmethod
    def warden_postmortem():
        # Only exists to be the attacker in Warden's death explosion.
        return Enemy(
            enemy_id=EnemyEnum.WARDEN,
            state=EntityState.fresh(),
            position=EntityPosition(0, 0),
            hp=EntityHp(hp=1, max_hp=1),
            action=EnemyActionEnum.WAIT,
            previous_action=EnemyActionEnum.WAIT,
            next_weapon=None,
            first_turn=False,
            elite_type=EnemyEliteEnum.NOT_ELITE,
            pattern_index=0,
            attack_queue=[],
        )

    @staticmethod
    def thorns_postmortem():
        # Only exists to be the attacker in Thorns' retribution.
        return Enemy(
            enemy_id=EnemyEnum.THORNS,
            state=EntityState.fresh(),
            position=EntityPosition(0, 0),
            hp=EntityHp(hp=1, max_hp=1),
            action=EnemyActionEnum.WAIT,
            previous_action=EnemyActionEnum.WAIT,
            next_weapon=None,
            first_turn=False,
            elite_type=EnemyEliteEnum.NOT_ELITE,
            pattern_index=0,
            attack_queue=[],
        )

    def clone(self):
        return Enemy(
            enemy_id=self.enemy_id,
            state=self.state.clone(),
            position=self.position.clone(),
            hp=self.hp.clone(),
            action=self.action,
            previous_action=self.previous_action,
            next_weapon=self.next_weapon.clone() if self.next_weapon is not None else None,
            first_turn=self.first_turn,
            elite_type=self.elite_type,
            pattern_index=self.pattern_index,
            attack_queue=[weapon.clone() for weapon in self.attack_queue],
        )

    def to_dict(self):
        return {
            ENEMY: self.enemy_id.value,
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
            ACTION: self.action.value,
            PREVIOUS_ACTION: self.previous_action.value,
            TILE_TO_PLAY: self.next_weapon.weapon_type.value,
            ENEMY_TILE_EFFECT: 0 if self.next_weapon.tile_effect is None else self.next_weapon.tile_effect.value,
            FIRST_TURN: self.first_turn,
            ELITE_TYPE: self.elite_type.value,
            PATTERN_INDEX: self.pattern_index,
        }

    def is_equal(self, other, debug: bool = False):
        name = self.get_name()
        result = self.entity_type == other.entity_type and \
                 self.enemy_id == other.enemy_id and \
                 self.state.is_equal(other.state) and \
                 self.position.is_equal(other.position) and \
                 self.hp.is_equal(other.hp) and \
                 Weapon.is_list_equal(self.attack_queue, other.attack_queue) and \
                 self.action == other.action and \
                 self.previous_action == other.previous_action and \
                 self.elite_type == other.elite_type and \
                 self.first_turn == other.first_turn and \
                 self.pattern_index == other.pattern_index
        # self.next_weapon == other.next_weapon and \
        if not debug:
            return result
        if self.entity_type != other.entity_type:
            raise PredictionError(f"wrong entity type ({name})")
        if self.enemy_id != other.enemy_id:
            raise PredictionError(f"wrong enemy id ({name})")
        if len(self.attack_queue) != len(other.attack_queue):
            raise PredictionError(
                f"wrong attack queue length ({name}) self: {Weapon.pretty_print_list(self.attack_queue)} other: {Weapon.pretty_print_list(other.attack_queue)}")
        for i in range(len(self.attack_queue)):
            if not self.attack_queue[i].is_equal(other.attack_queue[i]):
                raise PredictionError(f"wrong weapon in attack queue in position {i} ({name})")
        other_checks = self.state.is_equal(other.state, debug=name) and \
                       self.position.is_equal(other.position, debug=name) and \
                       self.hp.is_equal(other.hp, debug=name)
        if other_checks and not result:
            raise PredictionError("Other inconsistency in enemy found")
        return result

    def is_good_prediction(self, other, debug: bool = False):
        name = self.get_name()
        facing_matters = not self.is_thorns()
        result = self.entity_type == other.entity_type and \
                 self.enemy_id == other.enemy_id and \
                 self.elite_type == other.elite_type and \
                 self.state.is_equal(other.state) and \
                 self.position.is_equal(other.position, facing_matters) and \
                 self.first_turn == other.first_turn and \
                 self.hp.is_equal(other.hp)
        # if not debug:
        #     return result
        if self.entity_type != other.entity_type:
            if debug:
                raise PredictionError(f"wrong entity type ({name})")
            else:
                logger.queue_debug_error(f"wrong entity type ({name})")
            return False
        if self.enemy_id != other.enemy_id:
            if debug:
                raise PredictionError(f"wrong enemy id ({name}) self {self.enemy_id} other{other.enemy_id}")
            else:
                logger.queue_debug_error(f"wrong enemy id ({name}) self {self.enemy_id} other{other.enemy_id}")
            return False
        if self.first_turn != other.first_turn:
            if debug:
                raise PredictionError(f"wrong first turn ({name}) self {self.first_turn} other{other.first_turn}")
            else:
                logger.queue_debug_error(f"wrong first turn ({name}) self {self.first_turn} other{other.first_turn}")
            return False
        if debug:
            other_checks = self.state.is_equal(other.state, debug=name) and \
                           self.position.is_equal(other.position, facing_matters, debug=name) and \
                           self.hp.is_equal(other.hp, debug=name)
        else:
            other_checks = self.state.is_equal(other.state, debug=None) and \
                           self.position.is_equal(other.position, debug=None) and \
                           self.hp.is_equal(other.hp, debug=None)
        if other_checks and not result:
            if debug:
                raise PredictionError("Other inconsistency in enemy found")
            else:
                logger.queue_debug_error("Other inconsistency in enemy found")
        return result

    def get_name(self) -> str:
        enemy_elite = enemy_elite_name_mapper[self.elite_type]
        hp = f"{self.hp.hp}/{self.hp.max_hp}"
        state = self.state.debug_print()
        return f"{enemy_elite + ' ' if len(enemy_elite) else ''}{enemy_name_mapper[self.enemy_id]} {hp} [{state}]"

    def short_print(self) -> str:
        position = f"cell {self.position.cell}"  # , facing {'right' if self.position.facing == 1 else 'left'}"
        return f"{self.get_name()} {position}"

    def pretty_print(self) -> str:
        position = f"cell {self.position.cell}, facing {'right' if self.position.facing == 1 else 'left'}"
        if self.action == EnemyActionEnum.WAIT:
            action = f"waiting"
        elif self.action == EnemyActionEnum.MOVE_LEFT:
            action = f"moving left"
        elif self.action == EnemyActionEnum.MOVE_RIGHT:
            action = f"moving right"
        elif self.action == EnemyActionEnum.EXECUTE_QUEUE:
            action = f"about to execute"
        elif self.action == EnemyActionEnum.EXPAND_QUEUE:
            intended_weapon = weapon_mapper[self.next_weapon.weapon_type]
            action = f"about to add {intended_weapon} to attack queue"
        elif self.action == EnemyActionEnum.TURN_AROUND:
            action = f"turning around"
        elif self.action == EnemyActionEnum.TURN_AROUND_BOSS:
            action = f"turning around"
        else:
            action = f"performing unknown action {self.action}"
        first_turn = "(first turn)" if self.first_turn else ""
        weird_pattern = f"pattern: {self.pattern_index}" if self.pattern_index != 0 else ""
        action_alert = f"({self.action}({self.previous_action}))" if self.action != self.previous_action else ""
        if len(self.attack_queue):
            attack_queue = f"attack queue: {Weapon.short_print_list(self.attack_queue)}"
        else:
            attack_queue = "empty attack queue "
        retval = []
        for value in [self.get_name(), position, action, action_alert, first_turn, weird_pattern, attack_queue]:
            if len(value):
                retval.append(value)
        return ", ".join(retval)

    def will_attack(self) -> bool:
        return self.action == EnemyActionEnum.EXECUTE_QUEUE

    def is_heavy(self):
        return self.elite_type == EnemyEliteEnum.HEAVY

    def is_corrupted(self):
        return self.elite_type == EnemyEliteEnum.CORRUPTED

    def is_reactive(self):
        return self.elite_type == EnemyEliteEnum.REACTIVE_SHIELD

    def is_thorns(self) -> bool:
        return self.enemy_id == EnemyEnum.THORNS

    def is_boss(self):
        return self.enemy_id in [
            EnemyEnum.REI,
            EnemyEnum.DAISUKE,
            EnemyEnum.IWAO,
            EnemyEnum.BARU,
            EnemyEnum.THE_TWINS_A,
            EnemyEnum.THE_TWINS_B,
            EnemyEnum.THE_STATUE,
            EnemyEnum.KOWA,
            EnemyEnum.FUMIKO,
            EnemyEnum.SATO,
            EnemyEnum.HIDEYOSHI,
            EnemyEnum.NOBUNAGA,
            EnemyEnum.IEIASU,
            EnemyEnum.THE_SHOGUN,
            EnemyEnum.THE_SHOGUN_PHASE_TWO,
        ]

    def hit_clone(self, weapon: Weapon, twin_target) -> int:
        if self.enemy_id != EnemyEnum.THE_TWINS_B:
            return 0
        if twin_target is None:
            # happens when Twin B has already died
            return 0
        weapon_clone = weapon.clone()
        if weapon.attack_effect is None:
            pass
        elif weapon.attack_effect == WeaponAttackEffectEnum.POISON:
            pass
        else:
            weapon_clone.attack_effect = None
        return twin_target.hit(weapon_clone, None)
