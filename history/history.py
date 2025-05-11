from typing import Dict
from typing import List

from history.history_battle import BattleHistory
from history.history_deck import DeckHistory
from history.history_gold import GoldHistory
from history.history_map import MapHistory
from history.history_potions import PotionHistory
from history.history_room import RoomHistory
from history.history_skills import SkillsHistory


class History:
    gold: GoldHistory
    battles: List[BattleHistory]
    room: RoomHistory
    deck: DeckHistory
    skills: SkillsHistory
    map: MapHistory
    potions: PotionHistory

    def __init__(self, first_snapshot, map_history: Dict):
        self.gold = GoldHistory()
        self.battles = []
        self.deck = DeckHistory(first_snapshot)
        self.skills = SkillsHistory()
        self.map = MapHistory(map_history)
        self.potions = PotionHistory(first_snapshot)
        self.room = RoomHistory()

    def clone(self, snapshot):
        # TODO actually implement this (or is there even any need?)
        history = History(snapshot, {})
        history.room.traps = self.room.traps.copy()
        history.room.corrupted_waves = [wave.clone() for wave in self.room.corrupted_waves]
        history.room.bombs = self.room.bombs.copy()
        history.room.thorns = {cell: weapon.clone() for cell, weapon in self.room.thorns.items()}
        history.potions = self.potions.clone()
        return history
