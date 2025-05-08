from typing import List, Optional

from data.snapshot.prediction_error import PredictionError


class EntityPosition:
    cell: int
    facing: int
    died_in: Optional[int]

    def __init__(self,
                 cell: int,
                 facing: int,
                 died_in: Optional[int] = None
                 ):
        self.cell = cell
        self.facing = facing
        self.died_in = died_in

    def clone(self):
        return EntityPosition(
            cell=self.cell,
            facing=self.facing,
            died_in=self.died_in,
        )

    def clone_on_death(self):
        return EntityPosition(
            cell=self.get_death_cell(),
            facing=self.facing,
        )

    def is_equal(self, other, facing_matters: bool = True, debug: str = None):
        if not debug:
            return self.cell == other.cell and \
                   (not facing_matters or self.facing == other.facing)
        if self.cell != other.cell:
            raise PredictionError(f"wrong cell ({debug}) self: {self.cell} other: {other.cell}")
        if facing_matters and self.facing != other.facing:
            raise PredictionError(f"wrong facing ({debug})")
        return True

    def flip(self):
        self.facing = 1 if self.facing == 0 else 0

    def facing_right(self) -> bool:
        return self.facing == 1

    def get_spaces(self, positions: List[int]) -> List[int]:
        direction = 1 if self.facing_right() else -1
        return [self.cell + position * direction for position in positions]

    def get_direction(self):
        return 1 if self.facing == 1 else -1

    def get_direction_towards(self, other):
        return 1 if self.cell - other.position.cell < 0 else -1

    def get_death_cell(self):
        return self.died_in if self.died_in is not None else self.cell
