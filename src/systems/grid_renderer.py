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
                "corner_top_left": self.asset_manager.get_image(
                    "rooms/framework/corner_top_left.png"
                ),
                "corner_top_right": self.asset_manager.get_image(
                    "rooms/framework/corner_top_right.png"
                ),
                "corner_bottom_left": self.asset_manager.get_image(
                    "rooms/framework/corner_bottom_left.png"
                ),
                "corner_bottom_right": self.asset_manager.get_image(
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
            TileType.EMPTY: None,  # Empty tiles are transparent
        }

    def _get_wall_type(self, x: int, y: int) -> str:
        """Determine wall type based on surrounding tiles"""
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

        # Corner cases
        if up and left and not right and not down:
            return "corner_bottom_right"
        if up and right and not left and not down:
            return "corner_bottom_left"
        if down and left and not right and not up:
            return "corner_top_right"
        if down and right and not left and not up:
            return "corner_top_left"

        # Horizontal or vertical walls
        if left or right:
            return "horizontal"
        return "vertical"

    def _get_door_type(self, x: int, y: int) -> str:
        """Determine door type based on surrounding tiles"""
        # Check if there's another door tile adjacent
        left_door = (x - 1, y) in self.grid.cells and self.grid.cells[
            (x - 1, y)
        ] == TileType.DOOR
        right_door = (x + 1, y) in self.grid.cells and self.grid.cells[
            (x + 1, y)
        ] == TileType.DOOR
        up_door = (x, y - 1) in self.grid.cells and self.grid.cells[
            (x, y - 1)
        ] == TileType.DOOR
        down_door = (x, y + 1) in self.grid.cells and self.grid.cells[
            (x, y + 1)
        ] == TileType.DOOR

        if left_door:
            return "horizontal_right"
        if right_door:
            return "horizontal_left"
        if up_door:
            return "vertical_bottom"
        if down_door:
            return "vertical_top"

        # Default to horizontal_left if no adjacent doors
        return "horizontal_left"

    def render(self, surface: pygame.Surface, camera):
        """Render the grid based on actual tile types"""
        for pos, tile_type in self.grid.cells.items():
            x, y = pos
            screen_pos = camera.world_to_screen(x * self.tile_size, y * self.tile_size)

            if tile_type == TileType.WALL:
                wall_type = self._get_wall_type(x, y)
                surface.blit(self.textures[TileType.WALL][wall_type], screen_pos)
            elif tile_type == TileType.DOOR:
                door_type = self._get_door_type(x, y)
                surface.blit(self.textures[TileType.DOOR][door_type], screen_pos)
            elif tile_type == TileType.FLOOR:
                surface.blit(self.textures[TileType.FLOOR], screen_pos)

    def set_camera(self, camera):
        """Set camera reference"""
        self.camera = camera
