from typing import List, Optional, Tuple

import pygame

from entities.room import Room
from systems.debug_system import DebugSystem
from ui.layouts.base_layout import BaseLayout


class RoomBuilderLayout(BaseLayout):
    def __init__(self, screen: pygame.Surface, room_manager):
        super().__init__(screen)
        self.selected_room_type: Optional[str] = None
        self.ghost_room: Optional[Room] = None
        self.valid_placement = False
        self.grid_size = 32
        self.ship_rect = None
        self.debug_system = DebugSystem()
        self.room_renderer = room_manager.room_renderer
        self.room_manager = room_manager

    def select_room_type(self, room_type: str):
        """Select a room type to build"""
        self.selected_room_type = room_type
        room_config = self.room_renderer.room_config["room_types"][room_type]
        size = (
            room_config["min_size"][0] * self.grid_size,
            room_config["min_size"][1] * self.grid_size,
        )

        # Create ghost room surface
        ghost_surface = pygame.Surface(size, pygame.SRCALPHA)
        self.room_renderer.render_room(
            surface=ghost_surface,
            room_type=room_type,
            rect=pygame.Rect(0, 0, *size),
            doors=[],  # Empty list for ghost room
        )

        # Create ghost room
        self.ghost_room = Room(room_type, None, 0, 0)
        self.ghost_room.image = ghost_surface
        self.ghost_room.rect = ghost_surface.get_rect()

        # Set initial alpha
        self.ghost_room.image.set_alpha(128)

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

        # Must be sharing exactly one wall with an existing room
        shared_wall_count = 0
        for room in existing_rooms:
            # Check for interior overlap (not including walls)
            ghost_interior = self.ghost_room.rect.inflate(
                -self.grid_size * 2, -self.grid_size * 2
            )
            room_interior = room.rect.inflate(-self.grid_size * 2, -self.grid_size * 2)

            if ghost_interior.colliderect(room_interior):
                return False

            # Check if we're sharing a wall
            shared_wall = self._get_shared_wall(self.ghost_room.rect, room.rect)
            if shared_wall:
                shared_wall_count += 1
                # Snap to the shared wall
                self._snap_to_shared_wall(self.ghost_room.rect, room.rect, shared_wall)

        return shared_wall_count == 1

    def _get_shared_wall(self, rect1: pygame.Rect, rect2: pygame.Rect) -> Optional[str]:
        """Check if two rectangles can share a wall"""
        # Check for sufficient overlap for a doorway
        min_overlap = self.grid_size * 2

        # Check vertical walls
        vertical_overlap = (
            min(rect1.bottom - self.grid_size, rect2.bottom - self.grid_size)
            - max(rect1.top + self.grid_size, rect2.top + self.grid_size)
        ) >= min_overlap

        if vertical_overlap:
            # Check if right wall of rect2 can connect to left wall of rect1
            if abs(rect2.right - rect1.left) <= self.grid_size:
                return "left"
            # Check if left wall of rect2 can connect to right wall of rect1
            if abs(rect2.left - rect1.right) <= self.grid_size:
                return "right"

        # Check horizontal walls
        horizontal_overlap = (
            min(rect1.right - self.grid_size, rect2.right - self.grid_size)
            - max(rect1.left + self.grid_size, rect2.left + self.grid_size)
        ) >= min_overlap

        if horizontal_overlap:
            # Check if bottom wall of rect2 can connect to top wall of rect1
            if abs(rect2.bottom - rect1.top) <= self.grid_size:
                return "top"
            # Check if top wall of rect2 can connect to bottom wall of rect1
            if abs(rect2.top - rect1.bottom) <= self.grid_size:
                return "bottom"

        return None

    def _snap_to_shared_wall(
        self, ghost_rect: pygame.Rect, room_rect: pygame.Rect, shared_wall: str
    ):
        """Snap ghost room to align with existing room wall"""
        if shared_wall == "left":
            ghost_rect.left = room_rect.right - self.grid_size
        elif shared_wall == "right":
            ghost_rect.right = room_rect.left + self.grid_size
        elif shared_wall == "top":
            ghost_rect.top = room_rect.bottom - self.grid_size
        elif shared_wall == "bottom":
            ghost_rect.bottom = room_rect.top + self.grid_size

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
