from typing import List

from history_battle import BattleHistory
from history_deck import DeckHistory
from history_gold import GoldHistory
from history_map import MapHistory
from history_path import PathHistory
from history_skills import SkillsHistory
from snapshot import Snapshot


class History:
    gold: GoldHistory
    battles: List[BattleHistory]
    deck: DeckHistory
    skills: SkillsHistory
    path: PathHistory
    map: MapHistory

    def __init__(self, first_snapshot: Snapshot):
        self.gold = GoldHistory()
        self.battles = []
        self.deck = DeckHistory(first_snapshot)
        self.skills = SkillsHistory()
        self.path = PathHistory()
        self.map = MapHistory(first_snapshot)
