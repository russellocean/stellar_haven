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
        self.room_manager = room_manager

        # Colors as class constants
        self.VALID_COLOR = (0, 255, 0, 128)
        self.INVALID_COLOR = (255, 0, 0, 128)
        self.GRID_COLOR = (255, 255, 255, 30)

        self._setup_debug()

    def _setup_debug(self):
        """Initialize debug system and watches"""
        self.debug_system = DebugSystem()
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

    def clear_selection(self):
        """Clear current selection and ghost"""
        self.selected_type = None
        self.selected_category = None
        self.ghost_position = None
        self.valid_placement = False

    def _get_ghost_position(self, mouse_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate grid position based on category"""
        grid_x = mouse_pos[0] // self.grid.cell_size
        grid_y = mouse_pos[1] // self.grid.cell_size

        if self.selected_category == "rooms":
            room_config = self.grid.room_config["room_types"][self.selected_type]
            grid_size = room_config["grid_size"]
            grid_x -= grid_size[0] // 2
            grid_y -= grid_size[1] // 2
        elif self.selected_category == "structures":
            grid_x -= 1  # Center 2-tile wide door

        return grid_x, grid_y

    def update(self, mouse_pos: Tuple[int, int], existing_rooms: List[Room]) -> bool:
        """Update ghost position and check placement validity"""
        if not self.selected_type or not self.visible:
            return False

        self.ghost_position = self._get_ghost_position(mouse_pos)
        grid_x, grid_y = self.ghost_position

        # Check validity based on category
        if self.selected_category == "rooms":
            self.valid_placement = self.grid.is_valid_room_placement(
                grid_x, grid_y, self.selected_type
            )
        elif self.selected_category == "structures":
            self.valid_placement = self.grid.is_valid_door_placement(grid_x, grid_y)
        else:
            self.valid_placement = self.grid.is_valid_tile_placement(grid_x, grid_y)

        return self.valid_placement

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
