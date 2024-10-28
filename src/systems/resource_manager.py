from typing import Dict


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

    def add_resource(self, resource: str, amount: float):
        """Add resource up to max capacity"""
        if resource in self.resources:
            self.resources[resource] = min(
                self.resources[resource] + amount, self.max_resources[resource]
            )

    def consume_resource(self, resource: str, amount: float) -> bool:
        """
        Consume resource if available
        Returns False if resource is depleted
        """
        if resource in self.resources:
            if self.resources[resource] >= amount:
                self.resources[resource] -= amount
                return True
            self.resources[resource] = 0
            return False
        return False

    def get_resource_percentage(self, resource: str) -> float:
        """Get resource level as a percentage"""
        if resource in self.resources and resource in self.max_resources:
            return (self.resources[resource] / self.max_resources[resource]) * 100
        return 0.0
