from typing import List

from data.weapon.weapon import Weapon
from history.potions.history_potions import PotionSimulation


class Predictions:
    potential_hero_attack_queues: List[List[Weapon]]
    potential_hero_decks: List[List[Weapon]]
    combo_started: bool
    summons: int
    enemies_cleared: bool
    new_potions: int
    allow_more_coins: bool
    allow_more_turn_arounds: bool
    potion_simulation: PotionSimulation

    def __init__(self,
                 potential_hero_attack_queues: List[List[Weapon]] = None,
                 potential_hero_decks: List[List[Weapon]] = None,
                 combo_started: bool = None,
                 summons: int = 0,
                 enemies_cleared: bool = False,
                 new_potions: int = 0,
                 allow_more_coins: bool = False,
                 allow_more_turn_arounds: bool = False,
                 potion_simulation: PotionSimulation = None,
                 ):
        self.potential_hero_attack_queues = potential_hero_attack_queues or []
        self.potential_hero_decks = potential_hero_decks or []
        self.combo_started = combo_started
        self.summons = summons
        self.enemies_cleared = enemies_cleared
        self.new_potions = new_potions
        self.allow_more_coins = allow_more_coins
        self.allow_more_turn_arounds = allow_more_turn_arounds
        self.potion_simulation = potion_simulation or PotionSimulation()

    def clone(self):
        # The weapons in here won't be interacted with, so don't need cloning.
        return Predictions(
            potential_hero_attack_queues=self.potential_hero_attack_queues,
            potential_hero_decks=self.potential_hero_decks,
            combo_started=self.combo_started,
            summons=self.summons,
            enemies_cleared=self.enemies_cleared,
            new_potions=self.new_potions,
            allow_more_coins=self.allow_more_coins,
            allow_more_turn_arounds=self.allow_more_turn_arounds,
            potion_simulation=self.potion_simulation,
        )
