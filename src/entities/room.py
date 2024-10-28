from typing import Dict

from entities.entity import Entity
from systems.asset_manager import AssetManager


class Room(Entity):
    def __init__(self, name: str, image_path: str, x: int, y: int):
        self.name = name
        self.asset_manager = AssetManager()

        # Load room config
        room_config = self.asset_manager.get_config("rooms").get(name, {})

        # Initialize with provided image path for now
        super().__init__(image_path, x, y)

        # Initialize room properties from config
        self.resource_generators = room_config.get("resource_generation", {})
        self.resource_consumers = room_config.get("resource_consumption", {})
        self.description = room_config.get("description", "")

        # Initialize resources
        self.resources: Dict[str, float] = {}

    def update(self, resource_manager=None):
        """Update room state"""
        if resource_manager:
            # Handle resource generation
            for resource, rate in self.resource_generators.items():
                resource_manager.add_resource(resource, rate)

            # Handle resource consumption
            for resource, rate in self.resource_consumers.items():
                resource_manager.consume_resource(resource, rate)

    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is inside the room"""
        return self.rect.collidepoint(x, y)
