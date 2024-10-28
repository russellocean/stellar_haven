import pygame

from systems.debug_system import DebugSystem


class CollisionSystem:
    def __init__(self, room_manager):
        self.room_manager = room_manager
        self.grid_size = 32
        self.collision_map = {}  # (x, y) -> bool
        self.floor_map = {}  # (x) -> List[y] storing floor heights
        self.ignored_floor = None  # (x, y) tuple of floor to ignore
        self.update_collision_map()

        # Debug colors
        self.WALKABLE_COLOR = (0, 255, 0, 100)  # Semi-transparent green
        self.UNWALKABLE_COLOR = (255, 0, 0, 100)  # Semi-transparent red
        self.GRID_COLOR = (255, 255, 255, 50)  # Semi-transparent white

        self.camera = None
        self.debug = DebugSystem()

    def update_collision_map(self):
        """Generate collision map from current room layout"""
        self.collision_map.clear()
        self.floor_map.clear()

        # Add all room boundaries
        for room in self.room_manager.get_rooms():
            grid_left = room.rect.left // self.grid_size
            grid_right = room.rect.right // self.grid_size
            grid_top = room.rect.top // self.grid_size
            grid_bottom = room.rect.bottom // self.grid_size

            # Mark walkable areas and floors in one pass
            for x in range(grid_left, grid_right):
                # Store floor position
                if x not in self.floor_map:
                    self.floor_map[x] = []
                self.floor_map[x].append(grid_bottom)

                # Mark walkable areas
                for y in range(grid_top, grid_bottom):
                    self.collision_map[(x, y)] = True

    def is_position_valid(self, rect: pygame.Rect) -> bool:
        """Check if a position is valid (inside any room)"""
        # Convert rect to grid coordinates
        grid_left = rect.left // self.grid_size
        grid_right = rect.right // self.grid_size
        grid_top = rect.top // self.grid_size
        grid_bottom = (
            rect.bottom - 1
        ) // self.grid_size  # Check one pixel above bottom

        # Check if all points are in walkable area
        for x in range(grid_left, grid_right + 1):
            for y in range(grid_top, grid_bottom + 1):
                if (x, y) not in self.collision_map:
                    return False
        return True

    def get_valid_floor(self, x: int, y: int) -> int:
        """Find the nearest valid floor position below a point"""
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size

        while grid_y < (y + 1000) // self.grid_size:  # Reasonable search limit
            if (grid_x, grid_y) not in self.collision_map:
                return (grid_y - 1) * self.grid_size
            grid_y += 1
        return y  # No floor found, return original position

    def draw_debug(self, screen):
        """Draw debug visualization with direct camera offset"""
        if not self.debug.enabled:  # Only draw if debug is enabled
            return

        debug_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        if not self.camera:
            return

        # Get camera offset directly
        cam_x, cam_y = self.camera.offset_x, self.camera.offset_y
        screen_w, screen_h = screen.get_size()

        # Draw grid for reference (in world space)
        for x in range(0, screen_w + self.grid_size, self.grid_size):
            world_x = x - cam_x
            pygame.draw.line(
                debug_surface, self.GRID_COLOR, (world_x, 0), (world_x, screen_h)
            )
        for y in range(0, screen_h + self.grid_size, self.grid_size):
            world_y = y - cam_y
            pygame.draw.line(
                debug_surface, self.GRID_COLOR, (0, world_y), (screen_w, world_y)
            )

        # Draw walkable areas
        for grid_x, grid_y in self.collision_map:
            world_x = (grid_x * self.grid_size) - cam_x
            world_y = (grid_y * self.grid_size) - cam_y

            rect = pygame.Rect(world_x, world_y, self.grid_size, self.grid_size)
            pygame.draw.rect(debug_surface, self.WALKABLE_COLOR, rect)

        # Draw floors
        for grid_x, floor_heights in self.floor_map.items():
            world_x = (grid_x * self.grid_size) - cam_x

            for grid_y in floor_heights:
                world_y = (grid_y * self.grid_size) - cam_y
                floor_rect = pygame.Rect(
                    world_x, world_y, self.grid_size, 2  # Line thickness
                )
                pygame.draw.rect(debug_surface, self.UNWALKABLE_COLOR, floor_rect)

        screen.blit(debug_surface, (0, 0))

    def draw(self, screen):
        """Regular draw method (for non-debug use)"""
        pass  # Only draw in debug mode

    def ignore_floor(self, x, y):
        """Temporarily ignore a specific floor for collision"""
        self.ignored_floor = (x, y)

    def clear_ignored_floor(self):
        """Clear the ignored floor"""
        self.ignored_floor = None

    def set_camera(self, camera):
        """Set camera reference for debug visualization"""
        self.camera = camera
