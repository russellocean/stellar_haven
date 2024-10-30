from typing import Dict, List, Optional, Tuple

import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager


class Grid:
    def __init__(self, cell_size: int = 32):
        self.cell_size = cell_size
        self.cells: Dict[Tuple[int, int], TileType] = {}
        self.rooms: Dict[str, dict] = {}  # Stores room data including rect and type
        self.asset_manager = AssetManager()
        self.room_config = self.asset_manager.get_config("rooms")

    def add_room(
        self, room_id: str, room_type: str, world_x: int, world_y: int
    ) -> pygame.Rect:
        """Add a room to the grid and return its rect"""
        # Get room size from config
        grid_size = self.room_config["room_types"][room_type]["grid_size"]
        pixel_size = (grid_size[0] * self.cell_size, grid_size[1] * self.cell_size)

        # Create room rect
        room_rect = pygame.Rect(world_x, world_y, *pixel_size)

        # Store room data
        self.rooms[room_id] = {
            "type": room_type,
            "rect": room_rect,
            "grid_size": grid_size,
        }

        # Add room tiles to collision map
        self._add_room_tiles(room_id)

        # Process connections and add doors
        self._process_connections(room_id)

        return room_rect

    def _add_room_tiles(self, room_id: str) -> None:
        """Add floor and wall tiles for a room - side view perspective"""
        room = self.rooms[room_id]
        rect = room["rect"]

        # Convert to grid coordinates
        left, top = self.world_to_grid(rect.left, rect.top)
        right = left + room["grid_size"][0]
        bottom = top + room["grid_size"][1]

        # Add walls on left and right sides
        for y in range(top, bottom):
            self.cells[(left, y)] = TileType.WALL
            self.cells[(right - 1, y)] = TileType.WALL

        # Add ceiling
        for x in range(left + 1, right - 1):
            self.cells[(x, top)] = TileType.WALL

        # Add floor at the bottom
        for x in range(left + 1, right - 1):
            self.cells[(x, bottom - 1)] = TileType.FLOOR

        # Add empty space in the middle
        for x in range(left + 1, right - 1):
            for y in range(top + 1, bottom - 1):
                self.cells[(x, y)] = TileType.EMPTY

    def _process_connections(self, room_id: str) -> None:
        """Process connections for a room"""
        new_room = self.rooms[room_id]

        for other_id, other_room in self.rooms.items():
            if other_id != room_id:
                self._add_doors_if_adjacent(new_room, other_room)

    def _add_doors_if_adjacent(self, room1: dict, room2: dict) -> None:
        """Add doors between adjacent rooms following door rules"""
        rect1, rect2 = room1["rect"], room2["rect"]
        door_rules = self.room_config["door_rules"]
        min_corner_dist = door_rules["min_distance_from_corner"]

        # Check horizontal adjacency (vertical walls)
        if rect1.right == rect2.left or rect1.left == rect2.right:
            overlap_start = max(rect1.top, rect2.top)
            overlap_end = min(rect1.bottom, rect2.bottom)
            valid_door_range = (
                overlap_end - overlap_start - (2 * min_corner_dist * self.cell_size)
            )

            if valid_door_range >= door_rules["door_size"][1] * self.cell_size:
                door_y = overlap_start + (min_corner_dist * self.cell_size)
                door_x = rect1.right if rect1.right == rect2.left else rect1.left

                # Add door tiles
                grid_x, grid_y = self.world_to_grid(door_x, door_y)
                self.cells[(grid_x, grid_y)] = TileType.DOOR
                self.cells[(grid_x, grid_y + 1)] = TileType.DOOR

        # Check vertical adjacency (horizontal walls)
        elif rect1.bottom == rect2.top or rect1.top == rect2.bottom:
            overlap_start = max(rect1.left, rect2.left)
            overlap_end = min(rect1.right, rect2.right)
            valid_door_range = (
                overlap_end - overlap_start - (2 * min_corner_dist * self.cell_size)
            )

            if valid_door_range >= door_rules["door_size"][0] * self.cell_size:
                door_x = overlap_start + (min_corner_dist * self.cell_size)
                door_y = rect1.bottom if rect1.bottom == rect2.top else rect1.top

                # Add door tiles
                grid_x, grid_y = self.world_to_grid(door_x, door_y)
                self.cells[(grid_x, grid_y)] = TileType.DOOR
                self.cells[(grid_x + 1, grid_y)] = TileType.DOOR

    def is_valid_room_placement(self, rect: pygame.Rect) -> bool:
        """Check if a room can be placed at the given position"""
        # Convert to grid coordinates
        left, top = self.world_to_grid(rect.left, rect.top)
        right, bottom = self.world_to_grid(rect.right, rect.bottom)

        # Check if area is clear
        for x in range(left - 1, right + 1):
            for y in range(top - 1, bottom + 1):
                if (x, y) in self.cells:
                    return False

        # Check if adjacent to at least one room (except first room)
        if self.rooms:
            has_adjacent = False
            for room in self.rooms.values():
                if (
                    abs(rect.left - room["rect"].right) <= self.cell_size
                    or abs(rect.right - room["rect"].left) <= self.cell_size
                    or abs(rect.top - room["rect"].bottom) <= self.cell_size
                    or abs(rect.bottom - room["rect"].top) <= self.cell_size
                ):
                    has_adjacent = True
                    break
            if not has_adjacent:
                return False

        return True

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

    def get_room_by_position(self, x: int, y: int) -> Optional[str]:
        """Get the room ID at a specific position"""
        for room_id, room in self.rooms.items():
            if room["rect"].collidepoint(x, y):
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
