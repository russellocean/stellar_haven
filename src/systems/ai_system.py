import random
from typing import List

import pygame

from grid.tile_type import TileType


class AICharacter:
    def __init__(self, x: int, y: int, room_bounds):
        # Physics constants
        self.GRAVITY = 0.5
        self.WALK_SPEED = 1  # Very slow, casual walking speed

        # Initialize position and movement
        self.rect = pygame.Rect(x, y, 20, 30)
        self.velocity = pygame.Vector2(0, 0)
        self.room_bounds = room_bounds
        self.on_ground = False
        self.facing_right = True

        # State management
        self.state = "idle"
        self.state_timer = 0
        self.IDLE_TIME = random.uniform(2.0, 4.0)  # Random idle duration
        self.WALK_TIME = random.uniform(1.5, 3.0)  # Random walk duration


class AISystem:
    def __init__(self, room_manager, collision_system):
        self.room_manager = room_manager
        self.collision_system = collision_system
        self.characters: List[AICharacter] = []
        self.camera = None

        # Spawn one AI in each room
        for room_id, room in room_manager.rooms.items():
            # Get room data from grid
            room_data = room_manager.grid.rooms[room_id]
            grid_pos = room_data["grid_pos"]
            grid_size = room_data["grid_size"]

            # Calculate room boundaries in world coordinates
            left = grid_pos[0] * room_manager.grid.cell_size
            right = (grid_pos[0] + grid_size[0]) * room_manager.grid.cell_size

            # Add margin to keep AI away from walls
            margin = room_manager.grid.cell_size * 1.5
            room_bounds = {"left": left + margin, "right": right - margin}

            # Spawn at room center
            center_x, center_y = room_manager.get_room_center(room)
            self.spawn_character(center_x, center_y, room_bounds)

    def set_camera(self, camera):
        self.camera = camera

    def spawn_character(self, x: int, y: int, room_bounds):
        character = AICharacter(x, y, room_bounds)
        self.characters.append(character)
        return character

    def update(self, delta_time: float):
        for character in self.characters:
            # Update state timer and handle state changes
            character.state_timer -= delta_time
            if character.state_timer <= 0:
                if character.state == "idle":
                    # Start walking in a random direction
                    character.state = "walking"
                    character.state_timer = character.WALK_TIME
                    character.facing_right = random.choice([True, False])
                    character.velocity.x = (
                        character.WALK_SPEED
                        if character.facing_right
                        else -character.WALK_SPEED
                    )
                else:
                    # Return to idle
                    character.state = "idle"
                    character.state_timer = character.IDLE_TIME
                    character.velocity.x = 0

            # Apply gravity if not on ground
            if not character.on_ground:
                character.velocity.y += character.GRAVITY

            # Check room bounds
            if character.rect.centerx >= character.room_bounds["right"]:
                character.rect.centerx = character.room_bounds["right"]
                character.facing_right = False
                character.velocity.x = (
                    -character.WALK_SPEED if character.state == "walking" else 0
                )
            elif character.rect.centerx <= character.room_bounds["left"]:
                character.rect.centerx = character.room_bounds["left"]
                character.facing_right = True
                character.velocity.x = (
                    character.WALK_SPEED if character.state == "walking" else 0
                )

            # Update position with collision detection
            can_move, new_pos = self.collision_system.check_movement(
                character.rect, character.velocity, dropping=False
            )

            if can_move:
                character.rect.centerx = new_pos.x
                character.rect.bottom = new_pos.y
            else:
                # If we hit something while moving horizontally
                if abs(character.velocity.x) > 0:
                    character.facing_right = not character.facing_right
                    character.velocity.x = (
                        character.WALK_SPEED
                        if character.facing_right
                        else -character.WALK_SPEED
                    )
                # If we hit something while falling
                if character.velocity.y > 0:
                    character.velocity.y = 0
                    character.on_ground = True

            # Check ground state
            self._check_ground_state(character)

    def _check_ground_state(self, character: AICharacter):
        """Check if character is actually on ground"""
        if character.velocity.y < 0:
            character.on_ground = False
            return

        grid_x, grid_y = self.room_manager.grid.world_to_grid(
            character.rect.centerx, character.rect.bottom + 1
        )
        tile = self.room_manager.grid.get_tile(grid_x, grid_y)

        if tile and (tile.blocks_movement or tile == TileType.PLATFORM):
            character.on_ground = True
        else:
            character.on_ground = False

    def draw(self, screen: pygame.Surface):
        if not self.camera:
            return

        debug_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        for character in self.characters:
            screen_rect = self.camera.apply(character.rect)
            # Draw character body in red with black outline
            pygame.draw.rect(debug_surface, (255, 0, 0), screen_rect)
            pygame.draw.rect(debug_surface, (0, 0, 0), screen_rect, 2)

        screen.blit(debug_surface, (0, 0))
