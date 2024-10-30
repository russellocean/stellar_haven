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
        """Check if a room can connect properly by comparing corner positions"""
        # Get corner positions for the ghost room
        ghost_corners = [
            (grid_x, grid_y),  # Top-left
            (grid_x + width - 1, grid_y),  # Top-right
            (grid_x, grid_y + height - 1),  # Bottom-left
            (grid_x + width - 1, grid_y + height - 1),  # Bottom-right
        ]

        # Check if any ghost corner position has an existing corner tile
        for corner_x, corner_y in ghost_corners:
            if self.get_tile(corner_x, corner_y) == TileType.CORNER:
                return True

        return False

    def _add_door_between_rooms(self, nx, ny, nw, nh, ox, oy, ow, oh) -> None:
        """Add door at floor level where walls overlap"""
        floor_y = ny + nh - 2  # Floor is always 1 tile above bottom wall

        # For side-by-side rooms
        if nx + nw == ox:  # New room is left of other room
            door_x = nx + nw - 1
        elif nx == ox + ow:  # New room is right of other room
            door_x = nx
        else:  # Rooms must be overlapping horizontally
            # Find middle of overlap
            overlap_start = max(nx, ox)
            overlap_end = min(nx + nw, ox + ow)
            door_x = overlap_start + (overlap_end - overlap_start) // 2

        # Place floor and door
        self.set_tile(door_x, floor_y, TileType.FLOOR)  # Floor level
        self.set_tile(door_x, floor_y - 1, TileType.DOOR)  # Door bottom
        self.set_tile(door_x, floor_y - 2, TileType.DOOR)  # Door top
