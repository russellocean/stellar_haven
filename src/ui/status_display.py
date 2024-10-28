import pygame


class StatusDisplay:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen, resource_manager):
        y_offset = 10
        for resource, value in resource_manager.resources.items():
            text = f"{resource}: {value:.1f}"
            surface = self.font.render(text, True, (255, 255, 255))
            screen.blit(surface, (10, y_offset))
            y_offset += 30
