import pygame
from scenes.gameplay import GameplayScene


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.scenes = {"gameplay": GameplayScene(self)}
        self.current_scene = self.scenes["gameplay"]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            self.current_scene.handle_event(event)

    def update(self):
        self.current_scene.update()

    def draw(self):
        self.current_scene.draw(self.screen)
