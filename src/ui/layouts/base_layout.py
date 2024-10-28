import pygame

from systems.ui_system import UISystem


class BaseLayout:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.ui_system = UISystem()
        self.visible = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        return self.ui_system.handle_event(event)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        self._draw_background(surface)
        self.ui_system.draw(surface)

    def _draw_background(self, surface: pygame.Surface):
        """Override this for layout-specific background"""
        pass
