import asyncio
from enum import Enum, auto
from typing import Dict, Optional

import pygame

from scenes.scene import Scene
from systems.debug_system import DebugSystem


class SceneType(Enum):
    MAIN_MENU = auto()
    PROLOGUE = auto()
    GAMEPLAY = auto()
    PAUSE = auto()
    OPTIONS = auto()
    LOADING = auto()


class SceneManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SceneManager, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.scenes: Dict[SceneType, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.previous_scene: Optional[Scene] = None
        self.transition_alpha = 0
        self.is_transitioning = False
        self.debug = DebugSystem()

        # Add debug watches
        self.debug.add_watch(
            "Current Scene",
            lambda: (
                self.current_scene.__class__.__name__ if self.current_scene else None
            ),
        )
        self.debug.add_watch("Is Transitioning", lambda: self.is_transitioning)

    def add_scene(self, scene_type: SceneType, scene: Scene):
        """Register a scene"""
        self.scenes[scene_type] = scene

    def set_scene(self, scene_type: SceneType):
        """Immediately switch to a scene"""
        if scene_type not in self.scenes:
            self.debug.log(f"Scene {scene_type} not found!")
            return

        # Call on_exit for previous scene if it exists
        if self.current_scene and hasattr(self.current_scene, "on_exit"):
            self.current_scene.on_exit()

        self.previous_scene = self.current_scene
        self.current_scene = self.scenes[scene_type]

        # Call on_enter for new scene if it exists
        if hasattr(self.current_scene, "on_enter"):
            self.current_scene.on_enter()

        self.debug.log(f"Switched to scene: {scene_type}")

    async def transition_to(self, scene_type: SceneType):
        """Smoothly transition to a scene"""
        if scene_type not in self.scenes:
            self.debug.log(f"Scene {scene_type} not found!")
            return

        self.is_transitioning = True
        transition_surface = pygame.Surface(pygame.display.get_surface().get_size())
        transition_surface.fill((0, 0, 0))

        # Fade out
        for alpha in range(0, 255, 5):
            self.transition_alpha = alpha
            transition_surface.set_alpha(alpha)
            if self.current_scene:
                self.current_scene.draw(pygame.display.get_surface())
            pygame.display.get_surface().blit(transition_surface, (0, 0))
            pygame.display.flip()
            await asyncio.sleep(0.01)

        # Call on_exit for previous scene
        if self.current_scene and hasattr(self.current_scene, "on_exit"):
            self.current_scene.on_exit()

        self.previous_scene = self.current_scene
        self.current_scene = self.scenes[scene_type]

        # Call on_enter for new scene
        if hasattr(self.current_scene, "on_enter"):
            self.current_scene.on_enter()

        # Fade in
        for alpha in range(255, 0, -5):
            self.transition_alpha = alpha
            transition_surface.set_alpha(alpha)
            self.current_scene.draw(pygame.display.get_surface())
            pygame.display.get_surface().blit(transition_surface, (0, 0))
            pygame.display.flip()
            await asyncio.sleep(0.01)

        self.is_transitioning = False
        self.debug.log(f"Transitioned to scene: {scene_type}")

    def update(self):
        """Update current scene"""
        if self.current_scene and not self.is_transitioning:
            self.current_scene.update()

    def draw(self, screen: pygame.Surface):
        """Draw current scene"""
        if self.current_scene:
            self.current_scene.draw(screen)

    def clear_scene(self, scene_type: SceneType):
        """Remove a scene from the manager"""
        if scene_type in self.scenes:
            del self.scenes[scene_type]
            if self.current_scene == self.scenes.get(scene_type):
                self.current_scene = None
