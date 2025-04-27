from typing import List

from enums import RoomEnum
from weapon import Weapon


class AttackQueueChange:
    weapon: Weapon
    position: int

    def __init__(self, weapon: Weapon, position: int):
        self.weapon = weapon
        self.position = position


class TurnHistory:
    turn_number: int
    hero_turn: bool
    time_taken: int
    weapons_added: List[AttackQueueChange]
    weapons_removed: List[AttackQueueChange]
    weapons_reordered: bool
    attack_queue: List[Weapon]
    attack_queue_executed: bool
    move: int
    turn: bool
    damage_done: int
    friendly_damage_done: int
    enemies_slain: int
    friends_slain: int

    def __init__(self, turn_number: int, hero_turn: bool, attack_queue: List[Weapon]):
        self.turn_number = turn_number
        self.hero_turn = hero_turn
        self.time_taken = 0
        self.weapons_added = []
        self.weapons_removed = []
        self.weapons_reordered = False
        self.attack_queue = attack_queue
        self.attack_queue_executed = False
        self.move = 0
        self.turn = False
        self.damage_done = 0
        self.friendly_damage_done = 0
        self.enemies_slain = 0
        self.friends_slain = 0


class BattleHistory:
    turns: List[TurnHistory]
    room: RoomEnum
    progression: int

    def __init__(self, room: RoomEnum, progression: int):
        self.turns = []
        self.room = room
        self.progression = progression
