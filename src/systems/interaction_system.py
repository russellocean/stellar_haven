from typing import List, Tuple

import pygame

from entities.entity import Entity
from systems.camera import Camera
from systems.game_state_manager import GameState


class InteractionSystem:
    def __init__(self, camera: Camera, state_manager):
        self.camera = camera
        self.state_manager = state_manager
        self.interactables: List[Entity] = []
        self.hovered_entity = None  # Track currently hovered entity

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
        if self.state_manager.current_state != GameState.PLAYING:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for entity in self.interactables:
                if entity.is_hovered:
                    entity.interact()
                    return True
        return False

    def render(self, surface: pygame.Surface, camera):
        """Render all interactable entities"""
        for entity in self.interactables:
            if hasattr(entity, "render"):
                entity.render(surface, camera)
            elif hasattr(entity, "rect"):
                screen_pos = camera.world_to_screen(entity.rect.x, entity.rect.y)
                surface.blit(entity.image, screen_pos)

                # Draw hover effect
                if getattr(entity, "is_hovered", False):
                    highlight_rect = pygame.Rect(
                        *screen_pos, entity.rect.width, entity.rect.height
                    )
                    pygame.draw.rect(surface, (255, 255, 0), highlight_rect, 2)
