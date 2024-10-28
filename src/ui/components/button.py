from typing import Callable, Optional

import pygame

from .ui_component import UIComponent


class Button(UIComponent):
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        action: Callable,
        image_path: Optional[str] = None,
        font_size: int = 24,
        tooltip: str = None,  # Add tooltip support
        disabled: bool = False,  # Add disabled state
    ):
        super().__init__(rect, text, image_path, font_size)
        self.action = action
        self.tooltip = tooltip
        self.disabled = disabled

        # Enhance colors
        self.colors.update(
            {
                "pressed": (80, 80, 80),
                "disabled": (60, 60, 60),
                "disabled_text": (120, 120, 120),
                "border_normal": (100, 100, 100),
                "border_hover": (200, 200, 200),
                "border_pressed": (150, 150, 150),
            }
        )

        # Animation properties
        self.pulse_amount = 0
        self.pulse_direction = 1
        self.is_pulsing = False

    def start_pulse(self):
        """Start a pulsing animation"""
        self.is_pulsing = True

    def stop_pulse(self):
        """Stop the pulsing animation"""
        self.is_pulsing = False
        self.pulse_amount = 0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle click events"""
        if self.disabled:
            return False

        # Handle hover from parent
        super().handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_pressed = True
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.is_pressed
            self.is_pressed = False
            if self.is_hovered and was_pressed and not self.disabled:
                self.action()
                return True

        return False

    def update(self):
        """Update button state"""
        super().update()

        # Update pulse animation
        if self.is_pulsing:
            self.pulse_amount += 0.1 * self.pulse_direction
            if self.pulse_amount >= 1.0:
                self.pulse_amount = 1.0
                self.pulse_direction = -1
            elif self.pulse_amount <= 0.0:
                self.pulse_amount = 0.0
                self.pulse_direction = 1

    def _get_current_color(self) -> tuple:
        """Get the current button color based on state"""
        if self.disabled:
            return self.colors["disabled"]
        if self.is_pressed and self.is_hovered:
            return self.colors["pressed"]
        return super()._get_current_color()

    def _get_current_text_color(self) -> tuple:
        """Get the current text color based on state"""
        if self.disabled:
            return self.colors["disabled_text"]
        return super()._get_text_color()

    def _get_border_color(self) -> tuple:
        """Get the current border color based on state"""
        if self.disabled:
            return self.colors["border_normal"]
        if self.is_pressed and self.is_hovered:
            return self.colors["border_pressed"]
        if self.is_hovered:
            return self.colors["border_hover"]
        return self.colors["border_normal"]

    def draw(self, surface: pygame.Surface):
        """Draw the button with enhanced visuals"""
        # Draw base button
        rect = self.rect.copy()
        if self.is_pulsing:
            # Adjust rect for pulse animation
            pulse_offset = int(self.pulse_amount * 4)
            rect.inflate_ip(pulse_offset, pulse_offset)

        # Draw button background
        pygame.draw.rect(surface, self._get_current_color(), rect)

        # Draw border
        pygame.draw.rect(surface, self._get_border_color(), rect, 2)

        # Draw text
        if self.text:
            text_surface = self.font.render(
                self.text, True, self._get_current_text_color()
            )
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)

        # Draw image if present
        if self.image:
            image_rect = self.image.get_rect(center=rect.center)
            surface.blit(self.image, image_rect)

        # Draw tooltip if hovered
        if self.tooltip and self.is_hovered:
            self._draw_tooltip(surface)

    def _draw_tooltip(self, surface: pygame.Surface):
        """Draw tooltip when hovered"""
        if not self.tooltip:
            return

        tooltip_surface = self.font.render(self.tooltip, True, (255, 255, 255))
        tooltip_rect = tooltip_surface.get_rect()
        padding = 5

        # Position tooltip above button
        tooltip_rect.midbottom = (self.rect.centerx, self.rect.top - 5)

        # Draw tooltip background
        bg_rect = tooltip_rect.inflate(padding * 2, padding * 2)
        pygame.draw.rect(surface, (40, 40, 40), bg_rect)
        pygame.draw.rect(surface, (100, 100, 100), bg_rect, 1)

        # Draw tooltip text
        surface.blit(tooltip_surface, tooltip_rect)
