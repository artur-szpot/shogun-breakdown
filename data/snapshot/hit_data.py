class HitData:
    hits: int
    targets_hit: int
    kills: int

    def __init__(self, hits: int, targets_hit: int, kills: int):
        self.hits = hits
        self.targets_hit = targets_hit
        self.kills = kills

    @staticmethod
    def empty():
        return HitData(hits=0, targets_hit=0, kills=0)

    def merge(self, other):
        self.hits = self.hits + other.hits
        self.targets_hit = self.targets_hit + other.targets_hit
        self.kills = self.kills + other.kills
