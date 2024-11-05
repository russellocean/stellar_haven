from typing import Dict, List

from entities.room import Room
from grid.grid import Grid
from systems.collision_system import CollisionSystem
from systems.debug_system import DebugSystem


class RoomManager:
    def __init__(self, center_x: int, center_y: int):
        self.grid = Grid(cell_size=16)
        self.rooms: Dict[str, Room] = {}
        self.collision_system = CollisionSystem(self.grid)
        self.starting_room = None  # Reference to starting room

        # Initialize debug system
        self.debug = DebugSystem()
        self.debug.add_watch("Total Rooms", lambda: len(self.rooms))

        # Create initial ship
        self._create_initial_ship(center_x, center_y)

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
            # Create Room entity
            room = Room(
                room_type=room_type,
                grid_pos=(grid_x, grid_y),
                cell_size=self.grid.cell_size,
            )
            self.rooms[room_id] = room
            print(f"Added room {room_id} at grid pos ({grid_x}, {grid_y})")
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
        return (center_x * self.grid.cell_size, center_y * self.grid.cell_size)

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
