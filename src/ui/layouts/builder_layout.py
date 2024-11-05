from typing import List, Optional, Tuple

import pygame

from entities.room import Room
from systems.debug_system import DebugSystem
from ui.layouts.base_layout import BaseLayout


class BuilderLayout(BaseLayout):
    def __init__(self, screen: pygame.Surface, room_manager):
        super().__init__(screen)
        self.selected_type: Optional[str] = None
        self.selected_category: Optional[str] = None
        self.ghost_position: Optional[Tuple[int, int]] = None
        self.valid_placement = False
        self.grid = room_manager.grid
        self.debug_system = DebugSystem()
        self.room_manager = room_manager

        # Ghost rendering colors
        self.VALID_COLOR = (0, 255, 0, 128)  # Semi-transparent green
        self.INVALID_COLOR = (255, 0, 0, 128)  # Semi-transparent red
        self.GRID_COLOR = (255, 255, 255, 30)  # Very transparent white

        self.debug_system.add_watch("Ghost Position", lambda: self.ghost_position)
        self.debug_system.add_watch("Valid Placement", lambda: self.valid_placement)
        self.debug_system.add_watch("Selected Type", lambda: self.selected_type)
        self.debug_system.add_watch("Selected Category", lambda: self.selected_category)

    def select_build_type(self, category: str, build_type: str):
        """Select a type to build"""
        self.selected_category = category
        self.selected_type = build_type
        self.ghost_position = None
        self.valid_placement = False

    def update(self, mouse_pos: Tuple[int, int], existing_rooms: List[Room]) -> bool:
        """Update ghost position and check placement validity"""
        if not self.selected_type or not self.visible:
            return False

        grid_x = mouse_pos[0] // self.grid.cell_size
        grid_y = mouse_pos[1] // self.grid.cell_size

        # Handle different categories
        if self.selected_category == "rooms":
            room_config = self.grid.room_config["room_types"][self.selected_type]
            grid_size = room_config["grid_size"]
            grid_x -= grid_size[0] // 2
            grid_y -= grid_size[1] // 2
            self.valid_placement = self.grid.is_valid_room_placement(
                grid_x, grid_y, self.selected_type
            )
        elif self.selected_category == "doors":
            # Center the door horizontally (2 tiles wide)
            grid_x -= 1
            self.valid_placement = self.grid.is_valid_door_placement(grid_x, grid_y)
        else:
            # Single-tile items
            self.valid_placement = self.grid.is_valid_tile_placement(grid_x, grid_y)

        self.ghost_position = (grid_x, grid_y)
        return self.valid_placement

    def draw(self, surface: pygame.Surface):
        """Draw ghost and placement grid"""
        if not self.visible or not self.selected_type or not self.ghost_position:
            return

        world_x = self.ghost_position[0] * self.grid.cell_size
        world_y = self.ghost_position[1] * self.grid.cell_size

        if self.selected_category == "rooms":
            room_config = self.grid.room_config["room_types"][self.selected_type]
            grid_size = room_config["grid_size"]
            width = grid_size[0] * self.grid.cell_size
            height = grid_size[1] * self.grid.cell_size

            # Create ghost room surface
            ghost_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            color = self.VALID_COLOR if self.valid_placement else self.INVALID_COLOR

            # Draw room outline
            pygame.draw.rect(ghost_surface, color, ghost_surface.get_rect(), 0)

            # Draw internal grid lines
            self._draw_room_grid(ghost_surface, grid_size)
        elif self.selected_category == "doors":
            # Create ghost door surface (2x3)
            ghost_surface = pygame.Surface(
                (self.grid.cell_size * 2, self.grid.cell_size * 3), pygame.SRCALPHA
            )
            color = self.VALID_COLOR if self.valid_placement else self.INVALID_COLOR
            pygame.draw.rect(ghost_surface, color, ghost_surface.get_rect(), 0)
        else:
            # Draw single-tile ghost
            ghost_surface = pygame.Surface(
                (self.grid.cell_size, self.grid.cell_size), pygame.SRCALPHA
            )
            color = self.VALID_COLOR if self.valid_placement else self.INVALID_COLOR
            pygame.draw.rect(ghost_surface, color, ghost_surface.get_rect(), 0)

        # Apply camera offset
        if hasattr(self, "camera"):
            screen_x = world_x - self.camera.x
            screen_y = world_y - self.camera.y
        else:
            screen_x = world_x
            screen_y = world_y

        # Draw the ghost at screen position
        surface.blit(ghost_surface, (screen_x, screen_y))

        # Draw placement grid around the ghost
        if self.selected_category == "rooms":
            self._draw_placement_grid(surface, screen_x, screen_y, width, height)

    def _draw_room_grid(self, surface: pygame.Surface, grid_size: Tuple[int, int]):
        """Draw internal grid lines for the room"""
        width, height = surface.get_size()

        # Draw vertical lines
        for x in range(0, width, self.grid.cell_size):
            pygame.draw.line(surface, self.GRID_COLOR, (x, 0), (x, height))

        # Draw horizontal lines
        for y in range(0, height, self.grid.cell_size):
            pygame.draw.line(surface, self.GRID_COLOR, (0, y), (width, y))

    def _draw_placement_grid(
        self, surface: pygame.Surface, x: int, y: int, width: int, height: int
    ):
        """Draw grid lines around placement area"""
        # Inflate the area by one cell on each side
        grid_rect = pygame.Rect(
            x - self.grid.cell_size,
            y - self.grid.cell_size,
            width + self.grid.cell_size * 2,
            height + self.grid.cell_size * 2,
        )

        # Draw vertical lines
        for gx in range(grid_rect.left, grid_rect.right + 1, self.grid.cell_size):
            pygame.draw.line(
                surface, self.GRID_COLOR, (gx, grid_rect.top), (gx, grid_rect.bottom)
            )

        # Draw horizontal lines
        for gy in range(grid_rect.top, grid_rect.bottom + 1, self.grid.cell_size):
            pygame.draw.line(
                surface, self.GRID_COLOR, (grid_rect.left, gy), (grid_rect.right, gy)
            )
