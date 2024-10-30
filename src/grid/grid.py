from typing import Dict, List, Optional, Tuple

import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager


class Grid:
    def __init__(self, cell_size: int = 32):
        self.cell_size = cell_size
        self.cells: Dict[Tuple[int, int], TileType] = {}
        self.rooms: Dict[str, dict] = {}  # Keep room data for door connections
        self.asset_manager = AssetManager()
        self.room_config = self.asset_manager.get_config("rooms")

    def add_room(self, room_id: str, room_type: str, grid_x: int, grid_y: int) -> bool:
        """Add a room at grid coordinates"""
        # Generate unique room ID if not provided
        if room_id is None:
            room_id = f"room_{len(self.rooms)}"

        # Get room size from config
        room_data = self.room_config["room_types"][room_type]
        width, height = room_data["grid_size"]

        # Store room data
        self.rooms[room_id] = {
            "type": room_type,
            "grid_pos": (grid_x, grid_y),
            "grid_size": (width, height),
        }

        # Add room tiles
        self._add_room_tiles(room_id)
        self._process_connections(room_id)

        return True

    def _add_room_tiles(self, room_id: str) -> None:
        """Add wall tiles for a room with explicit corners and background"""
        room = self.rooms[room_id]
        x, y = room["grid_pos"]
        width, height = room["grid_size"]

        # Add background tiles first (for interior)
        for dx in range(1, width - 1):
            for dy in range(1, height - 1):
                self.set_tile(x + dx, y + dy, TileType.BACKGROUND)

        # Add horizontal walls (excluding corners)
        for dx in range(1, width - 1):
            self.set_tile(x + dx, y, TileType.WALL)  # Top wall
            self.set_tile(x + dx, y + height - 1, TileType.WALL)  # Bottom wall

        # Add vertical walls (excluding corners)
        for dy in range(1, height - 1):
            self.set_tile(x, y + dy, TileType.WALL)  # Left wall
            self.set_tile(x + width - 1, y + dy, TileType.WALL)  # Right wall

        # Add floor tiles one tile above bottom wall
        for dx in range(1, width - 1):
            self.set_tile(
                x + dx, y + height - 2, TileType.FLOOR
            )  # One tile above bottom

        # Add corners explicitly
        self.set_tile(x, y, TileType.CORNER)  # Top-left
        self.set_tile(x + width - 1, y, TileType.CORNER)  # Top-right
        self.set_tile(x, y + height - 1, TileType.CORNER)  # Bottom-left
        self.set_tile(x + width - 1, y + height - 1, TileType.CORNER)  # Bottom-right

    def _process_connections(self, room_id: str) -> None:
        """Process connections and add doors between rooms"""
        new_room = self.rooms[room_id]
        nx, ny = new_room["grid_pos"]
        nw, nh = new_room["grid_size"]

        for other_id, other in self.rooms.items():
            if other_id == room_id:
                continue

            ox, oy = other["grid_pos"]
            ow, oh = other["grid_size"]

            # Check for adjacent walls and add doors
            if self._are_rooms_adjacent(nx, ny, nw, nh, ox, oy, ow, oh):
                self._add_door_between_rooms(nx, ny, nw, nh, ox, oy, ow, oh)

    def _are_rooms_adjacent(self, nx, ny, nw, nh, ox, oy, ow, oh) -> bool:
        """Check if rooms share a wall (one tile overlap)"""
        # For vertical walls (side by side rooms)
        if nx + nw - 1 == ox or nx == ox + ow - 1:  # One tile overlap
            # Check if they overlap vertically (excluding corners)
            return not (ny + nh <= oy or ny >= oy + oh)

        # For horizontal walls (stacked rooms)
        if ny + nh - 1 == oy or ny == oy + oh - 1:  # One tile overlap
            # Check if they overlap horizontally (excluding corners)
            return not (nx + nw <= ox or nx >= ox + ow)

        return False

    def _has_wall_or_corner(self, x: int, y: int) -> bool:
        """Check if position has a wall or corner tile"""
        if (x, y) in self.cells:
            tile = self.cells[(x, y)]
            return tile in [TileType.WALL, TileType.CORNER]
        return False

    def _has_corner(self, x: int, y: int) -> bool:
        """Check if position has a corner tile"""
        return self.get_tile(x, y) == TileType.CORNER

    def is_valid_room_placement(self, grid_x: int, grid_y: int, room_type: str) -> bool:
        """Check if a room can be placed at grid coordinates"""
        width, height = self.room_config["room_types"][room_type]["grid_size"]

        # Check for overlaps with non-wall tiles
        for dx in range(width):
            for dy in range(height):
                pos = (grid_x + dx, grid_y + dy)
                if pos in self.cells:
                    tile = self.cells[pos]
                    # Allow overlapping with walls and corners
                    if tile not in [TileType.WALL, TileType.CORNER]:
                        return False

        # If this is the first room, it's valid
        if not self.rooms:
            return True

        # Check for valid connections to existing rooms
        return self._has_valid_connection(grid_x, grid_y, width, height)

    def get_doors_for_room(self, room_id: str) -> List[dict]:
        """Get all doors for a specific room"""
        room = self.rooms[room_id]
        rect = room["rect"]
        doors = []

        left, top = self.world_to_grid(rect.left, rect.top)

        for (x, y), tile_type in self.cells.items():
            if (
                tile_type == TileType.DOOR
                and left <= x < left + room["grid_size"][0]
                and top <= y < top + room["grid_size"][1]
            ):

                is_horizontal = (x + 1, y) in self.cells and self.cells[
                    (x + 1, y)
                ] == TileType.DOOR

                doors.append({"x": x - left, "y": y - top, "horizontal": is_horizontal})

        return doors

    def get_room_by_grid_position(self, grid_x: int, grid_y: int) -> Optional[str]:
        """Get the room ID at a specific grid position"""
        for room_id, room in self.rooms.items():
            if room["grid_pos"] == (grid_x, grid_y):
                return room_id
        return None

    def get_room_by_id(self, room_id: str) -> Optional[dict]:
        """Get the room data by ID"""
        return self.rooms.get(room_id)

    def get_room_type_by_id(self, room_id: str) -> Optional[str]:
        """Get the room type by ID"""
        room = self.get_room_by_id(room_id)
        return room["type"] if room else None

    def world_to_grid(self, x: int, y: int) -> Tuple[int, int]:
        return (x // self.cell_size, y // self.cell_size)

    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        return (grid_x * self.cell_size, grid_y * self.cell_size)

    def set_tile(self, x: int, y: int, tile_type: TileType) -> None:
        """Set a tile with validation to prevent multiple types"""
        if (x, y) in self.cells:
            current_type = self.cells[(x, y)]
            if current_type != tile_type:
                print(
                    f"WARNING: Changing tile at ({x}, {y}) from {current_type} to {tile_type}"
                )
        self.cells[(x, y)] = tile_type

    def get_tile(self, x: int, y: int) -> TileType:
        """Get the tile at a specific position"""
        return self.cells.get((x, y), TileType.EMPTY)

    def get_adjacent_tiles(self, x: int, y: int) -> List[TileType]:
        """Get the tiles directly adjacent (left, right, up, down) to a specific position"""
        return [
            self.get_tile(x - 1, y),
            self.get_tile(x + 1, y),
            self.get_tile(x, y - 1),
            self.get_tile(x, y + 1),
        ]

    def get_tile_in_room(self, room_id: str, x: int, y: int) -> TileType:
        """Get the tile at a specific position in a room"""
        room = self.rooms[room_id]
        return self.get_tile(x + room["grid_pos"][0], y + room["grid_pos"][1])

    def get_room_rect(self, room_id: str) -> pygame.Rect:
        """Get the rectangle of a room"""
        room = self.rooms[room_id]
        return pygame.Rect(
            room["grid_pos"][0] * self.cell_size,
            room["grid_pos"][1] * self.cell_size,
            *room["grid_size"],
        )

    def _has_valid_connection(
        self, grid_x: int, grid_y: int, width: int, height: int
    ) -> bool:
        """Check if a room can connect properly by comparing corner positions and ensuring wall connection"""
        # Get corner positions for the ghost room
        ghost_corners = [
            (grid_x, grid_y),  # Top-left
            (grid_x + width - 1, grid_y),  # Top-right
            (grid_x, grid_y + height - 1),  # Bottom-left
            (grid_x + width - 1, grid_y + height - 1),  # Bottom-right
        ]

        # Helper function to get wall positions for a corner
        def get_corner_walls(x: int, y: int, is_ghost: bool) -> List[Tuple[int, int]]:
            walls = []
            if is_ghost:
                # For ghost room, determine where walls would be based on corner position
                if x == grid_x:  # Left side
                    walls.append((x, y + 1))  # Vertical wall below
                    walls.append((x + 1, y))  # Horizontal wall right
                if x == grid_x + width - 1:  # Right side
                    walls.append((x, y + 1))  # Vertical wall below
                    walls.append((x - 1, y))  # Horizontal wall left
                if y == grid_y:  # Top side
                    walls.append((x, y + 1))  # Vertical wall below
                    walls.append((x, y + 1))  # Horizontal wall below
                if y == grid_y + height - 1:  # Bottom side
                    walls.append((x, y - 1))  # Vertical wall above
                    walls.append((x, y - 1))  # Horizontal wall above
            else:
                # For existing room, just get adjacent tiles
                adjacent = self.get_adjacent_tiles(x, y)
                for i, tile in enumerate(adjacent):
                    if tile == TileType.WALL:
                        # Convert adjacent index to position
                        if i == 0:  # Left
                            walls.append((x - 1, y))
                        elif i == 1:  # Right
                            walls.append((x + 1, y))
                        elif i == 2:  # Up
                            walls.append((x, y - 1))
                        elif i == 3:  # Down
                            walls.append((x, y + 1))
            return walls

        for corner_x, corner_y in ghost_corners:
            # First check if this corner overlaps with an existing corner
            if self.get_tile(corner_x, corner_y) == TileType.CORNER:
                # Get wall positions for both ghost and existing room
                ghost_walls = get_corner_walls(corner_x, corner_y, True)
                existing_walls = get_corner_walls(corner_x, corner_y, False)

                # Check if any walls match between ghost and existing
                for ghost_wall in ghost_walls:
                    for existing_wall in existing_walls:
                        if ghost_wall == existing_wall:
                            return True

        return False

    def _replace_tile(self, x: int, y: int, new_type: TileType) -> None:
        """Helper to replace a tile with validation"""
        current = self.get_tile(x, y)
        if current != TileType.EMPTY:
            print(f"Replacing {current} with {new_type} at ({x}, {y})")
        self.set_tile(x, y, new_type)

    def _get_wall_line(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> List[Tuple[int, int]]:
        """Get all positions in a straight line between two points"""
        positions = []
        if start_x == end_x:  # Vertical line
            for y in range(min(start_y, end_y), max(start_y, end_y) + 1):
                positions.append((start_x, y))
        else:  # Horizontal line
            for x in range(min(start_x, end_x), max(start_x, end_x) + 1):
                positions.append((x, start_y))
        return positions

    def _find_floor_center(self, positions: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Find the center position of a line of floor tiles"""
        floor_positions = [
            (x, y) for x, y in positions if self.get_tile(x, y) == TileType.FLOOR
        ]
        if floor_positions:
            center_idx = len(floor_positions) // 2
            return floor_positions[center_idx]
        return positions[len(positions) // 2]  # Fallback to center of line

    def _add_door_between_rooms(self, nx, ny, nw, nh, ox, oy, ow, oh) -> None:
        """Add door between rooms, handling both side-by-side and stacked configurations"""
        # For side-by-side rooms
        if nx + nw - 1 == ox or nx == ox + ow - 1:  # One tile overlap
            floor_y = ny + nh - 2  # Floor is always 1 tile above bottom wall

            # For side-by-side rooms
            if nx + nw - 1 == ox:  # New room is left of other room
                door_x = nx + nw - 1
            else:  # New room is right of other room
                door_x = nx

            # Check to see if the door which is going to be placed has an adjacent tile that is within the bounds of the new room

            # Place floor and door
            self.set_tile(door_x, floor_y, TileType.FLOOR)  # Floor level
            self.set_tile(door_x, floor_y - 1, TileType.DOOR)  # Door bottom
            self.set_tile(door_x, floor_y - 2, TileType.DOOR)  # Door top

        # For stacked rooms
        elif ny + nh - 1 == oy or ny == oy + oh - 1:  # One tile overlap
            # Find the overlapping wall line
            start_x = max(nx + 1, ox + 1)  # Skip corners
            end_x = min(nx + nw - 1, ox + ow - 1)  # Skip corners

            # Determine which wall we're connecting
            if ny + nh - 1 == oy:  # New room is above other room
                wall_y = ny + nh - 1
            else:  # New room is below other room
                wall_y = ny

            # Get all positions along the wall
            wall_positions = self._get_wall_line(start_x, wall_y, end_x, wall_y)

            # Replace walls with background except corners
            for x, y in wall_positions:
                if self.get_tile(x, y) == TileType.WALL:
                    self.set_tile(x, y, TileType.BACKGROUND)

            # Find center and add door
            center_x = (start_x + end_x) // 2
            self.set_tile(center_x, wall_y - 1, TileType.DOOR)
            self.set_tile(center_x - 1, wall_y - 1, TileType.DOOR)
            self.set_tile(center_x + 1, wall_y - 1, TileType.DOOR)
