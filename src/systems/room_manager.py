from typing import Dict, List

import pygame

from entities.room import Room
from grid.grid import Grid
from systems.collision_system import CollisionSystem
from systems.debug_system import DebugSystem
from systems.room_renderer import RoomRenderer


class RoomManager:
    def __init__(self, center_x: int, center_y: int):
        self.grid = Grid(cell_size=32)
        self.rooms: Dict[str, Room] = {}
        self.room_sprites = pygame.sprite.Group()
        self.room_renderer = RoomRenderer(self)
        self.collision_system = CollisionSystem(self.grid)
        self.ship_room = None

        # Initialize debug system
        self.debug = DebugSystem()
        self.debug.add_watch("Total Rooms", lambda: len(self.rooms))

        # Create initial ship room
        self._create_initial_ship(center_x, center_y)

    def _create_initial_ship(self, center_x: int, center_y: int):
        # Get bridge size from config
        room_type = "bridge"
        grid_size = self.grid.room_config["room_types"][room_type]["grid_size"]

        # Calculate position (centered)
        ship_x = center_x - (grid_size[0] * self.grid.cell_size) // 2
        ship_y = center_y - (grid_size[1] * self.grid.cell_size) // 2

        # Snap to grid
        ship_x = (ship_x // self.grid.cell_size) * self.grid.cell_size
        ship_y = (ship_y // self.grid.cell_size) * self.grid.cell_size

        # Add initial room and store reference
        self.ship_room = self.add_room(room_type, ship_x, ship_y)

    def add_room(self, room_type: str, x: int, y: int) -> Room:
        """Add a new room at the specified position"""
        room_id = f"{room_type}_{len(self.rooms)}"

        # Add room to grid first
        room_rect = self.grid.add_room(room_id, room_type, x, y)

        # Get doors for rendering
        doors = self.grid.get_doors_for_room(room_id)

        # Create room surface
        room_surface = pygame.Surface(room_rect.size, pygame.SRCALPHA)
        self.room_renderer.render_room(
            surface=room_surface, room_type=room_type, rect=room_rect, doors=doors
        )

        # Create room instance
        room = Room(room_type, None, x, y)
        room.image = room_surface
        room.rect = room_rect

        # Add to collections
        self.rooms[room_id] = room
        self.room_sprites.add(room)

        return room

    def get_connected_rooms(self, room: Room) -> List[Room]:
        """Get all rooms connected to the given room"""
        connected = []
        room_id = next(id for id, r in self.rooms.items() if r == room)

        for other_id, other_room in self.rooms.items():
            if other_id != room_id and self.grid.are_rooms_connected(room_id, other_id):
                connected.append(other_room)

        return connected
