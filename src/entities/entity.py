import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y):
        super().__init__()
        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
        else:
            # Create an empty surface if no image path is provided
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, *args, **kwargs):
        pass
