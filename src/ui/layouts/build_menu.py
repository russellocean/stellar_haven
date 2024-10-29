from typing import Callable, Optional

import pygame

from systems.room_renderer import RoomRenderer
from ui.components.button import Button

from .base_layout import BaseLayout


class BuildMenu(BaseLayout):
    def __init__(self, screen: pygame.Surface, on_select: Optional[Callable] = None):
        super().__init__(screen)
        self.on_select = on_select
        self.visible = False
        self.room_renderer = RoomRenderer()
        self._create_buttons()

    def _create_buttons(self):
        """Create room selection buttons"""
        start_x = self.screen.get_width() - 220
        start_y = 20
        button_width = 200
        button_height = 60
        spacing = 10

        room_types = self.room_renderer.room_config.get("room_types", {})

        for i, (room_type, config) in enumerate(room_types.items()):
            y_pos = start_y + (button_height + spacing) * i
            rect = pygame.Rect(start_x, y_pos, button_width, button_height)

            display_name = config.get(
                "display_name", room_type.replace("_", " ").title()
            )

            button = Button(
                rect=rect,
                text=display_name,
                action=lambda rt=room_type: self.select_room(rt),
                image_path=f"assets/images/ui/room_icons/{room_type}.png",
            )
            self.ui_system.add_element(button)

    def select_room(self, room_type: str):
        """Handle room selection"""
        if self.on_select:
            self.on_select(room_type)

        # Update button states
        for element in self.ui_system.elements:
            if isinstance(element, Button):
                element.active = element.text == room_type

    def _draw_background(self, surface: pygame.Surface):
        """Draw menu background"""
        menu_rect = pygame.Rect(surface.get_width() - 240, 0, 240, surface.get_height())
        background = pygame.Surface((240, surface.get_height()))
        background.set_alpha(128)
        background.fill((50, 50, 50))
        surface.blit(background, menu_rect)
