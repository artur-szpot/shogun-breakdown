from typing import List

from data.snapshot.snapshot import Snapshot
from history.history_battle import BattleHistory
from history.history_deck import DeckHistory
from history.history_gold import GoldHistory
from history.history_map import MapHistory
from history.history_path import PathHistory
from history.history_potions import PotionHistory
from history.history_skills import SkillsHistory


class History:
    gold: GoldHistory
    battles: List[BattleHistory]
    deck: DeckHistory
    skills: SkillsHistory
    path: PathHistory
    map: MapHistory
    potions: PotionHistory
    simulations: List[Snapshot]

    def __init__(self, first_snapshot: Snapshot):
        self.gold = GoldHistory()
        self.battles = []
        self.deck = DeckHistory(first_snapshot)
        self.skills = SkillsHistory()
        self.path = PathHistory()
        self.map = MapHistory(first_snapshot)
        self.potions = PotionHistory(first_snapshot)
        self.simulations = []
        self.board_size = first_snapshot.room.hero.position.cell * 2 + 1
