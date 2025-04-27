from enums import WeaponEnum, SkillEnum, WeaponAttackEffectEnum, WeaponTileEffectEnum, PotionEnum, RoomEnum, ShopEnum

weapon_mapper = {
    WeaponEnum.SPEAR: "Spear",
    WeaponEnum.LIGHTINING: "Lightning",
    WeaponEnum.TWIN_TESEEN: "Twin Tessen",
    WeaponEnum.SMOKE_BOMB: "Smoke Bomb",
    WeaponEnum.TANEGASHIMA: "Tanegashima",
    WeaponEnum.METEOR_HAMMER: "Meteor Hammer",
    WeaponEnum.SHADOW_KAMA: "Shadow Kama",
    WeaponEnum.CHARGE: "Charge",
    WeaponEnum.SCAR_STRIKE: "Scar Strike",
    WeaponEnum.BACK_SHADOW_DASH: "Back Shadow Dash",
    WeaponEnum.DRAGON_PUNCH: "Dragon Punch",
    WeaponEnum.SAI: "Sai",
    WeaponEnum.CHAKRAM: "Chakram",
    WeaponEnum.KI_PUSH: "Ki Push",
    WeaponEnum.KATANA: "Katana",
    WeaponEnum.TETSUBO: "Tetsubo",
    WeaponEnum.BLADE_OF_PATIENCE: "Blade of Patience",
    WeaponEnum.HOOKBLADE: "Hookblade",
    WeaponEnum.BO: "Bo",
    WeaponEnum.BACK_STRIKE: "Back Strike",
    WeaponEnum.SWIRL: "Swirl",
    WeaponEnum.NAGIBOKU: "Nagiboku",
    WeaponEnum.EARTH_IMPALE: "Earth Impale",
    WeaponEnum.BLAZING_SUISEI: "Blazing Suesei",
    WeaponEnum.SHURIKEN: "Shuriken",
    WeaponEnum.ARROW: "Arrow",
    WeaponEnum.KUNAI: "Kunai",
    WeaponEnum.MON: "Mon",
    WeaponEnum.CROSSBOW: "Crossbow",
    WeaponEnum.GRAPPLING_HOOK: "Grappling Hook",
    WeaponEnum.TRAP: "Trap",
    WeaponEnum.THORNS: "Thorns",
    WeaponEnum.SHADOW_DASH: "Shadow Dash",
    WeaponEnum.BACK_CHARGE: "Back Charge",
    WeaponEnum.BACK_SMOKE_BOMB: "Back Smoke Bomb",
    WeaponEnum.CURSE: "Curse",
    WeaponEnum.SHARP_TURN: "Sharp Turn",
    WeaponEnum.SIGNATURE_MOVE: "Signature Move",
    WeaponEnum.SWAP_TOSS: "Swap Toss",
    WeaponEnum.DASH: "Dash",
    WeaponEnum.ORIGIN_OF_SYMMETRY: "Origin of Symmetry",
    WeaponEnum.MIRROR: "Mirror",
}

skill_mapper = {
    SkillEnum.UNFRIENDLY_FIRE: "Unfriendly Fire",
    SkillEnum.MINDFULLNESS: "Mindfullness",
    SkillEnum.BIG_POCKETS: "Big Pockets",
    SkillEnum.ROGUE_RETAIL: "Rogue Retail",
    SkillEnum.BACK_STABBER: "Back Stabber",
    SkillEnum.SNIPER: "Sniper",
    SkillEnum.MONOMANCER: "Monomancer",
    SkillEnum.CLOSE_COMBAT: "Close Combat",
    SkillEnum.CENTRAL_DOMINION: "Central Dominion",
    SkillEnum.ODD_CURSE: "Odd Curse",
    SkillEnum.COMBO_COIN: "Combo Coin",
    SkillEnum.COMBO_RECHARGE: "Combo Recharge",
    SkillEnum.TRIPLE_COMBO_HEAL: "Triple-Combo Heal",
    SkillEnum.COMBO_CURSE: "Combo Curse",
    SkillEnum.COMBO_DEAL: "Combo Deal",
    SkillEnum.KOBUSHI_COMBO: "Kobushi Combo",
    SkillEnum.COMBO_BOON: "Combo Boon",
    SkillEnum.CHILLING_COMBO: "Chilling Combo",
    SkillEnum.HEALTHY: "Healthy",
    SkillEnum.FORTRESS: "Fortress",
    SkillEnum.REACTIVE_SHIELD: "Reactive Shield",
    SkillEnum.SHIELD_RETENTION: "Shield Retention",
    SkillEnum.KARMA: "Karma",
    SkillEnum.CHILLING_BLOOD: "Chilling Blood",
    SkillEnum.IRON_SKIN: "Iron Skin",
    SkillEnum.OVERFLOW_GUARD: "Overflow Guard",
    SkillEnum.TWO_WAY_MOVE: "Two-Way Move",
    SkillEnum.QUICK_RECOVERY: "Quick Recovery",
    SkillEnum.DAMAGING_MOVE: "Damaging Move",
    SkillEnum.DYNAMIC_BOOST: "Dynamic Boost",
    SkillEnum.CURSING_MOVE: "Cursing Move",
    SkillEnum.CHIKARA_CRUSH: "Chikara Crush",
    SkillEnum.MAMUSHI_MOVE: "Mamushi Move",
    SkillEnum.TWO_FACED_DANGER: "Two-Faced Danger",
    SkillEnum.FENGHUANGS_FEATHER: "Fenghuang's Feather",
    SkillEnum.SEIRUYS_SCALE: "Seiryu's Scale",
}

weapon_attack_effect_mapper = {
    WeaponAttackEffectEnum.CURSE: "curse",
    WeaponAttackEffectEnum.SHOCKWAVE: "shockwave",
}

weapon_tile_effect_mapper = {
    WeaponTileEffectEnum.IMMEDIATE: "immediate"
}

potion_mapper = {
    # 200 mass curse
    # 201 mass ice
    # 202
    # 203
    # mass poison
    PotionEnum.RAIN_OF_MIRROS: "Rain of Mirrors",  # 204 ?? 7?
    PotionEnum.EDAMAME_BREW: "Edamame Brew",  # 100
    PotionEnum.COOL_UP: "Cool Up",  # 101
    PotionEnum.SHIELD: "Kami Brew",  # 102 ?? 3?
    # 0 gold
}

upgrades_mapper = {
    200: "Was it shockwave?"
}

room_mapper = {
    "green-combat-1": RoomEnum.BAMBOO_GROVE,
    "brown-combat-1A": RoomEnum.WHISPERING_CAVES,
    "brown-combat-1B": RoomEnum.MOONLIT_PORT,
    "brown-combat-2": RoomEnum.MOONLIT_PORT,
    "red-combat-1": RoomEnum.SPIRIT_GATEWAY,
    "red-combat-2": RoomEnum.HOT_SPRINGS,
    "purple-combat-1": RoomEnum.FORSAKEN_LANDS,
    "purple-combat-2": RoomEnum.THEATRE_OF_SHADOWS,
    "white-combat-1": RoomEnum.HIDEYOSHI,
    "gray-combat-1": RoomEnum.NOBUNAGA,
    "shogun-combat-1": RoomEnum.SHOGUN,
}

boss_room_mapper = {
    RoomEnum.BAMBOO_GROVE: {4: True},
    RoomEnum.WHISPERING_CAVES: {6: True},
    RoomEnum.MOONLIT_PORT: {6: True},
    RoomEnum.SPIRIT_GATEWAY: {6: True},
    RoomEnum.HOT_SPRINGS: {6: True},
    RoomEnum.FORSAKEN_LANDS: {6: True},
    RoomEnum.THEATRE_OF_SHADOWS: {6: True},
    RoomEnum.HIDEYOSHI: {2: True},
    RoomEnum.NOBUNAGA: {2: True},
    RoomEnum.IEIASU: {2: True},
    RoomEnum.SHOGUN: {2: True},
}

room_name_mapper = {
    RoomEnum.BAMBOO_GROVE: "Bamboo Grove",
    RoomEnum.WHISPERING_CAVES: "Whispering Caves",
    RoomEnum.MOONLIT_PORT: "Moonlit Port",
    RoomEnum.SPIRIT_GATEWAY: "Spirit Gateway",
    RoomEnum.HOT_SPRINGS: "Hot Springs",
    RoomEnum.FORSAKEN_LANDS: "Forsaken Lands",
    RoomEnum.THEATRE_OF_SHADOWS: "Theatre of Shadows",
    RoomEnum.HIDEYOSHI: "Hideyoshi's Keep",
    RoomEnum.NOBUNAGA: "Nobunaga's Fortress",
    RoomEnum.IEIASU: "Ieiasu's Gardens",
    RoomEnum.SHOGUN: "The Shogun's Castle",
}

room_boss_mapper = {
    RoomEnum.BAMBOO_GROVE: "Daisuke",
    RoomEnum.WHISPERING_CAVES: "Iwao the Impaler",
    RoomEnum.MOONLIT_PORT: "The Twins",
    RoomEnum.SPIRIT_GATEWAY: "The Statue",
    RoomEnum.HOT_SPRINGS: "Kowa the Coward",
    RoomEnum.FORSAKEN_LANDS: "fumiko?",
    RoomEnum.THEATRE_OF_SHADOWS: "actor?",
    RoomEnum.HIDEYOSHI: "Hideyoshi the Cunning",
    RoomEnum.NOBUNAGA: "Nobunaga the Whatever",  # TODO
    RoomEnum.IEIASU: "Ieiasu the Cruel",  # TODO
    RoomEnum.SHOGUN: "The Shogun",  # TODO
}

room_corrupted_boss_mapper = {
    RoomEnum.BAMBOO_GROVE: "Corrupted Daisuke",
    RoomEnum.MOONLIT_PORT: "Corrupted Twins"
}

shop_mapper = {
    "green-shop-1A": ShopEnum.BAMBOO_GROVE_UP,
    "green-shop-1B": ShopEnum.BAMBOO_GROVE_DOWN,
    "brown-shop-1A": ShopEnum.BEFORE_MOONLIT_PORT_UP,
    "brown-shop-1B": ShopEnum.BEFORE_MOONLIT_PORT_CENTER,
    "brown-shop-1C": ShopEnum.BEFORE_MOONLIT_PORT_DOWN,
    "brown-combat-2": ShopEnum.MOONLIT_PORT,
    "red-shop-1A": ShopEnum.SPIRIT_GATEWAY_UP,
    "red-shop-1B": ShopEnum.SPIRIT_GATEWAY_DOWN,
    "purple-shop-1A": ShopEnum.FORSAKEN_LANDS_UP,
    "purple-shop-1B": ShopEnum.FORSAKEN_LANDS_DOWN,
    "white-shop-1": ShopEnum.HIDEYOSHI,
    "gray-shop-1": ShopEnum.NOBUNAGA,
    "gray-shop-x": ShopEnum.IEIASU,
    "shogun-shop-1": ShopEnum.SHOGUN,
}

shop_name_mapper = {
    ShopEnum.BAMBOO_GROVE_UP: "Shop after Bamboo Grove",
    ShopEnum.BAMBOO_GROVE_DOWN: "Shop after Bamboo Grove",
    ShopEnum.BEFORE_MOONLIT_PORT_UP: "Shop before Moonlit Port",
    ShopEnum.BEFORE_MOONLIT_PORT_CENTER: "Shop before Moonlit Port",
    ShopEnum.BEFORE_MOONLIT_PORT_DOWN: "Shop before Moonlit Port",
    ShopEnum.MOONLIT_PORT: "Moonlit Port shop",
    ShopEnum.SPIRIT_GATEWAY_UP: "Spirit Gateway shop",
    ShopEnum.SPIRIT_GATEWAY_DOWN: "Spirit Gateway shop",
    ShopEnum.FORSAKEN_LANDS_UP: "Forsaken Lands shop",
    ShopEnum.FORSAKEN_LANDS_DOWN: "Forsaken Lands shop",
    ShopEnum.HIDEYOSHI: "Shop before Hideyoshi's Keep",
    ShopEnum.NOBUNAGA: "Shop before Nobunaga's Fortress",
    ShopEnum.IEIASU: "Shop before Ieiasu's Gardens",
    ShopEnum.SHOGUN: "Shop before The Shogun's Castle",
}
