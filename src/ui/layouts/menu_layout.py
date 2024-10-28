import pygame

from systems.scene_manager import SceneManager, SceneType
from ui.components.button import Button
from ui.layouts.base_layout import BaseLayout


class MenuLayout(BaseLayout):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Initialize buttons
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        start_y = self.screen_height // 2 - 100

        # Store scene manager reference
        self.scene_manager = SceneManager()

        self.buttons = [
            Button(
                rect=pygame.Rect(button_x, start_y, button_width, button_height),
                text="Start Game",
                action=self._on_start_game,
                tooltip="Begin a new game",
            ),
            Button(
                rect=pygame.Rect(button_x, start_y + 70, button_width, button_height),
                text="Options",
                action=self._on_options,
                tooltip="Game settings",
            ),
            Button(
                rect=pygame.Rect(button_x, start_y + 140, button_width, button_height),
                text="Quit",
                action=self._on_quit,
                tooltip="Exit the game",
            ),
        ]

        # Title text
        self.title_font = pygame.font.Font(None, 74)
        self.title_text = self.title_font.render("Stellar Haven", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(
            centerx=self.screen_width // 2, centery=start_y - 100
        )

    def _on_start_game(self):
        """Handle start game button click"""
        print("Starting game...")  # Debug print
        self.scene_manager.set_scene(SceneType.GAMEPLAY)

    def _on_options(self):
        """Handle options button click"""
        self.scene_manager.set_scene(SceneType.OPTIONS)

    def _on_quit(self):
        """Handle quit button click"""
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_event(self, event):
        """Handle UI events"""
        for button in self.buttons:
            if button.handle_event(event):  # Use Button's built-in event handling
                return True
        return False

    def update(self):
        """Update menu elements"""
        for button in self.buttons:
            button.update()

    def draw(self, surface: pygame.Surface):
        """Draw menu elements"""
        # Draw background (could be more elaborate)
        surface.fill((0, 0, 20))

        # Draw title
        surface.blit(self.title_text, self.title_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
