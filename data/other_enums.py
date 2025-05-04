from enum import Enum


class GamePhase(Enum):
    BATTLE = 0
    BATTLE_REWARDS = 1
    MAP_JOURNEY = 2
    SHOP = 3


class WeaponUpgradePlace(Enum):
    REWARD = 0
    SHOP = 1
