import pygame

from systems.debug_system import DebugSystem


class CollisionSystem:
    def __init__(self, room_manager):
        self.room_manager = room_manager
        self.grid_size = 32
        self.collision_map = {}  # (x, y) -> TileType
        self.floor_map = {}  # x -> List[y] storing floor heights
        self.ignored_floor = None  # For drop-through functionality

        # Define tile types
        self.TILE_EMPTY = 0
        self.TILE_FLOOR = 1
        self.TILE_WALL = 2
        self.TILE_DOOR = 3

        # Debug colors
        self.TILE_COLORS = {
            self.TILE_EMPTY: (0, 0, 0, 0),
            self.TILE_FLOOR: (0, 255, 0, 100),
            self.TILE_WALL: (255, 0, 0, 100),
            self.TILE_DOOR: (0, 0, 255, 100),
        }

        self.GRID_COLOR = (100, 100, 100, 50)
        self.WALKABLE_COLOR = (0, 255, 0, 50)
        self.UNWALKABLE_COLOR = (255, 0, 0, 50)

        self.camera = None
        self.debug = DebugSystem()

        # Initial collision map update
        self.update_collision_map()

    def update_collision_map(self):
        """Generate collision map from current room layout"""
        self.collision_map.clear()
        self.floor_map.clear()

        for room in self.room_manager.get_rooms():
            grid_left = room.rect.left // self.grid_size
            grid_right = room.rect.right // self.grid_size
            grid_top = room.rect.top // self.grid_size
            grid_bottom = room.rect.bottom // self.grid_size

            # Add walls around the perimeter
            for x in range(grid_left, grid_right):
                self.collision_map[(x, grid_top)] = self.TILE_WALL
                self.collision_map[(x, grid_bottom - 1)] = self.TILE_WALL

            for y in range(grid_top, grid_bottom):
                self.collision_map[(grid_left, y)] = self.TILE_WALL
                self.collision_map[(grid_right - 1, y)] = self.TILE_WALL

            # Add floor tiles
            for x in range(grid_left + 1, grid_right - 1):
                for y in range(grid_top + 1, grid_bottom - 1):
                    self.collision_map[(x, y)] = self.TILE_FLOOR

                # Store floor positions
                if x not in self.floor_map:
                    self.floor_map[x] = []
                self.floor_map[x].append(grid_bottom - 1)

        # Process doors between rooms
        self._process_room_connections()

    def _process_room_connections(self):
        """Process connections between rooms and add doors"""
        processed_connections = set()

        for room in self.room_manager.get_rooms():
            for other_room in self.room_manager.get_rooms():
                if room != other_room:
                    connection = self._get_connection_point(room, other_room)
                    if connection and connection not in processed_connections:
                        self._add_door(connection)
                        processed_connections.add(connection)

    def _get_connection_point(self, room1, room2):
        """Get the connection point between two rooms if they're adjacent"""
        # Return format: (grid_x, grid_y, is_horizontal)
        grid1 = self._get_room_grid(room1)
        grid2 = self._get_room_grid(room2)

        # Check horizontal adjacency
        if abs(grid1.right - grid2.left) <= 1 and self._vertical_overlap(grid1, grid2):
            overlap_y = self._get_overlap_position(
                grid1.top, grid1.bottom, grid2.top, grid2.bottom
            )
            return (grid1.right, overlap_y, False)

        # Check vertical adjacency
        if abs(grid1.bottom - grid2.top) <= 1 and self._horizontal_overlap(
            grid1, grid2
        ):
            overlap_x = self._get_overlap_position(
                grid1.left, grid1.right, grid2.left, grid2.right
            )
            return (overlap_x, grid1.bottom, True)

        return None

    def _add_door(self, connection):
        """Add a door at the connection point"""
        x, y, is_horizontal = connection
        self.collision_map[(x, y)] = self.TILE_DOOR
        if is_horizontal:
            self.collision_map[(x + 1, y)] = self.TILE_DOOR
        else:
            self.collision_map[(x, y + 1)] = self.TILE_DOOR

    def is_position_valid(self, rect: pygame.Rect) -> bool:
        """Check if a position is valid (inside room and not in wall)"""
        grid_left = rect.left // self.grid_size
        grid_right = rect.right // self.grid_size
        grid_top = rect.top // self.grid_size
        grid_bottom = (rect.bottom - 1) // self.grid_size

        for x in range(grid_left, grid_right + 1):
            for y in range(grid_top, grid_bottom + 1):
                tile_type = self.collision_map.get((x, y), self.TILE_EMPTY)
                if tile_type in [self.TILE_EMPTY, self.TILE_WALL]:
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

    def _get_room_grid(self, room):
        """Convert room rect to grid coordinates"""
        return pygame.Rect(
            room.rect.left // self.grid_size,
            room.rect.top // self.grid_size,
            room.rect.width // self.grid_size,
            room.rect.height // self.grid_size,
        )

    def _vertical_overlap(self, grid1, grid2):
        """Check if two grid rects overlap vertically"""
        return grid1.top < grid2.bottom and grid1.bottom > grid2.top

    def _horizontal_overlap(self, grid1, grid2):
        """Check if two grid rects overlap horizontally"""
        return grid1.left < grid2.right and grid1.right > grid2.left

    def _get_overlap_position(self, start1, end1, start2, end2):
        """Get the middle position of overlap"""
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        return (overlap_start + overlap_end) // 2
