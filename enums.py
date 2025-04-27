from enum import Enum


class EntityType(Enum):
    HERO = 0
    ENEMY = 1
    OBSTACLE = 2


class GamePhase(Enum):
    BATTLE = 0
    BATTLE_REWARDS = 1
    MAP_JOURNEY = 2
    SHOP = 3


class ShopServiceEnum(Enum):
    REROLL_FOR_HP = 0
    MONEY_FOR_HP = 1
    FULL_HEAL_FOR_SKULLS = 2
    MONEY_FOR_SKULLS = 3


class ShopType(Enum):
    WARRING = 0
    COMBO = 1
    DANCER = 2
    GUARDING = 3
    DAMAGE = 4
    COOLDOWN = 5
    SLOT = 6
    SACRIFICE = 7
    ENCHANT = 8
    MOONLIT_PORT = 9


class WeaponEnum(Enum):
    ARROW = 1
    SPEAR = 2
    BO = 3
    LIGHTINING = 4
    SWIRL = 5
    DRAGON_PUNCH = 6
    GRAPPLING_HOOK = 7
    TWIN_TESEEN = 8
    TRAP = 9
    CHARGE = 12
    SMOKE_BOMB = 15
    NAGIBOKU = 17
    CHAKRAM = 19
    EARTH_IMPALE = 22
    MIRROR = 23
    SHADOW_KAMA = 25
    CROSSBOW = 31
    SWAP_TOSS = 32
    TANEGASHIMA = 34
    SCAR_STRIKE = 37
    METEOR_HAMMER = 39
    KI_PUSH = 40
    BACK_SHADOW_DASH = 45
    SAI = 46
    MON = 48

    KATANA = -1
    TETSUBO = -2
    BLADE_OF_PATIENCE = -3
    HOOKBLADE = -4
    BACK_STRIKE = -6
    BLAZING_SUISEI = -10
    SHURIKEN = -11
    KUNAI = -13
    THORNS = -18
    SHADOW_DASH = -19
    BACK_CHARGE = -20
    BACK_SMOKE_BOMB = -21
    CURSE = -22
    SHARP_TURN = -23
    SIGNATURE_MOVE = -24
    DASH = -26
    ORIGIN_OF_SYMMETRY = -27


class WeaponAttackEffectEnum(Enum):
    CURSE = 666
    ICE = 1
    SHOCKWAVE = 3
    POISON = 4


class WeaponTileEffectEnum(Enum):
    IMMEDIATE = 1


class SkillEnum(Enum):
    UNFRIENDLY_FIRE = -2
    MINDFULLNESS = -3
    BIG_POCKETS = -4
    ROGUE_RETAIL = -5
    BACK_STABBER = -6
    SNIPER = -7
    MONOMANCER = -8
    CLOSE_COMBAT = -9
    CENTRAL_DOMINION = -10
    ODD_CURSE = -11
    COMBO_COIN = -12
    COMBO_RECHARGE = -13
    TRIPLE_COMBO_HEAL = -14
    COMBO_CURSE = -15
    COMBO_DEAL = -16
    KOBUSHI_COMBO = -17
    COMBO_BOON = -18
    CHILLING_COMBO = -19
    HEALTHY = -20
    FORTRESS = -21
    REACTIVE_SHIELD = -22
    SHIELD_RETENTION = -23
    KARMA = -24
    CHILLING_BLOOD = -25
    IRON_SKIN = -26
    OVERFLOW_GUARD = -27
    TWO_WAY_MOVE = -28
    QUICK_RECOVERY = -29
    DAMAGING_MOVE = -30
    DYNAMIC_BOOST = -31
    CURSING_MOVE = -32
    CHIKARA_CRUSH = -33
    MAMUSHI_MOVE = -34
    TWO_FACED_DANGER = -35
    FENGHUANGS_FEATHER = -36
    SEIRUYS_SCALE = -37


class PotionEnum(Enum):
    RAIN_OF_MIRROS = 7
    EDAMAME_BREW = 0
    COOL_UP = 2
    SHIELD = 3


class LogLevel(Enum):
    SPLITS = 0
    DEBUG = 1
    NARRATIVE = 2


class RoomEnum(Enum):
    BAMBOO_GROVE = 0
    WHISPERING_CAVES = 1
    MOONLIT_PORT = 3
    SPIRIT_GATEWAY = 4
    FORSAKEN_LANDS = 5
    HOT_SPRINGS = 6
    THEATRE_OF_SHADOWS = 7
    HIDEYOSHI = 8
    NOBUNAGA = 9
    IEIASU = 10
    SHOGUN = 11


class ShopEnum(Enum):
    BAMBOO_GROVE_UP = 0
    BAMBOO_GROVE_DOWN = 1
    BEFORE_MOONLIT_PORT_UP = 2
    BEFORE_MOONLIT_PORT_CENTER = 3
    BEFORE_MOONLIT_PORT_DOWN = 4
    MOONLIT_PORT = 5
    SPIRIT_GATEWAY_UP = 6
    SPIRIT_GATEWAY_DOWN = 7
    FORSAKEN_LANDS_UP = 8
    FORSAKEN_LANDS_DOWN = 9
    HIDEYOSHI = 10
    NOBUNAGA = 11
    IEIASU = 12
    SHOGUN = 13


class WeaponUpgradePlace(Enum):
    REWARD = 0
    SHOP = 1
