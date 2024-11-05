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
            "structures": self._create_structure_buttons,
            "platforms": self._create_platform_buttons,
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
        buttons_to_remove = []
        for element in self.ui_system.elements:
            if isinstance(element, Button):
                # Keep category buttons, remove everything else
                is_category = any(
                    element.text.lower() == cat.title().lower()
                    for cat in self.categories
                )
                if not is_category:
                    buttons_to_remove.append(element)

        # Remove buttons outside the loop to avoid modifying while iterating
        for button in buttons_to_remove:
            self.ui_system.remove_element(button)

    def select_category(self, category: str):
        """Switch to a different category"""
        if category == self.selected_category:
            # If clicking the same category, just refresh the buttons
            self._clear_build_buttons()
            self._create_build_buttons()
        else:
            # Switching to new category
            self.selected_category = category
            self._clear_build_buttons()
            self._create_build_buttons()

            # Clear any active selection
            for element in self.ui_system.elements:
                if isinstance(element, Button):
                    element.active = False

    def _create_room_buttons(self):
        """Create room selection buttons with enhanced layout"""
        start_x = self.screen.get_width() - 220
        start_y = 150
        button_height = 70  # Taller buttons for more info
        spacing = 15  # More spacing between buttons

        room_types = self.room_manager.grid.room_config.get("room_types", {})

        for i, (room_type, config) in enumerate(room_types.items()):
            if config.get("is_starting_room", False):
                continue

            y_pos = start_y + (button_height + spacing) * i
            rect = pygame.Rect(start_x, y_pos, 200, button_height)

            # Format display text
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
                font_size=20,  # Slightly smaller font for better fit
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
        """Draw an enhanced menu background"""
        menu_rect = pygame.Rect(surface.get_width() - 240, 0, 240, surface.get_height())

        # Draw main background
        background = pygame.Surface((240, surface.get_height()))
        background.fill((30, 30, 35))  # Darker background

        # Add subtle gradient
        gradient = pygame.Surface((240, 100))
        gradient.fill((40, 40, 45))
        gradient.set_alpha(128)
        background.blit(gradient, (0, 0))

        # Draw border
        pygame.draw.line(background, (60, 60, 65), (0, 0), (0, surface.get_height()), 2)

        surface.blit(background, menu_rect)

    def _create_structure_buttons(self):
        """Create buttons for doors and other structural elements"""
        start_x = self.screen.get_width() - 220
        start_y = 150
        button_height = 70  # Taller buttons to match room style
        spacing = 15

        # Door button with enhanced styling
        rect = pygame.Rect(start_x, start_y, 200, button_height)
        button = Button(
            rect=rect,
            text="Door\nStructural Connection",  # Added subtitle for more info
            action=lambda: self.select_build_item("structures", "door_light_closed"),
            image_path="assets/images/ui/build_icon.png",
            tooltip="Connect rooms together",
            font_size=20,
        )
        self.ui_system.add_element(button)

    def _create_platform_buttons(self):
        """Create enhanced platform selection buttons"""
        start_x = self.screen.get_width() - 220
        start_y = 150
        button_height = 70  # Taller buttons to match room style
        spacing = 15

        platform_types = [
            ("platform_left", "Left Platform"),
            ("platform_center", "Center Platform"),
            ("platform_right", "Right Platform"),
        ]

        for i, (platform_type, display_name) in enumerate(platform_types):
            y_pos = start_y + (button_height + spacing) * i
            rect = pygame.Rect(start_x, y_pos, 200, button_height)

            button = Button(
                rect=rect,
                text=f"{display_name}\nStructural Support",  # Added subtitle for consistency
                action=lambda pt=platform_type: self.select_build_item("platforms", pt),
                image_path="assets/images/ui/build_icon.png",
                tooltip="Add structural support",
                font_size=20,
            )
            self.ui_system.add_element(button)
