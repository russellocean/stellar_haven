import pygame


class CollisionSystem:
    def __init__(self, room_manager):
        self.room_manager = room_manager
        self.grid_size = 32
        self.collision_map = {}  # (x, y) -> bool
        self.update_collision_map()

    def update_collision_map(self):
        """Generate collision map from current room layout"""
        self.collision_map.clear()

        # Add all room boundaries
        for room in self.room_manager.get_rooms():
            # Convert room rect to grid coordinates
            grid_left = room.rect.left // self.grid_size
            grid_right = room.rect.right // self.grid_size
            grid_top = room.rect.top // self.grid_size
            grid_bottom = room.rect.bottom // self.grid_size

            # Mark walkable areas
            for x in range(grid_left, grid_right):
                for y in range(grid_top, grid_bottom):
                    self.collision_map[(x, y)] = True

    def is_position_valid(self, rect: pygame.Rect) -> bool:
        """Check if a position is valid (inside any room)"""
        # Convert rect to grid coordinates
        grid_left = rect.left // self.grid_size
        grid_right = rect.right // self.grid_size
        grid_top = rect.top // self.grid_size
        grid_bottom = rect.bottom // self.grid_size

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
