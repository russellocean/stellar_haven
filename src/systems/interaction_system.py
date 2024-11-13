from typing import List, Tuple

import pygame

from entities.entity import Entity
from systems.camera import Camera


class InteractionSystem:
    def __init__(self, camera: Camera, state_manager):
        self.camera = camera
        self.state_manager = state_manager
        self.interactables: List[Entity] = []
        self.hovered_entity = None  # Track currently hovered entity
        self.font = pygame.font.Font(None, 24)

    def add_interactable(self, entity: Entity):
        """Register an interactable entity"""
        if entity.is_interactable:
            self.interactables.append(entity)

    def remove_interactable(self, entity: Entity):
        """Unregister an interactable entity"""
        if entity in self.interactables:
            self.interactables.remove(entity)

    def update(self, mouse_pos: Tuple[int, int]):
        """Update hover states based on mouse position"""
        # Convert screen mouse position to world coordinates
        world_pos = self.camera.screen_to_world(*mouse_pos)

        # Reset previous hover states
        if self.hovered_entity:
            self.hovered_entity.is_hovered = False
            self.hovered_entity = None

        # Check each interactable
        for entity in self.interactables:
            if entity.rect.collidepoint(world_pos):
                entity.is_hovered = True
                self.hovered_entity = entity
                break

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle interaction input"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check each interactable
            for entity in self.interactables:
                if entity.is_hovered:
                    if hasattr(entity, "interaction_callback"):
                        entity.interaction_callback()
                        return True
        return False

    def render(self, surface: pygame.Surface, camera):
        """Render all interactable entities and their tooltips"""
        for entity in self.interactables:
            if hasattr(entity, "render"):
                entity.render(surface, camera)

                if entity.is_hovered:
                    # Get screen position
                    screen_pos = camera.world_to_screen(entity.rect.x, entity.rect.y)

                    # Draw tooltip
                    if hasattr(entity, "name") and hasattr(entity, "description"):
                        # Create tooltip text surfaces with anti-aliasing
                        name_surface = self.font.render(
                            entity.name, True, (255, 255, 255)
                        )
                        desc_surface = self.font.render(
                            entity.description, True, (200, 200, 200)
                        )  # Slightly dimmer for description

                        # Calculate tooltip dimensions
                        padding = 8  # Increased padding
                        margin = 4  # Internal margin between texts
                        tooltip_width = max(
                            name_surface.get_width(), desc_surface.get_width()
                        ) + (padding * 2)
                        tooltip_height = (
                            name_surface.get_height()
                            + desc_surface.get_height()
                            + (padding * 2)
                            + margin
                        )

                        # Create background with alpha
                        tooltip_bg = pygame.Surface(
                            (tooltip_width, tooltip_height), pygame.SRCALPHA
                        )
                        background_color = (40, 40, 40, 230)  # Dark gray with alpha
                        pygame.draw.rect(
                            tooltip_bg,
                            background_color,
                            tooltip_bg.get_rect(),
                            border_radius=4,
                        )

                        # Add a subtle border
                        border_color = (100, 100, 100, 255)  # Light gray border
                        pygame.draw.rect(
                            tooltip_bg,
                            border_color,
                            tooltip_bg.get_rect(),
                            width=1,
                            border_radius=4,
                        )

                        # Position tooltip above entity
                        tooltip_x = (
                            screen_pos[0]
                            + (entity.rect.width // 2)
                            - (tooltip_width // 2)
                        )
                        tooltip_y = screen_pos[1] - tooltip_height - 8
                        # Draw background
                        surface.blit(tooltip_bg, (tooltip_x, tooltip_y))

                        # Draw name and description
                        surface.blit(
                            name_surface, (tooltip_x + padding, tooltip_y + padding)
                        )
                        surface.blit(
                            desc_surface,
                            (
                                tooltip_x + padding,
                                tooltip_y
                                + padding
                                + name_surface.get_height()
                                + margin,
                            ),
                        )
