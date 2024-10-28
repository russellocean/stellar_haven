import pygame

from scenes.scene import Scene
from ui.layouts.menu_layout import MenuLayout


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.menu_layout = MenuLayout(game.screen)
        self.ui_layer.append(self.menu_layout)

    def handle_event(self, event):
        if super().handle_event(event):
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Handle menu navigation
                return True
        return self.menu_layout.handle_event(event)

    def update(self):
        """Update menu scene"""
        super().update()
        # Update menu layout
        self.menu_layout.update()

    def draw(self, screen):
        """Draw all layers in order"""
        self.menu_layout.draw(screen)
        super().draw(screen)
