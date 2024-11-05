import pygame


class Camera:
    def __init__(self, width: int, height: int, tile_size: int = 16):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.target = None
        self.tile_size = tile_size

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

    def get_visible_area(self):
        """Return a pygame.Rect representing the visible area in world coordinates"""
        return pygame.Rect(
            self.x // self.tile_size,
            self.y // self.tile_size,
            (self.width // self.tile_size)
            + 2,  # Add buffer for partially visible tiles
            (self.height // self.tile_size) + 2,
        )
