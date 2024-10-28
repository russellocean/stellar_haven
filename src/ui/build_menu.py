from typing import Callable, Dict, Optional

import pygame

from .button import Button


class BuildMenu:
    def __init__(self, screen: pygame.Surface, on_select: Optional[Callable] = None):
        self.screen = screen
        self.buttons: Dict[str, Button] = {}
        self.visible = False
        self.on_select = on_select  # Callback when a room is selected
        self._create_buttons()

    def _create_buttons(self):
        # Position menu in top-right corner
        start_x = self.screen.get_width() - 220
        start_y = 20
        button_width = 200
        button_height = 60
        spacing = 10

        room_types = {
            "bridge": "Command Center",
            "engine_room": "Engine Room",
            "life_support": "Life Support",
            "medical_bay": "Medical Bay",
        }

        for i, (room_type, display_name) in enumerate(room_types.items()):
            y_pos = start_y + (button_height + spacing) * i

            # Create button with room preview image
            self.buttons[room_type] = Button(
                start_x,
                y_pos,
                button_width,
                button_height,
                display_name,
                lambda rt=room_type: self.select_room(rt),
                f"assets/images/rooms/{room_type}.png",
            )

    def select_room(self, room_type: str):
        """Callback for room selection"""
        if self.on_select:
            self.on_select(room_type)  # Call the callback with selected room type

        # Deactivate all buttons except the selected one
        for rt, button in self.buttons.items():
            button.active = rt == room_type

    def update(self, mouse_pos, mouse_clicked):
        if not self.visible:
            return None

        for button in self.buttons.values():
            button.update(mouse_pos, mouse_clicked)

    def draw(self):
        if not self.visible:
            return

        # Draw semi-transparent background
        menu_rect = pygame.Rect(
            self.screen.get_width() - 240, 0, 240, self.screen.get_height()
        )
        s = pygame.Surface((240, self.screen.get_height()))
        s.set_alpha(128)
        s.fill((50, 50, 50))
        self.screen.blit(s, menu_rect)

        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)
