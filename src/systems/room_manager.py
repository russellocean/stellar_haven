from typing import Dict, List

import pygame

from entities.room import Room
from grid.grid import Grid
from systems.collision_system import CollisionSystem
from systems.debug_system import DebugSystem


class RoomManager:
    def __init__(
        self,
        center_x: int,
        center_y: int,
        resource_manager=None,
        interaction_system=None,
    ):
        self.grid = Grid(cell_size=16)
        self.rooms: Dict[str, Room] = {}
        self.collision_system = CollisionSystem(self.grid)
        self.resource_manager = resource_manager
        self.starting_room = None  # Reference to starting room
        self.interaction_system = interaction_system

        # Initialize debug system
        self.debug = DebugSystem()
        self.debug.add_watch("Total Rooms", lambda: len(self.rooms))

        # Create initial ship
        self._create_initial_ship(center_x, center_y)

        self.camera = None  # Will be set by GameplayScene

    def _create_initial_ship(self, center_x: int, center_y: int):
        # Find the starting room type from config
        starting_room_type = next(
            (
                room_type
                for room_type, data in self.grid.room_config["room_types"].items()
                if data.get("is_starting_room", False)
            ),
            "starting_quarters",  # Fallback if not found
        )

        grid_size = self.grid.room_config["room_types"][starting_room_type]["grid_size"]

        # Calculate position (centered)
        ship_x = center_x - (grid_size[0] * self.grid.cell_size) // 2
        ship_y = center_y - (grid_size[1] * self.grid.cell_size) // 2

        # Snap to grid
        ship_x = (ship_x // self.grid.cell_size) * self.grid.cell_size
        ship_y = (ship_y // self.grid.cell_size) * self.grid.cell_size

        # Add initial room and store reference
        self.starting_room = self.add_room(
            starting_room_type, ship_x, ship_y, "starting_room"
        )

    def add_room(
        self, room_type: str, world_x: int, world_y: int, room_id: str = None
    ) -> Room:
        """Add a room at world coordinates"""
        # Convert world coordinates to grid coordinates
        grid_x = world_x // self.grid.cell_size
        grid_y = world_y // self.grid.cell_size

        # Generate room ID if not provided
        if room_id is None:
            room_id = f"room_{len(self.rooms)}"

        # Add room to grid
        if self.grid.add_room(room_id, room_type, grid_x, grid_y):
            # Create Room entity with all necessary references
            room = Room(
                room_type=room_type,
                grid_pos=(grid_x, grid_y),
                cell_size=self.grid.cell_size,
                room_id=room_id,
                resource_manager=self.resource_manager,
                grid=self.grid,
                interaction_system=self.interaction_system,
            )

            # Get valid interior positions for interactables
            interior_positions = self.grid.get_interior_positions(room_id)
            if interior_positions:
                # Pass interior positions to room for interactable placement
                room.set_interior_positions(interior_positions)

            self.rooms[room_id] = room

            # Register room with resource manager
            if self.resource_manager:
                self.resource_manager.register_room(room)

            return room
        return None

    def get_room_center(self, room: Room) -> tuple[int, int]:
        """Get the center position of a room in world coordinates"""
        # Get room's grid position directly from Room object
        grid_x, grid_y = room.grid_pos
        room_data = self.grid.room_config["room_types"][room.room_type]
        width, height = room_data["grid_size"]

        # Calculate center
        center_x = grid_x + (width // 2)
        center_y = grid_y + (height // 2)

        # Convert to world coordinates
        world_x = center_x * self.grid.cell_size
        world_y = center_y * self.grid.cell_size

        print(f"Room center calculated for {room.room_id}: ({world_x}, {world_y})")
        return (world_x, world_y)

    def get_connected_rooms(self, room: Room) -> List[Room]:
        """Get all rooms connected to the given room"""
        connected = []
        room_id = next(id for id, r in self.rooms.items() if r == room)

        for other_id, other_room in self.rooms.items():
            if other_id != room_id and self.grid.are_rooms_connected(room_id, other_id):
                connected.append(other_room)

        return connected

    def get_rooms(self) -> Dict[str, Room]:
        """Get all rooms"""
        return self.rooms

    def get_starting_position(self) -> tuple[int, int]:
        """Get the starting position of the ship in world coordinates"""
        return self.get_room_center(self.starting_room)

    def set_camera(self, camera):
        """Set camera reference"""
        self.camera = camera

    def render(self, surface: pygame.Surface, camera):
        """Render all rooms and their interactables"""
        self.camera = camera  # Store camera reference

        # First render all rooms and their decorations
        for room in self.rooms.values():
            room.render(surface, camera)

        # Then let interaction system render all interactables
        if self.interaction_system:
            self.interaction_system.render(surface, camera)
