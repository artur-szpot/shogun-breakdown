import base64
import json
from json import JSONDecodeError
from typing import List, Optional, Dict

from constants import MAP_SELECTION, DECK, POTIONS, SHOP_COMPONENT, MAP_SAVE, VERSION, RUN_NUMBER, RUN_IN_PROGRESS, \
    HERO, RUN_STATS, SKILLS, SKILL_LEVELS, PICKUPS, PICKUP_LOCATIONS, PROGRESSION_DATA, CORRUPTED_BOSS_SECTORS, \
    COMBAT_ROOM, SHOP_ROOM, REWARD_ROOM, CURRENT_LOCATION, CURRENT_LOCATION_NAME, UNCOVERED_LOCATIONS
from data.game_stats import GameStats
from data.mappers import shop_name_mapper
from data.other_enums import GamePhase
from data.room.room_battle import BattleRoom
from data.room.room_reward import RewardRoom
from data.shop.room_shop import ShopRoom
from data.skill.skills import Skills
from data.weapon.weapon import Weapon
from history.history import History
from history.potions.history_potions import PotionSnapshot
from logger import logger


class Snapshot:
    skills: Skills
    game_stats: GameStats
    hero_deck: List[Weapon]
    hero_potion_ids: List[int]
    game_phase: GamePhase
    room: BattleRoom
    shop: Optional[ShopRoom]
    reward: Optional[RewardRoom]
    history: Optional[History]

    def __init__(self,
                 skills: Skills,
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
        self.history = None

    @staticmethod
    def from_file(filename: str, first: bool = False):
        map_shops = None
        corrupted_boss_sectors = []
        try:
            with open(filename, mode='r') as source_file:
                source = source_file.read()
            raw_data = json.loads(base64.b64decode(source))
            # print('raw_data')
            # print(raw_data)
            if first:
                map_shops = raw_data[MAP_SAVE][SHOP_COMPONENT]
                corrupted_boss_sectors = raw_data[PROGRESSION_DATA][CORRUPTED_BOSS_SECTORS]
        except JSONDecodeError as e:
            logger.debug_error("Read of the file occured as it was being written to")
            # TODO think about the impact on history etc.
            return Snapshot.from_file(filename, first)
        # TODO recheck at some point
        # Uncomment for developer work - check if all data is recorded.
        # test_data(json.loads(json.dumps(raw_data)))
        retval = Snapshot.from_dict(raw_data)
        if first:
            retval.history = History(retval, map_shops, corrupted_boss_sectors)
        return retval

    @staticmethod
    def from_dict(raw_data: Dict):
        game_phase = GamePhase.BATTLE
        map_selection = raw_data[MAP_SELECTION]
        skills = Skills.from_dict(raw_data)

        reward_room = RewardRoom.from_dict(raw_data)
        if reward_room is not None:
            game_phase = GamePhase.BATTLE_REWARDS
        shop_room = ShopRoom.from_dict(raw_data)
        if shop_room is not None:
            game_phase = GamePhase.SHOP
        if map_selection:
            game_phase = GamePhase.MAP_JOURNEY
        battle_room = BattleRoom.from_dict(raw_data, skills)

        return Snapshot(
            skills=skills,
            game_stats=GameStats.from_dict(raw_data),
            hero_deck=[Weapon.from_dict(x) for x in raw_data[DECK]],
            hero_potion_ids=raw_data[POTIONS],
            game_phase=game_phase,
            room=battle_room,
            shop=shop_room,
            reward=reward_room,
        )

    def to_dict(self):
        map_shops = self.history.map.map_shops
        corrupted_boss_sectors = self.history.map.corrupted_boss_sectors
        current_room = ''
        if self.shop is not None:
            current_room = self.shop.location.value
        else:
            current_room = self.room.room.value
        return {
            VERSION: self.game_stats.version,
            RUN_IN_PROGRESS: True,
            RUN_NUMBER: 0,
            MAP_SELECTION: self.game_phase == GamePhase.MAP_JOURNEY,
            RUN_STATS: self.game_stats.to_dict(),
            SKILLS: self.skills.to_dict_skills(),
            SKILL_LEVELS: self.skills.to_dict_levels(),
            REWARD_ROOM: RewardRoom.empty_dict() if self.reward is None else self.reward.to_dict(),
            SHOP_ROOM: ShopRoom.empty_dict() if self.shop is None else self.shop.to_dict(),
            COMBAT_ROOM: self.room.to_dict(),
            PROGRESSION_DATA: self.room.to_dict_progression_data(corrupted_boss_sectors),
            PICKUPS: self.room.to_dict_pickups(),
            PICKUP_LOCATIONS: self.room.to_dict_pickup_cells(),
            DECK: [weapon.to_dict() for weapon in self.hero_deck],
            POTIONS: self.hero_potion_ids,
            HERO: self.room.hero.to_dict(),
            MAP_SAVE: {
                CURRENT_LOCATION_NAME: "cheater\ntown",
                CURRENT_LOCATION: current_room,
                UNCOVERED_LOCATIONS: [
                    "camp",
                    "green-combat-1",
                    "brown-combat-1A",
                    "brown-combat-1B",
                    "brown-combat-2",
                    "red-combat-1",
                    "red-combat-2",
                    "purple-combat-1",
                    "purple-combat-2",
                    "white-combat-1",
                    "gray-combat-1",
                    "darkGreen-combat-1",
                    "shogun-combat-1",
                ],
                SHOP_COMPONENT: map_shops
            },
        }

    def get_room(self, splits: bool = False):
        if self.game_phase in [GamePhase.BATTLE, GamePhase.BATTLE_REWARDS]:
            return self.room.get_name(self.game_phase == GamePhase.BATTLE_REWARDS, splits)
        elif self.game_phase == GamePhase.SHOP:
            shop_name = shop_name_mapper.get(self.shop.location)
            if shop_name is None:
                raise ValueError(f"Unknown shop name: {self.shop.location}")
            return shop_name

    def potion_snapshot(self) -> PotionSnapshot:
        return PotionSnapshot(
            coins=self.game_stats.coins,
            potions_ids=self.hero_potion_ids,
            ground_potions=self.room.pickups,
            total_used=self.game_stats.consumables_used,
            total_scrolls_dropped=self.game_stats.scroll_pickups,
            total_potions_dropped=self.game_stats.potion_pickups,
            total_heals_dropped=self.game_stats.heal_pickups
        )
