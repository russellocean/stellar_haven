from typing import Dict, Tuple

from entities.entity import Entity
from systems.asset_manager import AssetManager


class Room(Entity):
    def __init__(self, room_type: str, grid_pos: Tuple[int, int], cell_size: int):
        """Initialize a room
        Args:
            room_type (str): Type of room from config
            grid_pos (Tuple[int, int]): Position in grid coordinates
            cell_size (int): Size of each grid cell in pixels
        """
        # Calculate world position from grid position
        x = grid_pos[0] * cell_size
        y = grid_pos[1] * cell_size

        # Initialize parent entity
        super().__init__(None, x, y)

        self.room_type = room_type
        self.grid_pos = grid_pos
        self.cell_size = cell_size

        # Load room config
        self.asset_manager = AssetManager()
        room_config = self.asset_manager.get_config("rooms")["room_types"][room_type]

        # Set size based on grid size from config
        grid_size = room_config["grid_size"]
        self.width = grid_size[0] * cell_size
        self.height = grid_size[1] * cell_size

        # Initialize room properties from config
        self.resource_generators = room_config.get("resource_generation", {})
        self.resource_consumers = room_config.get("resource_consumption", {})
        self.description = room_config.get("description", "")

        # Initialize resources
        self.resources: Dict[str, float] = {}

    def update(self, resource_manager=None):
        """Update room state and handle resources"""
        if resource_manager:
            # Handle resource generation
            for resource, rate in self.resource_generators.items():
                resource_manager.add_resource(resource, rate)

            # Handle resource consumption
            for resource, rate in self.resource_consumers.items():
                resource_manager.consume_resource(resource, rate)

    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is inside the room"""
        return (
            self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height
        )

    def get_center(self) -> Tuple[int, int]:
        """Get the center position of the room in world coordinates"""
        return (self.x + (self.width // 2), self.y + (self.height // 2))
