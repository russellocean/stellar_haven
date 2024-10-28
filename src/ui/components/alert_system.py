from collections import deque

import pygame


class Alert:
    def __init__(
        self, message: str, duration: int, priority: int = 0, alert_type: str = None
    ):
        self.message = message
        self.duration = duration
        self.priority = priority
        self.alert_type = alert_type  # Used to identify unique alerts
        self.start_time = pygame.time.get_ticks()
        self.alpha = 255


class AlertSystem:
    def __init__(self, screen_width: int):
        self.alerts = deque(maxlen=5)  # Keep last 5 alerts
        self.font = pygame.font.Font(None, 32)
        self.screen_width = screen_width
        self.active_alerts = set()  # Track unique alert types

    def add_alert(
        self,
        message: str,
        duration: int = 3000,
        priority: int = 0,
        alert_type: str = None,
    ):
        """Add a new alert message if it's not already active"""
        if alert_type and alert_type in self.active_alerts:
            return  # Skip if this type of alert is already active

        alert = Alert(message, duration, priority, alert_type)
        self.alerts.append(alert)
        if alert_type:
            self.active_alerts.add(alert_type)

    def remove_alert_type(self, alert_type: str):
        """Remove an alert type from active alerts"""
        if alert_type in self.active_alerts:
            self.active_alerts.remove(alert_type)

    def update(self):
        """Update alert states"""
        current_time = pygame.time.get_ticks()
        # Remove expired alerts
        self.alerts = deque(
            [
                alert
                for alert in self.alerts
                if current_time - alert.start_time < alert.duration
            ],
            maxlen=5,
        )

        # Update alpha for fade effect
        for alert in self.alerts:
            time_left = alert.duration - (current_time - alert.start_time)
            if time_left < 500:  # Start fading in last 500ms
                alert.alpha = int((time_left / 500) * 255)

    def draw(self, surface: pygame.Surface):
        """Draw active alerts"""
        y_offset = 100  # Start below resource bars
        for alert in self.alerts:
            text_surface = self.font.render(alert.message, True, (255, 255, 255))
            text_surface.set_alpha(alert.alpha)
            x = (self.screen_width - text_surface.get_width()) // 2
            surface.blit(text_surface, (x, y_offset))
            y_offset += 40
