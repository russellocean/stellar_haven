from typing import Dict

from systems.debug_system import DebugSystem
from systems.event_system import EventSystem, GameEvent


class ResourceManager:
    def __init__(self):
        self.event_system = EventSystem()
        self._init_resources()
        self._init_debug()

    def _init_resources(self):
        """Initialize resource systems"""
        # Initialize resources with starting values
        self.resources: Dict[str, float] = {
            "power": 100.0,
            "oxygen": 100.0,
        }

        self.max_resources: Dict[str, float] = {
            "power": 100.0,
            "oxygen": 100.0,
        }

        # Base consumption rates per second (when no rooms are helping)
        self.base_consumption_rates = {
            "power": 0.1,  # Base power drain
            "oxygen": 0.05,  # Base oxygen consumption
        }

        # Track resource states
        self.critical_resources = set()
        self.active_rooms = []  # Rooms currently affecting resources

    def _init_debug(self):
        """Initialize debug tracking"""
        self.debug = DebugSystem()
        self.debug.add_watch("Power", lambda: f"{self.resources['power']:.1f}")
        self.debug.add_watch("Oxygen", lambda: f"{self.resources['oxygen']:.1f}")

    def update(self, dt: float = 1.0):
        """Update resource levels based on rooms and consumption"""
        for resource in self.resources:
            old_value = self.resources[resource]

            # Calculate net resource change
            net_change = self._calculate_net_resource_change(resource)

            # Apply change
            self.resources[resource] = max(
                0.0,
                min(
                    self.resources[resource] + net_change * dt,
                    self.max_resources[resource],
                ),
            )

            # Emit resource updated event
            self.event_system.emit(
                GameEvent.RESOURCE_UPDATED,
                resource=resource,
                amount=self.resources[resource],
                previous=old_value,
                change=net_change,
            )

            # Check resource status
            self._check_resource_status(resource)

    def _calculate_net_resource_change(self, resource: str) -> float:
        """Calculate net resource change considering rooms and base consumption"""
        net_change = -self.base_consumption_rates.get(resource, 0.0)

        # Add effects from active rooms
        for room in self.active_rooms:
            # Generation
            if resource in room.resource_generators:
                net_change += room.resource_generators[resource]
            # Consumption
            if resource in room.resource_consumers:
                net_change -= room.resource_consumers[resource]

        return net_change

    def _check_resource_status(self, resource: str):
        """Check and handle resource status changes"""
        current_value = self.resources[resource]
        max_value = self.max_resources[resource]

        # Check for critical status (below 20%)
        if current_value < (max_value * 0.2):
            if resource not in self.critical_resources:
                self.critical_resources.add(resource)
                self.event_system.emit(
                    GameEvent.RESOURCE_DEPLETED,
                    resource=resource,
                    current_value=current_value,
                )
                self.debug.log(f"{resource} critically low: {current_value:.1f}")

        # Check for restoration (above 50%)
        elif current_value > (max_value * 0.5):
            if resource in self.critical_resources:
                self.critical_resources.remove(resource)
                self.event_system.emit(
                    GameEvent.RESOURCE_RESTORED,
                    resource=resource,
                    current_value=current_value,
                )
                self.debug.log(f"{resource} restored: {current_value:.1f}")

    def register_room(self, room):
        """Register a room to affect resources"""
        if room not in self.active_rooms:
            self.active_rooms.append(room)
            self.debug.log(f"Registered room: {room.name}")

    def unregister_room(self, room):
        """Unregister a room from affecting resources"""
        if room in self.active_rooms:
            self.active_rooms.remove(room)
            self.debug.log(f"Unregistered room: {room.name}")

    def get_resource_percentage(self, resource: str) -> float:
        """Get resource level as a percentage"""
        if resource in self.resources and resource in self.max_resources:
            return (self.resources[resource] / self.max_resources[resource]) * 100
        return 0.0
