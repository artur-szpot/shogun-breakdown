from typing import List

from enums import SkillEnum, ShopEnum


class SkillHistory:
    skill: SkillEnum
    level: int
    acquired: ShopEnum
    leveled_up: List[ShopEnum]
    money_spent_on: int

    def __init__(self, skill: SkillEnum, price: int, shop: ShopEnum):
        self.skill = skill
        self.acquired = shop
        self.level = 1
        self.leveled_up = []
        self.money_spent_on = price

    def level_up(self, shop: ShopEnum, price: int):
        self.level += 1
        self.leveled_up.append(shop)
        self.money_spent_on += price


class SkillsHistory:
    skills: List[SkillHistory]

    def __init__(self):
        self.skills = []
