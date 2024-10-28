from typing import Callable, Tuple

import pygame


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        action: Callable,
        image_path: str = None,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.active = False

        # Colors
        self.normal_color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.active_color = (200, 200, 200)
        self.text_color = (255, 255, 255)

        # Load image if provided
        self.image = None
        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (width - 10, height - 10))

        # Setup font
        self.font = pygame.font.Font(None, 24)

    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool):
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)

        # Only trigger action on initial click, not while held
        if self.hovered and mouse_clicked and not was_hovered:
            self.action()
            return True
        return False

    def draw(self, screen):
        # Draw button background
        color = (
            self.active_color
            if self.active
            else (self.hover_color if self.hovered else self.normal_color)
        )
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2)  # Border

        # Draw image if available
        if self.image:
            image_rect = self.image.get_rect(center=self.rect.center)
            screen.blit(self.image, image_rect)

        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
