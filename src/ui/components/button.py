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
    ):
        super().__init__(rect, text, image_path, font_size)
        self.action = action

        # Add pressed color to the base colors
        self.colors["pressed"] = (80, 80, 80)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle click events"""
        # Handle hover from parent
        super().handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_pressed = True
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.is_pressed
            self.is_pressed = False
            if self.is_hovered and was_pressed:
                self.action()
                return True

        return False

    def _get_current_color(self) -> tuple:
        """Override to add pressed state"""
        if self.is_pressed and self.is_hovered:
            return self.colors["pressed"]
        return super()._get_current_color()
