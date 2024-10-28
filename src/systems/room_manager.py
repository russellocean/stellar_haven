from typing import Dict, List, Optional

import pygame

from entities.room import Room
from systems.collision_system import CollisionSystem


class RoomManager:
    def __init__(self, x: int, y: int):
        self.rooms: Dict[str, Room] = {}
        self.room_sprites = pygame.sprite.Group()
        GRID_SIZE = 32

        # Snap the position to grid
        x = (x // GRID_SIZE) * GRID_SIZE
        y = (y // GRID_SIZE) * GRID_SIZE

        # Calculate top-left position for ship room to be centered on screen
        ship_image = pygame.image.load("assets/images/ship_interior.png")
        ship_width = ship_image.get_width()
        ship_height = ship_image.get_height()

        ship_x = x - (ship_width // 2)
        ship_y = y - (ship_height // 2)

        # Snap to grid
        ship_x = (ship_x // GRID_SIZE) * GRID_SIZE
        ship_y = (ship_y // GRID_SIZE) * GRID_SIZE

        # Add ship interior using topleft positioning like other rooms
        self.ship_room = Room(
            "ship_interior", "assets/images/ship_interior.png", ship_x, ship_y
        )
        self.ship_room.rect = self.ship_room.image.get_rect(topleft=(ship_x, ship_y))

        self.rooms["ship_interior"] = self.ship_room
        self.room_sprites.add(self.ship_room)

        self.collision_system = CollisionSystem(self)

    def add_room(self, room_type: str, x: int, y: int) -> Room:
        """Add a new room at the specified position"""
        image_path = f"assets/images/rooms/{room_type}.png"
        room = Room(room_type, image_path, x, y)
        room.rect = room.image.get_rect(topleft=(x, y))

        room_id = f"{room_type}_{len(self.rooms)}"
        self.rooms[room_id] = room
        self.room_sprites.add(room)

        # Update collision map after adding room
        self.collision_system.update_collision_map()

        print(f"Added room {room_id} at {x}, {y} with size {room.rect.size}")
        return room

    def get_rooms(self) -> List[Room]:
        """Get list of all rooms"""
        return list(self.rooms.values())

    def get_room_at_position(self, x: int, y: int) -> Optional[Room]:
        """Return the room at the given position, or None if no room exists there"""
        for room in self.rooms.values():
            if room.rect.collidepoint(x, y):
                return room
        return None

    def update(self, resource_manager):
        """Update all rooms"""
        for room in self.rooms.values():
            room.update(resource_manager=resource_manager)

    def draw(self, screen):
        """Draw all rooms"""
        for room in self.rooms.values():
            screen.blit(room.image, room.rect)
            pygame.draw.rect(screen, (100, 100, 100), room.rect, 2)  # Border

    def get_connected_rooms(self, room: Room) -> List[Room]:
        """Get all rooms that are connected to the given room"""
        connected = []
        for other_room in self.rooms.values():
            if other_room != room:
                if self._is_adjacent(room.rect, other_room.rect):
                    print(f"Found connected room: {other_room.name} to {room.name}")
                    print(f"Room1 rect: {room.rect}")
                    print(f"Room2 rect: {other_room.rect}")
                    connected.append(other_room)
        return connected

    def _is_adjacent(self, rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """Check if two rectangles are adjacent (sharing an edge)"""
        # Add a small tolerance for edge detection
        tolerance = 32 // 2

        # Check for horizontal adjacency
        horizontal_adjacent = (
            abs(rect1.right - rect2.left) <= tolerance
            or abs(rect1.left - rect2.right) <= tolerance
        )
        vertical_overlap = (
            rect1.top < rect2.bottom - tolerance
            and rect1.bottom > rect2.top + tolerance
        )

        # Check for vertical adjacency
        vertical_adjacent = (
            abs(rect1.bottom - rect2.top) <= tolerance
            or abs(rect1.top - rect2.bottom) <= tolerance
        )
        horizontal_overlap = (
            rect1.left < rect2.right - tolerance
            and rect1.right > rect2.left + tolerance
        )

        if (horizontal_adjacent and vertical_overlap) or (
            vertical_adjacent and horizontal_overlap
        ):
            print(f"Adjacent rects: {rect1} and {rect2}")
            print(f"H-adj: {horizontal_adjacent}, V-overlap: {vertical_overlap}")
            print(f"V-adj: {vertical_adjacent}, H-overlap: {horizontal_overlap}")
            return True
        return False
