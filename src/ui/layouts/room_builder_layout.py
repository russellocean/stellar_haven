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
        self.grid = room_manager.grid  # Use the grid from room manager
        self.debug_system = DebugSystem()
        self.room_renderer = room_manager.room_renderer
        self.room_manager = room_manager

    def select_room_type(self, room_type: str):
        """Select a room type to build"""
        self.selected_room_type = room_type
        room_config = self.room_renderer.room_config["room_types"][room_type]
        size = (
            room_config["grid_size"][0] * self.grid.cell_size,
            room_config["grid_size"][1] * self.grid.cell_size,
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

        # Get room dimensions from config
        room_config = self.room_renderer.room_config["room_types"][
            self.selected_room_type
        ]
        grid_size = room_config["grid_size"]
        pixel_size = (
            grid_size[0] * self.grid.cell_size,
            grid_size[1] * self.grid.cell_size,
        )

        # Snap to grid
        x = (mouse_pos[0] // self.grid.cell_size) * self.grid.cell_size
        y = (mouse_pos[1] // self.grid.cell_size) * self.grid.cell_size

        # Center the room on the mouse cursor
        x -= pixel_size[0] // 2
        y -= pixel_size[1] // 2

        self.debug_system.add_watch("Ghost Room Position", lambda: f"({x}, {y})")

        # Update ghost room position
        ghost_rect = pygame.Rect(x, y, *pixel_size)
        self.ghost_room.rect = ghost_rect

        # Check placement validity using grid system
        self.valid_placement = self.grid.is_valid_room_placement(ghost_rect)

        # Update ghost room transparency
        self.ghost_room.image.set_alpha(128 if self.valid_placement else 64)

        return self.valid_placement

    def _draw_placement_grid(self, surface: pygame.Surface):
        """Draw placement grid when active"""
        if self.ghost_room:
            # Draw grid around placement area
            grid_rect = self.ghost_room.rect.inflate(
                self.grid.cell_size * 2, self.grid.cell_size * 2
            )

            # Draw vertical lines
            for x in range(grid_rect.left, grid_rect.right, self.grid.cell_size):
                pygame.draw.line(
                    surface,
                    (255, 255, 255, 30),
                    (x, grid_rect.top),
                    (x, grid_rect.bottom),
                )

            # Draw horizontal lines
            for y in range(grid_rect.top, grid_rect.bottom, self.grid.cell_size):
                pygame.draw.line(
                    surface,
                    (255, 255, 255, 30),
                    (grid_rect.left, y),
                    (grid_rect.right, y),
                )

    def draw(self, surface: pygame.Surface):
        """Override BaseLayout's draw method"""
        if not self.visible or not self.ghost_room:
            return

        # Draw ghost room
        surface.blit(self.ghost_room.image, self.ghost_room.rect)

        # Draw grid or other UI elements if needed
        self._draw_placement_grid(surface)
