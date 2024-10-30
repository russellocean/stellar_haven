import pygame

from grid.tile_type import TileType
from systems.debug_system import DebugSystem


class CollisionSystem:
    def __init__(self, grid):
        self.grid = grid
        self.debug = DebugSystem()
        self.camera = None

        # Debug colors
        self.TILE_COLORS = {
            TileType.EMPTY: (0, 0, 0, 0),
            TileType.FLOOR: (0, 255, 0, 100),
            TileType.WALL: (255, 0, 0, 100),
            TileType.DOOR: (0, 0, 255, 100),
        }

    def is_position_valid(self, rect: pygame.Rect) -> bool:
        """Check if a position is valid (inside room and not in wall)"""
        grid_left, grid_top = self.grid.world_to_grid(rect.left, rect.top)
        grid_right, grid_bottom = self.grid.world_to_grid(
            rect.right - 1, rect.bottom - 1
        )

        for x in range(grid_left, grid_right + 1):
            for y in range(grid_top, grid_bottom + 1):
                tile = self.grid.cells.get((x, y), TileType.EMPTY)
                if not tile.is_walkable:
                    return False
        return True

    def get_valid_floor(self, x: int, y: int) -> int:
        """Find the nearest valid floor position below a point"""
        grid_x, grid_y = self.grid.world_to_grid(x, y)

        while grid_y < (y + 1000) // self.grid.cell_size:  # Reasonable search limit
            if (grid_x, grid_y) in self.grid.cells:
                tile = self.grid.cells[(grid_x, grid_y)]
                if tile == TileType.FLOOR:
                    return grid_y * self.grid.cell_size
            grid_y += 1
        return y

    def draw_debug(self, screen):
        """Draw debug visualization"""
        if not self.debug.enabled or not self.camera:
            return

        debug_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        cam_x, cam_y = self.camera.offset_x, self.camera.offset_y

        # Draw grid
        for x, y in self.grid.cells:
            world_x = (x * self.grid.cell_size) - cam_x
            world_y = (y * self.grid.cell_size) - cam_y
            tile_type = self.grid.cells[(x, y)]

            rect = pygame.Rect(
                world_x, world_y, self.grid.cell_size, self.grid.cell_size
            )
            pygame.draw.rect(debug_surface, self.TILE_COLORS[tile_type], rect)

        screen.blit(debug_surface, (0, 0))

    def set_camera(self, camera):
        """Set camera reference for debug visualization"""
        self.camera = camera
