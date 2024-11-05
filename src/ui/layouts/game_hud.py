import pygame

from systems.event_system import EventData, EventSystem, GameEvent
from systems.resource_manager import ResourceManager
from ui.components.alert_system import AlertSystem
from ui.components.resource_bar import ResourceBar
from ui.components.room_name_display import RoomNameDisplay
from ui.layouts.base_layout import BaseLayout


class GameHUD(BaseLayout):
    def __init__(self, screen: pygame.Surface, resource_manager: ResourceManager):
        super().__init__(screen)
        self.event_system = EventSystem()
        self.resource_manager = resource_manager

        # Initialize UI components
        self._init_resource_bars()
        self._init_room_display()
        self._init_alert_system()

        # Subscribe to events
        self._setup_event_handlers()

    def _init_resource_bars(self):
        """Initialize resource monitoring bars"""
        self.resource_bars = {
            "power": ResourceBar("power", (10, 10)),
            "oxygen": ResourceBar("oxygen", (10, 40)),
        }

    def _init_room_display(self):
        """Initialize room name display"""
        self.room_name_display = RoomNameDisplay()
        # Position it at the top center of the screen
        self.room_name_display.rect.centerx = self.screen.get_width() // 2
        self.room_name_display.rect.top = 10

    def _init_alert_system(self):
        """Initialize alert system"""
        self.alert_system = AlertSystem(self.screen.get_width())

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
        """Handle resource update events"""
        resource = event_data.data.get("resource")
        amount = event_data.data.get("amount")
        if resource in self.resource_bars:
            self._check_resource_status(resource, amount)

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
        """Check resource levels and trigger alerts if needed"""
        max_amount = self.resource_manager.max_resources[resource]
        if amount < (max_amount * 0.2):  # 20% threshold
            self.alert_system.add_alert(
                f"Low {resource.title()}!",
                "warning",
                alert_type=f"resource_low_{resource}",
            )
        else:
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
