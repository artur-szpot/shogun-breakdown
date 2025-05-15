from typing import Dict, List

from constants import CORRUPTED_BOSS_SECTORS, PROGRESSION_DATA
from data.room.room_enums import RoomEnum
from data.shop.shop_enums import ShopEnum


class MapHistory:
    # what shops there are
    map_shops: Dict
    rooms_visited: List[RoomEnum]
    shops_visited: List[ShopEnum]
    corrupted_boss_sectors: List[int]

    def __init__(self, map_shops, corrupted_boss_sectors: List[int]):
        self.map_shops = map_shops
        self.rooms_visited = []
        self.shops_visited = []
        self.corrupted_boss_sectors = corrupted_boss_sectors
