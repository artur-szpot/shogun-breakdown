from typing import Optional

from data.room.room_enums import PickupEnum
from data.shop.shop_enums import ShopServiceEnum
from data.snapshot.snapshot import Snapshot
from history.history import History
from logger import logger


def entered_shop(history: History, previous_snapshot: Optional[Snapshot], new_snapshot: Snapshot) -> History:
    if previous_snapshot is None:
        logger.detail_info("== IN A SHOP ==")
    else:
        logger.detail_info("== ENTERED A SHOP ==")
    logger.detail_info(f"== {new_snapshot.get_room()} ==")
    logger.detail_info(f"== {new_snapshot.shop.pretty_print_shop()} ==")
    logger.line()
    for item in new_snapshot.shop.pretty_print_everything():
        logger.detail_text(item)
    logger.line()
    return history


def shop_update(history: History, previous_snapshot: Snapshot, new_snapshot: Snapshot) -> History:
    old_shop = previous_snapshot.shop
    old_service = old_shop.get_service_type()
    new_shop = new_snapshot.shop
    new_service = new_shop.get_service_type()

    # Potion update
    new_potion_ids = history.potions.shop_update(previous_snapshot, new_snapshot)

    # Was the shop restocked?
    was_restocked = len(new_shop.items) > len(old_shop.items) \
                    or (old_service == ShopServiceEnum.REROLL_FOR_HP
                        and (new_service is None or new_service != ShopServiceEnum.REROLL_FOR_HP))

    # If not, was any item purchased?
    if len(new_shop.items) < len(old_shop.items):
        for index, old_item in enumerate(old_shop.items):
            if index == len(new_shop.items) \
                    or not isinstance(old_item, type(new_shop.items[index])) \
                    or not isinstance(new_shop.items[index], type(old_item)) \
                    or not old_item.is_equal(new_shop.items[index]):
                logger.detail_success(old_item.sale_print())
                if old_item.edamame:
                    history.potions.queue_potion([PickupEnum.EDAMAME_BREW])
                    history.potions.shop_update(previous_snapshot, new_snapshot)
                return history

    # Potion update
    history.potions.process_queue(new_potion_ids)

    # Restock update
    if was_restocked:
        if previous_snapshot.room.hero.hp.hp >= new_snapshot.room.hero.hp.hp:
            raise ValueError("Blood price has not been paid!")
            # TODO account for potions everywhere!
        logger.detail_info("The shop has been restocked. New inventory:")
        for item in new_snapshot.shop.pretty_print_items():
            logger.detail_info(item)
        logger.line()
        return history

    # TODO What is this value?
    if new_shop.already_upgraded != old_shop.already_upgraded:
        logger.debug_info("DEBUG: alreadyUpgraded value changed")

    # Was the upgrade purchased?
    if new_shop.upgrade_price != old_shop.upgrade_price:
        logger.detail_success(f"Purchased the upgrade. Price increased to {new_shop.upgrade_price} coins.")
        return history

    # Was the service (other than restock) purchased?
    if old_service is not None and new_service is None:
        logger.detail_success(old_service.sale_print())
        return history

    return history
