import base64
import json
from json import JSONDecodeError
from typing import List, Optional, Dict

from constants import MAP_SELECTION, DECK, POTIONS
from data.game_stats import GameStats
from data.mappers import shop_name_mapper
from data.other_enums import GamePhase
from data.room.room_battle import BattleRoom
from data.room.room_reward import RewardRoom
from data.shop.room_shop import ShopRoom
from data.skill.skills import Skill
from data.weapon.weapon import Weapon
from logger import logger
from test_data import test_data


class Snapshot:
    skills: List[Skill]
    game_stats: GameStats
    hero_deck: List[Weapon]
    hero_potion_ids: List[int]
    game_phase: GamePhase
    room: BattleRoom
    shop: Optional[ShopRoom]
    reward: Optional[RewardRoom]

    def __init__(self,
                 skills: List[Skill],
                 game_stats: GameStats,
                 hero_deck: List[Weapon],
                 hero_potion_ids: List[int],
                 game_phase: GamePhase,
                 room: BattleRoom,
                 shop: Optional[ShopRoom] = None,
                 reward: Optional[RewardRoom] = None,
                 ):
        self.skills = skills
        self.game_stats = game_stats
        self.hero_deck = hero_deck
        self.hero_potion_ids = hero_potion_ids
        self.game_phase = game_phase
        self.room = room
        self.shop = shop
        self.reward = reward

    @staticmethod
    def from_file(filename: str):
        try:
            with open(filename, mode='r') as source_file:
                source = source_file.read()
            raw_data = json.loads(base64.b64decode(source))
        except JSONDecodeError as e:
            logger.debug_error("Read of the file occured as it was being written to")
            # TODO think about the impact on history etc.
            return Snapshot.from_file(filename)
        # TODO recheck at some point
        # Uncomment for developer work - check if all data is recorded.
        # test_data(json.loads(json.dumps(raw_data)))
        return Snapshot.from_dict(raw_data)

    @staticmethod
    def from_dict(raw_data: Dict):
        game_phase = GamePhase.BATTLE
        map_selection = raw_data[MAP_SELECTION]
        reward_room = RewardRoom.from_dict(raw_data)
        if reward_room is not None:
            game_phase = GamePhase.BATTLE_REWARDS
        shop_room = ShopRoom.from_dict(raw_data)
        if shop_room is not None:
            game_phase = GamePhase.SHOP
        if map_selection:
            game_phase = GamePhase.MAP_JOURNEY
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
        if self.game_phase in [GamePhase.BATTLE, GamePhase.BATTLE_REWARDS]:
            return self.room.get_name(self.game_phase == GamePhase.BATTLE_REWARDS)
        elif self.game_phase == GamePhase.SHOP:
            shop_name = shop_name_mapper.get(self.shop.location)
            if shop_name is None:
                raise ValueError(f"Unknown shop name: {self.shop.location}")
            return shop_name
