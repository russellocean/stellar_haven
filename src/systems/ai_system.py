import math
import random
from typing import List, Optional, Tuple

import pygame

from entities.room import Room
from systems.debug_system import DebugSystem


class AICharacter:
    def __init__(self, x: int, y: int):
        # Similar physics constants to Player
        self.GRAVITY = 0.5
        self.JUMP_POWER = -13
        self.DEFAULT_SPEED = 2
        self.EXPLORE_SPEED = 1

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
        self.WAIT_DURATION = 1.0
        self.EXPLORE_DURATION = 5.0
        self.explore_timer = 0.0
        self.is_exploring = False
        self.explore_target = None
        self.stuck_timer = 0

        # Debug
        self.debug = DebugSystem()
        self.debug.add_watch("AI Position", lambda: self.rect.topleft)
        self.debug.add_watch("AI Target", lambda: self.target_position)
        self.debug.add_watch(
            "AI Current Room",
            lambda: self.current_room.name if self.current_room else "None",
        )

        # Add visited rooms tracking
        self.visited_rooms = set()
        self.last_visited_room = None


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

        # Handle exploration mode
        if character.is_exploring:
            character.explore_timer -= delta_time
            print(f"Exploring... Time left: {character.explore_timer:.2f}")

            # If we don't have an exploration target, set one
            if not character.target_position:
                self._set_new_explore_target(character)

            # If exploration time is up
            if character.explore_timer <= 0:
                print("\n=== Exploration Complete ===")
                character.is_exploring = False
                character.target_position = None
                character.speed = character.DEFAULT_SPEED
                character.wait_timer = (
                    character.WAIT_DURATION
                )  # Wait before moving to next room
                return

        # If no target at all, get next room
        if not character.target_position:
            print("No target position, finding next room...")
            next_room = self._get_next_room(character)
            if next_room:
                target_x, target_y = self.room_manager.get_room_center(next_room)
                print(
                    f"Setting new target: ({target_x}, {target_y}) in room {next_room.room_id}"
                )
                character.target_position = (target_x, target_y)
                character.is_exploring = False

        # Move towards target
        if character.target_position:
            self._move_towards_target(character)

    def _get_next_room(self, character: AICharacter) -> Optional[Room]:
        """Get the next room to visit"""
        print("\n--- Room Selection ---")
        if character.current_room is None:
            print("No current room set!")
            return None

        # Add current room to visited rooms
        character.visited_rooms.add(character.current_room.room_id)

        # Get all available rooms
        available_rooms = list(self.room_manager.rooms.values())
        print(f"Total available rooms: {len(available_rooms)}")
        print(f"Available room IDs: {[room.room_id for room in available_rooms]}")
        print(f"Current room ID: {character.current_room.room_id}")
        print(f"Visited rooms: {character.visited_rooms}")

        # First, try to find unvisited adjacent rooms
        adjacent_rooms = [
            room
            for room in available_rooms
            if room.room_id != character.current_room.room_id
            and self._are_rooms_adjacent(character.current_room, room)
            and room.room_id not in character.visited_rooms
        ]

        if adjacent_rooms:
            next_room = random.choice(adjacent_rooms)
            print(f"Selected random unvisited adjacent room: {next_room.room_id}")
            return next_room

        # Then, try any unvisited room
        unvisited_rooms = [
            room
            for room in available_rooms
            if room.room_id not in character.visited_rooms
            and room.room_id != character.current_room.room_id
        ]

        if unvisited_rooms:
            next_room = random.choice(unvisited_rooms)
            print(f"Selected random unvisited room: {next_room.room_id}")
            return next_room

        # If all rooms have been visited, reset visited rooms (except current)
        print("All rooms visited, resetting visited rooms list")
        current_room_id = character.current_room.room_id
        character.visited_rooms = {current_room_id}

        # Select any room that's not the current room
        other_rooms = [
            room
            for room in available_rooms
            if room.room_id != character.current_room.room_id
        ]

        if other_rooms:
            next_room = random.choice(other_rooms)
            print(f"Selected random room for new cycle: {next_room.room_id}")
            return next_room

        print("No other rooms available")
        return None

    def _are_rooms_adjacent(self, room1: Room, room2: Room) -> bool:
        """Check if two rooms are adjacent"""
        # Get room grid positions
        pos1 = room1.grid_pos
        pos2 = room2.grid_pos

        # Calculate Manhattan distance between rooms
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])

        # Rooms are adjacent if they're next to each other (including diagonally)
        return dx <= 1 and dy <= 1

    def _update_room_location(self, character: AICharacter):
        """Update the current room of the character"""
        grid_x = character.rect.centerx // self.room_manager.grid.cell_size
        grid_y = character.rect.centery // self.room_manager.grid.cell_size

        room_id = self.room_manager.grid.get_room_by_grid_position(grid_x, grid_y)
        new_room = self.room_manager.rooms.get(room_id) if room_id else None

        # Only print when room changes or when there's no current room
        if character.current_room is None or (
            new_room
            and character.current_room
            and new_room.room_id != character.current_room.room_id
        ):
            print("\n=== Room Change Detected ===")
            print(f"Grid position: ({grid_x}, {grid_y})")
            print(
                f"Previous room: {character.current_room.room_id if character.current_room else 'None'}"
            )
            print(f"New room: {new_room.room_id if new_room else 'None'}")
            print(f"Target position: {character.target_position}")

        # Handle initial room assignment
        if character.current_room is None and new_room is not None:
            print(f"Setting initial room: {new_room.room_id}")
            character.current_room = new_room
            return

        # Handle room transitions - only if we've fully entered the new room
        if (
            new_room
            and character.current_room
            and new_room.room_id != character.current_room.room_id
        ):
            # Get the center of both rooms
            current_center = self.room_manager.get_room_center(character.current_room)
            new_center = self.room_manager.get_room_center(new_room)

            # Calculate which direction we're moving
            moving_right = new_center[0] > current_center[0]
            moving_left = new_center[0] < current_center[0]

            # Only transition if we've crossed far enough into the new room
            transition_threshold = (
                self.room_manager.grid.cell_size * 2
            )  # Adjust this value as needed

            if (
                moving_right
                and character.rect.left > new_center[0] - transition_threshold
            ) or (
                moving_left
                and character.rect.right < new_center[0] + transition_threshold
            ):
                print("\n=== Room Transition Complete ===")
                print(f"From {character.current_room.room_id} to {new_room.room_id}")
                character.current_room = new_room
                character.wait_timer = character.WAIT_DURATION
                character.target_position = None

    def _move_towards_target(self, character: AICharacter):
        """Move character towards current target"""
        if not character.target_position:
            return

        target_x, target_y = character.target_position

        # Calculate distances
        dx = target_x - character.rect.centerx
        dy = target_y - character.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)

        print(f"\nDistance to target: {distance:.2f}")
        print(f"Current pos: ({character.rect.centerx}, {character.rect.centery})")
        print(f"Target: ({target_x}, {target_y})")
        print(f"Height difference: {dy}")

        # Update stuck detection
        if (
            abs(character.velocity.x) < 0.1
            and abs(character.velocity.y) < 0.1
            and distance > 20
        ):
            if not hasattr(character, "stuck_timer"):
                character.stuck_timer = 0
            character.stuck_timer += 1
            print(f"Potentially stuck! Timer: {character.stuck_timer}")
        else:
            character.stuck_timer = 0

        # If we're close enough to target
        if distance < 10:
            if character.is_exploring:
                print("Reached exploration target, setting new one")
                self._set_new_explore_target(character)
            else:
                print("\n=== Room Center Reached ===")
                character.is_exploring = True
                character.explore_timer = character.EXPLORE_DURATION
                character.speed = character.EXPLORE_SPEED
                self._set_new_explore_target(character)
            return

        # Handle jumping first if we need to go up
        if character.on_ground:
            should_jump = False

            # Jump if target is significantly above us
            if dy < -30:  # Target is above
                print("Target is above us, checking if we should jump...")
                if self._is_path_blocked(character, target_x):
                    print("Path is blocked, need to jump!")
                    should_jump = True
                elif character.stuck_timer > 30:  # If stuck for half a second
                    print("We're stuck and need to go up, jumping!")
                    should_jump = True

            if should_jump:
                print("Initiating jump!")
                character.velocity.y = character.JUMP_POWER
                character.on_ground = False
                character.stuck_timer = 0  # Reset stuck timer after jumping
                return  # Skip horizontal movement this frame

        # Horizontal movement
        current_speed = (
            character.EXPLORE_SPEED
            if character.is_exploring
            else character.DEFAULT_SPEED
        )

        # Set velocity based on direction
        if abs(dx) > 5:
            character.velocity.x = current_speed if dx > 0 else -current_speed
        else:
            character.velocity.x = 0

        # Apply gravity if not on ground
        if not character.on_ground:
            character.velocity.y += character.GRAVITY

        print(f"Current velocity: ({character.velocity.x}, {character.velocity.y})")
        print(f"On ground: {character.on_ground}")
        print(f"Stuck timer: {character.stuck_timer}")

        # Update position with collision detection
        self._update_position(character)

    def _set_new_explore_target(self, character: AICharacter):
        """Set a new random exploration target within the current room"""
        if not character.current_room:
            return

        # Get room boundaries
        room_center_x, room_center_y = self.room_manager.get_room_center(
            character.current_room
        )
        room_width = self.room_manager.grid.cell_size * 4

        # Set random target within room bounds
        margin = self.room_manager.grid.cell_size
        min_x = int(room_center_x - room_width / 3 + margin)
        max_x = int(room_center_x + room_width / 3 - margin)

        # Make sure new target is different from current position
        current_x = character.rect.centerx
        target_x = current_x
        while abs(target_x - current_x) < self.room_manager.grid.cell_size:
            target_x = random.randint(min_x, max_x)

        target_y = room_center_y  # Stay at same height

        print("\n=== New Exploration Target ===")
        print(f"Current pos: ({character.rect.centerx}, {character.rect.centery})")
        print(f"New target: ({target_x}, {target_y})")

        character.target_position = (target_x, target_y)

    def _update_position(self, character: AICharacter):
        """Update character position with collision detection"""
        # Create velocity vector
        velocity = pygame.Vector2(character.velocity.x, character.velocity.y)

        # Check movement with collision system
        can_move, new_pos = self.collision_system.check_movement(
            character.rect, velocity, dropping=False
        )

        # Store previous position
        previous_pos = pygame.Vector2(character.rect.centerx, character.rect.bottom)

        if can_move:
            character.rect.centerx = new_pos.x
            character.rect.bottom = new_pos.y
        else:
            # If we hit a wall, stop horizontal movement
            if abs(velocity.x) > 0:
                character.rect.centerx = previous_pos.x
                character.velocity.x = 0

            # If we hit ground/ceiling, stop vertical movement
            if velocity.y != 0:
                character.rect.bottom = new_pos.y
                character.velocity.y = 0
                if velocity.y > 0:
                    character.on_ground = True

        # Always check ground state after movement
        self._check_ground_state(character)

        # Debug output
        if (
            character.rect.centerx == previous_pos.x
            and character.rect.bottom == previous_pos.y
        ):
            print("WARNING: Position didn't change despite velocity!")
            # Reset velocities if we're not actually moving
            character.velocity.x = 0
            character.velocity.y = 0

    def _check_ground_state(self, character: AICharacter):
        """Check if character is actually on ground"""
        if character.velocity.y < 0:  # If moving up, we're not on ground
            character.on_ground = False
            return

        # Check the tile directly below the character
        grid_x, grid_y = self.room_manager.grid.world_to_grid(
            character.rect.centerx, character.rect.bottom + 1
        )
        tile = self.room_manager.grid.get_tile(grid_x, grid_y)

        # We're on ground if there's a solid tile below us
        if tile and tile.blocks_movement:
            character.on_ground = True
        else:
            character.on_ground = False

    def _is_path_blocked(self, character: AICharacter, target_x: int) -> bool:
        """Check if there's an obstacle in the path"""
        check_x = character.rect.centerx
        step = 1 if target_x > check_x else -1

        # Check horizontal path
        while abs(check_x - character.rect.centerx) < abs(
            character.rect.centerx - target_x
        ):
            check_x += step

            # Check at character's height and slightly above
            for check_y in [
                character.rect.centery,
                character.rect.centery - character.rect.height,
            ]:
                grid_x, grid_y = self.room_manager.grid.world_to_grid(check_x, check_y)
                tile = self.room_manager.grid.get_tile(grid_x, grid_y)
                if tile and tile.blocks_movement:
                    print(f"Path blocked at ({grid_x}, {grid_y})")
                    return True

        return False

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
