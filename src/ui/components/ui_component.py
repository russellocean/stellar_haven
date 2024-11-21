from typing import Optional, Tuple

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
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        self.is_pressed = False

        # Initialize base colors
        self.colors = {
            "normal": (100, 100, 100),
            "hover": (150, 150, 150),
            "text": (255, 255, 255),
            "text_hover": (255, 255, 255),
            "border": (200, 200, 200),
        }

        # Load image if provided
        self.image = None
        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()

        # Text setup
        self._render_text()

    def _render_text(self):
        """Pre-render text (like React's useMemo)"""
        self.text_surface = self.font.render(self.text, True, self.colors["text"])
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self):
        """Update component state"""
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle UI events"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
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

    def _get_current_color(self) -> Tuple[int, int, int]:
        """Get the current color based on state"""
        if self.is_hovered:
            return self.colors["hover"]
        return self.colors["normal"]

    def _get_text_color(self) -> Tuple[int, int, int]:
        """Get the current text color"""
        if self.is_hovered:
            return self.colors["text_hover"]
        return self.colors["text"]
