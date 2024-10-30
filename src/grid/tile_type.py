from enum import Enum, auto


class TileType(Enum):
    EMPTY = auto()
    WALL = auto()
    FLOOR = auto()
    DOOR = auto()
    CORNER = auto()
    BACKGROUND = auto()

    @property
    def is_walkable(self) -> bool:
        return self in (TileType.FLOOR, TileType.DOOR)
