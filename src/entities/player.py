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
        self.gravity = 0.5
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

    def update(self, room_manager, input_manager):
        # Convert player position to grid coordinates
        grid_x = self.rect.centerx // room_manager.grid.cell_size
        grid_y = self.rect.centery // room_manager.grid.cell_size

        # Get current room using grid coordinates
        current_room_id = room_manager.grid.get_room_by_grid_position(grid_x, grid_y)

        if room_manager is None or input_manager is None:
            return

        # Handle horizontal movement
        self.velocity_x = 0
        if input_manager.is_action_pressed("move_left"):
            self.velocity_x = -self.speed
        if input_manager.is_action_pressed("move_right"):
            self.velocity_x = self.speed

        # Check if we're about to walk off a ledge
        if self.velocity_x != 0 and self.on_ground:
            # Get the position slightly ahead of where we're moving
            check_x = (
                self.rect.centerx
                + (self.velocity_x / abs(self.velocity_x)) * self.rect.width
            )
            check_y = self.rect.bottom + 1  # Check one pixel below feet

            grid_x, grid_y = room_manager.grid.world_to_grid(check_x, check_y)
            if (
                grid_x,
                grid_y,
            ) not in room_manager.grid.cells or room_manager.grid.cells[
                (grid_x, grid_y)
            ] != TileType.FLOOR:
                self.on_ground = False

        # Handle dropping through platforms
        if input_manager.is_action_pressed("move_down") and self.on_ground:
            grid_x, grid_y = room_manager.grid.world_to_grid(
                self.rect.centerx, self.rect.bottom
            )
            # Check if we're standing on a door
            if (grid_x, grid_y) in room_manager.grid.cells:
                if room_manager.grid.cells[(grid_x, grid_y)] == TileType.DOOR:
                    self.on_ground = False
                    self.velocity_y = 1  # Small downward velocity to start falling
                    # Move down slightly to clear the door collision
                    self.rect.y += 1

        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity

        # Handle jumping
        if input_manager.is_action_pressed("jump") and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

        # Update position and handle collisions
        self._update_position(room_manager, input_manager)

        # Check what room we're in
        current_room_id = room_manager.grid.get_room_by_grid_position(grid_x, grid_y)
        new_room = room_manager.rooms.get(current_room_id) if current_room_id else None

        # If we've entered a new room, emit the event
        if new_room != self.current_room:
            if new_room:
                self.event_system.emit(
                    GameEvent.ROOM_ENTERED, room=new_room, player=self
                )
            self.current_room = new_room

    def _update_position(self, room_manager, input_manager):
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
                # Only treat door as floor if we're moving down and not pressing down key
                if tile == TileType.DOOR and not input_manager.is_action_pressed(
                    "move_down"
                ):
                    self.rect.bottom = grid_y * room_manager.grid.cell_size
                    self.velocity_y = 0
                    self.on_ground = True
                elif tile == TileType.FLOOR or tile == TileType.WALL:
                    self.rect.bottom = grid_y * room_manager.grid.cell_size
                    self.velocity_y = 0
                    self.on_ground = True

        # Check for ceiling collision (only for walls, not doors)
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
                    # Doors should never block movement
                    if tile == TileType.DOOR:
                        continue
                    # Both walls and floors should block movement
                    if tile in (TileType.WALL, TileType.FLOOR):
                        return False
        return True
