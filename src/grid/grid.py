from typing import Dict, List, Optional, Tuple

from grid.tile_type import TileType
from systems.asset_manager import AssetManager


class Grid:
    def __init__(self, cell_size: int = 16):
        self.cell_size = cell_size
        self.cells: Dict[Tuple[int, int], TileType] = {}
        self.rooms: Dict[str, dict] = {}
        self.asset_manager = AssetManager()
        self.room_config = self.asset_manager.get_config("rooms")
        self.tilemap_config = self.asset_manager.get_config("tilemap_config")
        self.tile_change_callbacks = []
        self.tile_groups = self._initialize_tile_groups()

    def _initialize_tile_groups(self) -> Dict[str, dict]:
        """Initialize tile group definitions from config"""
        groups = {}
        for tilemap_path, tilemap_data in self.tilemap_config.items():
            if tilemap_path == "global":
                continue
            for group in tilemap_data.get("groups", []):
                metadata = group["metadata"]
                # Only add groups that are larger than 1x1
                if metadata["width"] > 1 or metadata["height"] > 1:
                    groups[metadata["name"]] = {
                        "width": metadata["width"],
                        "height": metadata["height"],
                        "type": metadata["type"],
                        "tile_type": TileType[metadata["type"].upper()],
                    }
        return groups

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
                self.set_tile(x + dx, y + dy, TileType.INTERIOR_BACKGROUND)

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
        # Skip for first room
        if len(self.rooms) <= 1:
            return

        new_room = self.rooms[room_id]
        nx, ny = new_room["grid_pos"]
        nw, nh = new_room["grid_size"]

        # Check for at least one valid connection
        for other_id, other in self.rooms.items():
            if other_id == room_id:
                continue

            ox, oy = other["grid_pos"]
            ow, oh = other["grid_size"]

            if self._are_rooms_adjacent(nx, ny, nw, nh, ox, oy, ow, oh):
                return  # Found a valid connection

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

        # Check for any overlaps with existing rooms
        for existing_room in self.rooms.values():
            ex, ey = existing_room["grid_pos"]
            ew, eh = existing_room["grid_size"]

            # Check if rectangles overlap
            if (
                grid_x < ex + ew
                and grid_x + width > ex
                and grid_y < ey + eh
                and grid_y + height > ey
            ):
                return False

        # If this is the first room, it's valid
        if not self.rooms:
            return True

        # Check for valid connections to existing rooms
        return self._has_valid_connection(grid_x, grid_y, width, height)

    def get_room_by_id(self, room_id: str) -> Optional[dict]:
        """Get the room data by ID"""
        return self.rooms.get(room_id)

    def get_room_by_grid_position(self, grid_x: int, grid_y: int) -> Optional[str]:
        """Get the room ID at a specific grid position"""
        for room_id, room in self.rooms.items():
            if room["grid_pos"] == (grid_x, grid_y):
                return room_id
        return None

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
        self._notify_tile_changes()  # Notify observers when a tile changes

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

    def add_tile_change_callback(self, callback):
        """Add a callback to be notified when tiles change"""
        self.tile_change_callbacks.append(callback)

    def _notify_tile_changes(self):
        """Notify all callbacks that tiles have changed"""
        for callback in self.tile_change_callbacks:
            callback()

    def is_valid_door_placement(self, grid_x: int, grid_y: int) -> bool:
        """
        Check if a door (2x3) can be placed at grid coordinates.
        Door must be placed on wall tiles, with wall tiles above and below.
        """
        # Check if the placement positions are currently walls
        door_positions = [
            (grid_x, grid_y),  # Left door tile
            (grid_x + 1, grid_y),  # Right door tile
        ]

        # Check if door positions are currently walls
        for x, y in door_positions:
            if self.get_tile(x, y) != TileType.WALL:
                return False

        # Check wall support above door
        wall_above = [
            (grid_x, grid_y - 1),  # Above left door
            (grid_x + 1, grid_y - 1),  # Above right door
        ]

        # Check wall support below door
        wall_below = [
            (grid_x, grid_y + 1),  # Below left door
            (grid_x + 1, grid_y + 1),  # Below right door
        ]

        # Verify walls exist above and below
        for pos in wall_above + wall_below:
            if self.get_tile(*pos) != TileType.WALL:
                return False

        return True

    def is_valid_tile_placement(self, grid_x: int, grid_y: int) -> bool:
        """Check if a single tile can be placed at grid coordinates"""
        # Check if position is already occupied
        if (grid_x, grid_y) in self.cells:
            return False

        # Check if position is adjacent to any existing tile
        adjacent_positions = [
            (grid_x - 1, grid_y),
            (grid_x + 1, grid_y),
            (grid_x, grid_y - 1),
            (grid_x, grid_y + 1),
        ]

        return any(pos in self.cells for pos in adjacent_positions)

    def is_valid_group_placement(
        self, grid_x: int, grid_y: int, group_name: str
    ) -> bool:
        """Generic validation for any tile group placement"""
        if group_name not in self.tile_groups:
            return False

        group = self.tile_groups[group_name]

        # Check door placement first, before the clear area check
        if group["type"] == "door":
            return self.is_valid_door_placement(grid_x, grid_y)

        # For non-door groups, check if area is clear
        width, height = group["width"], group["height"]
        for dx in range(width):
            for dy in range(height):
                if (grid_x + dx, grid_y + dy) in self.cells:
                    return False

        return True

    def place_tile_group(self, grid_x: int, grid_y: int, group_name: str) -> bool:
        """Place a tile group at the specified position"""
        if not self.is_valid_group_placement(grid_x, grid_y, group_name):
            return False

        group = self.tile_groups[group_name]
        for dx in range(group["width"]):
            for dy in range(group["height"]):
                self.set_tile(grid_x + dx, grid_y + dy, group["tile_type"])
        return True
