import pygame

from scenes.gameplay import GameplayScene
from scenes.menu_scene import MenuScene
from scenes.pause_scene import PauseScene
from scenes.prologue_scene import PrologueScene
from systems.scene_manager import SceneManager, SceneType


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.scene_manager = SceneManager()

        # Initialize scenes
        self.scene_manager.add_scene(SceneType.MAIN_MENU, MenuScene(self))
        self.scene_manager.add_scene(SceneType.PROLOGUE, PrologueScene(self))
        self.scene_manager.add_scene(SceneType.GAMEPLAY, GameplayScene(self))
        self.scene_manager.add_scene(SceneType.PAUSE, PauseScene(self))

        # Start with main menu
        self.scene_manager.set_scene(SceneType.MAIN_MENU)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Let current scene handle the event
            if self.scene_manager.current_scene:
                if self.scene_manager.current_scene.handle_event(event):
                    continue

            # Global ESC key handling for pause
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if isinstance(self.scene_manager.current_scene, GameplayScene):
                    self.scene_manager.set_scene(SceneType.PAUSE)
                elif isinstance(self.scene_manager.current_scene, PauseScene):
                    self.scene_manager.set_scene(SceneType.GAMEPLAY)

    def update(self):
        """Update game state"""
        self.scene_manager.update()

    def draw(self):
        self.scene_manager.draw(self.screen)
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()  # Make sure this is being called
            self.draw()
