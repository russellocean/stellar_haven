import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager


class GridRenderer:
    def __init__(self, grid, tile_size=32):
        self.grid = grid
        self.tile_size = tile_size
        self.asset_manager = AssetManager()
        self.camera = None

        # Load tile textures once
        self.textures = {
            TileType.WALL: {
                "horizontal": self.asset_manager.get_image(
                    "rooms/framework/wall_horizontal.png"
                ),
                "vertical": self.asset_manager.get_image(
                    "rooms/framework/wall_vertical.png"
                ),
            },
            TileType.CORNER: {
                "top_left": self.asset_manager.get_image(
                    "rooms/framework/corner_top_left.png"
                ),
                "top_right": self.asset_manager.get_image(
                    "rooms/framework/corner_top_right.png"
                ),
                "bottom_left": self.asset_manager.get_image(
                    "rooms/framework/corner_bottom_left.png"
                ),
                "bottom_right": self.asset_manager.get_image(
                    "rooms/framework/corner_bottom_right.png"
                ),
            },
            TileType.FLOOR: self.asset_manager.get_image(
                "rooms/interiors/floor_base.png"
            ),
            TileType.DOOR: {
                "horizontal_left": self.asset_manager.get_image(
                    "rooms/framework/door_horizontal_left.png"
                ),
                "horizontal_right": self.asset_manager.get_image(
                    "rooms/framework/door_horizontal_right.png"
                ),
                "vertical_top": self.asset_manager.get_image(
                    "rooms/framework/door_vertical_top.png"
                ),
                "vertical_bottom": self.asset_manager.get_image(
                    "rooms/framework/door_vertical_bottom.png"
                ),
            },
            TileType.BACKGROUND: self.asset_manager.get_image(
                "rooms/interiors/wall_base.png"
            ),
            TileType.EMPTY: None,  # Empty tiles are transparent
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
            return "top_left"
        if up and left:
            return "top_right"
        if down and right:
            return "bottom_left"
        if down and left:
            return "bottom_right"

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

    def render(self, surface: pygame.Surface, camera):
        """Render the grid based on actual tile types"""
        for pos, tile_type in self.grid.cells.items():
            x, y = pos
            screen_pos = camera.world_to_screen(x * self.tile_size, y * self.tile_size)

            # Render background first if it exists
            if tile_type == TileType.BACKGROUND:
                surface.blit(self.textures[TileType.BACKGROUND], screen_pos)
            elif tile_type == TileType.WALL:
                wall_type = self._get_wall_type(x, y)
                surface.blit(self.textures[TileType.WALL][wall_type], screen_pos)
            elif tile_type == TileType.CORNER:
                corner_type = self._get_corner_type(x, y)
                surface.blit(self.textures[TileType.CORNER][corner_type], screen_pos)
            elif tile_type == TileType.DOOR:
                door_type = self._get_door_type(x, y)
                surface.blit(self.textures[TileType.DOOR][door_type], screen_pos)
            elif tile_type == TileType.FLOOR:
                surface.blit(self.textures[TileType.FLOOR], screen_pos)

    def set_camera(self, camera):
        """Set camera reference"""
        self.camera = camera
