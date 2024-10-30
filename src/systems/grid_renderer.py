import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager


class GridRenderer:
    def __init__(self, grid, tile_size=32):
        self.grid = grid
        self.tile_size = tile_size
        self.asset_manager = AssetManager()
        self.camera = None

        # Load the industrial tileset
        tileset = self.asset_manager.get_image("1_Industrial_Tileset_1.png")
        tile_width = 32  # Assuming each tile is 32x32

        # Extract tiles from the tileset
        self.textures = {
            TileType.WALL: {
                "horizontal": tileset.subsurface(
                    (tile_width * 1, tile_width * 1, tile_width, tile_width)
                ),  # top wall
                "vertical": tileset.subsurface(
                    (tile_width * 3, tile_width * 2, tile_width, tile_width)
                ),  # side wall
            },
            TileType.CORNER: {
                "top_left": tileset.subsurface(
                    (0, tile_width * 1, tile_width, tile_width)
                ),
                "top_right": tileset.subsurface(
                    (tile_width * 2, tile_width * 1, tile_width, tile_width)
                ),
                "bottom_left": tileset.subsurface(
                    (0, tile_width * 3, tile_width, tile_width)
                ),
                "bottom_right": tileset.subsurface(
                    (tile_width * 2, tile_width * 3, tile_width, tile_width)
                ),
            },
            TileType.FLOOR: tileset.subsurface(
                (tile_width * 3, 0, tile_width, tile_width)
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
            TileType.BACKGROUND: {
                "top_left": tileset.subsurface(
                    (4 * tile_width, 0, tile_width, tile_width)
                ),
                "top_right": tileset.subsurface(
                    (5 * tile_width, 0, tile_width, tile_width)
                ),
                "bottom_left": tileset.subsurface(
                    (4 * tile_width, tile_width, tile_width, tile_width)
                ),
                "bottom_right": tileset.subsurface(
                    (5 * tile_width, tile_width, tile_width, tile_width)
                ),
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
        """Render the grid based on actual tile types"""
        for pos, tile_type in self.grid.cells.items():
            x, y = pos
            screen_pos = camera.world_to_screen(x * self.tile_size, y * self.tile_size)

            # Update background rendering
            if tile_type == TileType.BACKGROUND:
                bg_type = self._get_background_type(x, y)
                surface.blit(self.textures[TileType.BACKGROUND][bg_type], screen_pos)
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
