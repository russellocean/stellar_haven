from typing import Dict

from systems.debug_system import DebugSystem
from systems.event_system import EventSystem, GameEvent


class ResourceManager:
    def __init__(self):
        self.event_system = EventSystem()

        # Initialize resources
        self.resources: Dict[str, float] = {
            "power": 100.0,
            "oxygen": 100.0,
            "health": 100.0,
        }

        self.max_resources: Dict[str, float] = {
            "power": 100.0,
            "oxygen": 100.0,
            "health": 100.0,
        }

        # Track which resources have triggered low alerts
        self.critical_resources = set()

        # Base consumption rates per second
        self.base_consumption_rates = {
            "power": 0.1,  # Base power drain
            "oxygen": 0.05,  # Base oxygen consumption
        }

        self.debug = DebugSystem()

    def update(self):
        """Update resource levels based on consumption and generation"""
        for resource, rate in self.base_consumption_rates.items():
            old_value = self.resources[resource]
            self.consume_resource(resource, rate)

            # Debug log significant changes
            if abs(old_value - self.resources[resource]) > 1.0:
                self.debug.log(
                    f"{resource} changed by {old_value - self.resources[resource]:.1f}"
                )

    def consume_resource(self, resource: str, amount: float) -> bool:
        """Consume resource if available"""
        if resource in self.resources:
            if self.resources[resource] >= amount:
                self.resources[resource] = max(0, self.resources[resource] - amount)

                # Check if resource is critically low (below 20%) and hasn't been reported yet
                if (
                    self.resources[resource] < (self.max_resources[resource] * 0.2)
                    and resource not in self.critical_resources
                ):
                    self.critical_resources.add(resource)
                    self.debug.log(
                        f"{resource} critically low: {self.resources[resource]:.1f}"
                    )
                    self.event_system.emit(
                        GameEvent.RESOURCE_DEPLETED,
                        resource=resource,
                        current_value=self.resources[resource],
                    )
                return True
            self.resources[resource] = 0
            return False
        return False

    def add_resource(self, resource: str, amount: float):
        """Add resource up to max capacity"""
        if resource in self.resources:
            self.resources[resource] = min(
                self.resources[resource] + amount, self.max_resources[resource]
            )

            # If resource was critically low and is now above 50%, emit restored event
            if resource in self.critical_resources and self.resources[resource] > (
                self.max_resources[resource] * 0.5
            ):
                self.critical_resources.remove(resource)
                self.debug.log(f"{resource} restored: {self.resources[resource]:.1f}")
                self.event_system.emit(
                    GameEvent.RESOURCE_RESTORED,
                    resource=resource,
                    current_value=self.resources[resource],
                )

    def get_resource_percentage(self, resource: str) -> float:
        """Get resource level as a percentage"""
        if resource in self.resources and resource in self.max_resources:
            return (self.resources[resource] / self.max_resources[resource]) * 100
        return 0.0
