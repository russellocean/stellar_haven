from typing import Dict

import pygame

from entities.entity import Entity
from systems.asset_manager import AssetManager


class Room(Entity):
    def __init__(self, name: str, image_path: str, x: int, y: int):
        self.name = name
        self.asset_manager = AssetManager()

        # Load room config
        room_config = (
            self.asset_manager.get_config("rooms").get("room_types", {}).get(name, {})
        )

        # Create initial surface based on room size from config
        min_size = room_config.get("min_size", [6, 4])  # Default size if not specified
        initial_size = (min_size[0] * 32, min_size[1] * 32)

        # Initialize parent with empty surface
        super().__init__(None, x, y)
        self.image = pygame.Surface(initial_size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))  # Use topleft instead of center

        # Initialize room properties from config
        self.resource_generators = room_config.get("resource_generation", {})
        self.resource_consumers = room_config.get("resource_consumption", {})
        self.description = room_config.get("description", "")

        # Initialize resources
        self.resources: Dict[str, float] = {}

        self.room_type = name
        self.connected_rooms = []

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
