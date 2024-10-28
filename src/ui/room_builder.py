from typing import List, Optional, Tuple

import pygame

from entities.room import Room


class RoomBuilder:
    def __init__(self, screen):
        self.screen = screen
        self.selected_room_type: Optional[str] = None
        self.ghost_room: Optional[Room] = None
        self.valid_placement = False
        self.grid_size = 32  # Size of snap grid
        self.ship_rect = None  # Add this to store ship boundaries

        # Available room types and their costs
        self.room_types = {
            "bridge": {"size": (200, 150), "cost": 100},
            "engine_room": {"size": (200, 150), "cost": 150},
            "life_support": {"size": (200, 150), "cost": 120},
            "medical_bay": {"size": (200, 150), "cost": 130},
        }

    def select_room_type(self, room_type: str):
        """Select a room type to place"""
        if room_type in self.room_types:
            self.selected_room_type = room_type
            # Create ghost room
            self.ghost_room = Room(
                room_type,
                f"assets/images/rooms/{room_type}.png",
                0,
                0,  # Position will be updated with mouse
            )
            self.ghost_room.image.set_alpha(128)  # Make semi-transparent

    def update(self, mouse_pos: Tuple[int, int], existing_rooms: List[Room]) -> bool:
        """Update ghost room position and check placement validity"""
        if not self.ghost_room:
            return False

        # Get room dimensions
        room_width = self.ghost_room.rect.width
        room_height = self.ghost_room.rect.height

        # Center the room on the mouse cursor
        x = mouse_pos[0] - room_width // 2
        y = mouse_pos[1] - room_height // 2

        # Snap to grid
        x = round(x / self.grid_size) * self.grid_size
        y = round(y / self.grid_size) * self.grid_size

        # Update ghost room position to follow cursor
        self.ghost_room.rect.topleft = (x, y)

        # Check if placement is valid
        self.valid_placement = self._check_valid_placement(existing_rooms)

        # Update ghost room transparency based on validity
        self.ghost_room.image.set_alpha(128 if self.valid_placement else 64)

        return self.valid_placement

    def _check_valid_placement(self, existing_rooms: List[Room]) -> bool:
        """Check if current ghost room position is valid"""
        if not self.ghost_room:
            return False

        # Must be adjacent to at least one room but not overlapping
        adjacent = False
        for room in existing_rooms:
            # Check for overlap
            if self.ghost_room.rect.colliderect(room.rect):
                return False

            # Check for adjacency (sharing an edge)
            if self._is_adjacent(self.ghost_room.rect, room.rect):
                adjacent = True

        return adjacent

    def _is_adjacent(self, rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """Check if two rectangles are adjacent (sharing an edge)"""
        # Add a small tolerance for edge detection
        tolerance = self.grid_size // 2

        # Check for horizontal adjacency (left or right edges touching)
        horizontal_adjacent = (
            abs(rect1.right - rect2.left) <= tolerance
            or abs(rect1.left - rect2.right) <= tolerance
        )
        vertical_overlap = (
            rect1.top < rect2.bottom - tolerance
            and rect1.bottom > rect2.top + tolerance
        )

        if horizontal_adjacent and vertical_overlap:
            return True

        # Check for vertical adjacency (top or bottom edges touching)
        vertical_adjacent = (
            abs(rect1.bottom - rect2.top) <= tolerance
            or abs(rect1.top - rect2.bottom) <= tolerance
        )
        horizontal_overlap = (
            rect1.left < rect2.right - tolerance
            and rect1.right > rect2.left + tolerance
        )

        if vertical_adjacent and horizontal_overlap:
            return True

        return False

    def _is_adjacent_to_ship(self) -> bool:
        """Check if the room is adjacent to the ship's starting room"""
        if not self.ship_rect:
            return False

        # Use the same adjacency check for the ship rect
        return self._is_adjacent(self.ghost_room.rect, self.ship_rect)

    def draw(self):
        """Draw ghost room and any UI elements"""
        if self.ghost_room:
            self.screen.blit(self.ghost_room.image, self.ghost_room.rect)
