from itertools import combinations, combinations_with_replacement
from typing import Dict, List, Tuple, Set

from data.mappers import pickup_name_mapper
from data.room.room_enums import PickupEnum
from history.potions.potion_simulation import PotionSimulation
from history.potions.potion_snapshot import PotionSnapshot
from logger import logger


class PotionHistory:
    # Save what is known about which potion is which.
    current_guess_matrix: Dict[int, List[PickupEnum]] = {}
    # Queue information to make certain.
    assured_guess_queue: List[Tuple[int, PickupEnum]] = []

    def __init__(self, first_snapshot=None):
        if first_snapshot is not None:
            all_types = [
                PickupEnum.EDAMAME_BREW,
                PickupEnum.COOL_UP,
                PickupEnum.KAMI_BREW,
                PickupEnum.LUCKY_DIE,
                PickupEnum.MASS_CURSE,
                PickupEnum.MASS_ICE,
                PickupEnum.MASS_POISON,
                PickupEnum.RAIN_OF_MIRRORS,
            ]
            for potion_id in first_snapshot.hero_potion_ids:
                self.current_guess_matrix[potion_id] = all_types

    def clone(self):
        retval = PotionHistory()
        retval.current_guess_matrix = self.current_guess_matrix.copy()
        return retval

    def potion_update(self, previous_snapshot: PotionSnapshot, new_snapshot: PotionSnapshot,
                      selling_allowed: bool) -> List[PotionSimulation]:
        # Certain: how many were dropped.
        # TODO uncertain: does shop drop increase those totals
        total_new_drops = new_snapshot.total_dropped() - previous_snapshot.total_dropped()

        # Certain: what lay on the ground and no longer does was picked up.
        # Certain: what didn't lie on the ground and now does was just dropped.
        # Certain: the picked up stuff could have been used if place was freed to pick it up
        #          WHILE STAYING IN PLACE.
        # Certain: the new drops could not have been used, even if they were picked up.
        # Certain: the difference between types' increase and what's left on the ground is exactly
        #          what has been picked up (other than first certain point here).
        previous_ground = previous_snapshot.ground_potions
        new_ground = new_snapshot.ground_potions

        certain_picked_up_potions = []
        certain_picked_up_potion_types = []
        for cell, items in previous_ground.items():
            for pid, total in items.items():
                if pid == PickupEnum.GOLD:
                    continue
                if cell not in new_ground or pid not in new_ground[cell]:
                    certain_picked_up_potions.extend([pid] * total)
                    certain_picked_up_potion_types.append(pid)
                elif new_ground[cell][pid] < total:
                    certain_picked_up_potions.extend([pid] * (total - new_ground[cell][pid]))
                    certain_picked_up_potion_types.append(pid)

        certain_drops = []
        for cell, items in new_ground.items():
            for pid, total in items.items():
                if pid == PickupEnum.GOLD:
                    continue
                if cell not in previous_ground or pid not in previous_ground[cell]:
                    certain_drops.extend([pid] * total)
                elif previous_ground[cell][pid] < total:
                    certain_drops.extend([pid] * (total - previous_ground[cell][pid]))

        uncertain_picked_up_potions = []

        if len(certain_drops) > total_new_drops:
            raise ValueError(f"Wrong number of certain drops: {len(certain_drops)} vs expected total {total_new_drops}")

        # If not equal, let's find out what's what.
        elif len(certain_drops) < total_new_drops:
            dropped_scrolls = new_snapshot.total_scrolls_dropped - previous_snapshot.total_scrolls_dropped
            dropped_potions = new_snapshot.total_potions_dropped - previous_snapshot.total_potions_dropped
            dropped_heals = new_snapshot.total_heals_dropped - previous_snapshot.total_heals_dropped
            # Subtract what we know has been dropped.
            for drop in certain_drops:
                if drop == PickupEnum.EDAMAME_BREW:
                    dropped_heals -= 1
                elif drop in [PickupEnum.KAMI_BREW, PickupEnum.LUCKY_DIE, PickupEnum.COOL_UP]:
                    dropped_potions -= 1
                else:
                    dropped_scrolls -= 1
            # The rest must have been picked up.
            for i in range(dropped_scrolls):
                uncertain_picked_up_potions.append(
                    [PickupEnum.MASS_CURSE, PickupEnum.MASS_ICE, PickupEnum.RAIN_OF_MIRRORS, PickupEnum.MASS_POISON])
            for i in range(dropped_potions):
                uncertain_picked_up_potions.append([PickupEnum.COOL_UP, PickupEnum.KAMI_BREW, PickupEnum.LUCKY_DIE])
            for i in range(dropped_heals):
                certain_picked_up_potions.append(PickupEnum.EDAMAME_BREW)
                if PickupEnum.EDAMAME_BREW not in certain_picked_up_potion_types:
                    certain_picked_up_potion_types.append(PickupEnum.EDAMAME_BREW)

        # Certain: what was had PLUS what was picked up MINUS what is left is exactly what has been used/sold.
        # Certain: how many were used.
        potions_used_total = new_snapshot.total_used - previous_snapshot.total_used
        # Certain: how many were sold.
        potions_sold_total = len(previous_snapshot.potions_ids) + len(certain_picked_up_potions) \
                             + len(uncertain_picked_up_potions) - potions_used_total \
                             - len(new_snapshot.potions_ids)
        if potions_sold_total and not selling_allowed:
            raise ValueError(f"Selling potions is not allowed at this time, yet {potions_sold_total} were sold")

        previous_totals = previous_snapshot.id_totals()
        new_totals = new_snapshot.id_totals()

        # Certain: if an id was there and no longer is, that potion must have been used/sold.
        # These together are the previous IDs.
        certain_lost_ids = []
        certain_remaining_ids = []
        certain_remaining_ids_set = []
        for pid, total in previous_totals.items():
            if pid not in new_totals:
                certain_lost_ids.extend([pid] * total)
            else:
                if new_totals[pid] < total:
                    certain_lost_ids.extend([pid] * (total - new_totals[pid]))
                if new_totals[pid]:
                    certain_remaining_ids.extend([pid] * min(new_totals[pid], total))
                    certain_remaining_ids_set.append(pid)
        if len(certain_remaining_ids) + len(certain_lost_ids) != len(previous_snapshot.potions_ids):
            raise ValueError(f"The number of lost and remaining potion IDs must equal previous snapshot.")

        # Certain: if an id was not there and now is, that potion must have been picked up.
        certain_new_ids = []
        for pid, total in new_totals.items():
            if pid not in previous_totals:
                certain_new_ids.extend([pid] * total)
            elif previous_totals[pid] < total:
                certain_new_ids.extend([pid] * (total - previous_totals[pid]))

        # Certain ends here.

        # Prepare guesses for new pickups.
        # Dream: 1 pickup of certain type.
        if len(certain_picked_up_potions) == 1 \
                and len(uncertain_picked_up_potions) == 0 \
                and len(certain_new_ids) == 1:
            self.assured_guess(certain_new_ids[0], certain_picked_up_potions[0])
        # Dream2: 1 known type of pickup.
        elif len(certain_picked_up_potion_types) == 1 \
                and len(uncertain_picked_up_potions) == 0:
            # Dream: ID is new.
            if len(certain_new_ids) > 0:
                self.assured_guess(certain_new_ids[0], certain_picked_up_potions[0])
            # Less ideal: ID is old.
            else:
                self.reduce_guesses_new_certain(certain_picked_up_potions[0])
        # Getting real: more than one pickup type.
        elif len(certain_picked_up_potion_types) + len(uncertain_picked_up_potions) > 0:
            possible_types = certain_picked_up_potion_types[:]
            for uncertain in uncertain_picked_up_potions:
                for potion_type in uncertain:
                    if potion_type not in possible_types:
                        possible_types.append(potion_type)
            # For old IDs, nothing learned unless only 1 was uncertain.
            self.reduce_guesses_if_single_uncertain(possible_types)
            # Each certain new ID may be any of the picked up types.
            for new_id in certain_new_ids:
                self.broad_guess(new_id, possible_types)

        # Print out the new knowledge.
        logger.debug_info("POTIONS:")
        for potion_id in new_snapshot.potions_ids:
            logger.debug_info(
                f"{potion_id} ({'/'.join(pickup_name_mapper[t] for t in self.current_guess_matrix[potion_id])})")

        # Prepare scenarios for possible combinations of used/sold potions.

        # PCIKUPS CANNOT BE USED OR SOLD!
        # Certain: what was sold must have been present in previous snapshot.
        # If nothing was picked up, the certain lost IDs are what was sold/used.
        # Otherwise, the certain lost IDs are certain and the rest must come from certain remaining.
        potions_lost_total = potions_used_total + potions_sold_total

        if potions_lost_total == 0:
            return [PotionSimulation()]

        uncertain_lost_ids_total = potions_lost_total - len(certain_lost_ids)
        possible_lost_ids_pools: List[List[int]] = []
        # Permutate which those could have been.
        perms = combinations_with_replacement(certain_remaining_ids_set, uncertain_lost_ids_total)
        for perm in perms:
            new_pool = certain_lost_ids + [x for x in perm]
            if len(new_pool) != potions_lost_total:
                raise ValueError(f"Pool of lost potions has wrong length - expected {potions_lost_total}, "
                                 f"got {len(new_pool)}")
            possible_lost_ids_pools.append(new_pool)
        # Divvy up the IDs between sales and drinks.
        indices = [i for i in range(potions_used_total + potions_sold_total)]
        possible_sold_indices = combinations(indices, potions_sold_total)
        # The pools are guaranteed to be unique, but the choices from them can repeat, hence the need to hash them.
        possible_loss_scenarios: Dict[str, Tuple[List[int], List[int]]] = {}
        for pool in possible_lost_ids_pools:
            for sales_scenario in possible_sold_indices:
                sold = []
                used = []
                for i in range(potions_lost_total):
                    if i in sales_scenario:
                        sold.append(pool[i])
                    else:
                        used.append(pool[i])
                loss_hash = f"s{''.join(str(x) for x in sold)}u{''.join(str(x) for x in used)}"
                if loss_hash not in possible_loss_scenarios:
                    possible_loss_scenarios[loss_hash] = (sold, used)

        # Since the guesses are in certain terms, reduce the guesses into all possible scenarios.
        ids_to_simulate = previous_totals.keys()
        type_simulations: List[Dict[int, PickupEnum]] = []
        # Simulate each ID in turn.
        for simulated_id in ids_to_simulate:
            new_simulations: List[Dict[int, PickupEnum]] = []
            # If no simulations made yet (first ID being simulated), just simulate the possibilites.
            if not len(type_simulations):
                for possible_type in self.current_guess_matrix[simulated_id]:
                    new_simulations.append({simulated_id: possible_type})
            # Otherwise, add a new possible simulation for every existing previous guess.
            else:
                for previous_simulation in type_simulations:
                    ruled_out_types = previous_simulation.values()
                    for possible_type in self.current_guess_matrix[simulated_id]:
                        # If all possible types were used before, simulating ends here.
                        if possible_type not in ruled_out_types:
                            new_simulation = previous_simulation.copy()
                            new_simulation[simulated_id] = possible_type
                            new_simulations.append(new_simulation)
            type_simulations = new_simulations

        # Permutate possible loss scenarios by possible type scenarios.
        simulations = []
        for sold, used in possible_loss_scenarios.values():
            done_scenario_hashes = set()
            for type_scenario in type_simulations:
                _sold = [type_scenario[i] for i in sold]
                _used = [type_scenario[i] for i in used]
                done_scenario_hash = f"s{''.join(str(x.value) for x in set(_sold))}" \
                                     f"u{''.join(str(x.value) for x in set(_used))}"
                if done_scenario_hash in done_scenario_hashes:
                    continue
                simulation = PotionSimulation(sold, _sold, used, _used)
                simulations.append(simulation)
                done_scenario_hashes.add(done_scenario_hash)
        logger.debug_info(f"POTION SIMULATIONS: {len(simulations)}")
        return simulations

    def assured_guess(self, potion_id: int, potion_type: PickupEnum) -> None:
        logger.debug_info(f"Now certain that {potion_id} is {pickup_name_mapper[potion_type]}")
        if potion_id in self.current_guess_matrix:
            if len(self.current_guess_matrix[potion_id]) == 1:
                # We already knew that.
                if potion_type != self.current_guess_matrix[potion_id][0]:
                    raise ValueError(f"Wrong assumption made for ID {potion_id} - was "
                                     f"{pickup_name_mapper[self.current_guess_matrix[potion_id][0]]}, is " +
                                     pickup_name_mapper[potion_type])
                return

        # Mark the new knowledge.
        self.current_guess_matrix[potion_id] = [potion_type]

        # Apply the finding to other IDs.
        for p_id, guessed_types in self.current_guess_matrix.items():
            if p_id != potion_id:
                if potion_type in guessed_types:
                    guessed_types.remove(potion_type)
                    if len(guessed_types) == 1:
                        # New certain guess made, apply it afterwards.
                        self.assured_guess_queue.append((p_id, guessed_types[0]))

        # Run through the queue.
        if len(self.assured_guess_queue):
            next_assured_guess = self.assured_guess_queue.pop()
            self.assured_guess(next_assured_guess[0], next_assured_guess[1])

    def broad_guess(self, potion_id: int, potion_types: List[PickupEnum]) -> None:
        if potion_id in self.current_guess_matrix:
            # Refine the guess.
            new_guesses = []
            for guess in self.current_guess_matrix[potion_id]:
                if guess in potion_types:
                    new_guesses.append(guess)
            if len(new_guesses) == 1:
                self.assured_guess(potion_id, new_guesses[0])
            else:
                self.current_guess_matrix[potion_id] = new_guesses
            return

        # Rule out the assuredly mapped types.
        sure_types = []
        for guesses in self.current_guess_matrix.values():
            if len(guesses) == 1:
                sure_types.append(guesses[0])
        possible_types_left = []
        for potion_type in potion_types:
            if potion_type not in sure_types:
                possible_types_left.append(potion_type)

        # If this leaves only one possibility, hurray!
        if len(possible_types_left) == 1:
            return self.assured_guess(potion_id, possible_types_left[0])

        # Otherwise, make the vague guess.
        self.current_guess_matrix[potion_id] = possible_types_left

    def reduce_guesses_new_certain(self, potion_type: PickupEnum) -> None:
        logger.debug_info(f"Now certain that one of the IDs is {pickup_name_mapper[potion_type]}")
        for potion_id, possible_types in self.current_guess_matrix.items():
            if len(self.current_guess_matrix[potion_id]) == 1 \
                    and self.current_guess_matrix[potion_id][0] == potion_type:
                # We already knew that.
                if potion_type != self.current_guess_matrix[potion_id][0]:
                    raise ValueError(f"Wrong assumption made for ID {potion_id} - was "
                                     f"{pickup_name_mapper[self.current_guess_matrix[potion_id][0]]}, is " +
                                     pickup_name_mapper[potion_type])
                return

        # If there is only one candidate, the type is certain.
        # Otherwise, nothing learned, sadly.
        possible_ids = []
        for p_id, guessed_types in self.current_guess_matrix.items():
            if potion_type in guessed_types:
                possible_ids.append(p_id)
        if len(possible_ids) == 1:
            self.assured_guess(possible_ids[0], potion_type)

    def reduce_guesses_if_single_uncertain(self, potion_types: List[PickupEnum]) -> None:
        # If there is only one unsure guess, reduce it down to the allowed types.
        # Otherwise, nothing learned, sadly.
        possible_ids = []
        for p_id, guessed_types in self.current_guess_matrix.items():
            if len(guessed_types) > 1:
                possible_ids.append(p_id)
        if len(possible_ids) == 1:
            new_guesses = []
            for guess in self.current_guess_matrix[possible_ids[0]]:
                if guess in potion_types:
                    new_guesses.append(guess)
            if len(new_guesses) == 1:
                self.assured_guess(possible_ids[0], new_guesses[0])
            else:
                self.current_guess_matrix[possible_ids[0]] = new_guesses

    def confirmed_guesses(self, guesses: List[Dict[int, PickupEnum]]) -> None:
        reduced_guesses: Dict[int, Set[PickupEnum]] = {}
        for guess in guesses:
            for potion_id, potion_type in guess.items():
                if potion_id not in reduced_guesses:
                    reduced_guesses[potion_id] = set()
                reduced_guesses[potion_id].add(potion_type)
        for potion_id, possible_types in reduced_guesses:
            self.broad_guess(potion_id, possible_types)
