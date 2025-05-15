from typing import List, Dict, Optional, Tuple

from constants import CURRENT_LOCATION, MAP_SAVE, COMBAT_ROOM, \
    PROGRESSION, PROGRESSION_DATA, ENEMIES, PICKUP_LOCATIONS, PICKUPS, UNTIL_NEXT_WAVE, WAVE_NUMBER, HERO, ROOM_VARIANT, \
    CORRUPTED_BOSS_SECTORS
from data.entity.construct_entity import EntityConstructor
from data.entity.enemy import Enemy
from data.entity.entity import Entity
from data.entity.entity_enums import EnemyEnum
from data.entity.entity_mappers import enemy_name_mapper
from data.entity.hero import Hero
from data.mappers import room_number_mapper, boss_room_mapper, room_name_mapper
from data.room.room_enums import PickupEnum, RoomEnum
from data.skill.skills import Skills
from data.snapshot.hit_data import HitData
from data.snapshot.prediction_error import PredictionError
from data.weapon.weapon import Weapon
from data.weapon.weapon_enums import WeaponEnum
from logger import logger


def get_board_size(room: RoomEnum, progression: int, variant: int) -> int:
    # Reward room or shop; board size unimportant.
    if progression // 2 != (progression + 1) // 2 or variant == -1:
        return -1
    retval = {
        RoomEnum.BAMBOO_GROVE: {
            0: {0: 5},
            2: {0: 7},
            4: {
                0: 5,
                1: 7,
            }
        },
        RoomEnum.BAMBOO_GROVE.WHISPERING_CAVES: {
            0: {0: 5},
            2: {0: 7},
            4: {0: 7}
        },
        RoomEnum.HIBIKU_WASTELANDS: {
            0: {0: 7},
            2: {0: 5},
            4: {0: 7},
        },
        RoomEnum.MOONLIT_PORT: {
            0: {0: 7},
            2: {0: 5},
            4: {0: 9},
            6: {0: 7},
            8: {0: -2},  # the shop
        },
        RoomEnum.SPIRIT_GATEWAY: {
            0: {0: 7},
            2: {0: 7},
            4: {0: 9},
            6: {0: 7},
        },
        RoomEnum.FORSAKEN_GROUNDS: {
            0: {0: 7},
            2: {0: 9},
            4: {0: 7},
            6: {0: 7},
        },
        RoomEnum.HOT_SPRINGS: {
            0: {0: 7},
            2: {0: 5},
            4: {0: 9},
            6: {0: 7},
        },
        RoomEnum.THEATRE_OF_ILLUSIONS: {
            0: {0: 7},
            2: {0: 5},
            4: {0: 9},
            # 6: various, doesn't exist in save data anyway :|
        },
        RoomEnum.HIDEYOSHI: {
            0: {0: 7},
            2: {0: 7},
        },
        RoomEnum.NOBUNAGA: {
            0: {0: 7},
            2: {0: 7},
        },
        RoomEnum.IEIASU: {
            0: {0: 7},
            2: {0: 9},
        },
        RoomEnum.SHOGUN: {
            0: {0: 9},
            2: {0: 7},
        },
    }.get(room, {}).get(progression, {}).get(variant, -1)
    if retval == -1:
        logger.debug_error(f"ROOM {room} PROGRESSION {progression} VARIANT: {variant} MISSING!")
    return retval


class BattleRoom:
    room: RoomEnum
    progression: int
    hero: Hero
    enemies: List[Enemy]
    pickups: Dict[int, Dict[PickupEnum, int]]
    wave_number: int
    until_next_wave: int
    board_size: int
    variant: int
    is_boss_corrupted: bool

    def __init__(self,
                 room: RoomEnum,
                 progression: int,
                 hero: Hero,
                 enemies: List[Enemy],
                 pickups: Dict[int, Dict[PickupEnum, int]],
                 wave_number: int,
                 until_next_wave: int,
                 variant: int,
                 is_boss_corrupted: bool,
                 ):
        self.room = room
        self.progression = progression
        self.hero = hero
        self.enemies = enemies
        self.pickups = pickups
        self.wave_number = wave_number
        self.until_next_wave = until_next_wave
        self.variant = variant
        self.is_boss_corrupted = is_boss_corrupted
        self.board_size = get_board_size(room, progression, variant)

    @staticmethod
    def from_dict(source: Dict, skills: Skills):
        room_raw = source[MAP_SAVE][CURRENT_LOCATION]
        progression = source[PROGRESSION_DATA][PROGRESSION]
        room = None
        try:
            room = RoomEnum(room_raw)
        except ValueError:
            pass
        if room is not None:
            variant = source[PROGRESSION_DATA][ROOM_VARIANT]
            is_boss_corrupted = room_number_mapper[room] in source[PROGRESSION_DATA][CORRUPTED_BOSS_SECTORS]
        else:
            variant = -1
            is_boss_corrupted = False
        enemies = [EntityConstructor.from_dict(x) for x in source.get(COMBAT_ROOM, {}).get(ENEMIES, [])]
        pickups_raw = source.get(PICKUPS, [])
        pickup_locations = source.get(PICKUP_LOCATIONS, [])
        if len(pickups_raw) != len(pickup_locations):
            raise ValueError("Number of pickups must be the same as the number of their locations")
        pickups = {}
        gold = {}
        for i in range(len(pickups_raw)):
            pickup_type = PickupEnum(pickups_raw[i])
            loc = pickup_locations[i]
            if pickup_type == PickupEnum.GOLD:
                if loc in gold:
                    gold[loc] += 1
                else:
                    gold[loc] = 1
            else:
                if loc not in pickups:
                    pickups[loc] = {}
                if pickup_type in pickups[loc]:
                    pickups[loc][pickup_type] += 1
                else:
                    pickups[loc][pickup_type] = 1
        for loc, total in gold.items():
            if loc not in pickups:
                pickups[loc] = {}
            pickups[loc][PickupEnum.GOLD] = total
        return BattleRoom(
            room=room,
            progression=progression,
            hero=EntityConstructor.from_dict(source.get(HERO, {}), hero=True, skills=skills),
            enemies=enemies,
            pickups=pickups,
            wave_number=source.get(COMBAT_ROOM, {}).get(WAVE_NUMBER, -1),
            until_next_wave=source.get(COMBAT_ROOM, {}).get(UNTIL_NEXT_WAVE, -1),
            variant=variant,
            is_boss_corrupted=is_boss_corrupted,
        )

    def to_dict(self):
        return {
            ENEMIES: [enemy.to_dict() for enemy in self.enemies],
            WAVE_NUMBER: self.wave_number,
            UNTIL_NEXT_WAVE: self.until_next_wave,
        }

    def to_dict_progression_data(self, corrupted_boss_sectors):
        return {
            PROGRESSION: self.progression,
            ROOM_VARIANT: self.variant,
            CORRUPTED_BOSS_SECTORS: corrupted_boss_sectors,
        }

    def to_dict_pickups(self):
        retval = []
        for cell, pickup in self.pickups.items():
            for pickup_type, total in pickup.items():
                for i in range(total):
                    retval.append(pickup_type.value)
        return retval

    def to_dict_pickup_cells(self):
        retval = []
        for cell, pickup in self.pickups.items():
            for pickup_type, total in pickup.items():
                for i in range(total):
                    retval.append(cell)
        return retval

    def clone(self):
        pickups = {loc: {} for loc in self.pickups.keys()}
        for loc in pickups:
            for pickup_type, total in self.pickups[loc].items():
                pickups[loc][pickup_type] = total
        return BattleRoom(
            room=self.room,
            progression=self.progression,
            hero=self.hero.clone(),  # reconstructed
            enemies=[enemy.clone() for enemy in self.enemies],
            pickups=pickups,
            wave_number=self.wave_number,
            until_next_wave=self.until_next_wave,
            variant=self.variant,
            is_boss_corrupted=self.is_boss_corrupted,
        )

    def is_equal(self, other):
        if len(self.pickups) != len(other.pickups):
            return False
        for loc, pps in self.pickups:
            if loc not in other.pickups:
                return False
            if len(pps) != len(other.pickups[loc]):
                return False
            for p_type, total in pps.items():
                if p_type not in other.pickups[loc]:
                    return False
                if total != other.pickups[loc][p_type]:
                    return False

        return self.room == other.room \
               and self.progression == other.progression \
               and self.hero.is_equal(other.hero) \
               and len(self.enemies) == len(other.enemies) \
               and False not in [self.enemies[i].is_equal(other.enemies[i]) for i in
                                 range(len(self.enemies))] \
               and self.wave_number == other.wave_number \
               and self.until_next_wave == other.until_next_wave

    def is_good_prediction(self, other, summons: int, debug: bool = False):
        if self.wave_number == other.wave_number:
            if len(self.enemies) != len(other.enemies) + summons:
                if debug:
                    raise PredictionError(
                        f"wrong number of enemies in same wave self {len(self.enemies)} other {len(other.enemies)}")
                return False
            other_enemies = [other_enemy.clone() for other_enemy in other.enemies]
            unaccounted_for_enemies = 0
            for enemy in self.enemies:
                found = False
                for index, other_enemy in enumerate(other_enemies):
                    if not found and enemy.is_good_prediction(other_enemy, debug=False):
                        logger.queue_debug_warn(f"Compare against {other_enemies[index].pretty_print()}")
                        del other_enemies[index]
                        found = True
                if not found:
                    logger.queue_debug_warn(f"Could not find {enemy.pretty_print()}")
                    unaccounted_for_enemies += 1
            if unaccounted_for_enemies != summons:
                if debug:
                    raise PredictionError(
                        f"wrong number of enemies in same wave is {unaccounted_for_enemies} expected {summons}")
                return False
        else:
            enemies_ok = len(self.enemies) > len(other.enemies)
            if not enemies_ok:
                if debug:
                    raise PredictionError(
                        f"wrong number of enemies in new wave self {len(self.enemies)} other {len(other.enemies)}")
                return False
            for enemy in self.enemies:
                predicted = True in [e.is_good_prediction(enemy, debug=False) for e in other.enemies]
                newly_spawned = not predicted and enemy.hp.hp == enemy.hp.max_hp
                if not predicted and not newly_spawned:
                    if debug:
                        raise PredictionError(f"wrong enemies in new wave")
                    return False

        # NO LONGER RELEVANT - potions handled elsewhere; gold can be handled otherwise
        # # If pickup is predicted, it needs to be there.
        # for loc, pps in other.pickups.items():
        #     if loc not in self.pickups:
        #         if len(pps) > 1 or PickupEnum.ANY not in pps:
        #             if debug:
        #                 raise PredictionError(f"missing predicted pickup location")
        #             return False
        #     loc_has_any = PickupEnum.ANY in pps
        #     for p_type, total in pps.items():
        #         if p_type != PickupEnum.ANY:
        #             if p_type not in self.pickups[loc]:
        #                 if debug:
        #                     raise PredictionError(f"missing predicted pickup type")
        #                 return False
        #             if self.pickups[loc][p_type] > total and not loc_has_any:
        #                 if debug:
        #                     raise PredictionError(
        #                         f"wrong predicted pickup total loc {loc} type {p_type} self {self.pickups[loc][p_type]} other {total}")
        #                 return False
        #
        # # If pickup is there, it needs to be predicted.
        # self_pickups = [f'{loc}: {", ".join(pickup_name_mapper[pp] for pp in pps)}' for loc, pps in
        #                 self.pickups.items()]
        # other_pickups = [f'{loc}: {", ".join(pickup_name_mapper[pp] for pp in pps)}' for loc, pps in
        #                  other.pickups.items()]
        # pickup_debug = f"SELF: {', '.join(self_pickups)}, OTHER: {', '.join(other_pickups)}"
        # for loc, pps in self.pickups.items():
        #     if loc not in other.pickups:
        #         if debug:
        #             raise PredictionError(f"unpredicted pickup location {pickup_debug}")
        #         return False
        #     for p_type, total in pps.items():
        #         if PickupEnum.ANY not in other.pickups[loc]:
        #             if p_type not in other.pickups[loc]:
        #                 if debug:
        #                     raise PredictionError(f"unpredicted pickup type {p_type.value} {pickup_debug}")
        #                 return False
        #             if other.pickups[loc][p_type] != total:
        #                 if debug:
        #                     raise PredictionError(
        #                         f"unpredicted pickup total loc: {loc} type: {p_type.value} total: {total} {pickup_debug}")
        #                 return False

        return self.room == other.room and \
               self.progression == other.progression and \
               self.hero.is_equal(other.hero, debug)

    def is_boss_room(self) -> bool:
        return boss_room_mapper.get(self.room, {}).get(self.progression, False)

    def get_the_boss(self) -> Optional[Enemy]:
        if not self.is_boss_room():
            return None
        for enemy in self.enemies:
            if enemy.is_boss():
                return enemy
        raise ValueError("Could not find the boss in a boss room")

    def get_name(self, reward: bool = False, splits: bool = False) -> str:
        room_name = room_name_mapper.get(self.room)
        if room_name is None:
            raise ValueError(f"Unknown room name: {self.room}")
        if not splits:
            room_name = f"{room_name}[{self.board_size}]"

        if self.is_boss_room():
            boss_id = self.get_the_boss().enemy_id.value
            if self.is_boss_corrupted:
                # boss_name = room_corrupted_boss_mapper.get(self.room)
                boss_id *= 100
                boss_enum = EnemyEnum(boss_id)
                boss_name = enemy_name_mapper.get(boss_enum, f"Unknown boss: {boss_id}")
            else:
                # boss_name = room_boss_mapper.get(self.room)
                boss_enum = EnemyEnum(boss_id)
                boss_name = enemy_name_mapper.get(boss_enum, f"Unknown corrupted boss: {boss_id}")
            if boss_name is None:
                raise ValueError(f"Unknown boss name: {self.room}")
            if reward:
                return f"{room_name}, boss battle ({boss_name}) rewards"
            if splits:
                return f"{room_name}, boss battle"
            return f"{room_name}, boss battle ({boss_name})"

        if reward:
            return f"{room_name}, battle #{(self.progression + 1) // 2} rewards"
        return f"{room_name}, battle #{(self.progression // 2) + 1}"

    def pretty_print_pickups(self) -> str:
        retval = []
        for loc, pps in self.pickups.items():
            pps_str = []
            for pp, total in pps.items():
                pps_str.append(f"{pp.value}({total})")
            retval.append(f"{loc}: {', '.join(pps_str)}")
        return ", ".join(retval)

    def get_push_target_in_direction(self, entity: Entity, direction: int, push_range=10) -> Tuple[
        int, Optional[Entity]]:
        current_cell = entity.position.cell
        logger.queue_debug_text(f"entity {entity.short_print()} getting pushed in direction {direction}")
        for i in range(push_range):
            if not self.is_legal_position(current_cell + direction):
                return current_cell, None
            current_cell += direction
            collisions = self.find_targets([current_cell])
            if len(collisions):
                logger.queue_debug_text(f"Collided with {collisions[0].pretty_print()}")
                return current_cell - direction, collisions[0]
            if not self.is_legal_position(current_cell):
                return current_cell - direction, None
        return current_cell, None

    def get_first_target_ahead(self, attacker: Entity) -> Optional[Entity]:
        direction = attacker.position.get_direction()
        current_cell = attacker.position.cell
        while True:
            current_cell += direction
            if not self.is_legal_position(current_cell):
                return None
            for enemy in self.enemies:
                if enemy.position.cell == current_cell:
                    return enemy
            if self.hero.position.cell == current_cell:
                return self.hero

    def get_first_target_space_ahead(self, attacker: Entity) -> Optional[int]:
        direction = attacker.position.get_direction()
        return self.get_first_target_space_in_direction(attacker, direction)

    def get_first_target_space_behind(self, attacker: Entity) -> Optional[int]:
        direction = -attacker.position.get_direction()
        return self.get_first_target_space_in_direction(attacker, direction)

    def get_first_target_space_ahead_in_range(self, attacker: Entity, weapon_range: int) -> Optional[
        int]:
        direction = attacker.position.get_direction()
        return self.get_first_target_space_in_direction(attacker, direction, weapon_range)

    def get_first_target_spaces_around(self, attacker: Entity) -> List[int]:
        targets = []
        target_right = self.get_first_target_space_in_direction(attacker, 1)
        if target_right is not None:
            targets.append(target_right)
        target_left = self.get_first_target_space_in_direction(attacker, -1)
        if target_left is not None:
            targets.append(target_left)
        return targets

    def get_first_target_space_in_direction(self, attacker: Entity, direction: int, weapon_range: int = 10) -> Optional[
        int]:
        current_cell = attacker.position.cell
        for i in range(weapon_range):
            current_cell += direction
            if not self.is_legal_position(current_cell):
                return None
            if len(self.find_targets([current_cell])):
                return current_cell

    def get_last_target_space_ahead(self, attacker: Entity) -> Optional[int]:
        direction = -attacker.position.get_direction()
        current_cell = self.board_size if attacker.position.facing == 1 else -1
        while True:
            current_cell += direction
            if current_cell == attacker.position.cell:
                return None
            for enemy in self.enemies:
                if enemy.position.cell == current_cell:
                    return current_cell
            if self.hero.position.cell == current_cell:
                return current_cell

    def get_last_free_space_ahead(self, attacker: Entity) -> int:
        direction = attacker.position.get_direction()
        return self.get_last_free_space_in_direction(attacker, direction)

    def get_last_free_space_behind(self, attacker: Entity) -> int:
        direction = -attacker.position.get_direction()
        return self.get_last_free_space_in_direction(attacker, direction)

    def get_last_free_space_in_direction(self, attacker: Entity, direction: int) -> int:
        current_cell = attacker.position.cell
        while True:
            new_cell = current_cell + direction
            if not self.is_legal_position(current_cell):
                return current_cell - direction
            if len(self.find_targets([new_cell])) > 0:
                return current_cell
            current_cell = new_cell

    def get_crossbow_targets_spaces(self, attacker: Entity) -> List[int]:
        first_target = self.get_first_target_ahead(attacker)
        if first_target is None:
            return []
        direction = attacker.position.get_direction()
        _, second_target = self.get_push_target_in_direction(first_target, direction)
        if second_target is None:
            return [first_target.position.cell]
        return [first_target.position.cell, second_target.position.cell]

    def get_all_targets_cells(self) -> List[int]:
        return [i for i in range(self.board_size)]

    def get_all_hurt_enemies_cells(self) -> List[int]:
        targets = []
        for enemy in self.enemies:
            if enemy.hp.hp < enemy.hp.max_hp:
                targets.append(enemy.position.cell)
        return targets

    def find_targets(self, target_cells: List[Optional[int]]):
        targets = []
        for enemy in self.enemies:
            if enemy.position.cell in target_cells:
                targets.append(enemy)
        if self.hero.position.cell in target_cells:
            targets.append(self.hero)
        return targets

    def find_connected_targets(self, attacker: Entity, target_cells: List[Optional[int]]) -> Tuple[
        List[int], List[int]]:
        attacker_cell = attacker.position.cell
        logger.queue_debug_text(
            f"Looking for connected targets. Attacker cell: {attacker_cell}, targets: {target_cells}")
        shock_targets = set()
        direct_targets = self.find_targets(target_cells)
        logger.queue_debug_text(f"Targets found: {[e.short_print() for e in direct_targets]}")
        for direct_target in direct_targets:
            current_cell = direct_target.position.cell
            while True:
                current_cell += 1
                if not self.is_legal_position(current_cell):
                    break
                if current_cell in shock_targets or current_cell == attacker_cell:
                    continue
                if not len(self.find_targets([current_cell])) > 0:
                    break
                shock_targets.add(current_cell)
            current_cell = direct_target.position.cell
            while True:
                current_cell -= 1
                if not self.is_legal_position(current_cell):
                    break
                if current_cell in shock_targets or current_cell == attacker_cell:
                    continue
                if not len(self.find_targets([current_cell])) > 0:
                    break
                shock_targets.add(current_cell)
        return [dt.position.cell for dt in direct_targets], list(shock_targets)

    def hit_entities(self, attacker: Entity, target_cells: List[Optional[int]], weapon: Weapon,
                     simulate_move=None) -> HitData:
        hit_data = HitData.empty()
        does_shock = weapon.is_shocking()
        twin_target = None
        for enemy in self.enemies:
            if enemy.enemy_id == EnemyEnum.THE_TWINS_A:
                twin_target = enemy
        if does_shock:
            direct_target_cells, shock_target_cells = self.find_connected_targets(attacker, target_cells)
        else:
            direct_target_cells = target_cells
            shock_target_cells = []
        direct_targets = self.find_targets(direct_target_cells)
        logger.queue_debug_text(f"direct targets: {[', '.join(t.short_print() for t in direct_targets)]}")
        shock_targets = self.find_targets(shock_target_cells)
        logger.queue_debug_text(f"shock targets: {[', '.join(t.short_print() for t in shock_targets)]}")
        if not len(direct_targets):
            return hit_data
        for target in direct_targets:
            if weapon.weapon_type == WeaponEnum.CORRUPTED_WAVE and attacker.is_equal(target):
                hit_data.hits += target.boss_corruption_heal(weapon)
            else:
                hit_data.hits += target.hit(weapon, twin_target)
            # if target.enemy_id == EnemyEnum.THORNS:
            #     hit_data.hits += attacker.hit(Weapon.thorns(), twin_target)
        if does_shock:
            shock_itself = Weapon.shock()
            for target in shock_targets:
                hit_data.hits += target.hit(shock_itself, twin_target)
        # Additional effects of particular weapons.
        stop_weapon = Weapon.stop()
        if weapon.weapon_type == WeaponEnum.BO:
            for target in direct_targets:
                target.position.flip()
        elif weapon.weapon_type in [WeaponEnum.DRAGON_PUNCH, WeaponEnum.TWIN_TESSEN,
                                    WeaponEnum.KI_PUSH, WeaponEnum.PUSH]:
            for target in direct_targets:
                if target.is_heavy():
                    continue
                direction = attacker.position.get_direction_towards(target)
                stop_cell, stop_target = self.get_push_target_in_direction(target, direction)
                if stop_target is None:
                    logger.queue_debug_text(f"stop cell: {stop_cell} stop_target: NONE")
                else:
                    logger.queue_debug_text(f"stop cell: {stop_cell} stop_target: {stop_target.short_print()}")
                if stop_target:
                    hit_data.hits += target.hit(stop_weapon, twin_target)
                    hit_data.hits += stop_target.hit(stop_weapon, twin_target)
                hit_data2 = simulate_move(target, stop_cell, dash=True)
                hit_data.merge(hit_data2)
        elif weapon.weapon_type in [WeaponEnum.TANEGASHIMA]:
            for target in direct_targets:
                if target.is_heavy():
                    continue
                # push target
                direction = attacker.position.get_direction_towards(target)
                stop_cell, stop_target = self.get_push_target_in_direction(target, direction, 1)
                if stop_target:
                    hit_data.hits += target.hit(stop_weapon, twin_target)
                    hit_data.hits += stop_target.hit(stop_weapon, twin_target)
                hit_data2 = simulate_move(target, stop_cell, dash=True)
                hit_data.merge(hit_data2)
                # push attacker back
                direction = -attacker.position.get_direction_towards(target)
                stop_cell, stop_target = self.get_push_target_in_direction(attacker, direction, 1)
                if stop_target:
                    hit_data.hits += attacker.hit(stop_weapon, twin_target)
                    hit_data.hits += stop_target.hit(stop_weapon, twin_target)
                hit_data2 = simulate_move(attacker, stop_cell, dash=True)
                hit_data.merge(hit_data2)
        elif weapon.weapon_type in [WeaponEnum.GRAPPLING_HOOK]:
            for target in direct_targets:
                if target.is_heavy():
                    continue
                direction = 1 if attacker.position.cell - target.position.cell < 0 else -1
                hit_data2 = simulate_move(target, attacker.position.cell + direction, dash=True)
                hit_data.merge(hit_data2)
        hit_data.targets_hit = len(direct_targets)
        return hit_data

    def curse_entities(self, attacker: Entity, target_cells: List[int]):
        single_targets = self.find_targets(target_cells)
        for target in single_targets:
            target.state.curse = True

    def is_legal_position(self, position: int) -> bool:
        return 0 <= position < self.board_size

    def is_edge_space(self, position: int) -> bool:
        return position == 0 or position == self.board_size - 1
