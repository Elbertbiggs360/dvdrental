from enum import Enum, auto, unique

@unique
class Ratings(Enum):
    PG = auto()
    G = auto()
    NC17 = auto()
    PG13 = auto()