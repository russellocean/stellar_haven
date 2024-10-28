from typing import Callable, Dict, List

import pygame


class DebugSystem:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DebugSystem, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.enabled = False
        self.watches: Dict[str, Callable] = {}
        self.logs: List[str] = []
        self.font = pygame.font.Font(None, 24)
        self.show_fps = True
        self.show_position = True
        self.clock = pygame.time.Clock()

    def toggle(self):
        """Toggle debug overlay"""
        self.enabled = not self.enabled
        print(f"Debug overlay {'enabled' if self.enabled else 'disabled'}")

    def add_watch(self, name: str, callback: Callable):
        """Add a value to watch in debug overlay"""
        self.watches[name] = callback

    def remove_watch(self, name: str):
        """Remove a watched value"""
        if name in self.watches:
            del self.watches[name]

    def log(self, message: str):
        """Add a message to debug log"""
        timestamp = pygame.time.get_ticks()
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > 10:  # Keep last 10 logs
            self.logs.pop(0)

    def clear_logs(self):
        """Clear all debug logs"""
        self.logs.clear()

    def draw(self, surface: pygame.Surface, player=None, camera=None):
        """Draw debug information"""
        if not self.enabled:
            return

        y = 10
        x = 10

        # Draw FPS
        if self.show_fps:
            fps = int(self.clock.get_fps())
            fps_text = f"FPS: {fps}"
            fps_surface = self.font.render(fps_text, True, (255, 255, 0))
            surface.blit(fps_surface, (x, y))
            y += 25

        # Draw player position if available
        if self.show_position and player and camera:
            screen_pos = camera.apply(player.rect).center
            world_pos = player.rect.center
            pos_text = f"Screen: {screen_pos}, World: {world_pos}"
            pos_surface = self.font.render(pos_text, True, (255, 255, 0))
            surface.blit(pos_surface, (x, y))
            y += 25

        # Draw watches
        for name, callback in self.watches.items():
            try:
                value = callback()
                text = f"{name}: {value}"
                text_surface = self.font.render(text, True, (255, 255, 0))
                surface.blit(text_surface, (x, y))
                y += 25
            except Exception as e:
                print(f"Error in debug watch '{name}': {e}")

        # Draw logs
        y += 10  # Add some space before logs
        for log in self.logs:
            text_surface = self.font.render(log, True, (255, 255, 0))
            surface.blit(text_surface, (x, y))
            y += 25
