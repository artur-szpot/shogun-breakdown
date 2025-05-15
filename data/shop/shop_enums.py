from enum import Enum


class ShopServiceEnum(Enum):
    REROLL_FOR_HP = 0
    MONEY_FOR_HP = 1
    FULL_HEAL_FOR_SKULLS = 2
    MONEY_FOR_SKULLS = 3


class ShopType(Enum):
    DAMAGE = "DamageUpgrade"
    COOLDOWN = "CooldownUpgrade"
    SACRIFICE = "SacrificeTile"
    WARRIORS_GAMBLE = "WarriorGamble"
    WARRING = "WarringShop"
    COMBO = "ComboShop"
    DANCER = "DancerShop"
    GUARDING = "GuardingShop"
    SLOT = "MaxLevelUpgrade"
    ENCHANT = "EnchantUpgrade"
    MOONLIT_PORT = "MoonlitPortShop"


class ShopEnum(Enum):
    BAMBOO_GROVE_UP = "green-shop-1A"
    BAMBOO_GROVE_DOWN = "green-shop-1B"
    BEFORE_MOONLIT_PORT_UP = "brown-shop-1A"
    BEFORE_MOONLIT_PORT_CENTER = "brown-shop-1B"
    BEFORE_MOONLIT_PORT_DOWN = "brown-shop-1C"
    MOONLIT_PORT = "brown-combat-2"
    SPIRIT_GATEWAY_UP = "red-shop-1A"
    SPIRIT_GATEWAY_DOWN = "red-shop-1B"
    FORSAKEN_LANDS_UP = "purple-shop-1A"
    FORSAKEN_LANDS_DOWN = "purple-shop-1B"
    HIDEYOSHI = "white-shop-1"
    NOBUNAGA = "gray-shop-1"
    IEIASU = "darkGreen-shop-1"
    SHOGUN = "shogun-shop-1"
