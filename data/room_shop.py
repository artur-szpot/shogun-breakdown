from typing import List, Dict, Optional

from constants import RIGHT_SHOP_TYPE, SHOP_ROOM, LEFT_SHOP_TYPE, FREE_POTION, SHOP_DATA, ALREADY_UPGRADED, \
    SHOP_ITEMS_SALE, SHOP_ITEM_NAMES, PRICE, REWARD, TILE_UPGRADE, IN_PROGRESS, CURRENT_LOCATION, MAP_SAVE
from data.mappers import shop_mapper
from enums import ShopServiceEnum, ShopType, SkillEnum, ShopEnum

skill_price_mapper = {
    SkillEnum.UNFRIENDLY_FIRE: -1,
    SkillEnum.MINDFULLNESS: -1,
    SkillEnum.BIG_POCKETS: -1,
    SkillEnum.ROGUE_RETAIL: -1,
    SkillEnum.BACK_STABBER: -1,
    SkillEnum.SNIPER: -1,
    SkillEnum.MONOMANCER: -1,
    SkillEnum.CLOSE_COMBAT: -1,
    SkillEnum.CENTRAL_DOMINION: -1,
    SkillEnum.ODD_CURSE: -1,
    SkillEnum.COMBO_COIN: -1,
    SkillEnum.COMBO_RECHARGE: -1,
    SkillEnum.TRIPLE_COMBO_HEAL: -1,
    SkillEnum.COMBO_CURSE: -1,
    SkillEnum.COMBO_DEAL: -1,
    SkillEnum.KOBUSHI_COMBO: -1,
    SkillEnum.COMBO_BOON: -1,
    SkillEnum.CHILLING_COMBO: -1,
    SkillEnum.HEALTHY: -1,
    SkillEnum.FORTRESS: -1,
    SkillEnum.REACTIVE_SHIELD: -1,
    SkillEnum.SHIELD_RETENTION: -1,
    SkillEnum.KARMA: -1,
    SkillEnum.CHILLING_BLOOD: -1,
    SkillEnum.IRON_SKIN: -1,
    SkillEnum.OVERFLOW_GUARD: -1,
    SkillEnum.TWO_WAY_MOVE: -1,
    SkillEnum.QUICK_RECOVERY: -1,
    SkillEnum.DAMAGING_MOVE: -1,
    SkillEnum.DYNAMIC_BOOST: -1,
    SkillEnum.CURSING_MOVE: -1,
    SkillEnum.CHIKARA_CRUSH: -1,
    SkillEnum.MAMUSHI_MOVE: -1,
    SkillEnum.TWO_FACED_DANGER: -1,
    SkillEnum.FENGHUANGS_FEATHER: -1,
    SkillEnum.SEIRUYS_SCALE: -1,
}


class ShopItem:
    edamame: bool
    missing: Optional[str]
    price: int
    on_sale: bool

    def __init__(self, price: int, edamame: bool = False):
        self.price = price
        self.on_sale = False
        self.edamame = edamame

    @staticmethod
    def edamame():
        return ShopItem(5, True)

    @staticmethod
    def missing(name: str):
        retval = ShopItem(-1)
        retval.missing = name
        return retval

    def sale(self):
        self.on_sale = True
        self.price = 2


class ShopSkill(ShopItem):
    skill: SkillEnum

    def __init__(self, price: int, skill: SkillEnum):
        super().__init__(price)
        self.skill = skill

    @staticmethod
    def of(skill: SkillEnum):
        price = skill_price_mapper.get(skill, -1)
        return ShopSkill(price, skill)

    def sale(self):
        self.on_sale = True
        self.price = self.price // 2


class ShopService(ShopItem):
    service: ShopServiceEnum

    def __init__(self, price: int, service: ShopServiceEnum):
        super().__init__(price)
        self.service = service

    @staticmethod
    def of(service: ShopServiceEnum):
        price = 2
        return ShopService(price, service)

    def sale(self):
        self.on_sale = True
        self.price = 1


shop_types_mapper = {
    "DamageUpgrade": ShopType.DAMAGE,
    "CooldownUpgrade": ShopType.COOLDOWN,
    "SacrificeTile": ShopType.SACRIFICE,
    "WarringShop": ShopType.WARRING,
    "ComboShop": ShopType.COMBO,
    "DancerShop": ShopType.DANCER,
    "GuardingShop": ShopType.GUARDING,
    "MaxLevelUpgrade": ShopType.SLOT,
    "EnchantUpgrade": ShopType.ENCHANT,
    "MoonlitPortShop": ShopType.MOONLIT_PORT,
}

shop_item_mapper = {
    "UnfriendlyFireShopItem": ShopSkill.of(SkillEnum.UNFRIENDLY_FIRE),
    "MindfulnessShopItem": ShopSkill.of(SkillEnum.MINDFULLNESS),
    "EdamameBrewShopItem": ShopItem.edamame(),
    "RerollForHp": ShopService.of(ShopServiceEnum.REROLL_FOR_HP),
}


class ShopRoom:
    available_upgrade: int
    upgrade_price: int
    items: List[ShopItem]
    already_upgraded: bool  # TODO what does that mean?
    free_potion: bool
    shop_types: List[ShopType]
    location: ShopEnum

    def __init__(self,
                 available_upgrade: int,
                 upgrade_price: int,
                 items: List[ShopItem],
                 already_upgraded: bool,
                 free_potion: bool,
                 shop_types: List[ShopType],
                 location: ShopEnum
                 ):
        self.available_upgrade = available_upgrade
        self.upgrade_price = upgrade_price
        self.items = items
        self.already_upgraded = already_upgraded
        self.free_potion = free_potion
        self.shop_types = shop_types
        self.location = location

    @staticmethod
    def from_dict(source: Dict):
        if not source[SHOP_ROOM][REWARD][IN_PROGRESS]:
            return None
        available_upgrade = source[SHOP_ROOM][REWARD][TILE_UPGRADE]
        price = source[SHOP_ROOM][REWARD][PRICE]
        items_raw = source[SHOP_ROOM][SHOP_DATA][SHOP_ITEM_NAMES]
        items_on_sale = source[SHOP_ROOM][SHOP_DATA][SHOP_ITEMS_SALE]
        if len(items_raw) != len(items_on_sale):
            raise ValueError("Number of items and their sale statuses must be equal")
        items = []
        for i in range(len(items_raw)):
            code = items_raw[i]
            new_item = shop_item_mapper.get(code, ShopItem.missing(code))
            if items_on_sale[i]:
                new_item.sale()
            items.append(new_item)
        already_upgraded = source[SHOP_ROOM][SHOP_DATA][ALREADY_UPGRADED]
        free_potion = source[SHOP_ROOM][SHOP_DATA][FREE_POTION]
        left_type = source[SHOP_ROOM][LEFT_SHOP_TYPE]
        right_type = source[SHOP_ROOM][RIGHT_SHOP_TYPE]
        if left_type not in shop_types_mapper:
            raise ValueError(f"Missing shop translation for {left_type}")
        if right_type not in shop_types_mapper:
            raise ValueError(f"Missing shop translation for {right_type}")
        shop_types = [shop_types_mapper[left_type], shop_types_mapper[right_type]]
        location_raw = source[MAP_SAVE][CURRENT_LOCATION]
        location = shop_mapper.get(location_raw, None)
        if location is None:
            raise ValueError(f"Unknown shop location: {location_raw}")
        return ShopRoom(
            available_upgrade=available_upgrade,
            upgrade_price=price,
            items=items,
            already_upgraded=already_upgraded,
            free_potion=free_potion,
            shop_types=shop_types,
            location=location,
        )
