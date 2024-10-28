from entities.entity import Entity


class Room(Entity):
    def __init__(self, name: str, image_path: str, x: int, y: int):
        super().__init__(image_path, x, y)
        self.name = name
        self.resources = {}
        self.resource_generators = {}
        self.resource_consumers = {}
        self._initialize_room_properties()

    def _initialize_room_properties(self):
        """Initialize room-specific resources and rates"""
        if self.name == "engine_room":
            self.resource_generators["power"] = 0.5
            self.resource_consumers["oxygen"] = 0.2
        elif self.name == "life_support":
            self.resource_generators["oxygen"] = 0.3
            self.resource_consumers["power"] = 0.1
        elif self.name == "bridge":
            self.resource_consumers["power"] = 0.1
            self.resource_consumers["oxygen"] = 0.1

    def update(self, *args, **kwargs):
        """Update room resources if resource_manager is provided"""
        resource_manager = kwargs.get("resource_manager")
        if resource_manager:
            # Generate resources
            for resource, rate in self.resource_generators.items():
                resource_manager.add_resource(resource, rate)

            # Consume resources
            for resource, rate in self.resource_consumers.items():
                resource_manager.consume_resource(resource, rate)

    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is inside the room"""
        return self.rect.collidepoint(x, y)
