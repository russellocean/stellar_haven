from typing import Dict, List, Optional, Tuple

import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager


class Grid:
    def __init__(self, cell_size: int = 16):
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

        # Recalculate corners for any adjacent rooms
        for other_id, other in self.rooms.items():
            if other_id != room_id:
                ox, oy = other["grid_pos"]
                ow, oh = other["grid_size"]
                if self._are_rooms_adjacent(
                    grid_x, grid_y, width, height, ox, oy, ow, oh
                ):
                    self._recalculate_corners(other_id)

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

        # Add horizontal walls (including corners initially as walls)
        for dx in range(width):
            self.set_tile(x + dx, y, TileType.WALL)  # Top wall
            self.set_tile(x + dx, y + height - 1, TileType.WALL)  # Bottom wall

        # Add vertical walls (including corners initially as walls)
        for dy in range(height):
            self.set_tile(x, y + dy, TileType.WALL)  # Left wall
            self.set_tile(x + width - 1, y + dy, TileType.WALL)  # Right wall

        # Recalculate corners after walls are placed
        self._recalculate_corners(room_id)

    def _process_connections(self, room_id: str) -> None:
        """Verify room has valid connections to existing rooms"""
        new_room = self.rooms[room_id]
        nx, ny = new_room["grid_pos"]
        nw, nh = new_room["grid_size"]

        # Check if room has at least one valid connection
        has_connection = False
        for other_id, other in self.rooms.items():
            if other_id == room_id:
                continue

            ox, oy = other["grid_pos"]
            ow, oh = other["grid_size"]

            if self._are_rooms_adjacent(nx, ny, nw, nh, ox, oy, ow, oh):
                has_connection = True
                break

        if not has_connection and len(self.rooms) > 1:
            raise ValueError("Room must connect to at least one existing room")

    def _are_rooms_adjacent(
        self, nx: int, ny: int, nw: int, nh: int, ox: int, oy: int, ow: int, oh: int
    ) -> bool:
        """Check if rooms are adjacent (sharing a side, not overlapping)"""
        # For vertical adjacency (side by side rooms)
        if nx + nw == ox or nx == ox + ow:  # Rooms touch but don't overlap
            # Check if they overlap vertically (excluding corners)
            return not (ny + nh <= oy or ny >= oy + oh)

        # For horizontal adjacency (stacked rooms)
        if ny + nh == oy or ny == oy + oh:  # Rooms touch but don't overlap
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
        """Check if a room can connect properly to existing rooms"""
        # Skip connection check for first room
        if not self.rooms:
            return True

        # Check each existing room for adjacency
        for room_id, room in self.rooms.items():
            rx, ry = room["grid_pos"]
            rw, rh = room["grid_size"]

            # If rooms would be adjacent, it's a valid connection
            if self._are_rooms_adjacent(grid_x, grid_y, width, height, rx, ry, rw, rh):
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

    def _recalculate_corners(self, room_id: str) -> None:
        """Recalculate corners for a room and its adjacent rooms"""
        room = self.rooms[room_id]
        x, y = room["grid_pos"]
        width, height = room["grid_size"]

        # Get area to check (including adjacent tiles)
        check_area = [
            (cx, cy)
            for cx in range(x - 1, x + width + 1)
            for cy in range(y - 1, y + height + 1)
        ]

        # Check each position
        for cx, cy in check_area:
            # Skip if not a wall or corner
            if not self._has_wall_or_corner(cx, cy):
                continue

            # Check if this is part of a horizontal wall
            is_horizontal = self._has_wall_or_corner(
                cx - 1, cy
            ) or self._has_wall_or_corner(cx + 1, cy)

            # Check if this is part of a vertical wall
            is_vertical = self._has_wall_or_corner(
                cx, cy - 1
            ) or self._has_wall_or_corner(cx, cy + 1)

            # Only make it a corner if we have both horizontal and vertical walls
            # and it's not part of a continuous wall
            if is_horizontal and is_vertical and not (is_horizontal and is_vertical):
                self.set_tile(cx, cy, TileType.CORNER)
            else:
                self.set_tile(cx, cy, TileType.WALL)
