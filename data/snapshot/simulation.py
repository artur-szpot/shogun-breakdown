from typing import List, Optional, Dict

from data.entity.construct_entity import EntityConstructor
from data.entity.entity import Entity
from data.entity.entity_enums import EnemyActionEnum, EnemyEnum, HeroEnum, EntityType
from data.entity.hero import Hero
from data.game_stats import GameStats
from data.other_enums import GamePhase
from data.room.room_battle import BattleRoom
from data.room.room_enums import PickupEnum
from data.room.room_reward import RewardRoom
from data.shop.room_shop import ShopRoom
from data.skill.skills import Skill
from data.snapshot.hit_data import HitData
from data.snapshot.permutate_queues import permutate_possible_attack_queues_with_new_weapon
from data.snapshot.prediction_error import PredictionError
from data.snapshot.predictions import Predictions
from data.snapshot.snapshot import Snapshot
from data.weapon.weapon import Weapon
from data.weapon.weapon_enums import WeaponEnum, WeaponAttackEffectEnum
from logger import logger


class Simulation(Snapshot):
    predictions: Predictions

    def __init__(self,
                 skills: List[Skill],
                 game_stats: GameStats,
                 hero_deck: List[Weapon],
                 hero_potion_ids: List[int],
                 game_phase: GamePhase,
                 room: BattleRoom,
                 shop: Optional[ShopRoom] = None,
                 reward: Optional[RewardRoom] = None,
                 predictions: Optional[Predictions] = None):
        super().__init__(
            skills=skills,
            game_stats=game_stats,
            hero_deck=hero_deck,
            hero_potion_ids=hero_potion_ids,
            game_phase=game_phase,
            room=room,
            shop=shop,
            reward=reward,
        )
        self.predictions = predictions or Predictions()

    @staticmethod
    def of(snapshot: Snapshot, predictions: Optional[Predictions] = None):
        return Simulation(
            skills=snapshot.skills,  # can be copied, cannot change during battle
            game_stats=snapshot.game_stats.clone(),  # reconstructed
            hero_deck=[weapon.clone() for weapon in snapshot.hero_deck],  # reconstructed
            hero_potion_ids=snapshot.hero_potion_ids[:],  # reconstructed
            game_phase=snapshot.game_phase,  # can be copied, cannot change during battle
            room=snapshot.room.clone(),  # reconstructed
            shop=snapshot.shop,  # can be copied, cannot change during battle
            reward=snapshot.reward,  # can be copied, cannot change during battle
            predictions=predictions.clone() if predictions is not None else None,
        )

    def clone_simulation(self):
        return Simulation(
            skills=self.skills,  # can be copied, cannot change during battle
            game_stats=self.game_stats.clone(),  # reconstructed
            hero_deck=[weapon.clone() for weapon in self.hero_deck],  # reconstructed
            hero_potion_ids=self.hero_potion_ids[:],  # reconstructed
            game_phase=self.game_phase,  # can be copied, cannot change during battle
            room=self.room.clone(),  # reconstructed
            shop=self.shop,  # can be copied, cannot change during battle
            reward=self.reward,  # can be copied, cannot change during battle
            predictions=self.predictions.clone(),
        )

    # def is_equal(self, other):
    #     return self.game_stats.is_equal(other.game_stats) \
    #            and len(self.hero_deck) == len(other.hero_deck) \
    #            and False not in [self.hero_deck[i].is_equal(other.hero_deck[i]) for i in
    #                              range(len(self.hero_deck))] \
    #            and len(self.hero_potion_ids) == len(other.hero_potion_ids) \
    #            and False not in [self.hero_potion_ids[i] == other.hero_potion_ids[i] for i in
    #                              range(len(self.hero_potion_ids))] \
    #            and self.game_phase == other.game_phase \
    #            and self.room.is_equal(other.room)

    @staticmethod
    def simulation_move_right(snapshot: Snapshot, predictions: Optional[Predictions] = None):
        new_cell = snapshot.room.hero.position.cell + 1
        if not snapshot.room.is_legal_position(new_cell):
            return None
        return Simulation.simulation_move(snapshot, predictions, new_cell)

    @staticmethod
    def simulation_move_left(snapshot: Snapshot, predictions: Optional[Predictions] = None):
        new_cell = snapshot.room.hero.position.cell - 1
        if not snapshot.room.is_legal_position(new_cell):
            return None
        return Simulation.simulation_move(snapshot, predictions, new_cell)

    @staticmethod
    def simulation_move(snapshot: Snapshot, predictions: Optional[Predictions], new_cell: int):
        # Are there enemies there? (Specials handled separately!)
        if len(snapshot.room.find_targets([new_cell])) > 0:
            return None
        # All good, let's go.
        # logger.debug_info(f"BEFORE MOVE SIMULATION - ENEMIES:")
        # for index, enemy in enumerate(snapshot.room.enemies):
        #     logger.debug_text(f"{index}. {enemy.pretty_print()}")
        simulation = Simulation.of(snapshot, predictions)
        # logger.debug_info(f"AFTER MOVE SIMULATION - ENEMIES:")
        # for index, enemy in enumerate(simulation.room.enemies):
        #     logger.debug_text(f"{index}. {enemy.pretty_print()}")
        simulation.simulate_move(simulation.room.hero, new_cell)
        simulation.simulate_passing_turn()
        return simulation

    @staticmethod
    def simulation_turn_around(snapshot: Snapshot, predictions: Optional[Predictions] = None, free=False):
        simulation = Simulation.of(snapshot, predictions)
        if not free:
            simulation.simulate_passing_turn()
        simulation.room.hero.position.flip()
        simulation.game_stats.turn_arounds += 1
        return simulation
        # TODO turn around twice and get hit with a skill

    @staticmethod
    def simulation_wait(snapshot: Snapshot, predictions: Optional[Predictions] = None):
        simulation = Simulation.of(snapshot, predictions)
        simulation.simulate_passing_turn()
        return simulation

    @staticmethod
    def simulation_signature_move(snapshot: Snapshot, predictions: Optional[Predictions] = None):
        simulation = Simulation.of(snapshot, predictions)
        if not simulation.can_execute_signature_move(simulation.room.hero, other_direction=False):
            return None
        simulation.execute_signature_move(simulation.room.hero)
        simulation.simulate_passing_turn()
        return simulation

    @staticmethod
    def simulation_adding_weapon_to_queue(snapshot: Snapshot, weapon: Weapon):
        simulation = Simulation.simulation_wait(snapshot)
        possible_attack_queues = permutate_possible_attack_queues_with_new_weapon(
            attack_queue=simulation.room.hero.attack_queue,
            hero_deck=simulation.hero_deck,
            new_weapon=weapon,
        )
        simulation.predictions.potential_hero_attack_queues = possible_attack_queues
        return simulation

    @staticmethod
    def simulation_execute_queue(snapshot: Snapshot, attack_queue: List[Weapon], previous_hero_cell: int):
        logger.queue_debug_text("")
        logger.queue_debug_text(f"Begin simulation {Weapon.pretty_print_list(attack_queue)}")
        logger.queue_debug_text("")
        # Prepare simulation.
        simulation = Simulation.of(snapshot)
        # Execute the queue.
        attack_queue = [weapon.clone() for weapon in attack_queue]
        for weapon in attack_queue:
            simulation.execute_weapon(
                attacker=simulation.room.hero,
                weapon=weapon,
                previous_hero_cell=previous_hero_cell,
            )
        # Permutate possible deck arrangements after weapon usage.
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
        # Other considerations.
        simulation.room.hero.attack_queue = []
        simulation.simulate_passing_turn(skip_attack_queue=True)
        simulation.predictions.potential_hero_decks = simulated_decks
        return simulation

    def execute_weapon(self, attacker: Entity, weapon: Weapon, previous_hero_cell: int) -> None:
        # SEPARATE LOGIC
        if weapon.weapon_type == WeaponEnum.KUNAI:
            return self.execute_kunai(attacker, weapon, previous_hero_cell)
        elif weapon.weapon_type == WeaponEnum.HOOKBLADE:
            # Sanity check.
            if weapon.strength != weapon.base_strength:
                raise ValueError(f"Hookblade's base strength isn't what I thought. Strength: {weapon.strength} base: {weapon.base_strength}")
            return self.execute_hookblade(attacker, weapon, previous_hero_cell)
        elif weapon.weapon_type == WeaponEnum.METEOR_HAMMER:
            targets = [self.room.get_first_target_space_ahead_in_range(attacker, 3)]
            hit_data = self.room.hit_entities(attacker, targets, weapon)
            if hit_data.targets_hit > 0:
                targets = attacker.position.get_spaces([-1])
                hit_data2 = self.room.hit_entities(attacker, targets, weapon)
                hit_data.merge(hit_data2)
            return self.execute_weapon_aftermath(attacker, weapon, previous_hero_cell, hit_data)
        elif weapon.weapon_type == WeaponEnum.BLAZING_SUISEI:
            targets = [self.room.get_first_target_space_ahead_in_range(attacker, 3)]
            hit_data = self.room.hit_entities(attacker, targets, weapon)
            killed = True in [enemy.hp.hp <= 0 for enemy in self.room.enemies]
            if killed:
                targets = [targets[0] - 1, targets[0] + 1]
                hit_data2 = self.room.hit_entities(attacker, targets, Weapon.explosion())
                hit_data.merge(hit_data2)
            return self.execute_weapon_aftermath(attacker, weapon, previous_hero_cell, hit_data)

        hit_data = HitData.empty()
        attacker_cell = attacker.position.cell
        targets: Optional[List[int]] = None

        # MELEE ATTACKS
        if weapon.weapon_type in [WeaponEnum.KATANA, WeaponEnum.SAI, WeaponEnum.BO, WeaponEnum.TETSUBO,
                                  WeaponEnum.BLADE_OF_PATIENCE, WeaponEnum.DRAGON_PUNCH]:
            targets = attacker.position.get_spaces([1])
        elif weapon.weapon_type == WeaponEnum.SPEAR:
            targets = attacker.position.get_spaces([1, 2])
        elif weapon.weapon_type == WeaponEnum.BACK_STRIKE:
            targets = attacker.position.get_spaces([-1])
        elif weapon.weapon_type in [WeaponEnum.SWIRL, WeaponEnum.TWIN_TESSEN]:
            targets = attacker.position.get_spaces([-1, 1])
        elif weapon.weapon_type == WeaponEnum.NAGIBOKU:
            targets = attacker.position.get_spaces([-2, -1, 1, 2])

        # RANGED ATTACKS
        elif weapon.weapon_type in [WeaponEnum.ARROW, WeaponEnum.SHURIKEN, WeaponEnum.GRAPPLING_HOOK,
                                    WeaponEnum.KI_PUSH, WeaponEnum.TANEGASHIMA]:
            targets = [self.room.get_first_target_space_ahead(attacker)]
        elif weapon.weapon_type == WeaponEnum.MON:
            targets = [self.room.get_first_target_space_ahead(attacker)]
            self.game_stats.coins -= 1
        elif weapon.weapon_type == WeaponEnum.LIGHTINING:
            targets = [self.room.get_last_target_space_ahead(attacker)]
        elif weapon.weapon_type == WeaponEnum.CHAKRAM:
            targets = self.room.get_first_target_spaces_around(attacker)
            weapon.strength = weapon.base_strength
        elif weapon.weapon_type == WeaponEnum.EARTH_IMPALE:
            targets = attacker.position.get_spaces([-2, 2])
        elif weapon.weapon_type == WeaponEnum.SHADOW_KAMA:
            targets = attacker.position.get_spaces([2])
        elif weapon.weapon_type == WeaponEnum.CROSSBOW:
            targets = self.room.get_crossbow_targets_spaces(attacker)
        elif weapon.weapon_type == WeaponEnum.VOLLEY:
            # enemy only! hero is always the target
            targets = [previous_hero_cell]

        # GLOBAL ATTACKS
        elif weapon.weapon_type == WeaponEnum.CORRUPTED_WAVE_LTR:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.CORRUPTED_WAVE_RTL:
            raise PredictionError(f"Cannot simulate using {weapon.weapon_type} yet")
        elif weapon.weapon_type == WeaponEnum.CORRUPTED_EXPLOSION:
            targets = self.room.get_all_targets_cells()
        elif weapon.weapon_type == WeaponEnum.CORRUPTED_BARRAGE:
            targets = self.room.get_all_targets_cells()
        elif weapon.weapon_type == WeaponEnum.SCAR_STRIKE:
            targets = self.room.get_all_hurt_enemies_cells()

        if targets is not None:
            logger.queue_debug_text(f"{attacker.short_print()} attacking cells {targets} with {weapon.short_print()}")
            hit_data = self.room.hit_entities(attacker, targets, weapon, simulate_move=self.simulate_move)
            return self.execute_weapon_aftermath(attacker, weapon, previous_hero_cell, hit_data)

        # MOVE
        elif weapon.weapon_type == WeaponEnum.MIRROR:
            hit_data = self.simulate_swap(attacker, (self.room.board_size - 1) // 2, target_required=False,
                                          flip_targets=True)
        elif weapon.weapon_type == WeaponEnum.DASH:
            target_cell = self.room.get_last_free_space_ahead(attacker)
            hit_data = self.simulate_move(attacker, target_cell, dash=True)
        elif weapon.weapon_type == WeaponEnum.SWAP_TOSS:
            if not self.room.is_edge_space(attacker_cell):
                target1 = self.room.find_targets([attacker_cell - 1])
                target2 = self.room.find_targets([attacker_cell + 1])
                if (not len(target1) or not target1[0].is_heavy()) and (not len(target2) or not target2[0].is_heavy()):
                    if len(target1):
                        hit_data2 = self.simulate_move(target1[0], attacker_cell + 1)
                        hit_data.merge(hit_data2)
                    if len(target2):
                        hit_data2 = self.simulate_move(target2[0], attacker_cell - 1)
                        hit_data.merge(hit_data2)
        elif weapon.weapon_type == WeaponEnum.ORIGIN_OF_SYMMETRY:
            hit_data = self.simulate_swap(attacker, (self.room.board_size - 1) // 2)

        # MOVE AND ATTACK
        elif weapon.weapon_type == WeaponEnum.SHARP_TURN:
            targets = attacker.position.get_spaces([-1, 1])
            hit_data = self.room.hit_entities(attacker, targets, weapon)
            attacker.position.flip()
            if attacker.entity_type == EntityType.HERO:
                self.game_stats.turn_arounds += 1
        elif weapon.weapon_type == WeaponEnum.CHARGE:
            target_cell = self.room.get_last_free_space_ahead(attacker)
            hit_data = self.simulate_move(attacker, target_cell, dash=True)
            if attacker.hp.hp > 0:
                target = attacker.position.get_spaces([1])
                hit_data2 = self.room.hit_entities(attacker, target, weapon)
                hit_data.merge(hit_data2)
        elif weapon.weapon_type in [WeaponEnum.BACK_CHARGE, WeaponEnum.BACK_CHARGE_ALT]:
            target_cell = self.room.get_last_free_space_behind(attacker)
            hit_data = self.simulate_move(attacker, target_cell, dash=True)
            if attacker.hp.hp > 0:
                targets = attacker.position.get_spaces([-1])
                hit_data2 = self.room.hit_entities(attacker, targets, weapon)
                hit_data.merge(hit_data2)
        elif weapon.weapon_type == WeaponEnum.SHADOW_DASH:
            direct_targets, shock_targets = self.room.find_connected_targets(
                attacker,
                [self.room.get_first_target_space_ahead(attacker)],
            )
            all_targets: List[int] = direct_targets + shock_targets
            if attacker.position.facing == 1:
                new_cell = max(all_targets) + 1
            else:
                new_cell = min(all_targets) - 1
            if self.room.is_legal_position(new_cell):
                hit_data = self.simulate_move(attacker, new_cell, dash=True)
                hit_data2 = self.room.hit_entities(attacker, all_targets, weapon)
                hit_data.merge(hit_data2)
        elif weapon.weapon_type == WeaponEnum.BACK_SHADOW_DASH:
            direct_targets, shock_targets = self.room.find_connected_targets(
                attacker,
                [self.room.get_first_target_space_behind(attacker)],
            )
            all_targets: List[int] = direct_targets + shock_targets
            if attacker.position.facing == 1:
                new_cell = min(all_targets) - 1
            else:
                new_cell = max(all_targets) + 1
            if self.room.is_legal_position(new_cell):
                hit_data = self.simulate_move(attacker, new_cell, dash=True)
                hit_data2 = self.room.hit_entities(attacker, all_targets, weapon)
                hit_data.merge(hit_data2)
        elif weapon.weapon_type == WeaponEnum.SMOKE_BOMB:
            target = self.room.get_first_target_space_ahead(attacker)
            target_entity = self.room.find_targets([target])
            if len(target_entity) and not target_entity[0].is_heavy():
                hit_data = self.room.hit_entities(attacker, [target], weapon)
                hit_data2 = self.simulate_swap(attacker, target)
                hit_data.merge(hit_data2)
        elif weapon.weapon_type == WeaponEnum.BACK_SMOKE_BOMB:
            target = self.room.get_first_target_space_behind(attacker)
            target_entity = self.room.find_targets([target])
            if len(target_entity) and not target_entity[0].is_heavy():
                hit_data = self.room.hit_entities(attacker, [target], weapon)
                hit_data2 = self.simulate_swap(attacker, target)
                hit_data.merge(hit_data2)

        # SUMMONS
        elif weapon.weapon_type == WeaponEnum.BOSS_SUMMON:
            self.predictions.summons += 1
            pass
        elif weapon.weapon_type == WeaponEnum.THORNS:
            targets = attacker.position.get_spaces([1])
            target_entity = self.room.find_targets(targets)
            if len(target_entity) or not self.room.is_legal_position(targets[0]):
                pass
            self.room.enemies.append(EntityConstructor.thorns(targets[0]))
        elif weapon.weapon_type == WeaponEnum.TRAP:
            targets = attacker.position.get_spaces([1])
            if not self.room.is_legal_position(targets[0]):
                pass
            self.room.enemies.append(EntityConstructor.trap(targets[0]))

        # OTHER
        elif weapon.weapon_type == WeaponEnum.MAKU:
            # TODO: allow this to happen, ensure this causes "too many enemies" error
            logger.queue_debug_error("Make i.e. scene change, WTF is going to happen?")
            pass
        elif weapon.weapon_type == WeaponEnum.SIGNATURE_MOVE:
            if not attacker.is_hero():
                raise PredictionError("enemies are not allowed to execute signature move")
            hit_data = self.execute_signature_move(attacker)
        elif weapon.weapon_type == WeaponEnum.COPYCAT_MIRROR:
            # We don't care about enemy attack queues
            pass
        elif weapon.weapon_type == WeaponEnum.SHIELD_SELF:
            attacker.state.shield = True
        elif weapon.weapon_type == WeaponEnum.SHIELD_ALLY:
            # Is used at a higher level differently, should never come here.
            raise PredictionError(f"Shielding ally should have been processed elsewhere")
        elif weapon.weapon_type == WeaponEnum.CURSE:
            target = self.room.get_first_target_space_ahead(attacker)
            if target is not None:
                self.room.curse_entities(attacker, [target])

        return self.execute_weapon_aftermath(attacker, weapon, previous_hero_cell, hit_data)

    def execute_weapon_aftermath(self, attacker: Entity, weapon: Optional[Weapon],
                                 previous_hero_cell: int, hit_data: HitData, cause: str = ""):
        # Put weapon on cooldown.
        if weapon is not None:
            logger.queue_debug_text(f"Aftermath of {weapon.pretty_print()}")
            weapon.cooldown_charge = 0
        else:
            logger.queue_debug_text(f"Aftermath of {cause}")

        # Clear out the dead.
        enemies_left = []
        boss_killed = False
        logger.queue_debug_text("cleaning up enemies")
        for enemy in self.room.enemies:
            if enemy.hp.hp > 0:
                logger.queue_debug_text(f"{enemy.short_print()} is OK")
                enemies_left.append(enemy)
            else:
                logger.queue_debug_text(f"{enemy.short_print()} died")
                # Mark boss being killed.
                if enemy.is_boss():
                    boss_killed = True
                # Drop anything.
                loc = enemy.position.get_death_cell()
                if loc not in self.room.pickups:
                    self.room.pickups[loc] = {}
                self.room.pickups[loc][PickupEnum.ANY] = 1
                self.predictions.new_potions += 1
                # Increase strength of Chakrams.
                for queue_weapon in self.room.hero.attack_queue:
                    if queue_weapon.weapon_type == WeaponEnum.CHAKRAM and queue_weapon.strength < 9:
                        queue_weapon.strength += 1
                for deck_weapon in self.hero_deck:
                    if deck_weapon.weapon_type == WeaponEnum.CHAKRAM and deck_weapon.strength < 9:
                        deck_weapon.strength += 1
                # Increase combo.
                if not self.room.is_boss_room():
                    if not self.predictions.combo_started:
                        logger.queue_debug_text("combo started")
                        self.predictions.combo_started = True
                    else:
                        logger.queue_debug_text("combo increased")
                        self.game_stats.combos += 1
                # Increase friendly kills.
                if not attacker.is_hero(): # ?????? and not self.room.is_boss_room():
                    self.game_stats.friendly_kills += 1
                # Spawn Corrupted Progeny.
                if enemy.is_corrupted():
                    logger.queue_debug_text("spawning corrupted progeny")
                    enemies_left.append(enemy.corrupted_progeny())
        self.room.enemies = enemies_left
        if not len(enemies_left) or boss_killed:
            self.predictions.enemies_cleared = True

        # Count the hits.
        self.game_stats.hits += hit_data.hits

        # Perform double attack if applicable.
        if weapon is not None:
            undoubled_weapon = weapon.clone()
            undoubled_weapon.attack_effect = None
            weapon.strength = weapon.base_strength
            if weapon.attack_effect is not None and weapon.attack_effect == WeaponAttackEffectEnum.DOUBLE_STRIKE:
                return self.execute_weapon(attacker, undoubled_weapon, previous_hero_cell)

        logger.queue_debug_text("")

    def execute_kunai(self, attacker: Entity, weapon: Weapon, previous_hero_cell: int) -> None:
        kunai = weapon.kunai()
        kunai_total = weapon.strength
        if weapon.attack_effect is not None:
            if weapon.attack_effect == WeaponAttackEffectEnum.DOUBLE_STRIKE:
                kunai_total *= 2
            else:
                kunai.attack_effect = weapon.attack_effect
        for i in range(kunai_total):
            target = self.room.get_first_target_space_ahead(attacker)
            hit_data = self.room.hit_entities(attacker, [target], kunai)
            self.execute_weapon_aftermath(attacker, kunai, previous_hero_cell, hit_data)

    def execute_hookblade(self, attacker: Entity, weapon: Weapon, previous_hero_cell: int) -> None:
        # Find the target and hit it.
        target_space = self.room.get_first_target_space_ahead(attacker)
        target_entity = self.room.find_targets([target_space])

        # If no target, stop.
        if len(target_entity) == 0:
            return

        # Hit the target and clean up.
        hit_data = self.room.hit_entities(attacker, [target_space], weapon, self.simulate_move)
        self.execute_weapon_aftermath(attacker, weapon, previous_hero_cell, hit_data)

        # If the target died, move.
        target_entity = self.room.find_targets([target_space])
        if len(target_entity) == 0:
            self.simulate_move(attacker, target_space)
            # If there's strength left, continue attacking.
            if weapon.strength > 0:
                updated_hookblade = weapon.clone()
                updated_hookblade.strength -= 1
                return self.execute_hookblade(attacker, updated_hookblade, previous_hero_cell)
            else:
                if weapon.is_double_strike():
                    updated_hookblade = weapon.clone()
                    updated_hookblade.strength = updated_hookblade.base_strength
                    updated_hookblade.attack_effect = None
                    return self.execute_hookblade(attacker, updated_hookblade, previous_hero_cell)

    def can_execute_signature_move(self, hero: Hero, other_direction=False) -> bool:
        if not hero.is_hero():
            return False
        direction = hero.position.get_direction() * (-1 if other_direction else 1)
        hero_cell = hero.position.cell
        if hero.hero_id == HeroEnum.WANDERER:
            targets = self.room.find_targets([hero_cell + direction])
            return len(targets) > 0 and not targets[0].is_heavy()
        elif hero.hero_id == HeroEnum.RONIN:
            if self.room.is_edge_space(hero_cell + direction):
                return False
            targets = self.room.find_targets([hero_cell + direction])
            return len(targets) > 0 and not targets[0].is_heavy()
        elif hero.hero_id == HeroEnum.JUJITSUKA:
            targets = self.room.find_targets([hero_cell - direction])
            blockers = self.room.find_targets([hero_cell + direction])
            return len(targets) and not len(blockers) and not targets[0].is_heavy()
        elif hero.hero_id == HeroEnum.CHAIN_MASTER:
            if self.room.is_edge_space(hero_cell):
                return False
            targets = self.room.find_targets([hero_cell - direction, hero_cell + direction])
            return len(targets) > 0 and True not in [t.is_heavy() for t in targets]
        elif hero.hero_id == HeroEnum.SHADOW:
            direct_targets, shock_targets = self.room.find_connected_targets(hero, [hero_cell + direction])
            all_targets: List[int] = direct_targets + shock_targets
            if not len(all_targets):
                return False
            if direction == 1:
                new_cell = max(all_targets) + 1
            else:
                new_cell = min(all_targets) - 1
            return self.room.is_legal_position(new_cell)
        else:
            raise ValueError(f"Unexpected hero to execute signature move: {hero.hero_id}")

    def execute_signature_move(self, hero: Hero, other_direction=False) -> HitData:
        if not hero.is_hero():
            raise ValueError(f"Non-hero entity {hero.pretty_print()} trying to perform signature move")
        if not self.can_execute_signature_move(hero, other_direction):
            return HitData.empty()
        direction = hero.position.get_direction() * (-1 if other_direction else 1)
        hero_cell = hero.position.cell
        logger.queue_debug_text(
            f"{hero.short_print()} in cell {hero.position.cell} executing in direction {direction}")
        targets = []
        hit_data = HitData.empty()
        if hero.hero_id == HeroEnum.WANDERER:
            targets = self.room.find_targets([hero_cell + direction])
            if len(targets):
                self.simulate_move(self.room.hero, targets[0].position.cell)
                self.simulate_move(targets[0], hero_cell)
        elif hero.hero_id == HeroEnum.RONIN:
            targets = self.room.find_targets([hero_cell + direction])
            if len(targets):
                hit_data = self.room.hit_entities(hero, [hero_cell + direction], Weapon.push(),
                                                  simulate_move=self.simulate_move)
        elif hero.hero_id == HeroEnum.JUJITSUKA:
            targets = self.room.find_targets([hero_cell - direction])
            if len(targets):
                self.simulate_move(targets[0], hero_cell + direction)
                if targets[0].hp.hp > 0:
                    hit_data = self.room.hit_entities(hero, [hero_cell + direction], Weapon.push(),
                                                      simulate_move=self.simulate_move)
        elif hero.hero_id == HeroEnum.CHAIN_MASTER:
            target1 = self.room.find_targets([hero_cell - direction])
            target2 = self.room.find_targets([hero_cell + direction])
            targets = []
            hit_data = HitData.empty()
            if len(target1):
                hit_data2 = self.simulate_move(target1[0], hero_cell + direction)
                hit_data.merge(hit_data2)
                targets.append(target1[0])
            if len(target2):
                hit_data2 = self.simulate_move(target2[0], hero_cell - direction)
                hit_data.merge(hit_data2)
                targets.append(target2[0])
        elif hero.hero_id == HeroEnum.SHADOW:
            direct_targets, shock_targets = self.room.find_connected_targets(hero, [hero_cell + direction])
            all_targets: List[int] = direct_targets + shock_targets
            if direction == 1:
                new_cell = max(all_targets) + 1
            else:
                new_cell = min(all_targets) - 1
            self.simulate_move(self.room.hero, new_cell, dash=True)

        # apply poison, damage, curse etc.
        self.execute_weapon_aftermath(hero, weapon=None, previous_hero_cell=-1, hit_data=hit_data,
                                      cause="signature move")
        return hit_data

    def simulate_move(self, mover: Entity, new_cell: int, dash=False) -> HitData:
        hit_data = HitData.empty()
        # Pick stuff up.
        if dash:
            direction = 1 if mover.position.cell - new_cell < 0 else -1
            route = range(mover.position.cell + direction, new_cell + direction, direction)
        else:
            route = [new_cell]
        for temp_cell in route:
            if mover.is_hero():
                if temp_cell in self.room.pickups:
                    updated_pickups = self.simulate_pickups(self.room.pickups[temp_cell])
                    if updated_pickups is None:
                        del self.room.pickups[temp_cell]
                    else:
                        self.room.pickups[temp_cell] = updated_pickups
                        if PickupEnum.GOLD in self.room.pickups[temp_cell]:
                            del self.room.pickups[temp_cell][PickupEnum.GOLD]
                            if len(self.room.pickups[temp_cell]) == 0:
                                del self.room.pickups[temp_cell]
            elif mover.hp.hp > 0:
                for enemy in self.room.enemies:
                    if enemy.enemy_id == EnemyEnum.TRAP:
                        # TODO where is trap damage stored
                        logger.queue_debug_text(f"I should learn this earlier but trap is {enemy.pretty_print()}")
                        enemy.hp.hp = 0  # hopefully this is a good way to clear the trap
                        hit_data = self.room.hit_entities(self.room.hero, [mover.position.cell], Weapon.trap(3))
        # Actually move.
        mover.position.cell = new_cell
        return hit_data

    def simulate_pickups(self, pickups: Dict[PickupEnum, int]) -> Optional[Dict[PickupEnum, int]]:
        potions_to_pick_up = []
        for pickup_type, total in pickups.items():
            if pickup_type == PickupEnum.GOLD:
                self.game_stats.coins += total
            else:
                for i in range(total):
                    potions_to_pick_up.append(pickup_type)
        MAX_POTIONS = 3  # TODO apply the big bag skill
        if len(potions_to_pick_up) > MAX_POTIONS - len(self.hero_potion_ids):
            # TODO I will worry about those predictions later (DEEEEEP)
            return pickups
        for potion in potions_to_pick_up:
            self.hero_potion_ids.append(-2 if potion == PickupEnum.ANY else -1)
            if pickups[potion] > 1:
                pickups[potion] -= 1
            else:
                del pickups[potion]
            # TODO Add to elixir predictions
            if potion in [PickupEnum.MASS_ICE, PickupEnum.MASS_CURSE, PickupEnum.MASS_POISON,
                          PickupEnum.RAIN_OF_MIRRORS]:
                # self.game_stats.scroll_pickups -= 1
                # TURNS OUT THESE ARE ROOM TOTALS OF WHAT'S DROPPED
                pass
            elif potion in [PickupEnum.COOL_UP, PickupEnum.KAMI_BREW, PickupEnum.LUCKY_DIE]:
                # self.game_stats.potion_pickups -= 1
                pass
            elif potion == PickupEnum.EDAMAME_BREW:
                # self.game_stats.heal_pickups -= 1
                pass
            elif potion == PickupEnum.ANY:
                # simulate picking up anything
                pass
            else:
                raise ValueError(f"Unexpected potion type: {potion.value}")
        return pickups if len(pickups) else None

    def simulate_swap(self, attacker: Entity, target_cell: int, target_required=True,
                      flip_targets=False) -> HitData:
        target = self.room.find_targets([target_cell])[0]
        if target is None and target_required:
            return HitData.empty()
        if target is not None and target.is_heavy():
            return HitData.empty()
        attacker_cell = attacker.position.cell
        hit_data = self.simulate_move(attacker, target_cell, dash=False)
        if flip_targets:
            attacker.position.flip()
            if attacker.is_hero():
                self.game_stats.turn_arounds += 1
        if target is not None:
            hit_data2 = self.simulate_move(target, attacker_cell, dash=False)
            hit_data.merge(hit_data2)
            if flip_targets:
                target.position.flip()
                if target.is_hero():
                    self.game_stats.turn_arounds += 1
        return hit_data

    def simulate_passing_turn(self, skip_attack_queue=False) -> None:
        # "self" is already a simulation at this point
        self.game_stats.turns += 1
        self.room.hero.special_move_cooldown += 1
        self.room.hero.state.pass_turn()
        if not skip_attack_queue:
            for weapon in self.hero_deck:
                if weapon.cooldown_charge < weapon.cooldown:
                    weapon.cooldown_charge += 1
        for weapon in self.room.hero.attack_queue:
            if weapon.weapon_type == WeaponEnum.BLADE_OF_PATIENCE and weapon.strength < 9:
                weapon.strength += 1

    def simulate_enemies(self, previous_hero_cell: int):
        # "self" is already a simulation at this point
        # Poisons happen first!
        for enemy in self.room.enemies:
            if enemy.state.poison > 0:
                enemy.hit(Weapon.poison_tick())
            enemy.state.pass_turn()
        self.execute_weapon_aftermath(
            attacker=self.room.hero,
            weapon=None,
            previous_hero_cell=previous_hero_cell,
            hit_data=HitData.empty(),
            cause="enemies poison cleanup"
        )
        # Moves happen first.
        for enemy in self.room.enemies:
            if enemy.state.ice > 0:
                continue
            new_cell = None
            if enemy.action == EnemyActionEnum.MOVE_RIGHT:
                logger.queue_debug_text(f"MOVE {enemy.pretty_print()}")
                new_cell = enemy.position.cell + 1
            elif enemy.action == EnemyActionEnum.MOVE_LEFT:
                logger.queue_debug_text(f"MOVE {enemy.pretty_print()}")
                new_cell = enemy.position.cell - 1
            elif enemy.action == EnemyActionEnum.TURN_AROUND:
                logger.queue_debug_text(f"TURN {enemy.pretty_print()}")
                enemy.position.flip()
            elif enemy.action == EnemyActionEnum.TURN_AROUND_BOSS:
                logger.queue_debug_text(f"TURN_BOSS {enemy.pretty_print()}")
                enemy.position.flip()
            if new_cell is not None:
                if self.room.is_legal_position(new_cell) and len(self.room.find_targets([new_cell])) == 0:
                    self.simulate_move(enemy, new_cell)
        # Not caring about expanding queue.
        # Attacks happen last.
        enemies_that_attack = []
        for enemy in self.room.enemies:
            if enemy.action == EnemyActionEnum.EXECUTE_QUEUE:
                if enemy.state.ice == 0:
                    enemies_that_attack.append(enemy)
        if len(enemies_that_attack) <= 1:
            logger.queue_debug_text(f"Only {len(enemies_that_attack)} enemies want to attack")
            for enemy in enemies_that_attack:
                if enemy.hp.hp <= 0:
                    continue
                logger.queue_debug_text(f"MOVE {enemy.pretty_print()}")
                for weapon in enemy.attack_queue:
                    if weapon.weapon_type == WeaponEnum.SHIELD_ALLY:
                        # TODO return several possibilities
                        pass
                    else:
                        self.execute_weapon(
                            attacker=enemy,
                            weapon=weapon,
                            previous_hero_cell=previous_hero_cell,
                        )
            return {"": self}
        logger.queue_debug_text(f"{len(enemies_that_attack)} enemies want to attack!!!")
        simulation_modes = {
            "file_order": [enemy.clone() for enemy in enemies_that_attack],
            "left_to_right": [],
            "right_to_left": [],
        }
        for i in range(self.room.board_size):
            for enemy in enemies_that_attack:
                if enemy.position.cell == i:
                    simulation_modes["left_to_right"].append(enemy.clone())
                elif enemy.position.cell == self.room.board_size - i - 1:
                    simulation_modes["right_to_left"].append(enemy.clone())
        simulations = {}
        for name, order in simulation_modes.items():
            simulation = self.clone_simulation()
            for enemy in order:
                for weapon in enemy.attack_queue:
                    if weapon.weapon_type == WeaponEnum.SHIELD_ALLY:
                        # TODO return several possibilities
                        pass
                    else:
                        simulation.execute_weapon(
                            attacker=enemy,
                            weapon=weapon,
                            previous_hero_cell=previous_hero_cell,
                        )
            simulations[name] = simulation
        return simulations
