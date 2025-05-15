from typing import Optional


class ShopItem:
    code: str
    edamame: bool
    missing: Optional[str]
    price: int
    on_sale: bool

    def __init__(self, code: str, price: int, edamame: bool = False):
        self.code = code
        self.price = price
        self.on_sale = False
        self.edamame = edamame

    @staticmethod
    def edamame():
        return ShopItem("EdamameBrewShopItem", 5, True)

    @staticmethod
    def missing(name: str):
        retval = ShopItem(name, -1)
        retval.missing = name
        return retval

    def sale(self):
        self.on_sale = True
        self.price = 2

    def pretty_print(self):
        if self.edamame:
            return f"Edamame Brew ({self.price} coins{' (sale!)' if self.on_sale else ''})"
        return f"Unknown Item \"{self.missing}\" ({self.price} coins{' (sale!)' if self.on_sale else ''})"

    def sale_print(self):
        if self.edamame:
            return f"Purchased Edamame Brew for {self.price} coins"
        return f"Purchased Unknown Item \"{self.missing}\" for {self.price} coins"

    def is_equal(self, other):
        return self.edamame == other.edamame \
               and self.price == other.price \
               and self.on_sale == other.on_sale
