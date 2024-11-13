import pygame

from entities.entity import Entity
from systems.asset_manager import AssetManager


class Generator(Entity):
    def __init__(self, x: int, y: int, resource_manager=None):
        super().__init__(None, x, y)

        # Load generator sprite
        self.asset_manager = AssetManager()
        generator_data = self.asset_manager.get_tilemap_group("generator")
        self.image = generator_data["surface"]
        self.rect = self.image.get_rect(center=(x, y))

        # Store resource manager reference
        self.resource_manager = resource_manager
        self.power_per_crank = 10

        # Make it interactable
        self.is_interactable = True
        self.interaction_callback = self.crank_generator
        self.interaction_range = 50

        # Add tooltip info
        self.name = "Hand Crank Generator"
        self.description = f"Click to generate {self.power_per_crank} power"

    def crank_generator(self):
        """Called when player interacts with generator"""
        if self.resource_manager:
            print(f"Adding {self.power_per_crank} power")  # Debug print
            self.resource_manager.add_resource("power", self.power_per_crank)
            self.show_feedback(f"+{self.power_per_crank} Power", (255, 255, 0))
        else:
            print("No resource manager!")  # Debug print

    def render(self, surface: pygame.Surface, camera):
        """Render the generator with camera offset"""
        screen_pos = camera.world_to_screen(self.rect.x, self.rect.y)
        surface.blit(self.image, screen_pos)

        # Draw hover effect
        if self.is_hovered:
            hover_rect = pygame.Rect(*screen_pos, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, (255, 255, 0), hover_rect, 2)

        # Use parent's feedback rendering
        self.render_feedback(surface, screen_pos)
