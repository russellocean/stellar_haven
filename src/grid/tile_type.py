from enum import Enum, auto


class TileType(Enum):
    EMPTY = auto()
    WALL = auto()
    DECORATION = auto()
    PLANET = auto()
    STAR = auto()
    DOOR = auto()
    FLOOR = auto()
    WINDOW = auto()
    FURNITURE = auto()
    BACKGROUND = auto()
    INTERIOR_BACKGROUND = auto()
    EXTERIOR = auto()
    CORNER = auto()

    @property
    def is_walkable(self) -> bool:
        return self in (TileType.FLOOR, TileType.DOOR)
