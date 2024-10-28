from typing import Dict

from systems.event_system import EventSystem, GameEvent


class ResourceManager:
    def __init__(self):
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
        self.event_system = EventSystem()

    def add_resource(self, resource: str, amount: float):
        """Add resource up to max capacity"""
        if resource in self.resources:
            self.resources[resource] = min(
                self.resources[resource] + amount, self.max_resources[resource]
            )

    def consume_resource(self, resource: str, amount: float) -> bool:
        """Consume resource and emit events"""
        if resource in self.resources:
            if self.resources[resource] >= amount:
                self.resources[resource] -= amount

                # Emit resource updated event
                self.event_system.emit(
                    GameEvent.RESOURCE_UPDATED,
                    resource=resource,
                    current_value=self.resources[resource],
                    max_value=self.max_resources[resource],
                )

                # Check if resource is critically low (below 10%)
                if self.resources[resource] < (self.max_resources[resource] * 0.1):
                    self.event_system.emit(
                        GameEvent.RESOURCE_DEPLETED,
                        resource=resource,
                        current_value=self.resources[resource],
                    )
                return True

            self.resources[resource] = 0
            self.event_system.emit(
                GameEvent.RESOURCE_DEPLETED, resource=resource, current_value=0
            )
            return False
        return False

    def get_resource_percentage(self, resource: str) -> float:
        """Get resource level as a percentage"""
        if resource in self.resources and resource in self.max_resources:
            return (self.resources[resource] / self.max_resources[resource]) * 100
        return 0.0
