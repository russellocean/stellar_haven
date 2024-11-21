from typing import Tuple

import pygame

from grid.tile_type import TileType
from systems.debug_system import DebugSystem


class CollisionSystem:
    def __init__(self, grid):
        self.grid = grid
        self.debug = DebugSystem()
        self.camera = None

    def check_movement(
        self, rect: pygame.Rect, velocity: pygame.Vector2, dropping: bool = False
    ) -> Tuple[bool, pygame.Vector2]:
        """
        Check if movement is valid and return (can_move, adjusted_position)
        """
        # Store original position
        original_pos = pygame.Vector2(rect.centerx, rect.bottom)
        new_pos = original_pos.copy()
        can_move = True

        # Handle horizontal movement first
        if velocity.x != 0:
            new_pos.x += velocity.x
            target_grid_x, _ = self.grid.world_to_grid(new_pos.x, rect.bottom - 2)

            # Check if we can move horizontally (check both feet and head level)
            feet_y = self.grid.world_to_grid(rect.centerx, rect.bottom - 1)[1]
            head_y = self.grid.world_to_grid(rect.centerx, rect.top + 1)[1]

            for check_y in [feet_y, head_y]:
                if not self._check_horizontal(target_grid_x, check_y):
                    can_move = False
                    new_pos.x = original_pos.x
                    break

        # Handle vertical movement
        if velocity.y != 0:
            new_pos.y += velocity.y

            # Check ceiling collision when moving up
            if velocity.y < 0:
                _, head_grid_y = self.grid.world_to_grid(
                    rect.centerx, rect.top + velocity.y
                )
                if not self._check_vertical(
                    self.grid.world_to_grid(rect.centerx, rect.top)[0],
                    head_grid_y,
                    moving_down=False,
                    dropping=False,
                ):
                    can_move = False
                    # Align to grid cell bottom when hitting ceiling
                    new_pos.y = (head_grid_y + 1) * self.grid.cell_size + rect.height

            # Check floor collision when moving down
            else:
                _, target_grid_y = self.grid.world_to_grid(rect.centerx, new_pos.y)
                if not self._check_vertical(
                    self.grid.world_to_grid(rect.centerx, rect.bottom)[0],
                    target_grid_y,
                    moving_down=True,
                    dropping=dropping,
                ):
                    can_move = False
                    # Align to grid cell top when hitting floor
                    new_pos.y = target_grid_y * self.grid.cell_size

        # If position hasn't changed at all, we definitely can't move
        if new_pos == original_pos:
            can_move = False

        return can_move, new_pos

    def _check_horizontal(self, grid_x: int, grid_y: int) -> bool:
        """Check if horizontal movement is valid at a specific grid position"""
        tile = self.grid.get_tile(grid_x, grid_y)
        return tile is None or (tile.is_walkable and not tile.blocks_movement)

    def _check_vertical(
        self, grid_x: int, target_y: int, moving_down: bool, dropping: bool
    ) -> bool:
        """Check if vertical movement is valid"""
        tile = self.grid.get_tile(grid_x, target_y)

        if tile is None or tile.is_walkable:
            if tile == TileType.PLATFORM:
                if moving_down and not dropping:
                    return False
            return True

        return not tile.blocks_movement

    def set_camera(self, camera):
        """Set camera reference for debug visualization"""
        self.camera = camera
