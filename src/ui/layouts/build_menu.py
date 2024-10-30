from typing import Callable, Optional

import pygame

from ui.components.button import Button

from .base_layout import BaseLayout


class BuildMenu(BaseLayout):
    def __init__(
        self, screen: pygame.Surface, room_manager, on_select: Optional[Callable] = None
    ):
        """Initialize build menu
        Args:
            screen: The game screen surface
            room_manager: Reference to the room manager
            on_select: Callback function when a room is selected
        """
        super().__init__(screen)
        self.room_manager = room_manager
        self.on_select = on_select
        self.visible = False
        self._create_buttons()

    def _create_buttons(self):
        """Create room selection buttons"""
        start_x = self.screen.get_width() - 220
        start_y = 20
        button_width = 200
        button_height = 60
        spacing = 10

        room_types = self.room_manager.grid.room_config.get("room_types", {})

        for i, (room_type, config) in enumerate(room_types.items()):
            if config.get("is_starting_room", False):
                continue

            y_pos = start_y + (button_height + spacing) * i
            rect = pygame.Rect(start_x, y_pos, button_width, button_height)

            display_name = config.get("name", room_type.replace("_", " ").title())

            resource_info = self._get_resource_info(config)
            if resource_info:
                display_name += f"\n{resource_info}"

            button = Button(
                rect=rect,
                text=display_name,
                action=lambda rt=room_type: self.select_room(rt),
                image_path=f"assets/images/ui/room_icons/{room_type}.png",
                tooltip=config.get("description", ""),
            )
            self.ui_system.add_element(button)

    def _get_resource_info(self, room_config: dict) -> str:
        """Generate resource information string for room"""
        info_parts = []

        if "resource_generation" in room_config:
            for resource, amount in room_config["resource_generation"].items():
                info_parts.append(f"+{amount} {resource}")

        if "resource_consumption" in room_config:
            for resource, amount in room_config["resource_consumption"].items():
                info_parts.append(f"-{amount} {resource}")

        return " | ".join(info_parts)

    def select_room(self, room_type: str):
        """Handle room selection"""
        if self.on_select:
            self.on_select(room_type)

        for element in self.ui_system.elements:
            if isinstance(element, Button):
                element.active = element.text.split("\n")[0] == room_type

    def _draw_background(self, surface: pygame.Surface):
        """Draw menu background"""
        menu_rect = pygame.Rect(surface.get_width() - 240, 0, 240, surface.get_height())
        background = pygame.Surface((240, surface.get_height()))
        background.set_alpha(128)
        background.fill((50, 50, 50))
        surface.blit(background, menu_rect)
