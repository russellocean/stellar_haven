import random

import pygame

from entities.player import Player
from entities.player_ship import PlayerShip
from input_manager import InputManager
from scenes.scene import Scene


class GameplayScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.input_manager = InputManager()
        # Center the ship on the screen
        self.player_ship = PlayerShip(
            game.screen.get_width() // 2, game.screen.get_height() // 2
        )
        # Start the player in the middle of the ship
        self.player = Player(
            game.screen.get_width() // 2, game.screen.get_height() // 2
        )

        self.all_sprites = pygame.sprite.Group(self.player_ship, self.player)
        self.background = pygame.Surface(game.screen.get_size())
        self.background.fill((0, 0, 0))
        self.stars = self.create_starfield(100)

    def create_starfield(self, num_stars):
        stars = []
        for _ in range(num_stars):
            x = random.randint(0, self.background.get_width())
            y = random.randint(0, self.background.get_height())
            stars.append((x, y))
        return stars

    def update(self):
        self.input_manager.update()
        self.all_sprites.update(self.player_ship, self.input_manager)
        self.scroll_starfield()

    def scroll_starfield(self):
        for i, star in enumerate(self.stars):
            x, y = star
            y += 1
            if y > self.background.get_height():
                y = 0
            self.stars[i] = (x, y)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        for star in self.stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 1)
        self.all_sprites.draw(screen)
