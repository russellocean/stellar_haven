from typing import Optional

import pygame

from systems.event_system import EventSystem, GameEvent
from systems.resource_manager import ResourceManager
from ui.components.alert_system import AlertSystem
from ui.components.resource_bar import ResourceBar
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
    def __init__(self, screen: pygame.Surface, resource_manager: ResourceManager):
        super().__init__(screen)
        self.event_system = EventSystem()
        self.room_name_display = RoomNameDisplay()
        self.resource_manager = resource_manager

        # Add resource bars
        self.resource_bars = {
            "power": ResourceBar("power", (10, 10)),
            "oxygen": ResourceBar("oxygen", (10, 40)),
            "health": ResourceBar("health", (10, 70)),
        }

        # Add alert system
        self.alert_system = AlertSystem(screen.get_width())

        # Subscribe to events
        self.event_system.subscribe(GameEvent.ROOM_ENTERED, self._handle_room_entered)
        self.event_system.subscribe(
            GameEvent.RESOURCE_DEPLETED, self._handle_resource_depleted
        )
        self.event_system.subscribe(
            GameEvent.RESOURCE_RESTORED, self._handle_resource_restored
        )

    def _handle_room_entered(self, event_data):
        """Handle room entry events"""
        room = event_data.data.get("room")
        if room and hasattr(room, "name"):
            self.room_name_display.show_room_name(room.name)

    def _handle_resource_depleted(self, event_data):
        """Handle resource depletion events"""
        resource = event_data.data.get("resource")
        if resource:
            self.alert_system.add_alert(
                f"Warning: {resource.title()} levels critical!",
                duration=3000,
                priority=1,
                alert_type=f"resource_low_{resource}",  # Unique alert type for each resource
            )

    def _handle_resource_restored(self, event_data):
        """Handle resource restored events"""
        resource = event_data.data.get("resource")
        if resource:
            self.alert_system.add_alert(
                f"{resource.title()} levels restored",
                duration=2000,
                priority=0,
                alert_type=f"resource_restored_{resource}",
            )
            # Clear the low resource alert type
            self.alert_system.remove_alert_type(f"resource_low_{resource}")

    def update(self):
        """Update HUD elements"""
        self.room_name_display.update()
        self.alert_system.update()

    def draw(self, surface: pygame.Surface):
        """Draw HUD elements"""
        # Draw resource bars
        for resource_name, bar in self.resource_bars.items():
            current = self.resource_manager.resources[resource_name]
            maximum = self.resource_manager.max_resources[resource_name]
            bar.draw(surface, current, maximum)

        # Draw room name
        self.room_name_display.draw(surface)

        # Draw alerts
        self.alert_system.draw(surface)
