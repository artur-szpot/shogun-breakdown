from itertools import permutations, combinations
from typing import List

from data.weapon.weapon import Weapon


def get_attack_queue_plus_immediates(attack_queue: List[Weapon], hero_deck: List[Weapon]) -> List[Weapon]:
    potential_weapons = attack_queue[:]
    # Add all immediates.
    for weapon in hero_deck:
        if not weapon.is_immediate():
            continue
        is_in_queue = 0
        number_copies = 0
        for potential in hero_deck:
            if potential.is_equal(weapon):
                number_copies += 1
        for potential in potential_weapons:
            if potential.is_equal(weapon):
                is_in_queue += 1
        if number_copies > is_in_queue:
            potential_weapons.append(weapon)
    return potential_weapons


def permutate_possible_attack_queues(attack_queue: List[Weapon], hero_deck: List[Weapon]) -> List[List[Weapon]]:
    potential_weapons = get_attack_queue_plus_immediates(attack_queue, hero_deck)
    max_queue_length = min(len(potential_weapons), 3)
    possible_queues = [[]]
    # Pick i (from 1 to max) items
    for i in range(max_queue_length):
        possible_queues.extend(permutations(potential_weapons, i + 1))
    return possible_queues


def permutate_possible_attack_queues_with_new_weapon(attack_queue: List[Weapon], hero_deck: List[Weapon],
                                                     new_weapon: Weapon) -> List[List[Weapon]]:
    potential_weapons = get_attack_queue_plus_immediates(attack_queue, hero_deck)
    max_queue_length = min(len(potential_weapons), 2)
    possible_queues_without: List[List[Weapon]] = [[]]
    # Pick i (from 1 to max) items
    for i in range(max_queue_length):
        perms = combinations(potential_weapons, i + 1)
        for perm in perms:
            possible_queues_without.append(perm)
    possible_queues: List[List[Weapon]] = []  # empty one is already here from previous
    for queue in possible_queues_without:
        queue_with = []
        for weapon in queue:
            queue_with.append(weapon)
        queue_with.append(new_weapon)
        perms = permutations(queue_with, len(queue_with))
        for perm in perms:
            possible_queues.append(perm)
    return possible_queues
