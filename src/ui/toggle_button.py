from typing import Callable, Tuple

import pygame


class ToggleButton:
    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        text: str,
        action: Callable,
        image_path: str = None,
    ):
        self.rect = pygame.Rect(x, y, size, size)
        self.text = text
        self.action = action
        self.toggled = False
        self.hovered = False
        self.was_pressed = False  # Add this line to track button press state

        # Colors
        self.normal_color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.active_color = (200, 200, 200)
        self.text_color = (255, 255, 255)

        # Load and scale image
        self.image = None
        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (size - 10, size - 10))

        # Setup font
        self.font = pygame.font.Font(None, size // 3)  # Adjusted font size

    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool):
        self.hovered = self.rect.collidepoint(mouse_pos)

        # Toggle only on initial press, not while held
        if self.hovered and mouse_clicked and not self.was_pressed:
            self.toggled = not self.toggled
            self.action()
            self.was_pressed = True
        elif not mouse_clicked:
            self.was_pressed = False

        return False

    def draw(self, screen: pygame.Surface):
        # Draw button background
        color = (
            self.active_color
            if self.toggled
            else (self.hover_color if self.hovered else self.normal_color)
        )
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2)  # Border

        # Draw image if available
        if self.image:
            image_rect = self.image.get_rect(center=self.rect.center)
            screen.blit(self.image, image_rect)

        # Draw text below the button
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(
            midtop=(self.rect.centerx, self.rect.bottom + 5)
        )
        screen.blit(text_surface, text_rect)
