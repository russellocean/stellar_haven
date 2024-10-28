import pygame


class Camera:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.offset_x = 0
        self.offset_y = 0

    def update(self, target_rect: pygame.Rect):
        """Update camera position to follow target"""
        # Center the camera on the target
        self.offset_x = target_rect.centerx - (self.width // 2)
        self.offset_y = target_rect.centery - (self.height // 2)

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Apply camera offset to a rectangle"""
        return pygame.Rect(
            rect.x - self.offset_x, rect.y - self.offset_y, rect.width, rect.height
        )
