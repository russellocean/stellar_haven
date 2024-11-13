import random
from typing import Dict, List, Tuple

import pygame

from entities.entity import Entity
from entities.generator import Generator
from systems.asset_manager import AssetManager


class Room(Entity):
    def __init__(
        self,
        room_type: str,
        grid_pos: Tuple[int, int],
        cell_size: int,
        resource_manager=None,
        grid=None,
        interaction_system=None,
    ):
        # Calculate world position from grid position
        x = grid_pos[0] * cell_size
        y = grid_pos[1] * cell_size

        # Store room properties
        self.room_type = room_type
        self.grid_pos = grid_pos
        self.cell_size = cell_size
        self.resource_manager = resource_manager
        self.grid = grid
        self.interaction_system = interaction_system

        # Load room config first
        self.asset_manager = AssetManager()
        room_config = self.asset_manager.get_config("rooms")["room_types"][room_type]

        # Set size based on grid size from config
        grid_size = room_config["grid_size"]
        self.width = grid_size[0] * cell_size
        self.height = grid_size[1] * cell_size

        # Initialize parent entity with calculated dimensions
        super().__init__(None, x, y)

        # Set name from config or use room type
        self.name = room_config.get("name", room_type.replace("_", " ").title())

        # Initialize room properties from config
        self.resource_generators = room_config.get("resource_generation", {})
        self.resource_consumers = room_config.get("resource_consumption", {})
        self.description = room_config.get("description", "")

        # Initialize resources
        self.resources: Dict[str, float] = {}

        # Add decorations and interactables tracking
        self.decorations: List[Entity] = []
        self.interactables: List[Entity] = []

        # Store interior positions
        self.interior_positions = []

        # Don't process decorations immediately
        self.decorations_config = room_config.get("decorations", {})

    def set_interior_positions(self, positions: List[Tuple[int, int]]):
        """Set valid interior positions for the room"""
        self.interior_positions = positions
        print(f"Set interior positions: {len(positions)} valid spots")  # Debug

        # Now process decorations after we have interior positions
        self._process_decorations(self.decorations_config)

    def _process_decorations(self, decorations_config: Dict):
        """Process all decorations and interactables from config"""
        if not self.grid:
            print("Warning: No grid system available!")
            return

        # Process each decoration
        for dec_name, config in decorations_config.items():
            if not config.get("required", False) and config.get("min_count", 0) == 0:
                continue

            # Get object size from tilemap config
            object_size = (1, 1)  # Default size
            if config.get("type") == "interactable":
                tilemap_data = self.asset_manager.get_tilemap_group(dec_name)
                if tilemap_data and "metadata" in tilemap_data:
                    object_size = (
                        tilemap_data["metadata"]["width"],
                        tilemap_data["metadata"]["height"],
                    )

            # Get valid positions for this specific object size
            available_positions = self.grid.get_interior_positions(
                room_id=next(
                    id
                    for id, r in self.grid.rooms.items()
                    if r["grid_pos"] == self.grid_pos
                ),
                object_size=object_size,
            )

            if not available_positions:
                print(
                    f"Warning: No valid positions for {dec_name} (size: {object_size})"
                )
                continue

            # Place the decorations
            count = random.randint(config["min_count"], config["max_count"])
            for i in range(count):
                if config.get("type") == "interactable":
                    if available_positions:
                        # Use first available position (center-most) instead of random
                        pos = available_positions[0]
                        world_x, world_y = self._grid_to_world(pos[0], pos[1])
                        self._place_interactable(dec_name, config, world_x, world_y)
                        # Remove used position
                        available_positions.remove(pos)

    def _place_interactable(self, name: str, config: Dict, x: int, y: int):
        """Place an interactable entity"""
        print(f"Placing interactable {name} at {x}, {y}")  # Debug

        entity = None
        if name == "generator":
            entity = Generator(x, y, self.resource_manager)
            print(f"Created generator entity: {entity}")  # Debug
        # Add more types as needed

        if entity and self.interaction_system:
            print(f"Adding {name} to interaction system")  # Debug
            self.interaction_system.add_interactable(entity)
            self.interactables.append(entity)
        else:
            print(
                f"Failed to add {name}: entity={entity}, interaction_system={self.interaction_system}"
            )  # Debug

    def _place_visual_decoration(self, name: str, config: Dict, x: int, y: int):
        """Place a visual decoration tile group"""
        if self.grid and "group_name" in config:
            grid_x, grid_y = self._world_to_grid(x, y)
            self.grid.place_tile_group(grid_x, grid_y, config["group_name"])

    def _get_valid_positions(self, position_types: List[str]) -> List[Tuple[int, int]]:
        """Get valid grid positions based on position types"""
        valid_positions = []
        room_width, room_height = (
            self.width // self.cell_size,
            self.height // self.cell_size,
        )

        # Iterate through all positions in room
        for y in range(room_height):
            for x in range(room_width):
                grid_x = self.grid_pos[0] + x
                grid_y = self.grid_pos[1] + y

                # Check each position type
                if "floor" in position_types and self._is_floor_position(x, y):
                    valid_positions.append((grid_x, grid_y))
                elif "wall" in position_types and self._is_wall_position(x, y):
                    valid_positions.append((grid_x, grid_y))
                elif "center" in position_types and self._is_center_position(x, y):
                    valid_positions.append((grid_x, grid_y))

        return valid_positions

    def _is_center_position(self, x: int, y: int) -> bool:
        """Check if position is in the center of the room"""
        room_width = self.width // self.cell_size
        room_height = self.height // self.cell_size

        # Define center area (middle 1/3 of room)
        center_x_start = room_width // 3
        center_x_end = (room_width * 2) // 3
        center_y_start = room_height // 3
        center_y_end = (room_height * 2) // 3

        return (
            center_x_start <= x <= center_x_end and center_y_start <= y <= center_y_end
        )

    def _is_wall_position(self, x: int, y: int) -> bool:
        """Check if position is along a wall"""
        room_width = self.width // self.cell_size
        room_height = self.height // self.cell_size

        # Check if position is along any wall but not in a corner
        is_horizontal_wall = (y == 0 or y == room_height - 1) and (
            0 < x < room_width - 1
        )
        is_vertical_wall = (x == 0 or x == room_width - 1) and (0 < y < room_height - 1)

        return is_horizontal_wall or is_vertical_wall

    def _is_floor_position(self, x: int, y: int) -> bool:
        """Check if position is on the floor just above the bottom wall"""
        room_width = self.width // self.cell_size
        room_height = self.height // self.cell_size

        # Position it one tile higher than before (room_height - 3 instead of room_height - 2)
        return y == room_height - 3 and 0 < x < room_width - 1

    def _grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """Convert grid coordinates to world coordinates"""
        return (grid_x * self.cell_size, grid_y * self.cell_size)

    def _world_to_grid(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates"""
        return (world_x // self.cell_size, world_y // self.cell_size)

    def _place_room_tiles(self, room_config: dict):
        """Place the visual tiles for the room"""
        # Place walls, floors, etc using the grid system
        if self.grid:
            for decoration in room_config.get("decorations", []):
                if "visual" in decoration:  # Only handle visual elements
                    self.grid.place_tile_group(
                        self.grid_pos[0] + decoration["offset_x"],
                        self.grid_pos[1] + decoration["offset_y"],
                        decoration["group_name"],
                    )

    def _place_interactables(self, interactables_config: List[dict]):
        """Place interactive elements in the room"""
        for config in interactables_config:
            # Calculate world position relative to room
            offset_x = config.get("offset_x", 0.5)  # Default to center
            offset_y = config.get("offset_y", 0.5)

            world_x = self.x + (self.width * offset_x)
            world_y = self.y + (self.height * offset_y)

            entity_type = config["type"]
            if entity_type == "generator":
                entity = Generator(world_x, world_y, self.resource_manager)
            # Add more types as needed
            # elif entity_type == "bed":
            #     entity = Bed(world_x, world_y)

            if entity and self.interaction_system:
                self.interaction_system.add_interactable(entity)

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

    def render(self, surface: pygame.Surface, camera):
        """Render room-specific elements"""
        # Draw decorations (non-interactable elements)
        for decoration in self.decorations:
            if hasattr(decoration, "render"):
                decoration.render(surface, camera)
            elif hasattr(decoration, "rect"):
                screen_pos = camera.world_to_screen(
                    decoration.rect.x, decoration.rect.y
                )
                surface.blit(decoration.image, screen_pos)

    def draw(self, surface: pygame.Surface):
        """Fallback draw method when no camera is available"""
        # Draw decorations
        for decoration in self.decorations:
            if hasattr(decoration, "draw"):
                decoration.draw(surface)
            elif hasattr(decoration, "rect"):
                surface.blit(decoration.image, decoration.rect)

        # Draw interactables
        for interactable in self.interactables:
            if hasattr(interactable, "draw"):
                interactable.draw(surface)
            elif hasattr(interactable, "rect"):
                surface.blit(interactable.image, interactable.rect)
