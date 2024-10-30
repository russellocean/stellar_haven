import random

import pygame

from entities.player import Player
from input_manager import InputManager
from scenes.scene import Scene
from systems.asset_manager import AssetManager
from systems.building_system import BuildingSystem
from systems.camera import Camera
from systems.debug_system import DebugSystem
from systems.game_state_manager import GameState, GameStateManager
from systems.resource_manager import ResourceManager
from systems.room_manager import RoomManager
from ui.layouts.game_hud import GameHUD


class Starfield:
    def __init__(self, screen_size):
        self.background = pygame.Surface(screen_size)
        self.background.fill((0, 0, 0))
        self.stars = []
        self.create_stars(100)

    def create_stars(self, num_stars):
        for _ in range(num_stars):
            x = random.randint(0, self.background.get_width())
            y = random.randint(0, self.background.get_height())
            self.stars.append([x, y])

    def update(self):
        for star in self.stars:
            star[1] += 1
            if star[1] > self.background.get_height():
                star[1] = 0

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        for star in self.stars:
            pygame.draw.circle(screen, (255, 255, 255), star, 1)


class GameplayScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.input_manager = InputManager()
        self.resource_manager = ResourceManager()
        self.state_manager = GameStateManager()

        # Add camera
        self.camera = Camera(game.screen.get_width(), game.screen.get_height())

        # Initialize core systems
        screen_center_x = game.screen.get_width() // 2
        screen_center_y = game.screen.get_height() // 2
        self.room_manager = RoomManager(screen_center_x, screen_center_y)

        # Initialize asset manager and preload room assets
        self.asset_manager = AssetManager()
        self.asset_manager.preload_images("images/rooms")

        # Setup core game elements
        self.starfield = Starfield(game.screen.get_size())
        self._init_player()

        # Initialize GameHUD with resource manager
        self.game_hud = GameHUD(game.screen, self.resource_manager)

        # Initialize building system before setting up layers
        self._init_building_system()

        # Setup layers after all systems are initialized
        self._setup_core_layers()

        # Initialize debug system
        self.debug_system = DebugSystem()

        # Add some useful debug watches
        self.debug_system.add_watch("Room Count", lambda: len(self.room_manager.rooms))
        self.debug_system.add_watch(
            "Power", lambda: f"{self.resource_manager.resources['power']:.1f}"
        )
        self.debug_system.add_watch(
            "Oxygen", lambda: f"{self.resource_manager.resources['oxygen']:.1f}"
        )

        # Add debug system to debug layer
        self.debug_layer.append(self.debug_system)

    def _setup_core_layers(self):
        """Setup essential game layers"""
        # Create sprite groups
        self.room_sprites = self.room_manager.room_sprites
        self.character_sprites = pygame.sprite.Group(self.player)

        # Add elements to layers in drawing order
        self.background_layer.append(self.starfield)
        self.game_layer.extend([self.room_sprites, self.character_sprites])
        self.system_layer.extend([self.building_system])
        self.ui_layer.append(self.game_hud)

        # Setup debug visualization
        self.room_manager.collision_system.set_camera(self.camera)
        self.debug_layer.append(self.room_manager.collision_system)

    def _init_building_system(self):
        """Initialize optional building system"""
        self.building_system = BuildingSystem(
            screen=self.game.screen, room_manager=self.room_manager
        )
        self.building_system.set_state_manager(self.state_manager)
        self.building_system.set_input_manager(self.input_manager)
        self.building_system.set_camera(self.camera)

        # Add to layers if initialized
        self.system_layer.append(self.building_system)

        # Add UI elements
        self.ui_system.add_element(self.building_system.toggle_button)
        self.ui_system.add_element(self.building_system.build_menu)

    def _init_player(self):
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

    def handle_event(self, event):
        # Scene's UI system handles events first
        if super().handle_event(event):
            return True

        # Handle input manager events
        action = self.input_manager.handle_event(event)
        if action == "toggle_build":
            self.building_system.toggle_building_mode()
            return True

        # Handle building system events if active
        if self.state_manager.current_state == GameState.BUILDING:
            if self.building_system.handle_event(event):
                return True

        # Add debug toggle (F3 key)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            self.debug_system.toggle()
            return True

        return False

    def update(self):
        # Update input first
        self.input_manager.update()

        # Update camera to follow player
        self.camera.update(self.player.rect)

        # Core game updates
        self.player.update(self.room_manager, self.input_manager)
        self.room_sprites.update(resource_manager=self.resource_manager)
        # self.room_manager.update(self.resource_manager)
        self.starfield.update()
        self.game_hud.update()

        # Let building system handle its own toggle
        self.building_system.update()

        super().update()
        self.debug_system.clock.tick()

    def draw(self, screen):
        # Use the parent Scene's draw method which will handle all layers
        super().draw(screen)
