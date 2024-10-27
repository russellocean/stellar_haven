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

    def update(self, ship=None, input_manager=None):
        if ship is None or input_manager is None:
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
        self._update_position(ship)

    def _update_position(self, ship):
        # Move the actual position and handle collisions
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Collision with ship boundaries
        if not ship.rect.contains(self.rect):
            if self.rect.left < ship.rect.left:
                self.rect.left = ship.rect.left
            if self.rect.right > ship.rect.right:
                self.rect.right = ship.rect.right
            if self.rect.top < ship.rect.top:
                self.rect.top = ship.rect.top
                self.velocity_y = 0
            if self.rect.bottom > ship.rect.bottom:
                self.rect.bottom = ship.rect.bottom
                self.velocity_y = 0
                self.on_ground = True
        else:
            if self.rect.bottom < ship.rect.bottom:
                self.on_ground = False
