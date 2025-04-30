from typing import List, Dict, Optional, Tuple

from constants import CURRENT_LOCATION, MAP_SAVE, COMBAT_ROOM, \
    PROGRESSION, PROGRESSION_DATA, ENEMIES, PICKUP_LOCATIONS, PICKUPS, UNTIL_NEXT_WAVE, WAVE_NUMBER, HERO
from data.entity import Entity
from data.hit_data import HitData
from data.mappers import room_mapper
from data.prediction_error import PredictionError
from data.weapon import Weapon
from enums import PickupEnum, RoomEnum, WeaponAttackEffectEnum, WeaponEnum, EnemyEliteEnum


class BattleRoom:
    room: RoomEnum
    progression: int
    hero: Entity
    enemies: List[Entity]
    pickups: Dict[int, Dict[PickupEnum, int]]
    wave_number: int
    until_next_wave: int

    def __init__(self,
                 room: RoomEnum,
                 progression: int,
                 hero: Entity,
                 enemies: List[Entity],
                 pickups: Dict[int, Dict[PickupEnum, int]],
                 wave_number: int,
                 until_next_wave: int,
                 ):
        self.room = room
        self.progression = progression
        self.hero = hero
        self.enemies = enemies
        self.pickups = pickups
        self.wave_number = wave_number
        self.until_next_wave = until_next_wave

    @staticmethod
    def from_dict(source: Dict):
        room_raw = source[MAP_SAVE][CURRENT_LOCATION]
        progression = source[PROGRESSION_DATA][PROGRESSION]
        room = room_mapper.get(room_raw)
        if room is None:
            print(f"Unknown room: {room_raw}")  # TODO remove, dev only
            return None
        enemies = [Entity.from_dict(x) for x in source[COMBAT_ROOM][ENEMIES]]
        pickups_raw = source[PICKUPS]
        pickup_locations = source[PICKUP_LOCATIONS]
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
            hero=Entity.from_dict(source.get(HERO, {}), hero=True),
            enemies=enemies,
            pickups=pickups,
            wave_number=source[COMBAT_ROOM][WAVE_NUMBER],
            until_next_wave=source[COMBAT_ROOM][UNTIL_NEXT_WAVE],
        )

    def clone(self):
        return BattleRoom(
            room=self.room,
            progression=self.progression,
            hero=self.hero.clone(),  # reconstructed
            enemies=[enemy.clone() for enemy in self.enemies],
            pickups=self.pickups.copy(),
            wave_number=self.wave_number,
            until_next_wave=self.until_next_wave,
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

    def is_good_prediction(self, other, debug: bool = False):
        if self.wave_number == other.wave_number:
            if len(self.enemies) != len(other.enemies):
                if debug:
                    raise PredictionError(f"wrong number of enemies in same wave")
                return False
            for i in range(len(self.enemies)):
                if not self.enemies[i].is_good_prediction(other.enemies[i], debug):
                    if debug:
                        raise PredictionError(f"wrong enemy #{i} in same wave")
                    return False
        else:
            enemies_ok = len(self.enemies) > len(other.enemies)
            if not enemies_ok:
                if debug:
                    raise PredictionError(f"wrong number of enemies")
                return False
            for enemy in self.enemies:
                predicted = True in [e.is_good_prediction(enemy) for e in other.enemies]
                newly_spawned = not predicted and enemy.hp.hp == enemy.hp.max_hp
                if not predicted and not newly_spawned:
                    if debug:
                        raise PredictionError(f"wrong enemies in new wave")
                    return False

        # If pickup is predicted, it needs to be there.
        for loc, pps in other.pickups.items():
            if loc not in self.pickups:
                if len(pps) > 1 or PickupEnum.ANY not in pps:
                    if debug:
                        raise PredictionError(f"missing predicted pickup location")
                    return False
            for p_type, total in pps.items():
                if p_type != PickupEnum.ANY:
                    if p_type not in self.pickups[loc]:
                        if debug:
                            raise PredictionError(f"missing predicted pickup type")
                        return False
                    if self.pickups[loc][p_type] != total:
                        if debug:
                            raise PredictionError(f"wrong predicted pickup total")
                        return False

        # If pickup is there, it needs to be predicted.
        for loc, pps in self.pickups.items():
            if loc not in other.pickups:
                if debug:
                    raise PredictionError(f"unpredicted pickup location")
                return False
            for p_type, total in pps.items():
                if PickupEnum.ANY not in other.pickups[loc]:
                    if p_type not in other.pickups[loc]:
                        if debug:
                            raise PredictionError(f"unpredicted pickup type {p_type.value}")
                        return False
                    if other.pickups[loc][p_type] != total:
                        if debug:
                            raise PredictionError(
                                f"unpredicted pickup total loc: {loc} type: {p_type.value} total: {total}")
                        return False

        return self.room == other.room and \
               self.progression == other.progression and \
               self.hero.is_equal(other.hero, debug)

    def pretty_print_pickups(self) -> str:
        retval = []
        for loc, pps in self.pickups.items():
            pps_str = []
            for pp, total in pps.items():
                pps_str.append(f"{pp.value}({total})")
            retval.append(f"{loc}: {', '.join(pps_str)}")
        return ", ".join(retval)

    def get_push_target_in_direction(self, entity: Entity, direction: int, board_size: int, push_range=10) -> Tuple[
        int, Optional[Entity]]:
        current_cell = entity.position.cell
        for i in range(push_range):
            current_cell += direction
            for enemy in self.enemies:
                if enemy.position.cell == current_cell:
                    return current_cell - direction, enemy
            if self.hero.position.cell == current_cell:
                return current_cell - direction, self.hero
            if current_cell == 0 or current_cell == board_size - 1:
                return current_cell, None
        return entity.position.cell + push_range, None

    def get_first_target_ahead(self, attacker: Entity, board_size: int) -> Optional[Entity]:
        direction = 1 if attacker.position.facing == 1 else -1
        current_cell = attacker.position.cell
        while True:
            current_cell += direction
            if current_cell < 0 or current_cell >= board_size:
                return None
            for enemy in self.enemies:
                if enemy.position.cell == current_cell:
                    return enemy
            if self.hero.position.cell == current_cell:
                return self.hero

    def get_first_target_space_ahead(self, attacker: Entity, board_size: int) -> Optional[int]:
        direction = 1 if attacker.position.facing == 1 else -1
        current_cell = attacker.position.cell
        while True:
            current_cell += direction
            if current_cell < 0 or current_cell >= board_size:
                return None
            for enemy in self.enemies:
                if enemy.position.cell == current_cell:
                    return current_cell
            if self.hero.position.cell == current_cell:
                return current_cell

    def get_first_target_space_ahead_in_range(self, attacker: Entity, weapon_range: int, board_size: int) -> Optional[
        int]:
        direction = 1 if attacker.position.facing == 1 else -1
        current_cell = attacker.position.cell
        for i in range(weapon_range):
            current_cell += direction
            if current_cell < 0 or current_cell >= board_size:
                return None
            for enemy in self.enemies:
                if enemy.position.cell == current_cell:
                    return current_cell
            if self.hero.position.cell == current_cell:
                return current_cell

    def get_last_target_space_ahead(self, attacker: Entity, board_size: int) -> Optional[int]:
        direction = -1 if attacker.position.facing == 1 else 1
        current_cell = board_size if attacker.position.facing == 1 else -1
        while True:
            current_cell += direction
            if current_cell == attacker.position.cell:
                return None
            for enemy in self.enemies:
                if enemy.position.cell == current_cell:
                    return current_cell
            if self.hero.position.cell == current_cell:
                return current_cell

    def get_first_target_spaces_around(self, attacker: Entity, board_size: int) -> List[int]:
        targets = []
        current_cell = attacker.position.cell
        while True:
            current_cell -= 1
            if current_cell < 0:
                break
            for enemy in self.enemies:
                if enemy.position.cell == current_cell:
                    targets.append(current_cell)
            if self.hero.position.cell == current_cell:
                targets.append(current_cell)
        current_cell = -1
        while True:
            current_cell += 1
            if current_cell >= board_size:
                break
            for enemy in self.enemies:
                if enemy.position.cell == current_cell:
                    targets.append(current_cell)
            if self.hero.position.cell == current_cell:
                targets.append(current_cell)
        return targets

    def get_crossbow_targets(self, attacker: Entity, board_size: int) -> List[int]:
        first_target = self.get_first_target_ahead(attacker, board_size)
        if first_target is None:
            return []
        direction = 1 if attacker.position.facing == 1 else -1
        _, second_target = self.get_push_target_in_direction(first_target, direction, board_size)
        if second_target is None:
            return [first_target.position.cell]
        return [first_target.position.cell, second_target.position.cell]

    def get_all_targets(self) -> List[int]:
        targets = [e.position.cell for e in self.enemies]
        targets.append(self.hero.position.cell)
        return targets

    def get_all_hurt_enemies_cells(self) -> List[int]:
        targets = []
        for enemy in self.enemies:
            if enemy.hp.hp < enemy.hp.max_hp:
                targets.append(enemy.position.cell)
        return targets

    def find_targets(self, target_cells: List[int]):
        targets = []
        for enemy in self.enemies:
            if enemy.position.cell in target_cells:
                targets.append(enemy)
        if self.hero.position.cell in target_cells:
            targets.append(self.hero)
        return targets

    def find_connected_targets(self, target_cells: List[int], board_size: int):
        single_targets = []
        double_targets = []
        targets = []
        for cell in target_cells:
            include = False
            for other_cell in target_cells:
                if other_cell == cell - 1:
                    include = True
                if other_cell == cell + 1:
                    include = True
            if include:
                double_targets.append(cell)
            else:
                single_targets.append(cell)
        for cell in target_cells:
            new_target_cell = cell
            while True:
                new_target_cell -= 1
                if new_target_cell < 0:
                    break
                if new_target_cell in target_cells:
                    break
                found = False
                for enemy in self.enemies:
                    if enemy.position.cell == new_target_cell:
                        targets.append(enemy)
                        found = True
                if not found:
                    break
            new_target_cell = cell
            while True:
                new_target_cell += 1
                if new_target_cell >= board_size:
                    break
                if new_target_cell in target_cells:
                    break
                found = False
                for enemy in self.enemies:
                    if enemy.position.cell == new_target_cell:
                        targets.append(enemy)
                        found = True
                if not found:
                    break
        return single_targets, double_targets, targets

    def hit_entities(self, attacker: Entity, target_cells: List[int], weapon: Weapon, board_size: int) -> HitData:
        hits = 0
        does_shock = weapon.attack_effect is not None and weapon.attack_effect == WeaponAttackEffectEnum.SHOCKWAVE
        # print(f"does_shock={does_shock}")
        if does_shock:
            single_target_cells, double_target_cells, shock_target_cells = self.find_connected_targets(target_cells,
                                                                                                       board_size)
        else:
            single_target_cells = target_cells
            double_target_cells = []
            shock_target_cells = []
        single_targets = self.find_targets(single_target_cells)
        double_targets = self.find_targets(double_target_cells)
        shock_targets = self.find_targets(shock_target_cells)
        direct_targets = single_targets[:] + double_targets[:]
        if not len(single_targets) and not len(double_targets):
            return HitData.empty()
        for target in single_targets:
            hits += target.hit(weapon)
        if does_shock:
            shock_weapon = weapon.clone()
            shock_weapon.strength += 1
            for target in double_targets:
                hits += target.hit(shock_weapon)

            shock_itself = Weapon.shock()
            for target in shock_targets:
                hits += target.hit(shock_itself)
        # apply additional effect like moving
        if weapon.weapon_type == WeaponEnum.BO:
            for target in direct_targets:
                target.position.flip()
        elif weapon.weapon_type in [WeaponEnum.DRAGON_PUNCH, WeaponEnum.TWIN_TESSEN,
                                    WeaponEnum.KI_PUSH, WeaponEnum.PUSH]:
            stop_weapon = Weapon.stop()
            for target in direct_targets:
                if target.enemy_intent is not None and target.enemy_intent.elite_type == EnemyEliteEnum.HEAVY:
                    continue
                direction = 1 if attacker.position.cell - target.position.cell < 0 else -1
                stop_cell, stop_target = self.get_push_target_in_direction(target, direction, board_size)
                if stop_target:
                    hits += target.hit(stop_weapon)
                    hits += stop_target.hit(stop_weapon)
                target.position.cell = stop_cell
        elif weapon.weapon_type in [WeaponEnum.TANEGASHIMA]:
            stop_weapon = Weapon.stop()
            for target in direct_targets:
                if target.enemy_intent is not None and target.enemy_intent.elite_type == EnemyEliteEnum.HEAVY:
                    continue
                # push target
                direction = 1 if attacker.position.cell - target.position.cell < 0 else -1
                stop_cell, stop_target = self.get_push_target_in_direction(target, direction, board_size, 1)
                if stop_target:
                    hits += target.hit(stop_weapon)
                    hits += stop_target.hit(stop_weapon)
                target.position.cell = stop_cell
                # push attacker
                direction = -1 if attacker.position.cell - target.position.cell < 0 else 1
                stop_cell, stop_target = self.get_push_target_in_direction(attacker, direction, board_size, 1)
                if stop_target:
                    hits += attacker.hit(stop_weapon)
                    hits += stop_target.hit(stop_weapon)
                attacker.position.cell = stop_cell
        elif weapon.weapon_type in [WeaponEnum.GRAPPLING_HOOK]:
            for target in direct_targets:
                if target.enemy_intent is not None and target.enemy_intent.elite_type == EnemyEliteEnum.HEAVY:
                    continue
                direction = 1 if attacker.position.cell - target.position.cell < 0 else -1
                target.position.cell = attacker.position.cell + direction
        return HitData(hits=hits, targets_hit=len(direct_targets))

    def curse_entities(self, attacker: Entity, target_cells: List[int]):
        single_targets = self.find_targets(target_cells)
        for target in single_targets:
            target.state.curse = True

    def swap_entities(self, attacker: Entity, target_cell: int):
        target = self.find_targets([target_cell])[0]
        if target is None:
            return
        attacker_cell = attacker.position.cell
        attacker.position.cell = target.position.cell
        target.position.cell = attacker_cell
