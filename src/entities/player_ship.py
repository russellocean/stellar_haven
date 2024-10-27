from entities.entity import Entity


class PlayerShip(Entity):
    def __init__(self, x, y):
        super().__init__("assets/images/ship_interior.png", x, y)
