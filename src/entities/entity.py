from typing import Callable, Optional

import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, image_path: Optional[str], x: int, y: int):
        super().__init__()
        self.image = (
            pygame.image.load(image_path).convert_alpha()
            if image_path
            else pygame.Surface((16, 16), pygame.SRCALPHA)
        )
        self.rect = self.image.get_rect(center=(x, y))

        self.is_interactable = False
        self.interaction_callback = None
        self.interaction_range = 32
        self.is_hovered = False

    def set_interactable(self, callback: Callable, interaction_range: int = 32):
        self.is_interactable = True
        self.interaction_callback = callback
        self.interaction_range = interaction_range

    def update_hover(self, mouse_pos: tuple[int, int]):
        if self.is_interactable:
            distance = (
                (mouse_pos[0] - self.rect.centerx) ** 2
                + (mouse_pos[1] - self.rect.centery) ** 2
            ) ** 0.5
            self.is_hovered = distance <= self.interaction_range

    def interact(self):
        if self.is_interactable and self.interaction_callback:
            self.interaction_callback()
