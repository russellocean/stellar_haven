import pygame

from scenes.scene import Scene
from systems.scene_manager import SceneManager, SceneType
from ui.components.button import Button


class PauseScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.setup_ui()

    def setup_ui(self):
        """Setup pause menu UI elements"""
        screen_width = self.game.screen.get_width()
        screen_height = self.game.screen.get_height()

        # Create semi-transparent background
        self.overlay = pygame.Surface((screen_width, screen_height))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(128)

        # Create buttons
        button_width = 200
        button_height = 50
        button_x = (screen_width - button_width) // 2
        start_y = screen_height // 2 - 100

        # Resume button
        self.resume_button = Button(
            rect=pygame.Rect(button_x, start_y, button_width, button_height),
            text="Resume",
            action=self.resume_game,
            tooltip="Return to game",
        )

        # Options button
        self.options_button = Button(
            rect=pygame.Rect(button_x, start_y + 70, button_width, button_height),
            text="Options",
            action=self.show_options,
            tooltip="Game settings",
        )

        # Main menu button
        self.menu_button = Button(
            rect=pygame.Rect(button_x, start_y + 140, button_width, button_height),
            text="Main Menu",
            action=self.return_to_menu,
            tooltip="Return to main menu",
        )

        # Add buttons to UI layer
        self.ui_layer.extend(
            [self.resume_button, self.options_button, self.menu_button]
        )

    def resume_game(self):
        """Resume the game"""
        SceneManager().set_scene(SceneType.GAMEPLAY)

    def show_options(self):
        """Show options menu"""
        SceneManager().set_scene(SceneType.OPTIONS)

    def return_to_menu(self):
        """Return to main menu"""
        SceneManager().set_scene(SceneType.MAIN_MENU)

    def handle_event(self, event):
        """Handle pause menu events"""
        # Handle ESC key to resume
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.resume_game()
            return True

        # Handle button events directly
        for element in self.ui_layer:
            if element.handle_event(event):
                return True

        return False

    def update(self):
        """Update pause menu state"""
        # Update UI elements
        for element in self.ui_layer:
            element.update()

    def draw(self, screen):
        # Draw the game scene in the background (if it exists)
        gameplay_scene = SceneManager().scenes.get(SceneType.GAMEPLAY)
        if gameplay_scene:
            gameplay_scene.draw(screen)

        # Draw semi-transparent overlay
        screen.blit(self.overlay, (0, 0))

        # Draw pause menu title
        font = pygame.font.Font(None, 74)
        title = font.render("Paused", True, (255, 255, 255))
        title_rect = title.get_rect(
            centerx=screen.get_width() // 2, centery=screen.get_height() // 3
        )
        screen.blit(title, title_rect)

        # Draw UI elements
        super().draw(screen)
