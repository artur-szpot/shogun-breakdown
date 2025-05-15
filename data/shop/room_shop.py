from typing import List, Dict, Optional

from constants import RIGHT_SHOP_TYPE, SHOP_ROOM, LEFT_SHOP_TYPE, FREE_POTION, SHOP_DATA, ALREADY_UPGRADED, \
    SHOP_ITEMS_SALE, SHOP_ITEM_NAMES, PRICE, REWARD, TILE_UPGRADE, IN_PROGRESS, CURRENT_LOCATION, MAP_SAVE, EXHAUSTED, \
    FREE_POTION_ALREADY_GIVEN, TILE_REWARDS
from data.mappers import upgrade_name_mapper
from data.room.room_enums import WeaponUpgradesEnum
from data.shop.shop_enums import ShopServiceEnum, ShopEnum, ShopType
from data.shop.shop_item import ShopItem
from data.shop.shop_mappers import shop_type_name_mapper
from data.shop.shop_service import ShopService
from data.shop.shop_skill import ShopSkill
from data.skill.skill_enums import SkillEnum

shop_item_mapper = {
    "UnfriendlyFireShopItem": ShopSkill.of("UnfriendlyFireShopItem", SkillEnum.UNFRIENDLY_FIRE),
    "MindfulnessShopItem": ShopSkill.of("MindfulnessShopItem", SkillEnum.MINDFULLNESS),
    "SniperShopItem": ShopSkill.of("SniperShopItem", SkillEnum.SNIPER),
    "BackStabberShopItem": ShopSkill.of("BackStabberShopItem", SkillEnum.BACK_STABBER),
    "CentralDominionShopItem": ShopSkill.of("CentralDominionShopItem", SkillEnum.CENTRAL_DOMINION),
    "ComboCoinShopItem": ShopSkill.of("ComboCoinShopItem", SkillEnum.COMBO_COIN),
    "TripleComboHealShopItem": ShopSkill.of("TripleComboHealShopItem", SkillEnum.TRIPLE_COMBO_HEAL),
    "ComboCurseShopItem": ShopSkill.of("ComboCurseShopItem", SkillEnum.COMBO_CURSE),
    "DamagingMoveShopItem": ShopSkill.of("DamagingMoveShopItem", SkillEnum.DAMAGING_MOVE),
    "RogueRetailShopItem": ShopSkill.of("RogueRetailShopItem", SkillEnum.ROGUE_RETAIL),
    "BigPocketsShopItem": ShopSkill.of("BigPocketsShopItem", SkillEnum.BIG_POCKETS),
    "MonomancerShopItem": ShopSkill.of("MonomancerShopItem", SkillEnum.MONOMANCER),
    "CloseCombatShopItem": ShopSkill.of("CloseCombatShopItem", SkillEnum.CLOSE_COMBAT),
    "OddCurseShopItem": ShopSkill.of("OddCurseShopItem", SkillEnum.ODD_CURSE),
    "ComboRechargeShopItem": ShopSkill.of("ComboRechargeShopItem", SkillEnum.COMBO_RECHARGE),
    "ComboDealShopItem": ShopSkill.of("ComboDealShopItem", SkillEnum.COMBO_DEAL),
    "KobushiComboShopItem": ShopSkill.of("KobushiComboShopItem", SkillEnum.KOBUSHI_COMBO),
    "ComboBoonShopItem": ShopSkill.of("ComboBoonShopItem", SkillEnum.COMBO_BOON),
    "ChillingComboShopItem": ShopSkill.of("ChillingComboShopItem", SkillEnum.CHILLING_COMBO),
    "HealthyShopItem": ShopSkill.of("HealthyShopItem", SkillEnum.HEALTHY),
    "FortressShopItem": ShopSkill.of("FortressShopItem", SkillEnum.FORTRESS),
    "ReactiveShieldShopItem": ShopSkill.of("ReactiveShieldShopItem", SkillEnum.REACTIVE_SHIELD),
    "ShieldRetentionShopItem": ShopSkill.of("ShieldRetentionShopItem", SkillEnum.SHIELD_RETENTION),
    "KarmaShopItem": ShopSkill.of("KarmaShopItem", SkillEnum.KARMA),
    "ChillingBloodShopItem": ShopSkill.of("ChillingBloodShopItem", SkillEnum.CHILLING_BLOOD),
    "IronSkinShopItem": ShopSkill.of("IronSkinShopItem", SkillEnum.IRON_SKIN),
    "OverflowGuardShopItem": ShopSkill.of("OverflowGuardShopItem", SkillEnum.OVERFLOW_GUARD),
    "TwoWayMoveShopItem": ShopSkill.of("TwoWayMoveShopItem", SkillEnum.TWO_WAY_MOVE),
    "QuickRecoveryShopItem": ShopSkill.of("QuickRecoveryShopItem", SkillEnum.QUICK_RECOVERY),
    "DynamicBoostShopItem": ShopSkill.of("DynamicBoostShopItem", SkillEnum.DYNAMIC_BOOST),
    "CursingMoveShopItem": ShopSkill.of("CursingMoveShopItem", SkillEnum.CURSING_MOVE),
    "ChikaraCrushShopItem": ShopSkill.of("ChikaraCrushShopItem", SkillEnum.CHIKARA_CRUSH),
    "MamushiMoveShopItem": ShopSkill.of("MamushiMoveShopItem", SkillEnum.MAMUSHI_MOVE),
    "TwoFacedDangerShopItem": ShopSkill.of("TwoFacedDangerShopItem", SkillEnum.TWO_FACED_DANGER),
    "FenghuangFeatherShopItem": ShopSkill.of("FenghuangFeatherShopItem", SkillEnum.FENGHUANGS_FEATHER),
    "SeiryuScaleShopItem": ShopSkill.of("SeiryuScaleShopItem", SkillEnum.SEIRUYS_SCALE),

    "EdamameBrewShopItem": ShopItem.edamame(),

    "RerollForHp": ShopService.of("RerollForHp", ShopServiceEnum.REROLL_FOR_HP),
    "SkullsForCoins": ShopService.of("SkullsForCoins", ShopServiceEnum.MONEY_FOR_SKULLS),
    "FullHealForSkulls": ShopService.of("FullHealForSkulls", ShopServiceEnum.FULL_HEAL_FOR_SKULLS),
    "BloodExchange": ShopService.of("BloodExchange", ShopServiceEnum.MONEY_FOR_HP),
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
        shop_types = [ShopType(left_type), ShopType(right_type)]
        location_raw = source[MAP_SAVE][CURRENT_LOCATION]
        location = ShopEnum(location_raw)
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

    @staticmethod
    def empty_dict():
        return {
            REWARD: {
                IN_PROGRESS: False,
                TILE_UPGRADE: 0,
                TILE_REWARDS: [],
                PRICE: 0,
                EXHAUSTED: False,
            },
            SHOP_DATA: {
                SHOP_ITEM_NAMES: [],
                SHOP_ITEMS_SALE: [],
                ALREADY_UPGRADED: False,
                FREE_POTION: False,
                FREE_POTION_ALREADY_GIVEN: False,
            },
            LEFT_SHOP_TYPE: '',
            RIGHT_SHOP_TYPE: '',
        }

    def to_dict_reward(self):
        return {
            REWARD: {
                IN_PROGRESS: True,
                TILE_UPGRADE: self.available_upgrade,
                PRICE: self.upgrade_price,
                EXHAUSTED: self.exhausted,
            },
        }

    def to_dict(self):
        return {
            SHOP_ROOM: {
                REWARD: {
                    IN_PROGRESS: True,
                    TILE_UPGRADE: self.available_upgrade,
                    PRICE: self.upgrade_price,
                    EXHAUSTED: self.exhausted,
                },
                SHOP_DATA: {
                    SHOP_ITEM_NAMES: [i.code for i in self.items],
                    SHOP_ITEMS_SALE: [i.on_sale for i in self.items],
                    ALREADY_UPGRADED: self.already_upgraded,
                    FREE_POTION: self.free_potion,
                    FREE_POTION_ALREADY_GIVEN: True,
                },
                LEFT_SHOP_TYPE: self.shop_types[0].value,
                RIGHT_SHOP_TYPE: self.shop_types[1].value,
            }
        }

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
