import base64
import itertools
import json
from typing import List, Optional, Dict

from constants import MAP_SELECTION, DECK, POTIONS, TARGETS_HIT, HITS
from data.entity import Entity
from data.game_stats import GameStats
from data.hit_data import HitData
from data.mappers import room_name_mapper, room_boss_mapper, shop_name_mapper, boss_room_mapper
from data.prediction_error import PredictionError
from data.room_battle import BattleRoom
from data.room_reward import RewardRoom
from data.room_shop import ShopRoom
from data.skills import Skill
from data.weapon import Weapon
from enums import GamePhase, PickupEnum, EnemyActionEnum, WeaponTileEffectEnum, WeaponEnum, WeaponAttackEffectEnum, \
    EntityType, HeroEnum
from test_data import test_data


class Snapshot:
    skills: List[Skill]
    game_stats: GameStats
    hero_deck: List[Weapon]
    hero_potion_ids: List[int]
    game_phase: GamePhase
    room: Optional[BattleRoom]
    shop: Optional[ShopRoom]
    reward: Optional[RewardRoom]
    potential_hero_attack_queues: Optional[List[List[Weapon]]]
    potential_hero_decks: Optional[List[List[Weapon]]]

    def __init__(self,
                 skills: List[Skill],
                 game_stats: GameStats,
                 hero_deck: List[Weapon],
                 hero_potion_ids: List[int],
                 game_phase: GamePhase,
                 room: Optional[BattleRoom] = None,
                 shop: Optional[ShopRoom] = None,
                 reward: Optional[RewardRoom] = None,
                 potential_hero_attack_queues: Optional[List[List[Weapon]]] = None,
                 potential_hero_decks: Optional[List[List[Weapon]]] = None,
                 ):
        self.skills = skills
        self.game_stats = game_stats
        self.hero_deck = hero_deck
        self.hero_potion_ids = hero_potion_ids
        self.game_phase = game_phase
        self.room = room
        self.shop = shop
        self.reward = reward
        self.potential_hero_attack_queues = potential_hero_attack_queues
        self.potential_hero_decks = potential_hero_decks

    @staticmethod
    def from_file(source: str):
        raw_data = json.loads(base64.b64decode(source))
        # Uncomment for developer work - check if all data is recorded.
        test_data(json.loads(json.dumps(raw_data)))
        return Snapshot.from_dict(raw_data)

    @staticmethod
    def from_dict(raw_data: Dict):
        game_phase = GamePhase.BATTLE
        map_selection = raw_data[MAP_SELECTION]
        if map_selection:
            game_phase = GamePhase.MAP_JOURNEY
        reward_room = RewardRoom.from_dict(raw_data)
        if reward_room is not None:
            game_phase = GamePhase.BATTLE_REWARDS
        shop_room = ShopRoom.from_dict(raw_data)
        if shop_room is not None:
            game_phase = GamePhase.SHOP
        battle_room = BattleRoom.from_dict(raw_data)

        return Snapshot(
            skills=Skill.from_dict(raw_data),
            game_stats=GameStats.from_dict(raw_data),
            hero_deck=[Weapon.from_dict(x) for x in raw_data[DECK]],
            hero_potion_ids=raw_data[POTIONS],
            game_phase=game_phase,
            room=battle_room,
            shop=shop_room,
            reward=reward_room,
        )

    def get_room(self):
        is_boss_battle = False
        room_name = None
        boss_name = None
        if self.game_phase in [GamePhase.BATTLE, GamePhase.BATTLE_REWARDS]:
            is_boss_battle = boss_room_mapper.get(self.room.room, {}).get(self.room.progression, False)
            room_name = room_name_mapper.get(self.room.room)
            boss_name = room_boss_mapper.get(self.room.room)
            if room_name is None:
                raise ValueError(f"Unknown room name: {self.room.room}")
            if boss_name is None:
                raise ValueError(f"Unknown boss name: {self.room.room}")
        if self.game_phase == GamePhase.BATTLE:
            if is_boss_battle:
                return f"{room_name}, boss battle ({boss_name})"
            else:
                return f"{room_name}, battle #{(self.room.progression // 2) + 1}"
        elif self.game_phase == GamePhase.BATTLE_REWARDS:
            if is_boss_battle:
                return f"{room_name}, boss battle ({boss_name}) rewards"
            else:
                return f"{room_name}, battle #{(self.room.progression + 1) // 2} rewards"
        elif self.game_phase == GamePhase.SHOP:
            shop_name = shop_name_mapper.get(self.shop.location)
            if shop_name is None:
                raise ValueError(f"Unknown shop name: {self.shop.location}")
            return f"{shop_name}"

    def clone(self, possible_attack_queues: Optional[List[List[Weapon]]] = None):
        return Snapshot(
            skills=self.skills,  # can be copied, cannot change during battle
            game_stats=self.game_stats.clone(),  # reconstructed
            hero_deck=[weapon.clone() for weapon in self.hero_deck],  # reconstructed
            hero_potion_ids=self.hero_potion_ids[:],  # reconstructed
            game_phase=self.game_phase,  # can be copied, cannot change during battle
            room=self.room.clone(),  # reconstructed
            shop=self.shop,  # can be copied, cannot change during battle
            reward=self.reward,  # can be copied, cannot change during battle
            potential_hero_attack_queues=possible_attack_queues,
        )

    def is_equal(self, other):
        return self.game_stats.is_equal(other.game_stats) \
               and len(self.hero_deck) == len(other.hero_deck) \
               and False not in [self.hero_deck[i].is_equal(other.hero_deck[i]) for i in
                                 range(len(self.hero_deck))] \
               and len(self.hero_potion_ids) == len(other.hero_potion_ids) \
               and False not in [self.hero_potion_ids[i] == other.hero_potion_ids[i] for i in
                                 range(len(self.hero_potion_ids))] \
               and self.game_phase == other.game_phase \
               and self.room.is_equal(other.room)

    def reduce_potential_attack_queues(self, other):
        if self.game_phase == GamePhase.BATTLE_REWARDS:
            other.room.hero.attack_queue = []
            return other
        if other.potential_hero_attack_queues is None:
            return other
        for phaq in other.potential_hero_attack_queues:
            # print(f"phaq: {Weapon.debug_print_list(phaq)}")
            # print(f"self: {Weapon.debug_print_list(self.room.hero.attack_queue)}")
            if len(phaq) == len(self.room.hero.attack_queue):
                if False not in [weapon.is_equal(self.room.hero.attack_queue[index])
                                 for index, weapon in enumerate(phaq)]:
                    other.room.hero.attack_queue = phaq
                    return other
        return None

    def reduce_potential_decks(self, other):
        if self.game_phase == GamePhase.BATTLE_REWARDS:
            other.hero_deck = [weapon.clone() for weapon in self.hero_deck]
            return other
        if other.potential_hero_decks is None:
            return other
        for phd in other.potential_hero_decks:
            # print(f"phd: {Weapon.debug_print_list(phd)}")
            # print(f"self: {Weapon.debug_print_list(self.hero_deck)}")
            if len(phd) == len(self.hero_deck):
                if False not in [weapon.is_equal(self.hero_deck[index], debug=True)
                                 for index, weapon in enumerate(phd)]:
                    other.hero_deck = phd
                    return other
        return None

    def is_good_prediction(self, other, debug: bool = False):
        other = self.reduce_potential_attack_queues(other)
        if other is None:
            if debug:
                raise PredictionError(f"none of the potential attack queues check out")
            return False
        other = self.reduce_potential_decks(other)
        if other is None:
            if debug:
                raise PredictionError(f"none of the potential decks check out")
            return False
        if len(self.hero_potion_ids) != len(other.hero_potion_ids):
            if debug:
                raise PredictionError(f"wrong number of potions")
            return False
        for potion_id in other.hero_potion_ids:
            if potion_id != -1 and potion_id not in self.hero_potion_ids:
                if debug:
                    raise PredictionError(f"predicted potion missing")
                return False
        if len(self.hero_deck) != len(other.hero_deck):
            if debug:
                raise PredictionError(f"wrong hero deck size")
            return False
        for i in range(len(self.hero_deck)):
            if not self.hero_deck[i].is_equal(other.hero_deck[i], debug):
                if debug:
                    raise PredictionError(f"wrong hero deck state")
                return False
        if self.game_phase != other.game_phase:
            if debug:
                raise PredictionError(f"wrong game phase")
            return False
        return self.game_stats.is_equal(other.game_stats, debug) \
               and self.room.is_good_prediction(other.room, debug)

    def simulation_move_right(self, possible_attack_queues: List[List[Weapon]], board_size: int):
        current_cell = self.room.hero.position.cell
        new_cell = self.room.hero.position.cell + 1
        # Is there board there?
        if current_cell == board_size - 1:
            return None
        # Common move logic.
        return self.simulation_move(possible_attack_queues, new_cell)

    def simulation_move_left(self, possible_attack_queues: List[List[Weapon]]):
        current_cell = self.room.hero.position.cell
        new_cell = self.room.hero.position.cell - 1
        # Is there board there?
        if current_cell == 0:
            return None
        # Common move logic.
        return self.simulation_move(possible_attack_queues, new_cell)

    def simulation_turn_around(self, possible_attack_queues: List[List[Weapon]], free=False):
        simulation = self.clone(possible_attack_queues=possible_attack_queues)
        if not free:
            simulation.simulate_passing_turn()
        simulation.room.hero.position.flip()
        simulation.game_stats.turn_arounds += 1
        return simulation

    def simulation_wait(self, possible_attack_queues: Optional[List[List[Weapon]]] = None):
        simulation = self.clone(possible_attack_queues=possible_attack_queues)
        simulation.simulate_passing_turn()
        return simulation

    def simulation_execute_queue(self, attack_queue: List[Weapon], board_size: int):
        simulation = self.clone()
        attack_queue = [weapon.clone() for weapon in attack_queue]
        for weapon in attack_queue:
            simulation.execute_weapon(simulation.room.hero, weapon, board_size, simulation.room.hero.position.cell)
        possible_deck_weapons_used = {}
        for index, weapon in enumerate(attack_queue):
            possible_deck_indices = []
            for deck_index, deck_weapon in enumerate(simulation.hero_deck):
                if deck_weapon.is_same_tile(weapon):
                    possible_deck_indices.append(deck_index)
            if not len(possible_deck_indices):
                raise PredictionError(f"Could not find the tile corresponding to {weapon.pretty_print()} in the deck")
            possible_deck_weapons_used[index] = possible_deck_indices
        simulated_decks = [[weapon.clone() for weapon in simulation.hero_deck]]
        for weapon in simulated_decks[0]:
            if weapon.cooldown_charge < weapon.cooldown:
                weapon.cooldown_charge += 1
        for index, possible_deck_indices in possible_deck_weapons_used.items():
            new_simulated_decks = []
            for sim_deck in simulated_decks:
                for pdi in possible_deck_indices:
                    new_sim_deck = sim_deck[:]
                    new_sim_deck[pdi] = attack_queue[index]
                    new_simulated_decks.append(new_sim_deck)
            simulated_decks = new_simulated_decks
        simulation.room.hero.attack_queue = []
        simulation.simulate_passing_turn(skip_attack_queue=True)
        simulation.potential_hero_decks = simulated_decks
        return simulation

    @staticmethod
    def merge_hit_data(hit_data1, hit_data2):
        return {
            HITS: hit_data1.get(HITS, 0) + hit_data2.get(HITS, 0),
            TARGETS_HIT: hit_data1.get(TARGETS_HIT, 0) + hit_data2.get(TARGETS_HIT, 0),
        }

    def execute_weapon(self, attacker: Entity, weapon: Weapon, board_size: int, previous_hero_cell: int,
                       combo_started: bool) -> bool:
        hit_data: Optional[HitData] = None
        # MELEE ATTACKS
        if weapon.weapon_type in [WeaponEnum.KATANA, WeaponEnum.SAI, WeaponEnum.BO, WeaponEnum.TETSUBO,
                                  WeaponEnum.BLADE_OF_PATIENCE, WeaponEnum.DRAGON_PUNCH]:
            targets = attacker.get_spaces_in_front()
            hit_data = self.room.hit_entities(attacker, targets, weapon, board_size)
        elif weapon.weapon_type == WeaponEnum.SPEAR:
            targets = attacker.get_spaces_in_front(2)
            hit_data = self.room.hit_entities(attacker, targets, weapon, board_size)
        elif weapon.weapon_type == WeaponEnum.BACK_STRIKE:
            target = attacker.get_space_in_the_back()
            hit_data = self.room.hit_entities(attacker, [target], weapon, board_size)
        elif weapon.weapon_type in [WeaponEnum.SWIRL, WeaponEnum.TWIN_TESSEN]:
            targets = attacker.get_spaces_around()
            hit_data = self.room.hit_entities(attacker, targets, weapon, board_size)
        elif weapon.weapon_type == WeaponEnum.NAGIBOKU:
            targets = attacker.get_spaces_around(2)
            hit_data = self.room.hit_entities(attacker, targets, weapon, board_size)

        # RANGED ATTACKS
        elif weapon.weapon_type in [WeaponEnum.ARROW, WeaponEnum.SHURIKEN, WeaponEnum.GRAPPLING_HOOK,
                                    WeaponEnum.KI_PUSH, WeaponEnum.TANEGASHIMA]:
            target = self.room.get_first_target_space_ahead(attacker, board_size)
            hit_data = self.room.hit_entities(attacker, [target], weapon, board_size)
        elif weapon.weapon_type == WeaponEnum.MON:
            target = self.room.get_first_target_space_ahead(attacker, board_size)
            hit_data = self.room.hit_entities(attacker, [target], weapon, board_size)
            self.game_stats.coins -= 1
        elif weapon.weapon_type == WeaponEnum.LIGHTINING:
            target = self.room.get_last_target_space_ahead(attacker, board_size)
            if target is not None:
                hit_data = self.room.hit_entities(attacker, [target], weapon, board_size)
        elif weapon.weapon_type == WeaponEnum.CHAKRAM:
            targets = self.room.get_first_target_spaces_around(attacker, board_size)
            hit_data = self.room.hit_entities(attacker, targets, weapon, board_size)
            weapon.strength = weapon.base_strength
        elif weapon.weapon_type == WeaponEnum.EARTH_IMPALE:
            targets = attacker.get_spaces_away_around(2)
            hit_data = self.room.hit_entities(attacker, targets, weapon, board_size)
        elif weapon.weapon_type == WeaponEnum.SHADOW_KAMA:
            target = attacker.get_space_away_in_front(2)
            hit_data = self.room.hit_entities(attacker, [target], weapon, board_size)
        elif weapon.weapon_type == WeaponEnum.KUNAI:
            return self.execute_kunai(attacker, weapon)
        elif weapon.weapon_type == WeaponEnum.CROSSBOW:
            targets = self.room.get_crossbow_targets(attacker, board_size)
            hit_data = self.room.hit_entities(attacker, targets, weapon, board_size)
        elif weapon.weapon_type == WeaponEnum.METEOR_HAMMER:
            target = self.room.get_first_target_space_ahead_in_range(attacker, 3, board_size)
            hit_data = self.room.hit_entities(attacker, [target], weapon, board_size)
            if hit_data.targets_hit > 0:
                target = attacker.get_space_in_the_back()
                hit_data2 = self.room.hit_entities(attacker, [target], weapon, board_size)
                hit_data = hit_data.merge(hit_data2)
        elif weapon.weapon_type == WeaponEnum.BLAZING_SUISEI:
            target = self.room.get_first_target_space_ahead_in_range(attacker, 3, board_size)
            hit_data = self.room.hit_entities(attacker, [target], weapon, board_size)
            killed = True in [enemy.hp.hp < 0 for enemy in self.room.enemies]
            if killed:
                hit_data2 = self.room.hit_entities(attacker, [target - 1, target + 1], Weapon.explosion(), board_size)
                hit_data = hit_data.merge(hit_data2)
        elif weapon.weapon_type == WeaponEnum.VOLLEY:
            # enemy only! hero is always the target
            hit_data = self.room.hit_entities(attacker, [previous_hero_cell], weapon, board_size)

        # GLOBAL ATTACKS
        elif weapon.weapon_type == WeaponEnum.CORRUPTED_WAVE_LTR:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.CORRUPTED_WAVE_RTL:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.CORRUPTED_EXPLOSION:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.CORRUPTED_BARRAGE:
            targets = self.room.get_all_targets()
            hit_data = self.room.hit_entities(attacker, targets, weapon, board_size)
        elif weapon.weapon_type == WeaponEnum.SCAR_STRIKE:
            targets = self.room.get_all_hurt_enemies_cells()
            hit_data = self.room.hit_entities(attacker, targets, weapon, board_size)

        # MOVE
        elif weapon.weapon_type == WeaponEnum.MIRROR:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.DASH:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.SWAP_TOSS:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.ORIGIN_OF_SYMMETRY:
            self.room.swap_entities(attacker, (board_size - 1) // 2)

        # MOVE AND ATTACK
        elif weapon.weapon_type == WeaponEnum.HOOKBLADE:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.SHARP_TURN:
            targets = attacker.get_spaces_around()
            hit_data = self.room.hit_entities(attacker, targets, weapon, board_size)
            attacker.position.flip()
            if attacker.entity_type == EntityType.HERO:
                self.game_stats.turn_arounds += 1
        elif weapon.weapon_type == WeaponEnum.CHARGE:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.BACK_CHARGE:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.SHADOW_DASH:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.BACK_SHADOW_DASH:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.SMOKE_BOMB:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.BACK_SMOKE_BOMB:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")

        # SUMMONS
        elif weapon.weapon_type == WeaponEnum.BOSS_SUMMON:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.THORNS:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.TRAP:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")

        # OTHER
        elif weapon.weapon_type == WeaponEnum.MAKU:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.SIGNATURE_MOVE:
            hit_data = self.execute_signature_move(attacker, board_size)
        elif weapon.weapon_type == WeaponEnum.COPYCAT_MIRROR:
            # We don't care about enemy attack queues
            pass
        elif weapon.weapon_type == WeaponEnum.SHIELD_ALLY:
            # Has several possiblites!
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.CURSE:
            target = self.room.get_first_target_space_ahead(attacker, board_size)
            if target is not None:
                self.room.curse_entities(attacker, [target])
        elif weapon.weapon_type == WeaponEnum.KILL_SUMMONS:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")

        return self.execute_weapon_aftermath(attacker, weapon, board_size, previous_hero_cell, combo_started, hit_data)

    def execute_weapon_aftermath(self, attacker: Entity, weapon: Optional[Weapon], board_size: int,
                                 previous_hero_cell: int,
                                 combo_started: bool, hit_data: HitData):
        # Put weapon on cooldown.
        if weapon is not None:
            weapon.cooldown_charge = 0

        # Clear out the dead.
        enemies_left = []
        for enemy in self.room.enemies:
            if enemy.hp.hp > 0:
                enemies_left.append(enemy)
            else:
                # Drop anything.
                loc = enemy.position.cell
                if loc not in self.room.pickups:
                    self.room.pickups[loc] = {}
                self.room.pickups[loc][PickupEnum.ANY] = 1
                # Increase strength of Chakrams.
                for queue_weapon in self.room.hero.attack_queue:
                    if queue_weapon.weapon_type == WeaponEnum.CHAKRAM and queue_weapon.strength < 9:
                        queue_weapon.strength += 1
                for deck_weapon in self.hero_deck:
                    if deck_weapon.weapon_type == WeaponEnum.CHAKRAM and deck_weapon.strength < 9:
                        deck_weapon.strength += 1
                # Game stats.
                if attacker.is_hero():
                    # history ?
                    # Increase combo.
                    if not combo_started:
                        combo_started = True
                    else:
                        self.game_stats.combos += 1
                else:
                    self.game_stats.friendly_kills += 1
        self.room.enemies = enemies_left

        # Count the hits.
        self.game_stats.hits += hit_data.hits

        # Perform double attack if applicable.
        if weapon is not None:
            undoubled_weapon = weapon.clone()
            undoubled_weapon.attack_effect = None
            weapon.strength = weapon.base_strength
            if weapon.attack_effect is not None and weapon.attack_effect == WeaponAttackEffectEnum.DOUBLE_STRIKE:
                return self.execute_weapon(attacker, undoubled_weapon, board_size, previous_hero_cell, combo_started)

        # Done.
        return combo_started

    def execute_kunai(self, attacker: Entity, weapon: Weapon, board_size: int, previous_hero_cell: int,
                      combo_started: bool) -> bool:
        kunai = weapon.kunai()
        kunai_total = weapon.strength
        if weapon.attack_effect is not None:
            if weapon.attack_effect == WeaponAttackEffectEnum.DOUBLE_STRIKE:
                kunai_total *= 2
            else:
                kunai.attack_effect = weapon.attack_effect
        for i in range(kunai_total):
            target = self.room.get_first_target_space_ahead(attacker, board_size)
            hit_data = self.room.hit_entities(attacker, [target], kunai, board_size)
            combo_started = self.execute_weapon_aftermath(attacker, kunai, board_size, previous_hero_cell,
                                                          combo_started, hit_data)
        return combo_started

    def can_execute_signature_move(self, attacker: Entity, board_size: int, other_direction=False) -> bool:
        if not attacker.is_hero():
            return False
        direction = (1 if attacker.position.facing == 1 else -1) * (-1 if other_direction else 1)
        hero_cell = attacker.position.cell
        if attacker.entity_id == HeroEnum.WANDERER:
            targets = self.room.find_targets([hero_cell + direction])
            return len(targets) > 0
        elif attacker.entity_id == HeroEnum.RONIN:
            targets = self.room.find_targets([hero_cell + direction])
            return len(targets) > 0
        elif attacker.entity_id == HeroEnum.JUJITSUKA:
            targets = self.room.find_targets([hero_cell - direction])
            blockers = self.room.find_targets([hero_cell + direction])
            return len(targets) and not len(blockers)
        elif attacker.entity_id == HeroEnum.CHAIN_MASTER:
            if hero_cell == 0 or hero_cell == board_size - 1:
                return False
            targets = self.room.find_targets([hero_cell - direction, hero_cell + direction])
            return len(targets) > 0
        elif attacker.entity_id == HeroEnum.SHADOW:
            single_targets, double_targets, shock_targets = self.room.find_connected_targets([hero_cell + direction],
                                                                                             board_size)
            all_targets: List[int] = single_targets + double_targets + shock_targets
            if not len(all_targets):
                return False
            if direction == 1:
                new_cell = max(all_targets) + 1
                if new_cell >= board_size:
                    return False
            else:
                new_cell = min(all_targets) - 1
                if new_cell < 0:
                    return False
            return True
        else:
            raise ValueError(f"Unexpected hero to execute signature move: {attacker.entity_id}")

    def execute_signature_move(self, attacker: Entity, board_size: int, other_direction=False) -> HitData:
        if not attacker.is_hero():
            raise ValueError(f"Non-hero entity {attacker.pretty_print()} trying to perform signature move")
        if not self.can_execute_signature_move(attacker, board_size, other_direction):
            return HitData.empty()
        direction = (1 if attacker.position.facing == 1 else -1) * (-1 if other_direction else 1)
        hero_cell = attacker.position.cell
        targets = []
        hit_data = HitData.empty()
        if attacker.entity_id == HeroEnum.WANDERER:
            targets = self.room.find_targets([hero_cell + direction])
            if len(targets):
                self.simulate_move(targets[0].position.cell, free=True)
                targets[0].position.cell = hero_cell
        elif attacker.entity_id == HeroEnum.RONIN:
            targets = self.room.find_targets([hero_cell + direction])
            if len(targets):
                hit_data = self.room.hit_entities(attacker, targets, Weapon.push(), board_size)
        elif attacker.entity_id == HeroEnum.JUJITSUKA:
            targets = self.room.find_targets([hero_cell - direction])
            blockers = self.room.find_targets([hero_cell + direction])
            if len(targets) and not len(blockers):
                hit_data = self.room.hit_entities(attacker, targets, Weapon.push(), board_size)
        elif attacker.entity_id == HeroEnum.CHAIN_MASTER:
            target1 = self.room.find_targets([hero_cell - direction])
            target2 = self.room.find_targets([hero_cell + direction])
            targets = []
            if len(target1):
                target1[0].position.cell = hero_cell + direction
                targets.append(target1[0])
            if len(target2):
                target2[0].position.cell = hero_cell - direction
                targets.append(target2[0])
        elif attacker.entity_id == HeroEnum.SHADOW:
            single_targets, double_targets, shock_targets = self.room.find_connected_targets([hero_cell + direction],
                                                                                             board_size)
            all_targets: List[int] = single_targets + double_targets + shock_targets
            if direction == 1:
                new_cell = max(all_targets) + 1
            else:
                new_cell = min(all_targets) - 1
            self.simulate_move(new_cell, free=True, dash=True)

        # apply poison, damage, curse etc.
        self.execute_weapon_aftermath(attacker, weapon=None, board_size=board_size, previous_hero_cell=-1,
                                      combo_started=False, hit_data=hit_data)
        return hit_data

    def simulation_signature_move(self,  possible_attack_queues: List[List[Weapon]], board_size: int, free=False):
        if not self.can_execute_signature_move(self.room.hero, board_size, other_direction=False):
            raise PredictionError(f"cannot execute special move")
        simulation = self.clone(possible_attack_queues)
        simulation.execute_signature_move(self.room.hero, board_size)
        return simulation

    def get_attack_queue_plus_immediates(self) -> List[Weapon]:
        potential_weapons = self.room.hero.attack_queue[:]
        # Add all immediates.
        for weapon in self.hero_deck:
            if weapon.tile_effect is None or weapon.tile_effect != WeaponTileEffectEnum.IMMEDIATE:
                continue
            is_in_queue = 0
            number_copies = 0
            for potential in self.hero_deck:
                if potential.is_equal(weapon):
                    number_copies += 1
            for potential in potential_weapons:
                if potential.is_equal(weapon):
                    is_in_queue += 1
            if number_copies > is_in_queue:
                potential_weapons.append(weapon)
        return potential_weapons

    def permutate_possible_attack_queues(self) -> List[List[Weapon]]:
        potential_weapons = self.get_attack_queue_plus_immediates()
        max_queue_length = min(len(potential_weapons), 3)
        possible_queues = [[]]
        # Pick i (from 1 to max) items
        for i in range(max_queue_length):
            possible_queues.extend(itertools.permutations(potential_weapons, i + 1))
        return possible_queues

    def permutate_possible_attack_queues_with_new_weapon(self, new_weapon: Weapon) -> List[List[Weapon]]:
        potential_weapons = self.get_attack_queue_plus_immediates()
        max_queue_length = min(len(potential_weapons), 2)
        possible_queues_without: List[List[Weapon]] = [[]]
        # Pick i (from 1 to max) items
        for i in range(max_queue_length):
            perms = itertools.combinations(potential_weapons, i + 1)
            for perm in perms:
                possible_queues_without.append(perm)
        possible_queues: List[List[Weapon]] = []  # empty one is already here from previous
        for queue in possible_queues_without:
            queue_with = []
            for weapon in queue:
                queue_with.append(weapon)
            queue_with.append(new_weapon)
            perms = itertools.permutations(queue_with, len(queue_with))
            for perm in perms:
                possible_queues.extend(perm)
        return possible_queues

    def simulation_adding_weapon_to_queue(self, weapon: Weapon):
        simulation = self.simulation_wait()
        possible_attack_queues = simulation.permutate_possible_attack_queues_with_new_weapon(weapon)
        print(f"wpn: {weapon.pretty_print()}")
        for paq in possible_attack_queues:
            print(f"paq: {Weapon.pretty_print_list(paq)}")
        simulation.potential_hero_attack_queues = possible_attack_queues
        return simulation

    def simulation_move(self, possible_attack_queues: List[List[Weapon]], new_cell: int, free=False):
        # Are there enemies there? (Specials handled separately!)
        for enemy in self.room.enemies:
            if enemy.position.cell == new_cell:
                return None
        # All good, let's go.
        simulation = self.clone(possible_attack_queues=possible_attack_queues)
        simulation.simulate_move(new_cell, free)
        return simulation

    def simulate_move(self, new_cell: int, free=False, dash=False) -> None:
        # Pass time.
        if not free:
            self.simulate_passing_turn()
        # Pick stuff up.
        if dash:
            direction = 1 if self.room.hero.position.cell - new_cell < 0 else -1
            route = range(self.room.hero.position.cell + direction, new_cell + direction, direction)
        else:
            route = [new_cell]
        for temp_cell in route:
            potions_to_pick_up = []
            if temp_cell in self.room.pickups:
                for pickup_type, total in self.room.pickups[temp_cell].items():
                    if pickup_type == PickupEnum.GOLD:
                        self.game_stats.coins += total
                    else:
                        for i in range(total):
                            potions_to_pick_up.append(pickup_type)
            if PickupEnum.GOLD in self.room.pickups[new_cell]:
                del self.room.pickups[temp_cell][PickupEnum.GOLD]
                if len(self.room.pickups[temp_cell]) == 0:
                    del self.room.pickups[temp_cell]
            MAX_POTIONS = 3  # TODO apply the big bag skill
            if len(potions_to_pick_up) > MAX_POTIONS - len(self.hero_potion_ids):
                # TODO I will worry about those predictions later (DEEEEEP)
                return None
            for potion in potions_to_pick_up:
                self.hero_potion_ids.append(-1)
                if self.room.pickups[temp_cell][potion] > 1:
                    self.room.pickups[temp_cell][potion] -= 1
                else:
                    del self.room.pickups[temp_cell][potion]
                # TODO Add to elixir predictions
                if potion in [PickupEnum.MASS_ICE, PickupEnum.MASS_CURSE, PickupEnum.MASS_POISON,
                              PickupEnum.RAIN_OF_MIRRORS]:
                    self.game_stats.scroll_pickups += 1
                elif potion in [PickupEnum.COOL_UP, PickupEnum.KAMI_BREW]:
                    self.game_stats.potion_pickups += 1
                elif potion == PickupEnum.EDAMAME_BREW:
                    self.game_stats.heal_pickups += 1
                else:
                    raise ValueError(f"Unexpected potion type: {potion.value}")
        # Actually move the hero.
        self.room.hero.position.cell = new_cell

    def simulate_passing_turn(self, skip_attack_queue=False) -> None:
        # "self" is already a simulation at this point
        self.game_stats.turns += 1
        self.room.hero.special_move_cooldown += 1
        if not skip_attack_queue:
            for weapon in self.hero_deck:
                if weapon.cooldown_charge < weapon.cooldown:
                    weapon.cooldown_charge += 1
        for weapon in self.room.hero.attack_queue:
            if weapon.weapon_type == WeaponEnum.BLADE_OF_PATIENCE and weapon.strength < 9:
                weapon.strength += 1

    def simulate_enemies(self) -> None:
        # "self" is already a simulation at this point
        # Moves happen first.
        for enemy in self.room.enemies:
            new_cell = None
            if enemy.enemy_intent.action == EnemyActionEnum.MOVE_RIGHT:
                new_cell = enemy.position.cell + 1
            elif enemy.enemy_intent.action == EnemyActionEnum.MOVE_LEFT:
                new_cell = enemy.position.cell - 1
            elif enemy.enemy_intent.action == EnemyActionEnum.TURN_AROUND:
                enemy.position.flip()
            elif enemy.enemy_intent.action == EnemyActionEnum.TURN_AROUND_BOSS:
                enemy.position.flip()
            if new_cell is not None:
                if self.room.hero.position.cell != new_cell:
                    enemy.position.cell = new_cell
        # Not caring about expanding queue.
        # Attacks happen last. TODO: What is the order?
        for enemy in self.room.enemies:
            if enemy.enemy_intent.action == EnemyActionEnum.EXECUTE_QUEUE:
                # ....?????
                pass
