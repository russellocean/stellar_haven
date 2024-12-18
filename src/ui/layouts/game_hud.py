import pygame

from systems.event_system import EventData, EventSystem, GameEvent
from systems.resource_manager import ResourceManager
from ui.components.alert_system import AlertSystem
from ui.components.resource_bar import ResourceBar
from ui.components.room_name_display import RoomNameDisplay
from ui.layouts.base_layout import BaseLayout


class GameHUD(BaseLayout):
    # Constants for positioning and appearance
    MARGIN = 20
    BAR_SPACING = 40
    BAR_WIDTH = 200
    BAR_HEIGHT = 25

    def __init__(self, screen: pygame.Surface, resource_manager: ResourceManager):
        super().__init__(screen)
        self.event_system = EventSystem()
        self.resource_manager = resource_manager
        self.screen_height = screen.get_height()
        self.screen_width = screen.get_width()

        # Initialize UI components
        self._init_resource_bars()
        self._init_room_display()
        self._init_alert_system()
        self._setup_event_handlers()

    def _init_resource_bars(self):
        """Initialize resource monitoring bars with enhanced visuals"""
        base_y = self.screen_height - self.MARGIN - self.BAR_HEIGHT

        # Power bar with yellow/gold theme
        self.resource_bars = {
            "power": ResourceBar(
                "power",
                (self.MARGIN, base_y),
                width=self.BAR_WIDTH,
                height=self.BAR_HEIGHT,
                color=(255, 215, 0),  # Gold for power
                icon_path="assets/images/ui/build_icon.png",
                animation_speed=0.15,
                show_rate=True,
            ),
            # Oxygen bar with blue theme
            "oxygen": ResourceBar(
                "oxygen",
                (self.MARGIN, base_y - self.BAR_SPACING),
                width=self.BAR_WIDTH,
                height=self.BAR_HEIGHT,
                color=(64, 156, 255),  # Blue for oxygen
                icon_path="assets/images/ui/build_icon.png",
                animation_speed=0.1,
                show_rate=True,
            ),
            # Credits counter with gold theme
            "credits": ResourceBar(
                "credits",
                (self.MARGIN, base_y - self.BAR_SPACING * 2),  # Position above oxygen
                width=self.BAR_WIDTH,
                height=self.BAR_HEIGHT,
                color=(255, 215, 0),  # Gold for credits
                icon_path="assets/images/ui/build_icon.png",
                animation_speed=0.1,
                show_rate=True,
            ),
        }

    def _init_room_display(self):
        """Initialize room name display with enhanced positioning"""
        self.room_name_display = RoomNameDisplay()
        # Position it at the top center with some padding
        self.room_name_display.rect.centerx = self.screen_width // 2
        self.room_name_display.rect.top = self.MARGIN

    def _init_alert_system(self):
        """Initialize alert system with improved positioning"""
        self.alert_system = AlertSystem(
            screen_width=self.screen_width,
            position=(0, self.screen_height // 4),
            max_alerts=3,
        )

    def _setup_event_handlers(self):
        """Setup event subscriptions"""
        self.event_system.subscribe(GameEvent.ROOM_ENTERED, self._handle_room_entered)
        self.event_system.subscribe(
            GameEvent.RESOURCE_UPDATED, self._handle_resource_update
        )
        self.event_system.subscribe(
            GameEvent.RESOURCE_DEPLETED, self._handle_resource_depleted
        )
        self.event_system.subscribe(
            GameEvent.RESOURCE_RESTORED, self._handle_resource_restored
        )

    def _handle_room_entered(self, event_data: EventData):
        """Handle room entry events"""
        room = event_data.data.get("room")
        if room:
            self.room_name_display.show_room_name(room.name)

    def _handle_resource_update(self, event_data: EventData):
        """Handle resource update events with improved feedback"""
        resource = event_data.data.get("resource")
        amount = event_data.data.get("amount")
        previous = event_data.data.get("previous", 0)
        change = event_data.data.get("change", 0)  # Get the rate of change

        if resource in self.resource_bars:
            # Update the rate display
            self.resource_bars[resource].update_rate(change)

            self._check_resource_status(resource, amount)

            # Add visual feedback for significant changes
            if abs(amount - previous) > (
                self.resource_manager.max_resources[resource] * 0.1
            ):
                self._show_resource_change_feedback(resource, amount - previous)

    def _show_resource_change_feedback(self, resource: str, change: float):
        """Show visual feedback for significant resource changes"""
        if change > 0:
            self.alert_system.add_alert(
                message=f"+{change:.1f} {resource.title()}",
                alert_type="info",
                duration=1000,
                position="bottom",
            )
        else:
            self.alert_system.add_alert(
                message=f"{change:.1f} {resource.title()}",
                alert_type="warning",
                duration=1000,
                position="bottom",
            )

    def _handle_resource_depleted(self, event_data: EventData):
        """Handle resource depletion events"""
        resource = event_data.data.get("resource")
        if resource in self.resource_bars:
            self.alert_system.add_alert(f"{resource.title()} Depleted!", "critical")

    def _handle_resource_restored(self, event_data: EventData):
        """Handle resource restoration events"""
        resource = event_data.data.get("resource")
        if resource in self.resource_bars:
            self.alert_system.remove_alert_type(f"resource_low_{resource}")

    def _check_resource_status(self, resource: str, amount: float):
        """Check resource levels with multiple thresholds"""
        if resource == "credits":
            return

        max_amount = self.resource_manager.max_resources[resource]
        percentage = amount / max_amount

        if percentage < 0.1:  # Critical threshold (10%)
            self.alert_system.add_alert(
                message=f"CRITICAL: {resource.title()} at {percentage:.0%}!",
                alert_type="critical",
                duration=5000,
                unique_id=f"resource_critical_{resource}",
            )
        elif percentage < 0.2:  # Warning threshold (20%)
            self.alert_system.add_alert(
                message=f"Low {resource.title()} - {percentage:.0%}",
                alert_type="warning",
                duration=3000,
                unique_id=f"resource_low_{resource}",
            )
        else:
            # Clear any existing warnings for this resource
            self.alert_system.remove_alert_type(f"resource_critical_{resource}")
            self.alert_system.remove_alert_type(f"resource_low_{resource}")

    def update(self):
        """Update HUD elements with animations"""
        self.room_name_display.update()
        self.alert_system.update()

        # Update resource bars with smooth transitions
        for bar in self.resource_bars.values():
            bar.update()

    def draw(self, surface: pygame.Surface):
        """Draw HUD elements with proper layering"""
        # Draw resource bars with current values
        for resource_name, bar in self.resource_bars.items():
            current = self.resource_manager.resources[resource_name]
            maximum = self.resource_manager.max_resources[resource_name]
            bar.draw(surface, current, maximum)

        # Draw room name with potential effects
        self.room_name_display.draw(surface)

        # Draw alerts on top
        self.alert_system.draw(surface)
