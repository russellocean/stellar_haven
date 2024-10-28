from typing import Optional

import pygame

from systems.event_system import EventSystem, GameEvent
from ui.layouts.base_layout import BaseLayout


class RoomNameDisplay:
    def __init__(self):
        self.font = pygame.font.Font(None, 48)
        self.current_text = ""
        self.alpha = 0  # For fade effect
        self.display_time = 0
        self.fade_in_duration = 500  # milliseconds
        self.display_duration = 2000  # milliseconds
        self.fade_out_duration = 500  # milliseconds
        self.start_time: Optional[int] = None

    def show_room_name(self, room_name: str):
        self.current_text = room_name.replace("_", " ").title()
        self.start_time = pygame.time.get_ticks()
        self.alpha = 0

    def update(self):
        if self.start_time is None:
            return

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time

        # Calculate alpha based on animation phase
        if elapsed < self.fade_in_duration:
            # Fade in
            self.alpha = int((elapsed / self.fade_in_duration) * 255)
        elif elapsed < self.fade_in_duration + self.display_duration:
            # Full display
            self.alpha = 255
        elif (
            elapsed
            < self.fade_in_duration + self.display_duration + self.fade_out_duration
        ):
            # Fade out
            fade_out_progress = (
                elapsed - (self.fade_in_duration + self.display_duration)
            ) / self.fade_out_duration
            self.alpha = int(255 * (1 - fade_out_progress))
        else:
            # Animation complete
            self.alpha = 0
            self.start_time = None

    def draw(self, surface: pygame.Surface):
        if self.alpha <= 0:
            return

        text_surface = self.font.render(self.current_text, True, (255, 255, 255))
        text_surface.set_alpha(self.alpha)

        # Center horizontally, position at top of screen with padding
        x = (surface.get_width() - text_surface.get_width()) // 2
        y = 30  # Padding from top

        surface.blit(text_surface, (x, y))


class GameHUD(BaseLayout):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.event_system = EventSystem()
        self.room_name_display = RoomNameDisplay()

        # Subscribe to room entry events
        self.event_system.subscribe(GameEvent.ROOM_ENTERED, self._handle_room_entered)

    def _handle_room_entered(self, event_data):
        """Handle room entry events"""
        room = event_data.data.get("room")
        if room and hasattr(room, "name"):
            self.room_name_display.show_room_name(room.name)

    def update(self):
        """Update HUD elements"""
        self.room_name_display.update()

    def draw(self, surface: pygame.Surface):
        """Draw HUD elements"""
        self.room_name_display.draw(surface)
