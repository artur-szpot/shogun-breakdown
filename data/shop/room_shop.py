from typing import List, Dict, Optional

from constants import RIGHT_SHOP_TYPE, SHOP_ROOM, LEFT_SHOP_TYPE, FREE_POTION, SHOP_DATA, ALREADY_UPGRADED, \
    SHOP_ITEMS_SALE, SHOP_ITEM_NAMES, PRICE, REWARD, TILE_UPGRADE, IN_PROGRESS, CURRENT_LOCATION, MAP_SAVE, EXHAUSTED
from data.mappers import shop_mapper, upgrade_name_mapper
from data.room.room_enums import WeaponUpgradesEnum
from data.shop.shop_enums import ShopServiceEnum, ShopEnum, ShopType
from data.shop.shop_item import ShopItem
from data.shop.shop_mappers import shop_type_name_mapper, shop_types_mapper
from data.shop.shop_service import ShopService
from data.shop.shop_skill import ShopSkill
from data.skill.skill_enums import SkillEnum

shop_item_mapper = {
    "UnfriendlyFireShopItem": ShopSkill.of(SkillEnum.UNFRIENDLY_FIRE),
    "MindfulnessShopItem": ShopSkill.of(SkillEnum.MINDFULLNESS),
    "SniperShopItem": ShopSkill.of(SkillEnum.SNIPER),
    "BackStabberShopItem": ShopSkill.of(SkillEnum.BACK_STABBER),
    "CentralDominionShopItem": ShopSkill.of(SkillEnum.CENTRAL_DOMINION),
    "ComboCoinShopItem": ShopSkill.of(SkillEnum.COMBO_COIN),
    "TripleComboHealShopItem": ShopSkill.of(SkillEnum.TRIPLE_COMBO_HEAL),
    "ComboCurseShopItem": ShopSkill.of(SkillEnum.COMBO_CURSE),
    "DamagingMoveShopItem": ShopSkill.of(SkillEnum.DAMAGING_MOVE),
    "RogueRetailShopItem": ShopSkill.of(SkillEnum.ROGUE_RETAIL),
    "BigPocketsShopItem": ShopSkill.of(SkillEnum.BIG_POCKETS),
    "MonomancerShopItem": ShopSkill.of(SkillEnum.MONOMANCER),
    "CloseCombatShopItem": ShopSkill.of(SkillEnum.CLOSE_COMBAT),
    "OddCurseShopItem": ShopSkill.of(SkillEnum.ODD_CURSE),
    "ComboRechargeShopItem": ShopSkill.of(SkillEnum.COMBO_RECHARGE),
    "ComboDealShopItem": ShopSkill.of(SkillEnum.COMBO_DEAL),
    "KobushiComboShopItem": ShopSkill.of(SkillEnum.KOBUSHI_COMBO),
    "ComboBoonShopItem": ShopSkill.of(SkillEnum.COMBO_BOON),
    "ChillingComboShopItem": ShopSkill.of(SkillEnum.CHILLING_COMBO),
    "HealthyShopItem": ShopSkill.of(SkillEnum.HEALTHY),
    "FortressShopItem": ShopSkill.of(SkillEnum.FORTRESS),
    "ReactiveShieldShopItem": ShopSkill.of(SkillEnum.REACTIVE_SHIELD),
    "ShieldRetentionShopItem": ShopSkill.of(SkillEnum.SHIELD_RETENTION),
    "KarmaShopItem": ShopSkill.of(SkillEnum.KARMA),
    "ChillingBloodShopItem": ShopSkill.of(SkillEnum.CHILLING_BLOOD),
    "IronSkinShopItem": ShopSkill.of(SkillEnum.IRON_SKIN),
    "OverflowGuardShopItem": ShopSkill.of(SkillEnum.OVERFLOW_GUARD),
    "TwoWayMoveShopItem": ShopSkill.of(SkillEnum.TWO_WAY_MOVE),
    "QuickRecoveryShopItem": ShopSkill.of(SkillEnum.QUICK_RECOVERY),
    "DynamicBoostShopItem": ShopSkill.of(SkillEnum.DYNAMIC_BOOST),
    "CursingMoveShopItem": ShopSkill.of(SkillEnum.CURSING_MOVE),
    "ChikaraCrushShopItem": ShopSkill.of(SkillEnum.CHIKARA_CRUSH),
    "MamushiMoveShopItem": ShopSkill.of(SkillEnum.MAMUSHI_MOVE),
    "TwoFacedDangerShopItem": ShopSkill.of(SkillEnum.TWO_FACED_DANGER),
    "FenghuangsFeatherShopItem": ShopSkill.of(SkillEnum.FENGHUANGS_FEATHER),
    "SeiryusScaleShopItem": ShopSkill.of(SkillEnum.SEIRUYS_SCALE),

    "EdamameBrewShopItem": ShopItem.edamame(),

    "RerollForHp": ShopService.of(ShopServiceEnum.REROLL_FOR_HP),
    "SkullsForCoins": ShopService.of(ShopServiceEnum.MONEY_FOR_SKULLS),
    "FullHealForSkulls": ShopService.of(ShopServiceEnum.FULL_HEAL_FOR_SKULLS),
    "BloodExchange": ShopService.of(ShopServiceEnum.MONEY_FOR_HP),
}


class ShopRoom:
    available_upgrade: int
    upgrade_price: int
    items: List[ShopItem]
    already_upgraded: bool  # TODO what does that mean?
    free_potion: bool
    shop_types: List[ShopType]
    location: ShopEnum
    exhausted: bool

    def __init__(self,
                 available_upgrade: int,
                 upgrade_price: int,
                 items: List[ShopItem],
                 already_upgraded: bool,
                 free_potion: bool,
                 shop_types: List[ShopType],
                 location: ShopEnum,
                 exhausted: bool,
                 ):
        self.available_upgrade = available_upgrade
        self.upgrade_price = upgrade_price
        self.items = items
        self.already_upgraded = already_upgraded
        self.free_potion = free_potion
        self.shop_types = shop_types
        self.location = location
        self.exhausted = exhausted

    @staticmethod
    def from_dict(source: Dict):
        if not source[SHOP_ROOM][REWARD][IN_PROGRESS]:
            return None
        available_upgrade = source[SHOP_ROOM][REWARD][TILE_UPGRADE]
        price = source[SHOP_ROOM][REWARD][PRICE]
        exhausted = source[SHOP_ROOM][REWARD][EXHAUSTED]
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
            exhausted=exhausted,
        )

    def pretty_print_shop(self) -> str:
        return " + ".join(shop_type_name_mapper[t] for t in self.shop_types)

    def pretty_print_everything(self) -> List[str]:
        up = WeaponUpgradesEnum(self.available_upgrade)
        retval = [f"{upgrade_name_mapper.get(up, f'Unknown upgrade {self.available_upgrade}')} "
                  f"({self.upgrade_price} coins)"]
        retval.extend(self.pretty_print_items())
        return retval

    def pretty_print_items(self) -> List[str]:
        return [item.pretty_print() for item in self.items]

    def get_service(self) -> Optional[ShopService]:
        for item in self.items:
            if isinstance(item, ShopService):
                return item
        return None
