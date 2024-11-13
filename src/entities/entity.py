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

        # Add tooltip properties
        self.name = ""
        self.description = ""
        self.show_tooltip = False
        self.feedback_text = None
        self.feedback_timer = 0
        self.feedback_duration = 1.0  # seconds
        self.feedback_start_y = 0  # Starting Y position
        self.feedback_offset = 0  # Current floating offset
        self.feedback_alpha = 255  # For fade effect

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

    def show_feedback(self, text: str, color=(255, 255, 0)):
        """Show temporary feedback text above entity"""
        self.feedback_text = {"text": text, "color": color}
        self.feedback_timer = self.feedback_duration
        self.feedback_alpha = 255
        self.feedback_offset = 0
        self.feedback_start_y = -20  # Start above entity

    def update(self, dt: float):
        """Update entity state"""
        # Update feedback timer and effects
        if self.feedback_timer > 0:
            self.feedback_timer = max(0, self.feedback_timer - dt)

            # Calculate fade based on remaining time
            fade_start = self.feedback_duration * 0.5  # Start fading at 50% of duration
            if self.feedback_timer < fade_start:
                fade_progress = self.feedback_timer / fade_start
                self.feedback_alpha = int(255 * fade_progress)

            # Float upward
            self.feedback_offset -= 30 * dt  # Speed of floating

            if self.feedback_timer == 0:
                self.feedback_text = None

    def render_feedback(self, surface: pygame.Surface, screen_pos: tuple[int, int]):
        """Render feedback text if active with effects"""
        if self.feedback_text and self.feedback_timer > 0:
            font = pygame.font.Font(None, 24)

            # Create the text surface
            text = font.render(
                self.feedback_text["text"], True, self.feedback_text["color"]
            )

            # Create a surface with alpha
            alpha_surface = pygame.Surface(text.get_rect().size, pygame.SRCALPHA)

            # Blit text with current alpha
            alpha_surface.fill((255, 255, 255, 0))  # Clear with transparent
            alpha_surface.blit(text, (0, 0))
            alpha_surface.set_alpha(self.feedback_alpha)

            # Calculate position with floating effect
            y_pos = screen_pos[1] + self.feedback_start_y + self.feedback_offset
            x_pos = (
                screen_pos[0] + (self.rect.width - text.get_width()) // 2
            )  # Center horizontally

            # Draw text with shadow for better visibility
            shadow_pos = (x_pos + 1, y_pos + 1)
            shadow_surface = font.render(self.feedback_text["text"], True, (0, 0, 0))
            shadow_surface.set_alpha(
                self.feedback_alpha // 2
            )  # Shadow is more transparent
            surface.blit(shadow_surface, shadow_pos)

            # Draw main text
            surface.blit(alpha_surface, (x_pos, y_pos))
