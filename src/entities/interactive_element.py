import pygame

from entities.entity import Entity


class InteractiveElement(Entity):
    def __init__(self, x, y, element_type):
        super().__init__(f"assets/images/{element_type}.png", x, y)
        self.element_type = element_type
        self.is_interactable = True
        self.interaction_radius = 50

    def can_interact(self, player):
        return (
            self.is_interactable
            and pygame.math.Vector2(self.rect.center).distance_to(
                pygame.math.Vector2(player.rect.center)
            )
            < self.interaction_radius
        )

    def interact(self):
        print(f"Interacting with {self.element_type}")
        # Add specific interaction logic here
