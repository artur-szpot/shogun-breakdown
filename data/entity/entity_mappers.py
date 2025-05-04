from data.entity.entity_enums import EnemyEliteEnum, EnemyEnum, HeroEnum
from data.room.room_enums import RoomEnum

hero_name_mapper = {
    HeroEnum.RONIN: "The Ronin",
    HeroEnum.WANDERER: "The Wanderer",
    HeroEnum.SHADOW: "The Shadow",
    HeroEnum.JUJITSUKA: "The Jujitsuka",
    HeroEnum.CHAIN_MASTER: "The Chain Master",
}

enemy_name_mapper = {
    EnemyEnum.SPIKE_CHARGER: "Spike Charger",
    EnemyEnum.ASHIGARU: "Ashigaru",
    EnemyEnum.ASHIGARU_ARCHER: "Ashigaru Archer",
    EnemyEnum.GUARDIAN: "Guardian",
    EnemyEnum.TWIN_TACHI: "Twin Tachi",
    EnemyEnum.YARI_MASTER: "Yari Master",
    EnemyEnum.YUMI_SNIPER: "Yumi Sniper",
    EnemyEnum.WARDEN: "Warden",
    EnemyEnum.STRIDER: "Strider",
    EnemyEnum.BLIGHT_CHARGER: "Blight Charger",
    EnemyEnum.BARRICADE: "Barricade",
    EnemyEnum.KABUKAI: "Kabukai",
    EnemyEnum.SHINOBI: "Shinobi",
    EnemyEnum.GRAPPLER: "Grappler",
    EnemyEnum.GRAPPLER_ALT: "Grappler",
    EnemyEnum.SUMMONER: "Summoner",
    EnemyEnum.SUMMONER_ALT: "Summoner",
    EnemyEnum.THORNS: "Thorns",
    EnemyEnum.SHADOW_CHARGER: "Shadow Charger",
    EnemyEnum.CORRUPTED_PROGENY: "Corrupted Progeny",
    EnemyEnum.THE_TWINS: "The Twins",
    EnemyEnum.THE_TWINS_A: "The A Twin",
    EnemyEnum.THE_TWINS_B: "The B Twin",
    EnemyEnum.NOBUNAGA: "Nobunaga the Wicked",
    EnemyEnum.FUMIKO: "Fumiko the Fallen",
    EnemyEnum.THE_SHOGUN: "The Shogun",
    EnemyEnum.THE_STATUE: "The Statue",
    EnemyEnum.THE_SHOGUN_PHASE_TWO: "The Shogun",
    EnemyEnum.REI: "Rei the Ruthless",
    EnemyEnum.IWAO: "Iwao the Impaler",
    EnemyEnum.BARU: "Baru the Barricader",
    EnemyEnum.KOWA: "Kowa the Coward",
    EnemyEnum.SATO: "Sato the Stagemaster",
    EnemyEnum.HIDEYOSHI: "Hideyoshi the Cunning",
    EnemyEnum.IEIASU: "Ieiasu the Cruel",
    EnemyEnum.DAISUKE: "Corrupted Daisuke",
    EnemyEnum.TRAP: "Trap",
}

room_boss_mapper = {
    RoomEnum.BAMBOO_GROVE: enemy_name_mapper[EnemyEnum.REI],
    RoomEnum.WHISPERING_CAVES: enemy_name_mapper[EnemyEnum.IWAO],
    RoomEnum.HIBIKU_WASTELANDS: enemy_name_mapper[EnemyEnum.BARU],
    RoomEnum.MOONLIT_PORT: enemy_name_mapper[EnemyEnum.THE_TWINS],
    RoomEnum.SPIRIT_GATEWAY: enemy_name_mapper[EnemyEnum.THE_STATUE],
    RoomEnum.HOT_SPRINGS: enemy_name_mapper[EnemyEnum.KOWA],
    RoomEnum.FORSAKEN_GROUNDS: enemy_name_mapper[EnemyEnum.FUMIKO],
    RoomEnum.THEATRE_OF_SHADOWS: enemy_name_mapper[EnemyEnum.SATO],
    RoomEnum.HIDEYOSHI: enemy_name_mapper[EnemyEnum.HIDEYOSHI],
    RoomEnum.NOBUNAGA: enemy_name_mapper[EnemyEnum.NOBUNAGA],
    RoomEnum.IEIASU: enemy_name_mapper[EnemyEnum.IEIASU],
    RoomEnum.SHOGUN: enemy_name_mapper[EnemyEnum.THE_SHOGUN],
}

enemy_elite_name_mapper = {
    EnemyEliteEnum.NOT_ELITE: "",
    EnemyEliteEnum.REACTIVE_SHIELD: "Reactive Shield",
    EnemyEliteEnum.DOUBLE_STRIKER: "Double Striker",
    EnemyEliteEnum.HEAVY: "Heavy",
    EnemyEliteEnum.QUICK: "Quick",
    EnemyEliteEnum.CORRUPTED: "Corrupted",
}
