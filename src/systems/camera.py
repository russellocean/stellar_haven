import pygame


class Camera:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.target = None

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Convert a rect from world space to screen space"""
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

    def world_to_screen(self, world_x: int, world_y: int) -> tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = world_x - self.x
        screen_y = world_y - self.y
        return (screen_x, screen_y)

    def screen_to_world(self, screen_x: int, screen_y: int) -> tuple[int, int]:
        """Convert screen coordinates to world coordinates"""
        world_x = screen_x + self.x
        world_y = screen_y + self.y
        return (world_x, world_y)

    def update(self, target_rect: pygame.Rect):
        """Update camera position to follow target"""
        # Center the camera on the target
        self.x = target_rect.centerx - self.width // 2
        self.y = target_rect.centery - self.height // 2
