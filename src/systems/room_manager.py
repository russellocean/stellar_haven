from typing import Dict, List, Optional

import pygame

from entities.room import Room


class RoomManager:
    def __init__(self, x: int, y: int):
        self.rooms: Dict[str, Room] = {}
        self.room_sprites = pygame.sprite.Group()

        # Add ship interior as the first room (base size: 32 * 20, 32 * 15)
        self.ship_room = Room("ship_interior", "assets/images/ship_interior.png", x, y)
        self.rooms["ship_interior"] = self.ship_room
        self.room_sprites.add(self.ship_room)

    def add_room(self, room_type: str, x: int, y: int) -> Room:
        """Add a new room at the specified position"""
        image_path = f"assets/images/rooms/{room_type}.png"
        room = Room(room_type, image_path, x, y)
        room.rect = room.image.get_rect(topleft=(x, y))

        room_id = f"{room_type}_{len(self.rooms)}"
        self.rooms[room_id] = room
        self.room_sprites.add(room)
        print(f"Added room {room_id} at {x}, {y} with size {room.rect.size}")
        return room

    def get_rooms(self) -> List[Room]:
        """Get list of all rooms"""
        return list(self.rooms.values())

    def get_room_at_position(self, x: int, y: int) -> Optional[Room]:
        """Get the room at the given position"""
        for room in self.rooms.values():
            if room.contains_point(x, y):
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
