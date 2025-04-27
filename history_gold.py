class GoldHistory:
    earned_in_battle: int
    earned_from_self_harm: int

    spent_on_using_weapons: int
    spent_on_gambling: int
    spent_on_skills: int
    spent_on_potions: int
    spent_on_upgrades: int

    def __init__(self):
        self.earned_in_battle = 0
        self.earned_from_self_harm = 0
        self.spent_on_using_weapons = 0
        self.spent_on_gambling = 0
        self.spent_on_skills = 0
        self.spent_on_potions = 0
        self.spent_on_upgrades = 0
