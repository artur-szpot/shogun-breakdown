from enum import Enum


class EntityType(Enum):
    HERO = 0
    ENEMY = 1


class EnemyEnum(Enum):
    ASHIGARU_ARCHER = 0
    SPIKE_CHARGER = 1
    GRAPPLER = 2 # TODO remove comment, I may be dumb -- can also be ashigaru or shielder... is it somehow "unknown"?
    SHINOBI = 3
    GUARDIAN = 4
    SHADOW_CHARGER = 5
    YARI_MASTER = 6
    SUMMONER_ALT = 7 # the one for the Statue
    TWIN_TACHI = 8
    ASHIGARU = 9
    # ARTIFACT: 10
    # ARTIFACT: 11 (dummy?)
    SUMMONER = 12
    # GRAPPLER = 13 # I must have been wrong? # TODO cleanup this mess
    SHIELDER = 13
    YUMI_SNIPER = 14
    BARRICADE = 15
    STRIDER = 16
    BLIGHT_CHARGER = 17
    WARDEN = 18
    KABUKAI = 19
    THORNS = 20
    SWAPPER = 21
    CORRUPTED_PROGENY = 22
    DAISUKE = 100  # = corrupted Rei TODO ?????
    # ARTIFACT: 101 (generic boss?)
    # ARTIFACT: 102
    KOWA = 103
    BARU = 104
    THE_STATUE = 105
    IEIASU = 106
    # ARTIFACT: 107
    IWAO = 108
    NOBUNAGA = 109
    HIDEYOSHI = 110
    THE_TWINS = 111112  # here for room name display
    THE_TWINS_A = 111
    THE_TWINS_B = 112
    FUMIKO = 113
    SATO = 114 # will remain unused due to the fact Theatre doesn't write save data?
    REI = 115
    THE_SHOGUN = 120
    THE_SHOGUN_PHASE_TWO = 121
    CURRUPTED_SOUL = 122

    DAISUKE_CORRUPTED = 10000
    KOWA_CORRUPTED = 10300
    BARU_CORRUPTED = 10400
    THE_STATUE_CORRUPTED = 10500
    IEIASU_CORRUPTED = 10600
    IWAO_CORRUPTED = 10800
    NOBUNAGA_CORRUPTED = 10900
    HIDEYOSHI_CORRUPTED = 11000
    THE_TWINS_CORRUPTED = 11111200
    THE_TWINS_A_CORRUPTED = 11100
    THE_TWINS_B_CORRUPTED = 11200
    FUMIKO_CORRUPTED = 11300
    SATO_CORRUPTED = 11400
    REI_CORRUPTED = 11500


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
    CHAIN_MASTER = 4
