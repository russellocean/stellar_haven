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
            TileType.PLATFORM: (0, 255, 0, 100),
            TileType.DECORATION: (255, 255, 0, 100),
            TileType.PLANET: (0, 255, 255, 100),
            TileType.STAR: (255, 255, 255, 100),
            TileType.WINDOW: (0, 128, 255, 100),
            TileType.FURNITURE: (128, 64, 0, 100),
            TileType.BACKGROUND: (64, 64, 64, 100),
            TileType.EXTERIOR: (192, 192, 192, 100),
        }

    def is_position_valid(
        self, rect: pygame.Rect, velocity: pygame.Vector2 = None
    ) -> bool:
        """
        Check if a position is valid, accounting for high velocities
        to prevent tunneling through tiles
        """
        if velocity is None:
            # Original single-point check for static collisions
            return self._check_rect_collision(rect)

        # For high-speed movement, check multiple points along the path
        num_steps = max(1, int(abs(velocity.y) / self.grid.cell_size))
        step_size = velocity.y / num_steps if num_steps > 0 else 0

        test_rect = rect.copy()
        for _ in range(num_steps):
            test_rect.y += step_size
            if self._check_rect_collision(test_rect, velocity):
                return True
        return False

    def _check_rect_collision(
        self, rect: pygame.Rect, velocity: pygame.Vector2 = None
    ) -> bool:
        """Helper method for basic rectangle collision check"""
        grid_left, grid_top = self.grid.world_to_grid(rect.left, rect.top)
        grid_right, grid_bottom = self.grid.world_to_grid(
            rect.right - 1, rect.bottom - 1
        )

        # Check each grid cell the rect overlaps
        for x in range(grid_left, grid_right + 1):
            for y in range(grid_top, grid_bottom + 1):
                tile = self.grid.get_tile(x, y)
                if tile:
                    if tile.blocks_movement:
                        return True
                    # Only collide with platforms if we're falling onto them from above
                    if tile == TileType.PLATFORM and velocity and velocity.y > 0:
                        # Check if the bottom of the rect is near the top of the platform
                        platform_top = y * self.grid.cell_size
                        if abs(rect.bottom - platform_top) < abs(velocity.y):
                            return True
        return False

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
                    tile = self.grid.get_tile(x, y)
                    colliding_tiles.append((x, y, tile))
        return colliding_tiles

    def get_valid_floor(self, x: int, y: int) -> int:
        """Find the nearest valid floor position below a point"""
        grid_x, grid_y = self.grid.world_to_grid(x, y)

        while grid_y < (y + 1000) // self.grid.cell_size:  # Reasonable search limit
            if (grid_x, grid_y) in self.grid.cells:
                tile = self.grid.get_tile(grid_x, grid_y)
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

            # Get the primary (non-background) tile at this position
            tile_type = self.grid.get_tile(
                x, y
            )  # Use get_tile instead of direct access

            rect = pygame.Rect(
                screen_x, screen_y, self.grid.cell_size, self.grid.cell_size
            )

            # Draw the tile color if we have one defined
            if tile_type in self.TILE_COLORS:
                pygame.draw.rect(debug_surface, self.TILE_COLORS[tile_type], rect)

        screen.blit(debug_surface, (0, 0))

    def set_camera(self, camera):
        """Set camera reference for debug visualization"""
        self.camera = camera
