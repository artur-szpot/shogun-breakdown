from typing import Dict, List, Optional, Tuple

from data.entity.entity_position import EntityPosition
from data.weapon.weapon import Weapon


class CorruptedWave:
    strength: int
    position: EntityPosition

    # TODO: does the Shogun wave heal him?

    def __init__(self, strength: int, position: EntityPosition):
        self.strength = strength
        self.position = position

    def clone(self):
        return CorruptedWave(
            strength=self.strength,
            position=self.position.clone(),
        )


class RoomHistory:
    traps: Dict[int, int]  # cell: strength
    thorns: Dict[int, Weapon]  # cell: weapon
    bombs: Dict[int, List[List[int]]]  # cell: time, strength
    corrupted_waves: List[CorruptedWave]

    def __init__(self):
        self.traps = {}
        self.corrupted_waves = []
        self.bombs = {}
        self.thorns = {}

    def hit_thorns(self, cell: int) -> Optional[Weapon]:
        if cell not in self.thorns:
            return None
        thorns = self.thorns[cell]
        del self.thorns[cell]
        return thorns

    def summon_thorns(self, cell: int, weapon: Weapon):
        if cell not in self.thorns:
            self.thorns[cell] = weapon

    def check_trap(self, cell: int) -> Optional[int]:
        if cell not in self.traps:
            return None
        strength = self.traps[cell]
        del self.traps[cell]
        return strength

    def set_trap(self, cell: int, strength: int):
        if cell not in self.traps:
            self.traps[cell] = strength

    def move_corrupted_waves(self, board_size: int):
        keep_waves = []
        for wave in self.corrupted_waves:
            wave.position += wave.position.get_direction()
            if 0 <= wave.position.cell < board_size:
                keep_waves.append(wave)
        self.corrupted_waves = keep_waves

    def spawn_corrupted_wave(self, cell: int, facing: int, strength: int):
        self.corrupted_waves.append(
            CorruptedWave(
                strength=strength,
                position=EntityPosition(cell=cell, facing=facing)
            )
        )

    def add_bomb(self, cell: int, strength: int):
        if cell not in self.bombs:
            self.bombs[cell] = []
        self.bombs[cell].append([2, strength])

    def tick_bombs(self) -> List[List[int]]:  # cell, strength of blow ups
        explosions = []
        bombs_kept = {}
        for cell, bombs in self.bombs.items():
            for bomb in bombs:
                bomb[0] -= 1
                if bomb[0]:
                    if cell not in bombs_kept:
                        bombs_kept[cell] = []
                    bombs_kept[cell].append(bomb)
                else:
                    explosions.append([cell, bomb[1]])
        self.bombs = bombs_kept
        return explosions
