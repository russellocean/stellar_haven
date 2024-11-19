import math
from typing import List, Optional, Tuple

import pygame

from entities.room import Room
from systems.debug_system import DebugSystem


class AICharacter:
    def __init__(self, x: int, y: int):
        # Similar physics constants to Player
        self.GRAVITY = 0.5
        self.JUMP_POWER = -12
        self.DEFAULT_SPEED = 4

        # Initialize position and movement
        self.rect = pygame.Rect(x, y, 20, 30)  # Same size as player
        self.velocity = pygame.Vector2(0, 0)
        self.speed = self.DEFAULT_SPEED
        self.on_ground = False
        self.current_room = None

        # Pathfinding variables
        self.current_path: List[Tuple[int, int]] = []
        self.target_position: Optional[Tuple[int, int]] = None
        self.wait_timer = 0.0
        self.WAIT_DURATION = 2.0  # 2 seconds instead of 2000 milliseconds

        # Debug
        self.debug = DebugSystem()
        self.debug.add_watch("AI Position", lambda: self.rect.topleft)
        self.debug.add_watch("AI Target", lambda: self.target_position)
        self.debug.add_watch(
            "AI Current Room",
            lambda: self.current_room.name if self.current_room else "None",
        )


class AISystem:
    def __init__(self, room_manager, collision_system):
        self.room_manager = room_manager
        self.collision_system = collision_system
        self.characters: List[AICharacter] = []
        self.debug = DebugSystem()
        self.camera = None

        # Get starting position and create initial AI character
        start_pos = room_manager.get_starting_position()
        self.spawn_character(*start_pos)

    def set_camera(self, camera):
        """Set camera for ai systems"""
        self.camera = camera

    def spawn_character(self, x: int, y: int):
        """Spawn a new AI character at the given position"""
        character = AICharacter(x, y)
        self.characters.append(character)
        return character

    def update(self, delta_time: float):
        """Update all AI characters"""
        for character in self.characters:
            self._update_character(character, delta_time)

    def _update_character(self, character: AICharacter, delta_time: float):
        """Update individual AI character"""
        print("\n--- AI Character Update ---")
        print(f"Delta time: {delta_time}")

        # Update room location
        self._update_room_location(character)

        # Handle room transitions and waiting
        if character.wait_timer > 0:
            print(f"Waiting... Timer: {character.wait_timer:.2f} seconds")
            character.wait_timer -= delta_time
            if character.wait_timer <= 0:
                print("Wait timer finished!")
                character.wait_timer = 0
            return

        # If no target, get next room
        if not character.target_position:
            print("No target position, finding next room...")
            next_room = self._get_next_room(character)
            if next_room:
                target_x, target_y = self.room_manager.get_room_center(next_room)
                print(
                    f"Setting new target: ({target_x}, {target_y}) in room {next_room.room_id}"
                )
                character.target_position = (target_x, target_y)
            else:
                print("No next room found!")
        else:
            print(f"Current target position: {character.target_position}")

        # Move towards target
        if character.target_position:
            self._move_towards_target(character)
            print(f"Current velocity: {character.velocity}")
            print(f"On ground: {character.on_ground}")

    def _get_next_room(self, character: AICharacter) -> Optional[Room]:
        """Get the next room to visit"""
        print("\n--- Room Selection ---")
        if character.current_room is None:
            print("No current room set!")
            return None

        # Get all available rooms
        available_rooms = list(self.room_manager.rooms.values())
        print(f"Total available rooms: {len(available_rooms)}")
        print(f"Available room IDs: {[room.room_id for room in available_rooms]}")
        print(f"Current room ID: {character.current_room.room_id}")

        # Filter out the current room
        other_rooms = [
            room
            for room in available_rooms
            if room.room_id != character.current_room.room_id
        ]
        print(f"Other rooms available: {[room.room_id for room in other_rooms]}")

        if other_rooms:
            next_room = other_rooms[0]
            print(f"Selected next room: {next_room.room_id}")
            return next_room

        print("No other rooms available")
        return None

    def _update_room_location(self, character: AICharacter):
        """Update the current room of the character"""
        grid_x = character.rect.centerx // self.room_manager.grid.cell_size
        grid_y = character.rect.centery // self.room_manager.grid.cell_size

        room_id = self.room_manager.grid.get_room_by_grid_position(grid_x, grid_y)
        new_room = self.room_manager.rooms.get(room_id) if room_id else None

        # Debug prints
        print("\nRoom Location Update:")
        print(f"Grid position: ({grid_x}, {grid_y})")
        print(f"Room ID from grid: {room_id}")
        print(f"Total rooms in manager: {len(self.room_manager.rooms)}")
        print(f"All room IDs: {list(self.room_manager.rooms.keys())}")

        # Handle initial room assignment
        if character.current_room is None and new_room is not None:
            print(f"Setting initial room: {new_room.room_id}")
            character.current_room = new_room
            # Don't set initial wait timer
            return

        # Handle room transitions
        if (
            new_room
            and character.current_room
            and new_room.room_id != character.current_room.room_id
        ):
            print(
                f"Room transition: {character.current_room.room_id} -> {new_room.room_id}"
            )
            character.current_room = new_room
            character.wait_timer = character.WAIT_DURATION
            character.target_position = None

    def _move_towards_target(self, character: AICharacter):
        """Move character towards current target"""
        if not character.target_position:
            return

        target_x, target_y = character.target_position

        print("\n--- Movement Update ---")
        print(f"Current position: ({character.rect.centerx}, {character.rect.centery})")
        print(f"Target position: ({target_x}, {target_y})")

        # Calculate distances
        dx = target_x - character.rect.centerx
        dy = target_y - character.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)

        print(f"Distance to target: {distance}")
        print(f"dx: {dx}, dy: {dy}")

        # If we're close enough to target, consider it reached
        if distance < 10:
            print("Target reached!")
            character.target_position = None
            character.wait_timer = character.WAIT_DURATION
            return

        # Horizontal movement
        if abs(dx) > 5:
            if dx > 0:
                character.velocity.x = character.speed
                print(f"Moving right with speed {character.speed}")
            else:
                character.velocity.x = -character.speed
                print(f"Moving left with speed {character.speed}")
        else:
            character.velocity.x = 0
            print("Stopped horizontal movement")

        # Apply gravity
        if not character.on_ground:
            character.velocity.y += character.GRAVITY
            print(f"Applying gravity: {character.velocity.y}")

        # Handle jumping
        if character.on_ground:
            if dy < -20:  # If target is significantly above us
                character.velocity.y = character.JUMP_POWER
                character.on_ground = False
                print("Jumping!")
            elif dy > 20:  # If target is below us
                print("Moving down")
                character.velocity.y += character.GRAVITY

        # Update position with collision detection
        self._update_position(character)

    def _update_position(self, character: AICharacter):
        """Update character position with collision detection"""
        print("\n--- Position Update ---")
        # Store previous position
        previous_pos = character.rect.topleft

        # Move horizontally
        character.rect.x += character.velocity.x
        if self.collision_system.is_position_valid(character.rect):
            print(f"Horizontal collision at {character.rect.topleft}")
            character.rect.topleft = previous_pos
            character.velocity.x = (
                -character.velocity.x
            )  # Reverse direction on collision

        # Move vertically
        character.rect.y += character.velocity.y
        if self.collision_system.is_position_valid(character.rect):
            print(f"Vertical collision at {character.rect.topleft}")
            character.rect.y = previous_pos[1]
            character.velocity.y = 0
            if character.velocity.y > 0:  # Was falling
                character.on_ground = True
                print("Landed on ground")
        elif not character.on_ground:
            character.velocity.y += character.GRAVITY

    def draw(self, screen: pygame.Surface):
        """Draw AI characters and debug information"""
        if not self.camera:
            return

        debug_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        for character in self.characters:
            # Convert world position to screen position
            screen_rect = self.camera.apply(character.rect)

            # Draw character body
            pygame.draw.rect(debug_surface, (255, 0, 0), screen_rect)
            # Draw outline
            pygame.draw.rect(debug_surface, (0, 0, 0), screen_rect, 2)

        screen.blit(debug_surface, (0, 0))
