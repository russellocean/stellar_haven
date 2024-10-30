from typing import Dict, List, Optional, Tuple

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
        """Check if two rooms are adjacent"""
        # Check if rooms share a vertical wall
        vertical_adjacent = (nx + nw == ox or nx == ox + ow) and not (
            ny + nh <= oy or ny >= oy + oh
        )

        # Check if rooms share a horizontal wall
        horizontal_adjacent = (ny + nh == oy or ny == oy + oh) and not (
            nx + nw <= ox or nx >= ox + ow
        )

        return vertical_adjacent or horizontal_adjacent

    def is_valid_room_placement(self, grid_x: int, grid_y: int, room_type: str) -> bool:
        """Check if a room can be placed at grid coordinates"""
        width, height = self.room_config["room_types"][room_type]["grid_size"]

        # Check for overlaps
        for dx in range(width):
            for dy in range(height):
                if (grid_x + dx, grid_y + dy) in self.cells:
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

    def _has_valid_connection(
        self, grid_x: int, grid_y: int, width: int, height: int
    ) -> bool:
        """Check if a room at the given position can connect to existing rooms"""
        # Check each existing room
        for other in self.rooms.values():
            ox, oy = other["grid_pos"]
            ow, oh = other["grid_size"]

            # Check if rooms are adjacent
            if self._are_rooms_adjacent(grid_x, grid_y, width, height, ox, oy, ow, oh):
                # If rooms are adjacent, it's a valid connection
                return True

        return False

    def _add_door_between_rooms(self, nx, ny, nw, nh, ox, oy, ow, oh) -> None:
        """Add doors between adjacent rooms (side-scroller style)"""
        # For side-scrollers, we primarily want horizontal connections
        # Vertical wall connection (side-by-side rooms)
        if nx + nw == ox or nx == ox + ow:
            # Place door near the bottom, but not on corners
            door_y = min(ny + nh - 2, oy + oh - 2)  # One tile up from bottom

            # Ensure we're not placing on corners
            if (
                door_y == ny
                or door_y == ny + nh - 1
                or door_y == oy
                or door_y == oy + oh - 1
            ):
                door_y -= 1  # Move up one more if we'd hit a corner

            # Place door at valid position
            if nx + nw == ox:  # New room is left of other room
                self.set_tile(nx + nw - 1, door_y, TileType.DOOR)
                self.set_tile(ox, door_y, TileType.DOOR)
            else:  # New room is right of other room
                self.set_tile(nx, door_y, TileType.DOOR)
                self.set_tile(ox + ow - 1, door_y, TileType.DOOR)

        # Horizontal wall connection (stacked rooms - less common in side-scrollers)
        elif ny + nh == oy or ny == oy + oh:
            # Find middle of overlapping x range, avoiding corners
            start_x = max(nx + 1, ox + 1)  # Avoid left corners
            end_x = min(nx + nw - 2, ox + ow - 2)  # Avoid right corners
            door_x = start_x + (end_x - start_x) // 2

            # Place door at valid position
            if ny + nh == oy:  # New room is above other room
                self.set_tile(door_x, ny + nh - 1, TileType.DOOR)
                self.set_tile(door_x, oy, TileType.DOOR)
            else:  # New room is below other room
                self.set_tile(door_x, ny, TileType.DOOR)
                self.set_tile(door_x, oy + oh - 1, TileType.DOOR)
