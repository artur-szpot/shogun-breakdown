from data.snapshot.prediction_error import PredictionError


class EntityState:
    shield: bool
    curse: bool
    ice: int
    poison: int

    def __init__(self,
                 shield: bool,
                 curse: bool,
                 ice: int,
                 poison: int):
        self.shield = shield
        self.curse = curse
        self.ice = ice
        self.poison = poison

    @staticmethod
    def fresh():
        return EntityState(
            shield=False,
            curse=False,
            ice=0,
            poison=0,
        )

    def clone(self):
        return EntityState(
            shield=self.shield,
            curse=self.curse,
            ice=self.ice,
            poison=self.poison,
        )

    def is_equal(self, other, debug: str = None):
        if not debug:
            return self.shield == other.shield and \
                   self.curse == other.curse and \
                   self.ice == other.ice and \
                   self.poison == other.poison
        if self.shield != other.shield:
            raise PredictionError(f"wrong shield state ({debug})")
        if self.curse != other.curse:
            raise PredictionError(f"wrong curse state ({debug})")
        if self.ice != other.ice:
            raise PredictionError(f"wrong ice state ({debug})")
        if self.poison != other.poison:
            raise PredictionError(f"wrong poison state ({debug})")
        return True

    def debug_print(self):
        retval = ""
        if self.curse:
            retval += "C"
        if self.shield:
            retval += "S"
        for i in range(self.ice):
            retval += "I"
        for i in range(self.poison):
            retval += "P"
        return retval

    def pass_turn(self):
        if self.ice > 0:
            self.ice -= 1
        if self.poison > 0:
            self.poison -= 1
