from enum import Enum


class PickupEnum(Enum):
    ANY = -1  # Allows setting predictions
    GOLD = 0
    EDAMAME_BREW = 100
    COOL_UP = 101
    KAMI_BREW = 102
    LUCKY_DIE = 103
    MASS_CURSE = 200
    MASS_ICE = 201
    MASS_POISON = 202
    # ARTIFACT: 203
    RAIN_OF_MIRRORS = 204


class RoomEnum(Enum):
    BAMBOO_GROVE = "green-combat-1"
    WHISPERING_CAVES = "brown-combat-1A"
    HIBIKU_WASTELANDS = "brown-combat-1B"
    MOONLIT_PORT = "brown-combat-2"
    SPIRIT_GATEWAY = "red-combat-1"
    HOT_SPRINGS = "red-combat-2"
    FORSAKEN_GROUNDS = "purple-combat-1"
    THEATRE_OF_ILLUSIONS = "purple-combat-2"
    HIDEYOSHI = "white-combat-1"
    NOBUNAGA = "gray-combat-1"
    IEIASU = "darkGreen-combat-1"
    SHOGUN = "shogun-combat-1"


class WeaponUpgradesEnum(Enum):
    DAMAGE_WITH_CD = 100
    DAMAGE = 101
    COOLDOWN_1 = 102
    COOLDOWN_2 = 103
    COOLDOWN_4_FOR_DAMAGE = 104
    DAMAGE_2_FOR_3_COOLDOWN = 105
    ICE = 201
    POISON = 202
    DOUBLE_STRIKE = 203
    PERFECT_STRIKE = 204
    CURSE = 205
    IMMEDIATE = 300
    SACRIFICE_TILE = 400
    WARRIORS_GAMBLE = 401
    PLUS_SLOT = 500
    PLUS_SLOT_MINUS_COOLDOWN = 501
