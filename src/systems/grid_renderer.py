import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager


class GridRenderer:
    def __init__(self, grid, tile_size=16):
        self.grid = grid
        self.tile_size = tile_size
        self.asset_manager = AssetManager()
        self.camera = None

        # Initialize texture mappings
        self.textures = {
            TileType.WALL: {
                "horizontal": self.asset_manager.get_tilemap_group("light_top_center"),
                "vertical": self.asset_manager.get_tilemap_group("dark_left"),
            },
            TileType.CORNER: {
                "top_left": self.asset_manager.get_tilemap_group("light_top_left"),
                "top_right": self.asset_manager.get_tilemap_group("light_top_right"),
                "bottom_left": self.asset_manager.get_tilemap_group("dark_bottom_left"),
                "bottom_right": self.asset_manager.get_tilemap_group(
                    "dark_bottom_right"
                ),
            },
            TileType.FLOOR: self.asset_manager.get_tilemap_group("platform_center"),
            TileType.DOOR: {
                "horizontal": self.asset_manager.get_tilemap_group("door_light_closed"),
                "vertical": self.asset_manager.get_tilemap_group("door_light_closed"),
            },
            TileType.BACKGROUND: {
                "default": self.asset_manager.get_tilemap_group("dark_center"),
            },
            TileType.EMPTY: None,
        }

    def _get_wall_type(self, x: int, y: int) -> str:
        """Determine wall type based on surrounding tiles"""
        # Check surrounding tiles
        left = (x - 1, y) in self.grid.cells and self.grid.cells[(x - 1, y)] in [
            TileType.WALL,
            TileType.CORNER,
        ]
        right = (x + 1, y) in self.grid.cells and self.grid.cells[(x + 1, y)] in [
            TileType.WALL,
            TileType.CORNER,
        ]

        # For walls, we only need to check if it's horizontal or vertical
        if left or right:
            return "horizontal"
        return "vertical"

    def _get_corner_type(self, x: int, y: int) -> str:
        """Determine corner type based on position relative to walls"""
        # Check surrounding tiles
        left = (x - 1, y) in self.grid.cells and self.grid.cells[
            (x - 1, y)
        ] == TileType.WALL
        right = (x + 1, y) in self.grid.cells and self.grid.cells[
            (x + 1, y)
        ] == TileType.WALL
        up = (x, y - 1) in self.grid.cells and self.grid.cells[
            (x, y - 1)
        ] == TileType.WALL
        down = (x, y + 1) in self.grid.cells and self.grid.cells[
            (x, y + 1)
        ] == TileType.WALL

        if up and right:
            return "bottom_left"
        if up and left:
            return "bottom_right"
        if down and right:
            return "top_left"
        if down and left:
            return "top_right"

        # Default to top_left if we can't determine
        return "top_left"

    def _get_door_type(self, x: int, y: int) -> str:
        """Determine door type based on surrounding walls"""
        # Check surrounding tiles
        left = (x - 1, y) in self.grid.cells and self.grid.cells[(x - 1, y)] in [
            TileType.WALL,
            TileType.DOOR,
        ]
        right = (x + 1, y) in self.grid.cells and self.grid.cells[(x + 1, y)] in [
            TileType.WALL,
            TileType.DOOR,
        ]
        up = (x, y - 1) in self.grid.cells and self.grid.cells[(x, y - 1)] in [
            TileType.WALL,
            TileType.DOOR,
        ]
        down = (x, y + 1) in self.grid.cells and self.grid.cells[(x, y + 1)] in [
            TileType.WALL,
            TileType.DOOR,
        ]

        # For side-scroller, we primarily want horizontal doors
        if left and right:  # Horizontal door
            if self.grid.cells.get((x - 1, y)) == TileType.DOOR:
                return "horizontal_right"
            return "horizontal_left"
        elif up and down:  # Vertical door
            if self.grid.cells.get((x, y - 1)) == TileType.DOOR:
                return "vertical_bottom"
            return "vertical_top"

        # Default to horizontal_left if we can't determine
        return "horizontal_left"

    def _get_background_type(self, x: int, y: int) -> str:
        """Determine which background tile to use based on world position"""
        # Use modulo to create a repeating 2x2 pattern
        is_right = x % 2 == 1
        is_bottom = y % 2 == 1

        if is_bottom:
            return "bottom_right" if is_right else "bottom_left"
        return "top_right" if is_right else "top_left"

    def render(self, surface: pygame.Surface, camera):
        """Render the grid using tilemap assets"""
        for pos, tile_type in self.grid.cells.items():
            x, y = pos
            screen_pos = camera.world_to_screen(x * self.tile_size, y * self.tile_size)

            texture = None
            if tile_type == TileType.BACKGROUND:
                texture = self.textures[TileType.BACKGROUND]["default"]
            elif tile_type == TileType.WALL:
                wall_type = self._get_wall_type(x, y)
                texture = self.textures[TileType.WALL][wall_type]
            elif tile_type == TileType.CORNER:
                corner_type = self._get_corner_type(x, y)
                texture = self.textures[TileType.CORNER][corner_type]
            elif tile_type == TileType.DOOR:
                door_type = (
                    "horizontal" if self._is_horizontal_door(x, y) else "vertical"
                )
                texture = self.textures[TileType.DOOR][door_type]
            elif tile_type == TileType.FLOOR:
                texture = self.textures[TileType.FLOOR]

            if texture:
                surface.blit(texture, screen_pos)

    def _is_horizontal_door(self, x: int, y: int) -> bool:
        """Helper to determine if a door is horizontal"""
        left = (x - 1, y) in self.grid.cells and self.grid.cells[(x - 1, y)] in [
            TileType.WALL,
            TileType.DOOR,
        ]
        right = (x + 1, y) in self.grid.cells and self.grid.cells[(x + 1, y)] in [
            TileType.WALL,
            TileType.DOOR,
        ]
        return left or right

    def set_camera(self, camera):
        """Set camera reference"""
        self.camera = camera
