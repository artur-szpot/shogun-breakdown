from typing import List

from enums import RoomEnum, ShopEnum


class PathHistory:
    rooms_visited: List[RoomEnum]
    shops_visited: List[ShopEnum]

    def __init__(self):
        self.rooms_visited = []
        self.shops_visited = []