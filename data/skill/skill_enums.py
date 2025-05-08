from enum import Enum


class SkillEnum(Enum):
    BACK_STABBER = 1001
    UNFRIENDLY_FIRE = 1003
    SNIPER = 1004
    MONOMANCER = 1006
    CLOSE_COMBAT = 1007
    CENTRAL_DOMINION = 1008

    COMBO_COIN = 2001 # no need to cover
    TRIPLE_COMBO_HEAL = 2002
    COMBO_CURSE = 2004
    COMBO_DEAL = 2005
    KOBUSHI_COMBO = 2006
    COMBO_BOON = 2007
    CHILLING_COMBO = 2008

    HEALTHY = 3001
    REACTIVE_SHIELD = 3003 # done
    KARMA = 3005
    CHILLING_BLOOD = 3007
    IRON_SKIN = 3008

    QUICK_RECOVERY = 4002
    DAMAGING_MOVE = 4003 # done
    DYNAMIC_BOOST = 4005
    CURSING_MOVE = 4006 # done
    TWO_FACED_DANGER = 4009

    FENGHUANGS_FEATHER = 5001

    BIG_POCKETS = 9002
    ROGUE_RETAIL = 9003

    # attack
    MINDFULLNESS = -3

    # combo
    ODD_CURSE = -11 # no need to cover -- affects newly spawning enemies anyway
    COMBO_RECHARGE = -13

    # guard
    FORTRESS = -21
    SHIELD_RETENTION = -23
    OVERFLOW_GUARD = -27

    # dancer
    TWO_WAY_MOVE = -28
    CHIKARA_CRUSH = -33
    MAMUSHI_MOVE = -34 # done

    # ??? moonlit?
    SEIRUYS_SCALE = -37
