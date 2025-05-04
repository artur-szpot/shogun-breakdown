from data.snapshot.prediction_error import PredictionError


class EntityHp:
    hp: int
    max_hp: int

    def __init__(self,
                 hp: int,
                 max_hp: int):
        self.hp = hp
        self.max_hp = max_hp

    def clone(self):
        return EntityHp(
            hp=self.hp,
            max_hp=self.max_hp
        )

    def is_equal(self, other, debug: str = None):
        if not debug:
            return self.hp == other.hp and \
                   self.max_hp == other.max_hp
        if self.hp != other.hp:
            raise PredictionError(f"wrong hp ({debug}) self: {self.hp} other: {other.hp}")
        if self.max_hp != other.max_hp:
            raise PredictionError(f"wrong max_hp ({debug})")
        return True
