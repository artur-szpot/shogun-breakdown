import base64
import json
from typing import List, Optional

from constants import HERO, MAP_SELECTION, MAP_SAVE, CURRENT_LOCATION, PROGRESSION, PROGRESSION_DATA, DECK, POTIONS
from entity import Entity
from enums import GamePhase, RoomEnum, PotionEnum
from game_stats import GameStats
from mappers import room_mapper, room_name_mapper, room_boss_mapper, shop_name_mapper, boss_room_mapper
from room_reward import RewardRoom
from room_shop import ShopRoom
from skills import Skill
from test_data import test_data
from weapon import Weapon


class Snapshot:
    skills: List[Skill]
    game_stats: GameStats
    hero: Entity
    hero_deck: List[Weapon]
    hero_potions: List[PotionEnum]
    other_entities: List[Entity]
    game_phase: GamePhase
    room: Optional[RoomEnum]
    progression: Optional[int]
    shop: Optional[ShopRoom]
    reward: Optional[RewardRoom]

    def __init__(self,
                 skills: List[Skill],
                 game_stats: GameStats,
                 hero: Entity,
                 hero_deck: List[Weapon],
                 hero_potions: List[PotionEnum],
                 other_entities: List[Entity],
                 game_phase: GamePhase,
                 room: Optional[RoomEnum] = None,
                 progression: Optional[int] = None,
                 shop: Optional[ShopRoom] = None,
                 reward: Optional[RewardRoom] = None,
                 ):
        self.skills = skills
        self.game_stats = game_stats
        self.hero = hero
        self.hero_deck = hero_deck
        self.hero_potions = hero_potions
        self.other_entities = other_entities
        self.game_phase = game_phase
        self.room = room
        self.progression = progression
        self.shop = shop
        self.reward = reward

    @staticmethod
    def from_file(source: str):
        raw_data = json.loads(base64.b64decode(source))
        # Uncomment for developer work - check if all data is recorded.
        test_data(json.loads(json.dumps(raw_data)))

        game_phase = GamePhase.BATTLE
        map_selection = raw_data[MAP_SELECTION]
        if map_selection:
            game_phase = GamePhase.MAP_JOURNEY
        reward_room = RewardRoom.from_dict(raw_data)
        if reward_room is not None:
            game_phase = GamePhase.BATTLE_REWARDS
        shop_room = ShopRoom.from_dict(raw_data)
        if shop_room is not None:
            game_phase = GamePhase.SHOP

        if game_phase in [GamePhase.BATTLE, GamePhase.BATTLE_REWARDS]:
            room_raw = raw_data[MAP_SAVE][CURRENT_LOCATION]
            progression = raw_data[PROGRESSION_DATA][PROGRESSION]
            room = room_mapper.get(room_raw)
            if room is None:
                raise ValueError(f"Unkown room: {room_raw}")
        else:
            room = None
            progression = None

        print(raw_data["pickups"])

        return Snapshot(
            skills=Skill.from_dict(raw_data),
            game_stats=GameStats.from_dict(raw_data),
            hero=Entity.from_dict(raw_data.get(HERO, {}), hero=True),
            hero_deck=[Weapon.from_dict(x) for x in raw_data[DECK]],
            hero_potions=[], # PotionEnum(x) for x in raw_data[POTIONS]],
            other_entities=[],  # TODO
            game_phase=game_phase,
            room=room,
            progression=progression,
            shop=shop_room,
            reward=reward_room,
        )

    def get_room(self):
        is_boss_battle = boss_room_mapper.get(self.room, {}).get(self.progression, False)
        room_name = room_name_mapper.get(self.room)
        boss_name = room_boss_mapper.get(self.room)
        if self.game_phase in [GamePhase.BATTLE, GamePhase.BATTLE_REWARDS]:
            if room_name is None:
                raise ValueError(f"Unknown room name: {self.room}")
            if boss_name is None:
                raise ValueError(f"Unknown boss name: {self.room}")
        if self.game_phase == GamePhase.BATTLE:
            if is_boss_battle:
                return f"{room_name}, boss battle ({boss_name})"
            else:
                return f"{room_name}, battle #{(self.progression // 2) + 1}"
        elif self.game_phase == GamePhase.BATTLE_REWARDS:
            if is_boss_battle:
                return f"{room_name}, boss battle ({boss_name}) rewards"
            else:
                return f"{room_name}, battle #{(self.progression + 1) // 2} rewards"
        elif self.game_phase == GamePhase.SHOP:
            shop_name = shop_name_mapper.get(self.shop.location)
            if shop_name is None:
                raise ValueError(f"Unknown shop name: {self.shop.location}")
            return f"{shop_name}"
