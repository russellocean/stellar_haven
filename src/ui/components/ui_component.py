from typing import Dict, Optional

import pygame


class UIComponent:
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        image_path: Optional[str] = None,
        font_size: int = 24,
    ):
        self.rect = rect
        self.text = text

        # Common state
        self.is_hovered = False
        self.is_pressed = False
        self.is_active = False

        # Common styles (like Tailwind classes)
        self.colors: Dict[str, tuple] = {
            "normal": (100, 100, 100),
            "hovered": (150, 150, 150),
            "active": (200, 200, 200),
            "text": (255, 255, 255),
            "border": (50, 50, 50),
        }

        # Load image if provided
        self.image = None
        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(
                self.image, (self.rect.width - 10, self.rect.height - 10)
            )

        # Text setup
        self.font = pygame.font.Font(None, font_size)
        self._render_text()

    def _render_text(self):
        """Pre-render text (like React's useMemo)"""
        self.text_surface = self.font.render(self.text, True, self.colors["text"])
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Base event handling (like React's event handlers)"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return self.is_hovered
        return False

    def draw(self, surface: pygame.Surface):
        """Base render method (like React's render)"""
        # Get current style based on state
        color = self._get_current_color()

        # Draw background
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, self.colors["border"], self.rect, 2)

        # Draw image if available
        if self.image:
            image_rect = self.image.get_rect(center=self.rect.center)
            surface.blit(self.image, image_rect)

        # Draw text
        surface.blit(self.text_surface, self.text_rect)

    def _get_current_color(self) -> tuple:
        """Get color based on current state (like Tailwind's conditional classes)"""
        if self.is_active:
            return self.colors["active"]
        elif self.is_hovered:
            return self.colors["hovered"]
        return self.colors["normal"]
