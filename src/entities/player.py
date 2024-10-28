from entities.entity import Entity


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

    def update(self, room_manager=None, input_manager=None):
        if room_manager is None or input_manager is None:
            return

        # Handle horizontal movement
        self.velocity_x = 0
        if input_manager.is_action_pressed("move_left"):
            self.velocity_x = -self.speed
        if input_manager.is_action_pressed("move_right"):
            self.velocity_x = self.speed

        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity

        # Handle jumping
        if input_manager.is_action_pressed("jump") and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

        # Update position and handle collisions
        self._update_position(room_manager)

        # Get current room
        # current_room = room_manager.get_room_at_position(
        #     self.rect.centerx, self.rect.centery
        # )
        # if current_room:
        #     print(f"Player in {current_room.name}")

    def _update_position(self, room_manager):
        previous_x = self.rect.x
        previous_y = self.rect.y

        # Move horizontally
        self.rect.x += self.velocity_x
        if not room_manager.collision_system.is_position_valid(self.rect):
            self.rect.x = previous_x

        # Move vertically
        self.rect.y += self.velocity_y
        if not room_manager.collision_system.is_position_valid(self.rect):
            self.rect.y = previous_y
            if self.velocity_y > 0:  # Was moving down
                self.on_ground = True
            self.velocity_y = 0

        # # Debug output
        # print(f"Player pos: {self.rect.x}, {self.rect.y}")
        # print(f"Inside room: {inside_any_room}")
        # print(f"On ground: {self.on_ground}")
        # print(f"Velocity: {self.velocity_x}, {self.velocity_y}")
