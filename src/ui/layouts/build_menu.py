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
        self.selected_category = "rooms"  # Default category
        self.categories = {
            "rooms": self._create_room_buttons,
            "doors": self._create_door_buttons,
            "platforms": self._create_platform_buttons,
            "decorations": self._create_decoration_buttons,
        }
        self._create_category_buttons()
        self._create_build_buttons()

    def _create_category_buttons(self):
        """Create category selection buttons"""
        start_x = self.screen.get_width() - 220
        start_y = 20
        button_height = 30
        spacing = 5

        for i, category in enumerate(self.categories.keys()):
            y_pos = start_y + (button_height + spacing) * i
            rect = pygame.Rect(start_x, y_pos, 200, button_height)

            button = Button(
                rect=rect,
                text=category.title(),
                action=lambda cat=category: self.select_category(cat),
            )
            self.ui_system.add_element(button)

    def _create_build_buttons(self):
        """Create buttons for current category"""
        if self.selected_category in self.categories:
            self.categories[self.selected_category]()

    def _clear_build_buttons(self):
        """Clear existing build buttons"""
        for element in self.ui_system.elements:
            if (
                isinstance(element, Button)
                and element.text.lower() not in self.categories
            ):
                self.ui_system.remove_element(element)

    def select_category(self, category: str):
        """Switch to a different category"""
        self.selected_category = category
        # Clear existing build buttons
        self._clear_build_buttons()
        # Create new buttons for category
        self._create_build_buttons()

    def _create_room_buttons(self):
        """Create room selection buttons"""
        start_x = self.screen.get_width() - 220
        start_y = 150  # Below category buttons
        button_height = 60
        spacing = 10

        room_types = self.room_manager.grid.room_config.get("room_types", {})

        for i, (room_type, config) in enumerate(room_types.items()):
            if config.get("is_starting_room", False):
                continue

            y_pos = start_y + (button_height + spacing) * i
            rect = pygame.Rect(start_x, y_pos, 200, button_height)

            display_name = config.get("name", room_type.replace("_", " ").title())

            resource_info = self._get_resource_info(config)
            if resource_info:
                display_name += f"\n{resource_info}"

            button = Button(
                rect=rect,
                text=display_name,
                action=lambda rt=room_type: self.select_build_item("rooms", rt),
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

    def select_build_item(self, category: str, item_type: str):
        """Handle build item selection"""
        if self.on_select:
            self.on_select(category, item_type)

        # Update button states
        for element in self.ui_system.elements:
            if isinstance(element, Button):
                if isinstance(element.text, str):  # Handle multiline text
                    element.active = (
                        element.text.split("\n")[0].lower()
                        == item_type.replace("_", " ").lower()
                    )

    def _draw_background(self, surface: pygame.Surface):
        """Draw menu background"""
        menu_rect = pygame.Rect(surface.get_width() - 240, 0, 240, surface.get_height())
        background = pygame.Surface((240, surface.get_height()))
        background.set_alpha(128)
        background.fill((50, 50, 50))
        surface.blit(background, menu_rect)

    def _create_door_buttons(self):
        """Create door selection buttons"""
        start_x = self.screen.get_width() - 220
        start_y = 150  # Below category buttons
        button_height = 60
        spacing = 10

        door_types = ["door_light_closed", "door_special_closed"]

        for i, door_type in enumerate(door_types):
            y_pos = start_y + (button_height + spacing) * i
            rect = pygame.Rect(start_x, y_pos, 200, button_height)

            button = Button(
                rect=rect,
                text=door_type.replace("_", " ").title(),
                action=lambda dt=door_type: self.select_build_item("doors", dt),
                image_path="assets/images/ui/build_icon.png",
                # image_path=f"assets/images/ui/door_icons/{door_type}.png",
            )
            self.ui_system.add_element(button)

    def _create_platform_buttons(self):
        """Create platform selection buttons"""
        start_x = self.screen.get_width() - 220
        start_y = 150
        button_height = 60
        spacing = 10

        platform_types = ["platform_left", "platform_center", "platform_right"]

        for i, platform_type in enumerate(platform_types):
            y_pos = start_y + (button_height + spacing) * i
            rect = pygame.Rect(start_x, y_pos, 200, button_height)

            button = Button(
                rect=rect,
                text=platform_type.replace("_", " ").title(),
                action=lambda pt=platform_type: self.select_build_item("platforms", pt),
                image_path="assets/images/ui/build_icon.png",
                # image_path=f"assets/images/ui/platform_icons/{platform_type}.png",
            )
            self.ui_system.add_element(button)

    def _create_decoration_buttons(self):
        """Create decoration selection buttons"""
        # To be implemented when decorations are added
        pass
