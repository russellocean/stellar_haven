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
            TileType.WALL: (255, 0, 0, 100),
            TileType.DOOR: (0, 0, 255, 100),
            TileType.CORNER: (255, 0, 255, 100),
            TileType.INTERIOR_BACKGROUND: (128, 128, 128, 100),
        }

    def is_position_valid(self, rect: pygame.Rect) -> bool:
        """Check if a position is valid (not blocked by walls or other obstacles)"""
        grid_left, grid_top = self.grid.world_to_grid(rect.left, rect.top)
        grid_right, grid_bottom = self.grid.world_to_grid(
            rect.right - 1, rect.bottom - 1
        )

        # Check each grid cell the rect overlaps
        for x in range(grid_left, grid_right + 1):
            for y in range(grid_top, grid_bottom + 1):
                tile = self.grid.cells.get((x, y), TileType.EMPTY)
                if tile.blocks_movement:
                    return False
        return True

    def check_collision_with_tile(self, rect: pygame.Rect, tile_pos: tuple) -> bool:
        """Check if a rect collides with a specific tile"""
        tile_rect = pygame.Rect(
            tile_pos[0] * self.grid.cell_size,
            tile_pos[1] * self.grid.cell_size,
            self.grid.cell_size,
            self.grid.cell_size,
        )
        return rect.colliderect(tile_rect)

    def get_colliding_tiles(self, rect: pygame.Rect) -> list:
        """Get all tiles that collide with a rect"""
        grid_left, grid_top = self.grid.world_to_grid(rect.left, rect.top)
        grid_right, grid_bottom = self.grid.world_to_grid(
            rect.right - 1, rect.bottom - 1
        )

        colliding_tiles = []
        for x in range(grid_left, grid_right + 1):
            for y in range(grid_top, grid_bottom + 1):
                if (x, y) in self.grid.cells:
                    colliding_tiles.append((x, y, self.grid.cells[(x, y)]))
        return colliding_tiles

    def get_valid_floor(self, x: int, y: int) -> int:
        """Find the nearest valid floor position below a point"""
        grid_x, grid_y = self.grid.world_to_grid(x, y)

        while grid_y < (y + 1000) // self.grid.cell_size:  # Reasonable search limit
            if (grid_x, grid_y) in self.grid.cells:
                tile = self.grid.cells[(grid_x, grid_y)]
                if tile.blocks_movement:
                    return grid_y * self.grid.cell_size
            grid_y += 1
        return y

    def draw_debug(self, screen):
        """Draw debug visualization"""
        if not self.debug.enabled or not self.camera:
            return

        debug_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        # Draw grid
        for x, y in self.grid.cells:
            # Convert world coordinates to screen coordinates
            world_x = x * self.grid.cell_size
            world_y = y * self.grid.cell_size
            screen_x, screen_y = self.camera.world_to_screen(world_x, world_y)

            tile_type = self.grid.cells[(x, y)]
            rect = pygame.Rect(
                screen_x, screen_y, self.grid.cell_size, self.grid.cell_size
            )
            pygame.draw.rect(debug_surface, self.TILE_COLORS[tile_type], rect)

        screen.blit(debug_surface, (0, 0))

    def set_camera(self, camera):
        """Set camera reference for debug visualization"""
        self.camera = camera
