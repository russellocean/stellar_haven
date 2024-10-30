from enum import Enum


class TileType(Enum):
    EMPTY = 0
    FLOOR = 1
    WALL = 2
    DOOR = 3

    @property
    def is_walkable(self) -> bool:
        return self in (TileType.FLOOR, TileType.DOOR)
