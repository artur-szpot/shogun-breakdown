from data.shop.shop_enums import ShopType
from data.skill.skill_enums import SkillEnum

skill_price_mapper = {
    SkillEnum.UNFRIENDLY_FIRE: 10,
    SkillEnum.BIG_POCKETS: 10,
    SkillEnum.COMBO_COIN: 15,
    SkillEnum.COMBO_CURSE: 15,
    SkillEnum.CENTRAL_DOMINION: 10,  # TODO capture levels!
    SkillEnum.IRON_SKIN: 20,
    SkillEnum.QUICK_RECOVERY: 15,
    SkillEnum.CURSING_MOVE: 15,
    SkillEnum.KARMA: 10,
    SkillEnum.ROGUE_RETAIL: 10,
    SkillEnum.DAMAGING_MOVE: 15,
    SkillEnum.KOBUSHI_COMBO: 15,
    SkillEnum.TRIPLE_COMBO_HEAL: 20,
    SkillEnum.SHIELD_RETENTION: 15,
    SkillEnum.HEALTHY: 15,

    # BUY THESE!
    SkillEnum.MINDFULLNESS: 20,
    SkillEnum.BACK_STABBER: 15,
    SkillEnum.SNIPER: 15,
    SkillEnum.MAMUSHI_MOVE: 20,
    SkillEnum.COMBO_RECHARGE: 20,
    SkillEnum.CLOSE_COMBAT: 20,

    SkillEnum.MONOMANCER: -1,
    SkillEnum.ODD_CURSE: -1,
    SkillEnum.COMBO_DEAL: -1,
    SkillEnum.COMBO_BOON: -1,
    SkillEnum.CHILLING_COMBO: -1,
    SkillEnum.FORTRESS: -1,
    SkillEnum.REACTIVE_SHIELD: -1,
    SkillEnum.CHILLING_BLOOD: -1,
    SkillEnum.OVERFLOW_GUARD: -1,
    SkillEnum.TWO_WAY_MOVE: -1,
    SkillEnum.DYNAMIC_BOOST: -1,
    SkillEnum.CHIKARA_CRUSH: -1,
    SkillEnum.TWO_FACED_DANGER: -1,
    SkillEnum.FENGHUANGS_FEATHER: -1,
    SkillEnum.SEIRUYS_SCALE: -1,
}

shop_types_mapper = {
    "DamageUpgrade": ShopType.DAMAGE,
    "CooldownUpgrade": ShopType.COOLDOWN,
    "SacrificeTile": ShopType.SACRIFICE,
    "WarriorGamble": ShopType.WARRIORS_GAMBLE,
    "WarringShop": ShopType.WARRING,
    "ComboShop": ShopType.COMBO,
    "DancerShop": ShopType.DANCER,
    "GuardingShop": ShopType.GUARDING,
    "MaxLevelUpgrade": ShopType.SLOT,
    "EnchantUpgrade": ShopType.ENCHANT,
    "MoonlitPortShop": ShopType.MOONLIT_PORT,
}

shop_type_name_mapper = {
    ShopType.DAMAGE: "Damage",
    ShopType.COOLDOWN: "Cooldown",
    ShopType.SACRIFICE: "Sacrifice Tile",
    ShopType.WARRING: "Warring",
    ShopType.COMBO: "Combo",
    ShopType.DANCER: "Dancer",
    ShopType.GUARDING: "Guarding",
    ShopType.SLOT: "Slot Upgrade",
    ShopType.ENCHANT: "Enchant",
    ShopType.MOONLIT_PORT: "Moonlit Port",
    ShopType.WARRIORS_GAMBLE: "Warrior's Gamble",
}
