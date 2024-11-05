import pygame

from entities.entity import Entity
from grid.tile_type import TileType
from systems.debug_system import DebugSystem
from systems.event_system import EventSystem, GameEvent


class Player(Entity):
    # Physics constants
    GRAVITY = 0.5
    JUMP_POWER = -15
    DEFAULT_SPEED = 5

    def __init__(self, x, y):
        super().__init__("assets/images/player.png", x, y)
        self.speed = self.DEFAULT_SPEED
        self.velocity = pygame.Vector2(0, 0)  # Use Vector2 for cleaner physics
        self.is_jumping = False
        self.on_ground = False
        self.event_system = EventSystem()
        self.current_room = None

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

        self._handle_movement(input_manager)
        self._handle_platform_drop(input_manager, room_manager)
        self._apply_physics()
        self._update_position(room_manager, input_manager)
        self._check_room_change(room_manager)

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

        grid_x, grid_y = room_manager.grid.world_to_grid(
            self.rect.centerx, self.rect.bottom
        )

        if (grid_x, grid_y) in room_manager.grid.cells:
            tile = room_manager.grid.cells[(grid_x, grid_y)]
            if tile.is_walkable and not tile.blocks_movement:
                self.on_ground = False
                self.velocity.y = 1
                self.rect.y += 1

    def _apply_physics(self):
        """Apply gravity and other physics"""
        if not self.on_ground:
            self.velocity.y += self.GRAVITY

    def _check_room_change(self, room_manager):
        """Check and handle room transitions"""
        grid_x = self.rect.centerx // room_manager.grid.cell_size
        grid_y = self.rect.centery // room_manager.grid.cell_size

        current_room_id = room_manager.grid.get_room_by_grid_position(grid_x, grid_y)
        new_room = room_manager.rooms.get(current_room_id) if current_room_id else None

        if new_room != self.current_room:
            if new_room:
                self.event_system.emit(
                    GameEvent.ROOM_ENTERED, room=new_room, player=self
                )
            self.current_room = new_room

    def _update_position(self, room_manager, input_manager):
        """Update player position with collision detection"""
        previous_pos = self.rect.topleft

        # Move horizontally
        self.rect.x += self.velocity.x
        if not room_manager.collision_system.is_position_valid(self.rect):
            self.rect.topleft = previous_pos

        # Move vertically
        self.rect.y += self.velocity.y
        self._handle_vertical_collision(room_manager, input_manager, previous_pos)

    def _handle_vertical_collision(self, room_manager, input_manager, previous_pos):
        """Handle vertical movement collisions"""
        grid_x, grid_y = room_manager.grid.world_to_grid(
            self.rect.centerx, self.rect.bottom
        )

        if (grid_x, grid_y) in room_manager.grid.cells:
            tile = room_manager.grid.cells[(grid_x, grid_y)]

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
