from typing import List, Optional

from data.other_enums import WeaponUpgradePlace
from data.room.room_enums import RoomEnum
from data.shop.shop_enums import ShopEnum
from data.weapon.weapon import Weapon


class WeaponRewardUpgradeSnapshot:
    room: RoomEnum
    progression: int

    def __init__(self, room: RoomEnum, progression: int):
        self.room = room
        self.progression = progression


class WeaponUpgradeSnapshot:
    where: WeaponUpgradePlace
    reward_detail: Optional[WeaponRewardUpgradeSnapshot]
    shop_detail: Optional[ShopEnum]
    price: int

    def __init__(self, where: WeaponUpgradePlace,
                 reward_detail: Optional[WeaponRewardUpgradeSnapshot] = None,
                 shop_detail: Optional[ShopEnum] = None,
                 price: int = 0):
        self.where = where
        self.reward_detail = reward_detail
        self.shop_detail = shop_detail
        self.price = price


class WeaponHistory:
    weapon_snapshots: List[Weapon]
    upgrade_snapshots: List[WeaponUpgradeSnapshot]
    total_price: int
    initial_weapon: bool

    def __init__(self, snapshot: Weapon, price: int, initial: bool):
        self.weapon_snapshots = [snapshot]
        self.total_price = price
        self.initial_weapon = initial

    @staticmethod
    def initial(snapshot: Weapon):
        return WeaponHistory(snapshot=snapshot, price=0, initial=True)

    @staticmethod
    def bought(snapshot: Weapon, price: int):
        return WeaponHistory(snapshot=snapshot, price=price, initial=False)

    def shop_upgrade(self, snapshot: Weapon, shop: ShopEnum, price: int):
        self.weapon_snapshots.append(snapshot)
        self.total_price += price
        self.upgrade_snapshots.append(WeaponUpgradeSnapshot(
            where=WeaponUpgradePlace.SHOP,
            shop_detail=shop,
            price=price
        ))

    def reward_upgrade(self, snapshot: Weapon, room: RoomEnum, progression: int):
        self.weapon_snapshots.append(snapshot)
        self.upgrade_snapshots.append(WeaponUpgradeSnapshot(
            where=WeaponUpgradePlace.REWARD,
            reward_detail=WeaponRewardUpgradeSnapshot(room=room, progression=progression),
        ))


class DeckHistory:
    deck: List[WeaponHistory]

    def __init__(self, first_snapshot):
        self.deck = []
        # for weapon in first_snapshot.hero_deck:
        #     # do something TODO!!!
