from data.shop.shop_enums import ShopServiceEnum
from data.shop.shop_item import ShopItem


class ShopService(ShopItem):
    service: ShopServiceEnum

    def __init__(self, price: int, service: ShopServiceEnum):
        super().__init__(price)
        self.service = service

    @staticmethod
    def of(service: ShopServiceEnum):
        price = -1
        if service == ShopServiceEnum.MONEY_FOR_HP:
            price = 2
        elif service == ShopServiceEnum.REROLL_FOR_HP:
            price = 1
        elif service == ShopServiceEnum.MONEY_FOR_SKULLS:
            price = 70  # TODO gives 15 coins
        elif service == ShopServiceEnum.FULL_HEAL_FOR_SKULLS:
            price = 35
        return ShopService(price, service)

    def sale(self):
        self.on_sale = True
        self.price = 1

    def print_values(self):
        price_in = "HP"
        service_name = ""
        if self.service == ShopServiceEnum.REROLL_FOR_HP:
            service_name = "Restock Shop"  # TODO find out real names
        elif self.service == ShopServiceEnum.FULL_HEAL_FOR_SKULLS:
            price_in = "skulls"
            service_name = "Bone Soup"
        elif self.service == ShopServiceEnum.MONEY_FOR_HP:
            service_name = "Blood Exchange"
        elif self.service == ShopServiceEnum.MONEY_FOR_SKULLS:
            price_in = "skulls"
            service_name = "Skull Money"  # TODO find out real names
        return price_in, service_name

    def pretty_print(self):
        price_in, service_name = self.print_values()
        return f"{service_name} ({self.price} {price_in}{' (sale!)' if self.on_sale else ''})"

    def sale_print(self):
        price_in, service_name = self.print_values()
        return f"Purchased {service_name} for {self.price} {price_in}"

    def is_equal(self, other):
        return self.service == other.service \
               and self.price == other.price \
               and self.on_sale == other.on_sale
