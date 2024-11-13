from typing import Dict

from systems.debug_system import DebugSystem
from systems.event_system import EventSystem, GameEvent


class ResourceManager:
    def __init__(self):
        self.event_system = EventSystem()
        self._init_resources()
        self._init_debug()
        self.resource_alerts = {
            "power": {"critical": 0.1, "warning": 0.2, "low": 0.3},  # 10%  # 20%  # 30%
            "oxygen": {
                "critical": 0.15,  # 15%
                "warning": 0.25,  # 25%
                "low": 0.35,  # 35%
            },
        }

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

            # Emit resource updated event with rate information
            self.event_system.emit(
                GameEvent.RESOURCE_UPDATED,
                resource=resource,
                amount=self.resources[resource],
                previous=old_value,
                change=net_change,  # This is the rate per second
            )

            # Check resource status
            self._check_resource_status(resource)

    def _calculate_net_resource_change(self, resource: str) -> float:
        """Calculate net resource change considering rooms and base consumption"""
        net_change = -self.base_consumption_rates.get(resource, 0.0)

        # Add effects from active rooms
        for room in self.active_rooms:
            # Add generation from room config
            if (
                hasattr(room, "resource_generators")
                and resource in room.resource_generators
            ):
                net_change += room.resource_generators[resource]

            # Subtract consumption from room config
            if (
                hasattr(room, "resource_consumers")
                and resource in room.resource_consumers
            ):
                net_change -= room.resource_consumers[resource]

        return net_change

    def _check_resource_status(self, resource: str):
        """Enhanced resource status checking with multiple thresholds"""
        current = self.resources[resource]
        maximum = self.max_resources[resource]
        percentage = current / maximum

        thresholds = self.resource_alerts[resource]

        if percentage <= thresholds["critical"]:
            if resource not in self.critical_resources:
                self.critical_resources.add(resource)
                self.event_system.emit(
                    GameEvent.RESOURCE_CRITICAL,
                    resource=resource,
                    percentage=percentage,
                    threshold="critical",
                )
        elif percentage <= thresholds["warning"]:
            self.event_system.emit(
                GameEvent.RESOURCE_WARNING,
                resource=resource,
                percentage=percentage,
                threshold="warning",
            )
        elif percentage <= thresholds["low"]:
            self.event_system.emit(
                GameEvent.RESOURCE_LOW,
                resource=resource,
                percentage=percentage,
                threshold="low",
            )
        elif resource in self.critical_resources:
            self.critical_resources.remove(resource)
            self.event_system.emit(
                GameEvent.RESOURCE_RESTORED, resource=resource, percentage=percentage
            )

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

    def add_resource(self, resource: str, amount: float):
        """Add a specified amount to a resource"""
        if resource in self.resources:
            old_value = self.resources[resource]
            self.resources[resource] = min(
                self.resources[resource] + amount, self.max_resources[resource]
            )

            # Emit resource updated event
            self.event_system.emit(
                GameEvent.RESOURCE_UPDATED,
                resource=resource,
                amount=self.resources[resource],
                previous=old_value,
                change=amount,
            )

            # Check if we're no longer in a critical state
            self._check_resource_status(resource)
