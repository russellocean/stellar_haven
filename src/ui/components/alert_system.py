from collections import deque
from typing import Tuple

import pygame


class Alert:
    def __init__(
        self,
        message: str,
        alert_type: str = "info",
        duration: int = 3000,
        priority: int = 0,
        position: str = "center",
    ):
        self.message = message
        self.duration = duration
        self.priority = priority
        self.alert_type = alert_type
        self.position = position
        self.start_time = pygame.time.get_ticks()
        self.alpha = 255

        # Colors based on alert type
        self.colors = {
            "info": (255, 255, 255),  # White
            "warning": (255, 165, 0),  # Orange
            "critical": (255, 0, 0),  # Red
            "success": (0, 255, 0),  # Green
        }
        self.color = self.colors.get(alert_type, self.colors["info"])


class AlertSystem:
    def __init__(
        self,
        screen_width: int,
        position: Tuple[int, int] = (0, 100),
        max_alerts: int = 5,
        spacing: int = 40,
    ):
        self.alerts = deque(maxlen=max_alerts)
        self.font = pygame.font.Font(None, 32)
        self.screen_width = screen_width
        self.position = position
        self.spacing = spacing
        self.active_alerts = {}  # Track unique alert types
        self.max_alerts = max_alerts

    def add_alert(
        self,
        message: str,
        alert_type: str = "info",
        duration: int = 3000,
        priority: int = 0,
        position: str = "center",
    ):
        """Add a new alert message"""
        # If it's a unique alert type, remove the old one first
        if alert_type in self.active_alerts:
            self.alerts.remove(self.active_alerts[alert_type])

        alert = Alert(message, alert_type, duration, priority, position)
        self.alerts.append(alert)

        # Track unique alerts
        if alert_type:
            self.active_alerts[alert_type] = alert

    def remove_alert_type(self, alert_type: str):
        """Remove an alert type"""
        if alert_type in self.active_alerts:
            if self.active_alerts[alert_type] in self.alerts:
                self.alerts.remove(self.active_alerts[alert_type])
            del self.active_alerts[alert_type]

    def update(self):
        """Update alert states"""
        current_time = pygame.time.get_ticks()
        expired_alerts = []

        for alert in self.alerts:
            time_left = alert.duration - (current_time - alert.start_time)

            if time_left <= 0:
                expired_alerts.append(alert)
            elif time_left < 500:  # Start fading in last 500ms
                alert.alpha = int((time_left / 500) * 255)

        # Remove expired alerts
        for alert in expired_alerts:
            if alert in self.alerts:
                self.alerts.remove(alert)
                if alert.alert_type in self.active_alerts:
                    del self.active_alerts[alert.alert_type]

    def draw(self, surface: pygame.Surface):
        """Draw active alerts"""
        base_x, base_y = self.position
        y_offset = 0

        for alert in self.alerts:
            text_surface = self.font.render(alert.message, True, alert.color)
            text_surface.set_alpha(alert.alpha)

            # Position based on alert's preference
            if alert.position == "center":
                x = (self.screen_width - text_surface.get_width()) // 2
            elif alert.position == "left":
                x = base_x + 10
            elif alert.position == "right":
                x = self.screen_width - text_surface.get_width() - 10
            else:
                x = base_x

            surface.blit(text_surface, (x, base_y + y_offset))
            y_offset += self.spacing
