import pygame

from systems.asset_manager import AssetManager
from systems.event_system import EventSystem
from systems.scene_manager import SceneManager, SceneType
from ui.components.button import Button
from ui.layouts.base_layout import BaseLayout


class MenuLayout(BaseLayout):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Load background image
        self.asset_manager = AssetManager()
        background = self.asset_manager.get_image(
            "main_menu/Stellar_Haven_Main_Menu_Background.png"
        )
        if background:
            # Calculate scaling while maintaining aspect ratio
            bg_aspect = background.get_width() / background.get_height()
            screen_aspect = self.screen_width / self.screen_height

            if screen_aspect > bg_aspect:  # Screen is wider than background
                new_height = self.screen_height
                new_width = int(new_height * bg_aspect)
            else:  # Screen is taller than background
                new_width = self.screen_width
                new_height = int(new_width / bg_aspect)

            self.background = pygame.transform.scale(
                background, (new_width, new_height)
            )
            # Calculate position to center the background
            self.background_rect = self.background.get_rect()
            self.background_rect.center = (
                self.screen_width // 2,
                self.screen_height // 2,
            )
        else:
            self.background = None
            print("Failed to load background image")

        # Initialize buttons
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        start_y = self.screen_height // 2 - 100

        # Store scene manager reference
        self.scene_manager = SceneManager()

        # Add event system reference
        self.event_system = EventSystem()

        self.buttons = [
            Button(
                rect=pygame.Rect(button_x, start_y, button_width, button_height),
                text="Start Game",
                action=self._on_start_game,
                tooltip="Begin your journey",
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

        # Replace title text with logo image
        logo = self.asset_manager.get_image("main_menu/logo.png")
        if logo:
            # Scale logo while maintaining aspect ratio
            logo_scale = 2.0  # Adjust this value to make logo bigger/smaller
            logo_width = int(logo.get_width() * logo_scale)
            logo_height = int(logo.get_height() * logo_scale)

            self.title_image = pygame.transform.scale(logo, (logo_width, logo_height))
            self.title_rect = self.title_image.get_rect(
                centerx=self.screen_width // 2,
                bottom=start_y - 20,  # Position above the buttons
            )
        else:
            print("Failed to load logo image")
            # Fallback to text if logo fails to load
            self.title_font = pygame.font.Font(None, 74)
            self.title_image = self.title_font.render(
                "Stellar Haven", True, (255, 255, 255)
            )
            self.title_rect = self.title_image.get_rect(
                centerx=self.screen_width // 2, centery=start_y - 100
            )

    def _on_start_game(self):
        """Handle start game button click"""
        # Change to prologue scene instead of gameplay
        self.scene_manager.set_scene(SceneType.PROLOGUE)

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
        # Fill with black first
        surface.fill((0, 0, 0))

        # Draw background if loaded
        if self.background:
            surface.blit(self.background, self.background_rect)
        else:
            surface.fill((0, 0, 20))

        # Draw logo/title
        surface.blit(self.title_image, self.title_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
