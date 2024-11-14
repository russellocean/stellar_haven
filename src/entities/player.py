import pygame

from entities.entity import Entity
from grid.tile_type import TileType
from systems.asset_manager import AssetManager
from systems.debug_system import DebugSystem
from systems.event_system import EventSystem, GameEvent


class Player(Entity):
    # Physics constants
    GRAVITY = 0.5
    JUMP_POWER = -13.5
    DEFAULT_SPEED = 5

    def __init__(self, x, y):
        # Initialize with first idle frame instead of static image
        super().__init__("assets/characters/no-helm/Idle/idle1.png", x, y)
        self.speed = self.DEFAULT_SPEED
        self.velocity = pygame.Vector2(0, 0)
        self.is_jumping = False
        self.on_ground = False
        self.event_system = EventSystem()
        self.current_room = None

        # Animation properties
        self.asset_manager = AssetManager()
        self.animation_frame = 0
        self.animation_timer = 0
        self.ANIMATION_SPEED = 0.1  # Seconds per frame
        self.facing_right = True
        self.last_update = pygame.time.get_ticks()

        # Load animations
        self.animations = {
            "idle": [
                self.asset_manager.get_image(f"characters/no-helm/Idle/idle{i}.png")
                for i in range(1, 5)
            ],
            "run": [
                self.asset_manager.get_image(f"characters/no-helm/run/run{i}.png")
                for i in range(1, 11)
            ],
            "jump": [
                self.asset_manager.get_image(
                    f"characters/no-helm/jump-no-gun/jump-no-gun{i}.png"
                )
                for i in range(1, 7)
            ],
        }
        self.current_animation = "idle"

        # Collision rect setup
        self.rect.width = 20  # Collision box size
        self.rect.height = 30

        # Sprite offset from collision rect
        self.sprite_offset_x = 0  # Adjust these values to center the sprite
        self.sprite_offset_y = 0  # Negative values move the sprite up/left

        # Center the collision rect on the sprite
        self.rect.centerx = x + self.image.get_width() // 2
        self.rect.bottom = y + self.image.get_height()

        self._setup_debug()

    def _setup_debug(self):
        """Initialize debug watches"""
        self.debug = DebugSystem()
        self.debug.add_watch("Player Speed", lambda: self.speed)
        self.debug.add_watch(
            "Current Room",
            lambda: self.current_room.name if self.current_room else "None",
        )
        self.debug.add_watch("Velocity", lambda: self.velocity)
        self.debug.add_watch("On Ground", lambda: self.on_ground)

    def update(self, room_manager, input_manager):
        if not room_manager or not input_manager:
            return

        self._check_ground_state(room_manager)
        self._handle_movement(input_manager)
        self._handle_platform_drop(input_manager, room_manager)
        self._apply_physics()
        self._update_position(room_manager, input_manager)
        self._check_room_change(room_manager)
        self._update_animation()

    def _handle_movement(self, input_manager):
        """Handle horizontal movement and jumping"""
        # Reset horizontal velocity
        self.velocity.x = 0

        # Handle left/right movement
        if input_manager.is_action_pressed("move_left"):
            self.velocity.x = -self.speed
        if input_manager.is_action_pressed("move_right"):
            self.velocity.x = self.speed

        # Handle jumping
        if input_manager.is_action_pressed("jump") and self.on_ground:
            self.velocity.y = self.JUMP_POWER
            self.on_ground = False

    def _handle_platform_drop(self, input_manager, room_manager):
        """Handle dropping through platforms"""
        if not (input_manager.is_action_pressed("move_down") and self.on_ground):
            return

        # Check multiple points along the bottom of the player's collision box
        left_x = self.rect.left
        right_x = self.rect.right - 1
        bottom_y = self.rect.bottom

        # Convert all check points to grid coordinates
        left_grid_x, grid_y = room_manager.grid.world_to_grid(left_x, bottom_y)
        right_grid_x, _ = room_manager.grid.world_to_grid(right_x, bottom_y)

        # Check if ALL points are safe to drop through
        can_drop = True
        for check_x in range(left_grid_x, right_grid_x + 1):
            if (check_x, grid_y) in room_manager.grid.cells:
                tile = room_manager.grid.get_tile(check_x, grid_y)
                # Only allow dropping if the tile is a platform
                if tile != TileType.PLATFORM:
                    can_drop = False
                    break

                # Check the tile below to make sure we're not dropping into a wall
                below_tile = room_manager.grid.get_tile(check_x, grid_y + 1)
                if below_tile and below_tile.blocks_movement:
                    can_drop = False
                    break

        if can_drop:
            self.on_ground = False
            self.velocity.y = 1  # Small initial downward velocity
            self.rect.y += 1  # Small position adjustment to clear the platform

    def _apply_physics(self):
        """Apply gravity and other physics"""
        if not self.on_ground:
            self.velocity.y += self.GRAVITY

    def _check_room_change(self, room_manager):
        """Check and handle room transitions"""
        # Get grid position of player's center
        grid_x = self.rect.centerx // room_manager.grid.cell_size
        grid_y = self.rect.centery // room_manager.grid.cell_size

        # Get room at current position
        current_room_id = room_manager.grid.get_room_by_grid_position(grid_x, grid_y)
        new_room = room_manager.rooms.get(current_room_id) if current_room_id else None

        # Only emit events if the room has actually changed
        if new_room != self.current_room:
            if self.current_room:
                self.event_system.emit(
                    GameEvent.ROOM_EXITED, room=self.current_room, player=self
                )
            if new_room:
                # Add debug output
                print(f"Entering room: {new_room.room_type}")
                self.event_system.emit(
                    GameEvent.ROOM_ENTERED, room=new_room, player=self
                )
            self.current_room = new_room

            # # Update debug watch
            # self.debug.watch(
            #     "Current Room",
            #     lambda: self.current_room.room_type if self.current_room else "None",
            # )

    def _update_position(self, room_manager, input_manager):
        """Update player position with collision detection"""
        previous_pos = self.rect.topleft

        # Move horizontally
        self.rect.x += self.velocity.x
        if room_manager.collision_system.is_position_valid(self.rect):
            self.rect.topleft = previous_pos

        # Move vertically with continuous collision detection
        if room_manager.collision_system.is_position_valid(self.rect, self.velocity):
            # Find the exact point of collision
            test_rect = self.rect.copy()
            step = 1 if self.velocity.y > 0 else -1

            while abs(test_rect.y - previous_pos[1]) < abs(self.velocity.y):
                test_rect.y += step
                if room_manager.collision_system.is_position_valid(test_rect):
                    test_rect.y -= step
                    break

            self.rect.y = test_rect.y
            self.velocity.y = 0
            if step > 0:  # Moving down
                self.on_ground = True
        else:
            self.rect.y += self.velocity.y

    def _handle_vertical_collision(self, room_manager, input_manager, previous_pos):
        """Handle vertical movement collisions"""
        grid_x, grid_y = room_manager.grid.world_to_grid(
            self.rect.centerx, self.rect.bottom
        )

        if (grid_x, grid_y) in room_manager.grid.cells:
            tile = room_manager.grid.get_tile(grid_x, grid_y)

            # Handle floor collision
            if self.velocity.y >= 0:
                if self._should_stop_on_tile(tile, input_manager):
                    self.rect.bottom = grid_y * room_manager.grid.cell_size
                    self.velocity.y = 0
                    self.on_ground = True

        # Handle ceiling collision
        if not room_manager.collision_system.is_position_valid(self.rect):
            self.rect.topleft = previous_pos
            if self.velocity.y < 0:
                self.velocity.y = 0

    def _should_stop_on_tile(self, tile: TileType, input_manager) -> bool:
        """Determine if player should stop on this tile type"""
        if tile == TileType.PLATFORM:
            return not input_manager.is_action_pressed("move_down")
        return tile.blocks_movement

    def _update_animation(self):
        """Update the animation frame based on player state"""
        # Calculate time since last update
        now = pygame.time.get_ticks()
        elapsed = (now - self.last_update) / 1000.0  # Convert to seconds
        self.animation_timer += elapsed
        self.last_update = now

        # Determine animation state
        if not self.on_ground:
            self.current_animation = "jump"
            # Set jump frame based on vertical velocity
            if self.velocity.y > 0:  # Rising
                # Use first 3 frames for rising animation
                if self.velocity.y < -8:
                    self.animation_frame = 0  # Initial jump
                elif self.velocity.y < -4:
                    self.animation_frame = 1  # Mid rise
                else:
                    self.animation_frame = 2  # Peak rise
            else:  # Falling
                self.animation_frame = 3  # Use frame 4 for falling
        elif self.velocity.y < 0:  # Just landed
            self.current_animation = "jump"
            # Use last two frames for landing animation
            if self.animation_timer < self.ANIMATION_SPEED:
                self.animation_frame = 4  # Initial landing
            else:
                self.animation_frame = 5  # Final landing
                if self.animation_timer >= self.ANIMATION_SPEED * 2:
                    self.animation_timer = 0  # Reset after landing
        elif abs(self.velocity.x) > 0:
            self.current_animation = "run"
            # Update frame if enough time has passed
            if self.animation_timer >= self.ANIMATION_SPEED:
                self.animation_frame = (self.animation_frame + 1) % len(
                    self.animations["run"]
                )
                self.animation_timer = 0  # Reset timer
        else:
            self.current_animation = "idle"
            # Update frame if enough time has passed
            if self.animation_timer >= self.ANIMATION_SPEED:
                self.animation_frame = (self.animation_frame + 1) % len(
                    self.animations["idle"]
                )
                self.animation_timer = 0  # Reset timer

        # Ensure animation frame is within bounds
        max_frames = len(self.animations[self.current_animation]) - 1
        self.animation_frame = min(self.animation_frame, max_frames)

        # Update facing direction and image
        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False

        # Update sprite image
        current_frame = self.animations[self.current_animation][self.animation_frame]
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        self.image = current_frame

        # Position the sprite relative to the collision rect
        self.image_rect = self.image.get_rect()
        self.image_rect.centerx = self.rect.centerx + self.sprite_offset_x
        self.image_rect.bottom = self.rect.bottom + self.sprite_offset_y

    def draw_debug(self, screen):
        """Draw debug visualization for player"""
        if not self.debug.enabled or not hasattr(self, "camera"):
            return

        # Create a debug surface
        debug_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        # Draw collision rect in red with partial transparency
        collision_color = (255, 0, 0, 100)  # Red with alpha

        # Convert world coordinates to screen coordinates
        screen_x, screen_y = self.camera.world_to_screen(self.rect.x, self.rect.y)
        debug_rect = pygame.Rect(screen_x, screen_y, self.rect.width, self.rect.height)

        # Draw the collision rectangle
        pygame.draw.rect(debug_surface, collision_color, debug_rect)

        # Draw the rect outline in solid red
        pygame.draw.rect(debug_surface, (255, 0, 0), debug_rect, 1)

        screen.blit(debug_surface, (0, 0))

    def _check_ground_state(self, room_manager):
        """Check if player is actually on ground"""
        if not self.on_ground:
            return

        # Check multiple points along the bottom of the player's collision box
        left_x = self.rect.left
        right_x = self.rect.right - 1
        bottom_y = self.rect.bottom + 1  # Check one pixel below

        # Convert all check points to grid coordinates
        left_grid_x, grid_y = room_manager.grid.world_to_grid(left_x, bottom_y)
        right_grid_x, _ = room_manager.grid.world_to_grid(right_x, bottom_y)

        # Check if ANY point has valid ground beneath
        has_ground = False
        for check_x in range(left_grid_x, right_grid_x + 1):
            if (check_x, grid_y) in room_manager.grid.cells:
                tile = room_manager.grid.get_tile(check_x, grid_y)
                if tile.blocks_movement or tile == TileType.PLATFORM:
                    has_ground = True
                    break

        # Only fall if there's no ground at all beneath us
        if not has_ground:
            self.on_ground = False
