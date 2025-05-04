from enum import Enum


class EntityType(Enum):
    HERO = 0
    ENEMY = 1
    OBSTACLE = 2


class EnemyEnum(Enum):
    ASHIGARU_ARCHER = 0
    SPIKE_CHARGER = 1
    GRAPPLER_ALT = 2 # can also be ashigaru or shielder... is it somehow "unknown"?
    SHINOBI = 3
    GUARDIAN = 4
    SHADOW_CHARGER = 5
    YARI_MASTER = 6
    TWIN_TACHI = 8
    ASHIGARU = 9
    SUMMONER_ALT = 7 # the one for the Statue
    SUMMONER = 12
    GRAPPLER = 13
    YUMI_SNIPER = 14
    BARRICADE = 15
    STRIDER = 16
    BLIGHT_CHARGER = 17
    WARDEN = 18
    KABUKAI = 19
    THORNS = 20
    CORRUPTED_PROGENY = 22
    DAISUKE = 100  # = corrupted Rei TODO ?????
    KOWA = 103
    BARU = 104
    THE_STATUE = 105
    IWAO = 108
    NOBUNAGA = 109
    THE_TWINS = 111112  # here for room name display
    THE_TWINS_A = 111
    THE_TWINS_B = 112
    FUMIKO = 113
    REI = 115
    THE_SHOGUN = 120
    THE_SHOGUN_PHASE_TWO = 121

    IEIASU = -2
    HIDEYOSHI = -3
    SATO = -4
    TRAP = -42


class EnemyEliteEnum(Enum):
    NOT_ELITE = 0
    REACTIVE_SHIELD = 1
    DOUBLE_STRIKER = 2
    HEAVY = 3
    QUICK = 4
    CORRUPTED = 5


class EnemyActionEnum(Enum):
    WAIT = 0
    MOVE_LEFT = 1
    MOVE_RIGHT = 2
    EXECUTE_QUEUE = 3
    EXPAND_QUEUE = 4
    TURN_AROUND = 5  # TODO ?????
    TURN_AROUND_BOSS = 6  # TODO ?????


class HeroEnum(Enum):
    WANDERER = 0
    RONIN = -1
    SHADOW = -2
    JUJITSUKA = 3
    CHAIN_MASTER = -4
