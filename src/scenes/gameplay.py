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
from systems.grid_renderer import GridRenderer
from systems.resource_manager import ResourceManager
from systems.room_manager import RoomManager
from ui.layouts.game_hud import GameHUD


class CelestialObject:
    def __init__(self, image, x, y, speed, scale=1.0, can_rotate=False):
        self.original_image = image
        self.scale = scale
        self.image = pygame.transform.scale(
            image, (int(image.get_width() * scale), int(image.get_height() * scale))
        )
        self.x = x
        self.y = y
        self.speed = speed
        self.can_rotate = can_rotate
        self.angle = random.randint(0, 360) if can_rotate else 0
        self.rotation_speed = random.uniform(-0.5, 0.5) if can_rotate else 0
        # Add parallax offset based on speed (slower = further back)
        self.parallax_factor = (
            speed * 0.1
        )  # Objects with higher speed will move more with camera

    def update(self):
        if self.can_rotate:
            self.angle += self.rotation_speed
            # Rotate the scaled image
            self.image = pygame.transform.rotate(
                pygame.transform.scale(
                    self.original_image,
                    (
                        int(self.original_image.get_width() * self.scale),
                        int(self.original_image.get_height() * self.scale),
                    ),
                ),
                self.angle,
            )


class Starfield:
    def __init__(self, screen_size):
        self.background = pygame.Surface(screen_size)
        self.background.fill((0, 0, 0))
        self.objects = []

        # Load sprite sheet
        spritesheet = pygame.image.load("assets/CelestialObjects.png").convert_alpha()

        # Extract sprites
        self.planets = [
            spritesheet.subsurface((i * 64, j * 64, 64, 64))
            for j in range(3)
            for i in range(4)
        ]
        self.moons = [
            spritesheet.subsurface((i * 32, 3 * 64, 32, 32)) for i in range(4)
        ]
        self.dwarf_stars = [
            spritesheet.subsurface((i * 32, 3 * 64 + 32, 32, 32)) for i in range(4)
        ]
        # Add fast-moving stars
        self.stars = [
            spritesheet.subsurface(((4 + i) * 32, 3 * 64 + 32, 32, 32))
            for i in range(4)
        ]

        self.create_celestial_objects()

        self.camera_x = 0
        self.camera_y = 0
        self.last_camera_x = 0
        self.last_camera_y = 0

    def create_celestial_objects(self):
        screen_w = self.background.get_width()
        screen_h = self.background.get_height()

        # Add fast-moving background stars (smallest, fastest)
        for _ in range(100):
            star = random.choice(self.stars)
            x = random.randint(0, screen_w)
            y = random.randint(-screen_h, screen_h)
            # 80% chance of slower speed, 20% chance of very fast speed
            if random.random() < 0.8:
                speed = random.uniform(1.5, 3.0)  # More common slower speed
            else:
                speed = random.uniform(6.0, 12.0)  # Rare but very fast
            self.objects.append(
                CelestialObject(star, x, y, speed, scale=0.4, can_rotate=True)
            )

        # Add planets (larger, slower, no rotation)
        for _ in range(5):
            planet = random.choice(self.planets)
            x = random.randint(0, screen_w)
            y = random.randint(-screen_h, screen_h)
            speed = random.uniform(0.1, 0.3)
            self.objects.append(
                CelestialObject(planet, x, y, speed, scale=0.8, can_rotate=False)
            )

        # Add moons (medium, medium speed, with rotation)
        for _ in range(8):
            moon = random.choice(self.moons)
            x = random.randint(0, screen_w)
            y = random.randint(-screen_h, screen_h)
            speed = random.uniform(0.3, 0.5)
            self.objects.append(
                CelestialObject(moon, x, y, speed, scale=1.0, can_rotate=True)
            )

        # Add dwarf stars (small, faster, with rotation)
        for _ in range(12):
            star = random.choice(self.dwarf_stars)
            x = random.randint(0, screen_w)
            y = random.randint(-screen_h, screen_h)
            speed = random.uniform(0.4, 0.6)
            self.objects.append(
                CelestialObject(star, x, y, speed, scale=0.7, can_rotate=True)
            )

    def update(self, camera_x=0, camera_y=0):
        screen_w = self.background.get_width()

        # Calculate camera movement delta
        dx = camera_x - self.last_camera_x
        dy = camera_y - self.last_camera_y

        for obj in self.objects:
            # Update horizontal position for scrolling
            obj.x += obj.speed
            if obj.x > screen_w:
                obj.x = -obj.image.get_width()

            # Apply parallax effect based on camera movement
            obj.x -= dx * obj.parallax_factor
            obj.y -= dy * obj.parallax_factor

            # Update rotation if applicable
            obj.update()

        # Store camera position for next frame
        self.last_camera_x = camera_x
        self.last_camera_y = camera_y

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        for obj in self.objects:
            # Center the rotated image at its position
            rect = obj.image.get_rect(center=(obj.x, obj.y))
            screen.blit(obj.image, rect)


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

        # Initialize grid renderer BEFORE setup_core_layers
        self.grid_renderer = GridRenderer(self.room_manager.grid)

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

        # Add grid renderer to game layer (before room sprites)
        self.game_layer.insert(0, self.grid_renderer)

    def _setup_core_layers(self):
        """Setup essential game layers"""
        # Create sprite groups
        self.character_sprites = pygame.sprite.Group(self.player)

        # Set camera for grid renderer
        self.grid_renderer.set_camera(self.camera)

        # Add elements to layers in drawing order
        self.background_layer.append(self.starfield)
        self.game_layer.extend([self.grid_renderer, self.character_sprites])
        self.system_layer.extend([self.building_system])
        self.ui_layer.append(self.game_hud)

        # Setup debug visualization
        self.room_manager.collision_system.set_camera(self.camera)
        self.debug_layer.append(self.room_manager.collision_system)

    def _init_building_system(self):
        """Initialize building system"""
        self.building_system = BuildingSystem(room_manager=self.room_manager)
        self.building_system.set_state_manager(self.state_manager)
        self.building_system.set_input_manager(self.input_manager)
        self.building_system.set_camera(self.camera)

        # Initialize UI elements with screen reference
        self.building_system.init_ui(self.game.screen)

        # Add to layers
        self.system_layer.append(self.building_system)

        # Add UI elements to UI system
        self.ui_system.add_element(self.building_system.toggle_button)
        self.ui_system.add_element(self.building_system.build_menu)

    def _init_player(self):
        # Get starting position from room manager
        player_x, player_y = self.room_manager.get_starting_position()
        self.player = Player(player_x, player_y)
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
        # self.room_sprites.update(resource_manager=self.resource_manager)
        # self.room_manager.update(self.resource_manager)
        self.starfield.update(self.camera.x, self.camera.y)
        self.game_hud.update()

        # Let building system handle its own toggle
        self.building_system.update()

        super().update()
        self.debug_system.clock.tick()

    def draw(self, screen):
        # Use the parent Scene's draw method which will handle all layers
        super().draw(screen)
