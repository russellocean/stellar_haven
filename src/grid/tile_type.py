from enum import Enum, auto


class TileType(Enum):
    EMPTY = auto()
    WALL = auto()
    DECORATION = auto()
    PLANET = auto()
    STAR = auto()
    DOOR = auto()
    WINDOW = auto()
    FURNITURE = auto()
    BACKGROUND = auto()
    INTERIOR_BACKGROUND = auto()
    EXTERIOR = auto()
    CORNER = auto()
    PLATFORM = auto()
    INTERACTABLE = auto()

    @property
    def is_walkable(self) -> bool:
        """Return True if the tile type can be walked through"""
        return self in (
            TileType.EMPTY,
            TileType.DOOR,
            TileType.INTERIOR_BACKGROUND,
            TileType.BACKGROUND,
            TileType.PLATFORM,  # Platform is special case, handled separately for dropping
            TileType.DECORATION,  # Decorations should be walkable
            TileType.FURNITURE,  # Furniture should be walkable
        )

    @property
    def blocks_movement(self) -> bool:
        """Return True if the tile type blocks movement"""
        return self in (TileType.WALL, TileType.CORNER, TileType.EXTERIOR)
