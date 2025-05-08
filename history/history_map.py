from typing import Dict, List

from data.room.room_enums import RoomEnum
from data.shop.shop_enums import ShopEnum


class MapHistory:
    # what shops there are
    map_history: Dict
    rooms_visited: List[RoomEnum]
    shops_visited: List[ShopEnum]

    def __init__(self, map_history: Dict):
        self.map_history = map_history
        self.rooms_visited = []
        self.shops_visited = []
