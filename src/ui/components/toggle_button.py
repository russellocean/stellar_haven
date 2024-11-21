from typing import Callable, Optional, Tuple

import pygame

from .ui_component import UIComponent


class ToggleButton(UIComponent):
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
        self.is_toggled = False
        self.was_pressed = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle toggle events"""
        # Handle hover from parent
        super().handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and not self.was_pressed:
                self.was_pressed = True
                self.action()
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.was_pressed = False

        return False

    def set_toggled(self, is_toggled: bool):
        """Set the toggle state externally"""
        self.is_active = is_toggled

    def _get_current_color(self) -> Tuple[int, int, int]:
        """Override color selection to include toggle state"""
        if self.is_toggled:
            return self.colors["active"]
        return super()._get_current_color()
