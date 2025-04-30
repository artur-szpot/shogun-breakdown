class HitData:
    hits: int
    targets_hit: int

    def __init__(self, hits: int, targets_hit: int):
        self.hits = hits
        self.targets_hit = targets_hit

    @staticmethod
    def empty():
        return HitData(hits=0, targets_hit=0)

    def merge(self, other):
        return HitData(
            hits=self.hits + other.hits,
            targets_hit=self.targets_hit + other.targets_hit,
        )
