from typing import Dict, List, Optional

import pygame

from entities.room import Room
from systems.collision_system import CollisionSystem
from systems.debug_system import DebugSystem
from systems.room_renderer import RoomRenderer


class RoomManager:
    def __init__(self, center_x: int, center_y: int):
        self.rooms: Dict[str, Room] = {}
        self.room_sprites = pygame.sprite.Group()
        self.room_renderer = RoomRenderer()
        GRID_SIZE = 32

        # Snap the position to grid
        center_x = (center_x // GRID_SIZE) * GRID_SIZE
        center_y = (center_y // GRID_SIZE) * GRID_SIZE

        # Create initial ship room with modular rendering
        ship_size = (8 * GRID_SIZE, 6 * GRID_SIZE)  # Example size
        ship_x = center_x - (ship_size[0] // 2)
        ship_y = center_y - (ship_size[1] // 2)

        # Snap to grid
        ship_x = (ship_x // GRID_SIZE) * GRID_SIZE
        ship_y = (ship_y // GRID_SIZE) * GRID_SIZE

        # Create ship room surface
        ship_surface = pygame.Surface(ship_size, pygame.SRCALPHA)
        self.room_renderer.render_room(
            surface=ship_surface,
            room_type="bridge",  # Use bridge as the initial room type
            rect=pygame.Rect(0, 0, *ship_size),
            connected_sides=[False, False, False, False],
        )

        # Add ship interior as a Room
        self.ship_room = Room("bridge", None, ship_x, ship_y)  # Pass None as image_path
        self.ship_room.image = ship_surface  # Set the rendered surface as the image
        self.ship_room.rect = ship_surface.get_rect(topleft=(ship_x, ship_y))

        self.rooms["ship_interior"] = self.ship_room
        self.room_sprites.add(self.ship_room)

        # Initialize systems
        self.collision_system = CollisionSystem(self)
        self.debug = DebugSystem()
        self.debug.add_watch("Total Rooms", lambda: len(self.rooms))
        self.debug.add_watch(
            "Connected Rooms",
            lambda: (
                len(self.get_connected_rooms(self.ship_room)) if self.ship_room else 0
            ),
        )
        self.debug.add_watch("Grid Size", lambda: self.collision_system.grid_size)

    def add_room(self, room_type: str, x: int, y: int) -> Room:
        """Add a new room at the specified position"""
        # Get room size from config
        room_config = self.room_renderer.room_config["room_types"][room_type]
        room_size = (
            room_config["min_size"][0] * 32,  # Use min_size as default
            room_config["min_size"][1] * 32,
        )

        # Create room surface
        room_surface = pygame.Surface(room_size, pygame.SRCALPHA)
        self.room_renderer.render_room(
            surface=room_surface,
            room_type=room_type,
            rect=pygame.Rect(0, 0, *room_size),
            connected_sides=[False, False, False, False],
        )

        # Create room instance
        room = Room(room_type, None, x, y)  # Pass None as image_path
        room.image = room_surface
        room.rect = room_surface.get_rect(topleft=(x, y))

        room_id = f"{room_type}_{len(self.rooms)}"
        self.rooms[room_id] = room
        self.room_sprites.add(room)

        # Update collision map
        self.collision_system.update_collision_map()
        self.debug.log(f"Added room {room_id} at {x}, {y} with size {room.rect.size}")

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
            # Update connected sides before drawing
            connected_sides = [
                any(
                    r.rect.bottom == room.rect.top
                    for r in self.rooms.values()
                    if r != room
                ),
                any(
                    r.rect.left == room.rect.right
                    for r in self.rooms.values()
                    if r != room
                ),
                any(
                    r.rect.top == room.rect.bottom
                    for r in self.rooms.values()
                    if r != room
                ),
                any(
                    r.rect.right == room.rect.left
                    for r in self.rooms.values()
                    if r != room
                ),
            ]

            # Re-render room with updated connections
            room_surface = pygame.Surface(room.rect.size, pygame.SRCALPHA)
            self.room_renderer.render_room(
                surface=room_surface,
                room_type=room.room_type,
                rect=room_surface.get_rect(),
                connected_sides=connected_sides,
            )
            room.image = room_surface

            # Draw the room
            screen.blit(room.image, room.rect)

            # Draw debug border if needed
            pygame.draw.rect(screen, (100, 100, 100), room.rect, 2)

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
