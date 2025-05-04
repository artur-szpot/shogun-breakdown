from data.mappers import skill_mapper
from data.shop.shop_item import ShopItem
from data.shop.shop_mappers import skill_price_mapper
from data.skill.skill_enums import SkillEnum


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

    def pretty_print(self):
        return f"{skill_mapper[self.skill]} ({self.price} coins{' (sale!)' if self.on_sale else ''})"

    def sale_print(self):
        return f"Purchased {skill_mapper[self.skill]} for {self.price} coins"

    def is_equal(self, other):
        return self.skill == other.skill \
               and self.price == other.price \
               and self.on_sale == other.on_sale
