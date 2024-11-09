from typing import Optional

import pygame

from systems.asset_manager import AssetManager


class DialogBox:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.asset_manager = AssetManager()

        # Dialog box dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        self.box_height = 200
        self.box_width = screen_width - 40
        self.box_rect = pygame.Rect(
            20, screen_height - self.box_height - 20, self.box_width, self.box_height
        )

        # Portrait dimensions
        self.portrait_size = 150
        self.portrait_rect = pygame.Rect(
            40, self.box_rect.top + 25, self.portrait_size, self.portrait_size
        )

        # Text properties
        self.font = pygame.font.Font(None, 32)
        self.text_color = (255, 255, 255)
        self.text_margin = 200  # Space after portrait
        self.line_spacing = 35

        # Current dialog state
        self.current_text = ""
        self.current_portrait: Optional[pygame.Surface] = None
        self.is_visible = False

        # Character portraits
        self.portraits = {
            "MAX": self.asset_manager.get_image(
                "portraits/Stellar_Haven_Maxwell_Portrait.png"
            ),
            "EVA": self.asset_manager.get_image(
                "portraits/Stellar_Haven_EVA_Portrait.png"
            ),
        }

    def show_dialog(self, character: str, text: str):
        """Show a dialog with the specified character and text"""
        self.current_text = text
        self.current_portrait = self.portraits.get(character.upper())
        self.is_visible = True

    def hide_dialog(self):
        """Hide the dialog box"""
        self.is_visible = False

    def draw(self, surface: pygame.Surface):
        """Draw the dialog box if visible"""
        if not self.is_visible:
            return

        # Draw semi-transparent background
        s = pygame.Surface((self.box_width, self.box_height))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        surface.blit(s, self.box_rect)

        # Draw border
        pygame.draw.rect(surface, (255, 255, 255), self.box_rect, 2)

        # Draw portrait if available
        if self.current_portrait:
            scaled_portrait = pygame.transform.scale(
                self.current_portrait, (self.portrait_size, self.portrait_size)
            )
            surface.blit(scaled_portrait, self.portrait_rect)

        # Draw text
        text_x = self.portrait_rect.right + 20
        text_y = self.box_rect.top + 25

        # Word wrap the text
        words = self.current_text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            text_surface = self.font.render(
                " ".join(current_line), True, self.text_color
            )
            if text_surface.get_width() > self.box_width - self.text_margin:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, self.text_color)
            surface.blit(text_surface, (text_x, text_y + i * self.line_spacing))
