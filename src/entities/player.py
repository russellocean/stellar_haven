from entities.entity import Entity
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
            grid_x = self.rect.centerx // room_manager.collision_system.grid_size
            current_floor_y = (
                self.rect.bottom // room_manager.collision_system.grid_size
            )

            # Check if there's a room below us
            if grid_x in room_manager.collision_system.floor_map:
                for floor_y in sorted(room_manager.collision_system.floor_map[grid_x]):
                    if floor_y > current_floor_y:
                        # Found a floor below us, ignore current floor
                        room_manager.collision_system.ignore_floor(
                            grid_x, current_floor_y
                        )
                        self.on_ground = False
                        self.velocity_y = 1  # Small downward velocity to start falling
                        break

        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity

        # Handle jumping
        if input_manager.is_action_pressed("jump") and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

        # Update position and handle collisions
        self._update_position(room_manager)

        # Clear ignored floor after movement
        room_manager.collision_system.clear_ignored_floor()

        # Check what room we're in
        current_pos = (self.rect.centerx, self.rect.centery)
        new_room = room_manager.get_room_at_position(*current_pos)

        # If we've entered a new room, emit the event
        if new_room != self.current_room:
            if new_room:
                self.event_system.emit(
                    GameEvent.ROOM_ENTERED, room=new_room, player=self
                )
            self.current_room = new_room

    def _update_position(self, room_manager):
        previous_x = self.rect.x
        previous_y = self.rect.y

        # Move horizontally
        self.rect.x += self.velocity_x
        if not room_manager.collision_system.is_position_valid(self.rect):
            self.rect.x = previous_x

        # Move vertically
        self.rect.y += self.velocity_y

        # Check for all floor collisions in one pass
        if self.velocity_y >= 0:  # Moving down or stationary
            grid_x = self.rect.centerx // room_manager.collision_system.grid_size
            if grid_x in room_manager.collision_system.floor_map:
                for floor_y in sorted(room_manager.collision_system.floor_map[grid_x]):
                    floor_pixel_y = floor_y * room_manager.collision_system.grid_size

                    # Skip if this is the ignored floor
                    if room_manager.collision_system.ignored_floor == (grid_x, floor_y):
                        continue

                    # Check if we're on or crossing this floor
                    if abs(self.rect.bottom - floor_pixel_y) <= 1 or (
                        self.rect.bottom > floor_pixel_y
                        and previous_y + self.rect.height <= floor_pixel_y + 1
                    ):
                        self.rect.bottom = floor_pixel_y
                        self.velocity_y = 0
                        self.on_ground = True
                        break
                else:  # No floor found
                    self.on_ground = False
            else:
                self.on_ground = False

        # Check for ceiling/wall collision
        if not room_manager.collision_system.is_position_valid(self.rect):
            self.rect.y = previous_y
            if self.velocity_y < 0:  # Hit ceiling
                self.velocity_y = 0

        # Remove the automatic ground state change
        # if self.velocity_y > 0:
        #     self.on_ground = False

        # # Debug output
        # print(f"Player pos: {self.rect.x}, {self.rect.y}")
        # print(f"Inside room: {inside_any_room}")
        # print(f"On ground: {self.on_ground}")
        # print(f"Velocity: {self.velocity_x}, {self.velocity_y}")
