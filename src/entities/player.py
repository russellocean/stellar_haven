from entities.entity import Entity
from grid.tile_type import TileType
from systems.debug_system import DebugSystem
from systems.event_system import EventSystem, GameEvent


class Player(Entity):
    def __init__(self, x, y):
        super().__init__("assets/images/player.png", x, y)
        self.speed = 5
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_power = -15
        self.is_jumping = False
        self.on_ground = False
        self.event_system = EventSystem()
        self.current_room = None
        self.debug = DebugSystem()
        self.debug.add_watch("Player Speed", lambda: self.speed)
        self.debug.add_watch(
            "Current Room",
            lambda: self.current_room.name if self.current_room else "None",
        )

    def update(self, room_manager=None, input_manager=None):
        if room_manager is None or input_manager is None:
            return

        # Handle horizontal movement
        self.velocity_x = 0
        if input_manager.is_action_pressed("move_left"):
            self.velocity_x = -self.speed
        if input_manager.is_action_pressed("move_right"):
            self.velocity_x = self.speed

        # Handle dropping through platforms
        if input_manager.is_action_pressed("move_down") and self.on_ground:
            grid_x, grid_y = room_manager.grid.world_to_grid(
                self.rect.centerx, self.rect.bottom
            )
            # Check for floor below
            next_y = grid_y + 1
            while next_y < grid_y + 5:  # Check up to 5 tiles down
                if (grid_x, next_y) in room_manager.grid.cells:
                    if room_manager.grid.cells[(grid_x, next_y)] == TileType.FLOOR:
                        self.on_ground = False
                        self.velocity_y = 1
                        break
                next_y += 1

        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity

        # Handle jumping
        if input_manager.is_action_pressed("jump") and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

        # Update position and handle collisions
        self._update_position(room_manager)

        # Check what room we're in
        current_room_id = room_manager.grid.get_room_by_position(
            self.rect.centerx, self.rect.centery
        )
        new_room = room_manager.rooms.get(current_room_id) if current_room_id else None

        # If we've entered a new room, emit the event
        if new_room != self.current_room:
            if new_room:
                self.event_system.emit(
                    GameEvent.ROOM_ENTERED, room=new_room, player=self
                )
            self.current_room = new_room

    def _update_position(self, room_manager):
        """Update player position with collision detection"""
        previous_x = self.rect.x
        previous_y = self.rect.y

        # Move horizontally
        self.rect.x += self.velocity_x
        if not self._is_position_valid(room_manager.grid):
            self.rect.x = previous_x

        # Move vertically
        self.rect.y += self.velocity_y

        # Check for floor collision when moving down
        if self.velocity_y >= 0:
            grid_x, grid_y = room_manager.grid.world_to_grid(
                self.rect.centerx, self.rect.bottom
            )
            if (grid_x, grid_y) in room_manager.grid.cells:
                tile = room_manager.grid.cells[(grid_x, grid_y)]
                if tile == TileType.FLOOR or tile == TileType.WALL:
                    self.rect.bottom = grid_y * room_manager.grid.cell_size
                    self.velocity_y = 0
                    self.on_ground = True

        # Check for ceiling collision
        if not self._is_position_valid(room_manager.grid):
            self.rect.y = previous_y
            if self.velocity_y < 0:  # Hit ceiling
                self.velocity_y = 0

    def _is_position_valid(self, grid):
        """Check if current position is valid (not inside walls)"""
        # Get grid coordinates for player bounds
        left, top = grid.world_to_grid(self.rect.left, self.rect.top)
        right, bottom = grid.world_to_grid(self.rect.right - 1, self.rect.bottom - 1)

        # Check each tile the player occupies
        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                if (x, y) in grid.cells:
                    tile = grid.cells[(x, y)]
                    if tile == TileType.WALL:
                        return False
        return True
