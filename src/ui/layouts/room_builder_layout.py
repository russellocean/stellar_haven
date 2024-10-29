from typing import List, Optional, Tuple

import pygame

from entities.room import Room
from systems.debug_system import DebugSystem
from systems.room_renderer import RoomRenderer
from ui.layouts.base_layout import BaseLayout


class RoomBuilderLayout(BaseLayout):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.selected_room_type: Optional[str] = None
        self.ghost_room: Optional[Room] = None
        self.valid_placement = False
        self.grid_size = 32
        self.ship_rect = None
        self.debug_system = DebugSystem()
        self.room_renderer = RoomRenderer()

    def select_room_type(self, room_type: str):
        """Select a room type to place"""
        if room_type in self.room_renderer.room_config["room_types"]:
            self.selected_room_type = room_type

            # Create ghost room using RoomRenderer
            room_config = self.room_renderer.room_config["room_types"][room_type]
            min_size = room_config.get("min_size", [6, 4])
            room_size = (min_size[0] * self.grid_size, min_size[1] * self.grid_size)

            # Create ghost room with empty surface
            self.ghost_room = Room(room_type, None, 0, 0)
            self.ghost_room.image = pygame.Surface(room_size, pygame.SRCALPHA)

            # Render the room
            self.room_renderer.render_room(
                surface=self.ghost_room.image,
                room_type=room_type,
                rect=pygame.Rect(0, 0, *room_size),
                connected_sides=[False, False, False, False],
            )

            # Set transparency for ghost effect
            self.ghost_room.image.fill(
                (255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT
            )

    def update(self, mouse_pos: Tuple[int, int], existing_rooms: List[Room]) -> bool:
        """Update ghost room position and check placement validity"""
        if not self.ghost_room or not self.visible:
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

        self.debug_system.add_watch("Ghost Room Position", lambda: f"({x}, {y})")

        # Update ghost room position
        self.ghost_room.rect.topleft = (x, y)

        # Check placement validity
        self.valid_placement = self._check_valid_placement(existing_rooms)

        # Update ghost room transparency
        self.ghost_room.image.set_alpha(128 if self.valid_placement else 64)

        return self.valid_placement

    def _check_valid_placement(self, existing_rooms: List[Room]) -> bool:
        """Check if current ghost room position is valid"""
        if not self.ghost_room:
            return False

        # Must be adjacent to at least one room but not overlapping
        adjacent = False
        for room in existing_rooms:
            if self.ghost_room.rect.colliderect(room.rect):
                return False
            if self._is_adjacent(self.ghost_room.rect, room.rect):
                adjacent = True

        return adjacent

    def _is_adjacent(self, rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """Check if two rectangles are adjacent with enough space for player passage"""
        tolerance = self.grid_size // 2
        min_passage = self.grid_size * 2  # Minimum 2 grid spaces for player

        # Check for horizontal adjacency (left or right edges touching)
        horizontal_adjacent = (
            abs(rect1.right - rect2.left) <= tolerance
            or abs(rect1.left - rect2.right) <= tolerance
        )
        # Ensure vertical overlap is enough for player height
        vertical_overlap = (
            rect1.top < rect2.bottom - tolerance - min_passage
            and rect1.bottom > rect2.top + tolerance + min_passage
        )

        if horizontal_adjacent and vertical_overlap:
            return True

        # Check for vertical adjacency (top or bottom edges touching)
        vertical_adjacent = (
            abs(rect1.bottom - rect2.top) <= tolerance
            or abs(rect1.top - rect2.bottom) <= tolerance
        )
        # Ensure horizontal overlap is enough for player width
        horizontal_overlap = (
            rect1.left < rect2.right - tolerance - min_passage
            and rect1.right > rect2.left + tolerance + min_passage
        )

        return vertical_adjacent and horizontal_overlap

    def draw(self, surface: pygame.Surface):
        """Override BaseLayout's draw method"""
        if not self.visible or not self.ghost_room:
            return

        # Draw ghost room
        surface.blit(self.ghost_room.image, self.ghost_room.rect)

        # Draw grid or other UI elements if needed
        self._draw_placement_grid(surface)

    def _draw_placement_grid(self, surface: pygame.Surface):
        """Draw placement grid when active"""
        if self.ghost_room:
            # Draw grid around placement area
            grid_rect = self.ghost_room.rect.inflate(
                self.grid_size * 2, self.grid_size * 2
            )

            # Draw vertical lines
            for x in range(grid_rect.left, grid_rect.right, self.grid_size):
                pygame.draw.line(
                    surface,
                    (255, 255, 255, 30),
                    (x, grid_rect.top),
                    (x, grid_rect.bottom),
                )

            # Draw horizontal lines
            for y in range(grid_rect.top, grid_rect.bottom, self.grid_size):
                pygame.draw.line(
                    surface,
                    (255, 255, 255, 30),
                    (grid_rect.left, y),
                    (grid_rect.right, y),
                )
