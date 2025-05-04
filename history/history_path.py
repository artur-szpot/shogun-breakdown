from typing import List

from data.room.room_enums import RoomEnum
from data.shop.shop_enums import ShopEnum


class PathHistory:
    rooms_visited: List[RoomEnum]
    shops_visited: List[ShopEnum]

    def __init__(self):
        self.rooms_visited = []
        self.shops_visited = []
