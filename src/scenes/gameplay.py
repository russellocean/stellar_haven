import random

import pygame

from entities.player import Player
from input_manager import InputManager
from scenes.scene import Scene
from systems.building_system import BuildingSystem
from systems.resource_manager import ResourceManager
from systems.room_manager import RoomManager


class GameplayScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.input_manager = InputManager()
        self.resource_manager = ResourceManager()

        # Initialize room manager with ship interior at center of screen
        screen_center_x = game.screen.get_width() // 2
        screen_center_y = game.screen.get_height() // 2
        self.room_manager = RoomManager(screen_center_x, screen_center_y)
        self.building_system = BuildingSystem(game.screen, self.room_manager)

        # Start the player in the middle of the ship interior
        ship_room = self.room_manager.ship_room
        player_x = ship_room.rect.left + (ship_room.rect.width // 2)
        player_y = ship_room.rect.top + (ship_room.rect.height // 2)
        print(
            f"Spawning player at {player_x}, {player_y} in ship room {ship_room.rect}"
        )
        self.player = Player(player_x, player_y)

        # Create sprite groups in order of drawing
        self.room_sprites = self.room_manager.room_sprites
        self.character_sprites = pygame.sprite.Group(self.player)

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

    def handle_event(self, event):
        self.building_system.handle_event(event)

    def update(self):
        self.input_manager.update()
        self.building_system.update()

        if not self.building_system.building_mode:
            # Normal gameplay updates
            self.player.update(self.room_manager, self.input_manager)
            self.room_sprites.update(resource_manager=self.resource_manager)

        self.room_manager.update(self.resource_manager)
        self.scroll_starfield()

    def scroll_starfield(self):
        for i, star in enumerate(self.stars):
            x, y = star
            y += 1
            if y > self.background.get_height():
                y = 0
            self.stars[i] = (x, y)

    def draw(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))
        for star in self.stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 1)

        # Draw all sprite layers
        self.room_sprites.draw(screen)  # This includes the ship interior
        self.character_sprites.draw(screen)

        # Draw building UI
        self.building_system.draw()
