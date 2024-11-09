import pygame

from scenes.gameplay import GameplayScene
from scenes.menu_scene import MenuScene
from scenes.pause_scene import PauseScene
from scenes.prologue_scene import PrologueScene
from systems.event_system import EventSystem, GameEvent
from systems.scene_manager import SceneManager, SceneType


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.scene_manager = SceneManager()
        self.event_system = EventSystem()

        # Subscribe to game state changes and prologue completion
        self.event_system.subscribe(
            GameEvent.GAME_STATE_CHANGED, self._on_game_state_changed
        )
        self.event_system.subscribe(
            GameEvent.PROLOGUE_COMPLETED, self._on_prologue_completed
        )

        # Initialize only the necessary starting scenes
        self.scene_manager.add_scene(SceneType.MAIN_MENU, MenuScene(self))
        self.scene_manager.add_scene(SceneType.PROLOGUE, PrologueScene(self))

        # Start with main menu
        self.scene_manager.set_scene(SceneType.MAIN_MENU)

    def _on_prologue_completed(self, event_data):
        """Handle prologue completion by creating and switching to gameplay scene"""
        # Create gameplay scene only when needed
        self.scene_manager.add_scene(SceneType.GAMEPLAY, GameplayScene(self))
        self.scene_manager.set_scene(SceneType.GAMEPLAY)

    def _on_game_state_changed(self, event_data):
        """Handle game state changes"""
        new_state = event_data.data.get("new_state")
        if new_state == "RESET":
            # Clear existing scenes and recreate necessary ones
            self.scene_manager.clear_scene(SceneType.GAMEPLAY)
            self.scene_manager.clear_scene(SceneType.PROLOGUE)
            # Recreate prologue scene
            self.scene_manager.add_scene(SceneType.PROLOGUE, PrologueScene(self))
            self.scene_manager.set_scene(SceneType.PROLOGUE)

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
