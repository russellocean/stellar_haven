import pygame

from entities.player import Player
from input_manager import InputManager
from scenes.scene import Scene
from systems.ai_system import AISystem
from systems.asset_manager import AssetManager
from systems.building_system import BuildingSystem
from systems.camera import Camera
from systems.debug_system import DebugSystem
from systems.dialog_system import DialogEntry, DialogSystem
from systems.game_state_manager import GameState, GameStateManager
from systems.grid_renderer import GridRenderer
from systems.interaction_system import InteractionSystem
from systems.resource_manager import ResourceManager
from systems.room_manager import RoomManager
from systems.starfield_system import StarfieldSystem
from ui.layouts.game_hud import GameHUD


class GameplayScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self._init_managers()
        self._init_systems()
        self._init_entities()
        self._init_ui()
        self._setup_debug()
        self._setup_layers()

        # Initialize dialog system for tutorial
        self.dialog_system = DialogSystem()
        self.dialog_system.initialize(game.screen)
        self._start_tutorial_sequence()

    def _init_managers(self):
        """Initialize all manager systems"""
        self.input_manager = InputManager()
        self.state_manager = GameStateManager()
        self.asset_manager = AssetManager()
        self.asset_manager.preload_images("images/rooms")

        # Initialize resource manager first
        self.resource_manager = ResourceManager()
        # Add custom resource configurations if needed
        self._setup_resource_config()

    def _setup_resource_config(self):
        """Setup custom resource configurations"""
        # Example: Modify base consumption rates
        self.resource_manager.base_consumption_rates.update(
            {
                "power": 0.05,  # Slower power drain
                "oxygen": 0.03,  # Slower oxygen consumption
            }
        )

        # Example: Modify maximum resource amounts
        self.resource_manager.max_resources.update(
            {
                "power": 200.0,  # Larger power capacity
                "oxygen": 150.0,  # Larger oxygen capacity
            }
        )

    def _init_systems(self):
        """Initialize core game systems"""
        # Create camera first
        self.camera = Camera(
            self.game.screen.get_width(), self.game.screen.get_height(), tile_size=16
        )

        # Create interaction system with camera
        self.interaction_system = InteractionSystem(self.camera, self.state_manager)

        # Create room manager with interaction system
        self.room_manager = RoomManager(
            self.game.screen.get_width() // 2,
            self.game.screen.get_height() // 2,
            resource_manager=self.resource_manager,
            interaction_system=self.interaction_system,
        )
        self.room_manager.set_camera(self.camera)

        self.grid_renderer = GridRenderer(self.room_manager.grid)
        self.starfield = StarfieldSystem(self.game.screen.get_size())

        # Initialize building system properly
        self.building_system = BuildingSystem(
            self.room_manager, self.resource_manager, self.game.screen
        )
        self.building_system.set_state_manager(self.state_manager)
        self.building_system.set_input_manager(self.input_manager)
        self.building_system.set_camera(self.camera)
        self.building_system.init_ui(self.game.screen)  # Initialize UI elements

        self.ai_system = AISystem(self.room_manager, self.room_manager.collision_system)
        self.ai_system.set_camera(self.camera)

    def _init_entities(self):
        # Get starting position from room manager
        player_x, player_y = self.room_manager.get_starting_position()
        self.player = Player(player_x, player_y)
        self.character_sprites = pygame.sprite.Group(self.player)
        # Set camera reference for player debug visualization
        self.player.camera = self.camera

    def _init_ui(self):
        # Initialize GameHUD with resource manager
        self.game_hud = GameHUD(self.game.screen, self.resource_manager)

        # Add building system UI elements to the scene's UI system
        if hasattr(self, "ui_system"):
            self.ui_system.add_element(self.building_system.toggle_button)
            self.ui_system.add_element(self.building_system.build_menu)

    def _setup_debug(self):
        """Setup debug system and watches"""
        self.debug_system = DebugSystem()
        self._add_debug_watches()

    def _add_debug_watches(self):
        """Add debug watches for monitoring game state"""
        # Add resource-related watches
        self.debug_system.add_watch(
            "Power Generation", lambda: f"{self._get_resource_rate('power'):+.2f}/s"
        )
        self.debug_system.add_watch(
            "Oxygen Generation", lambda: f"{self._get_resource_rate('oxygen'):+.2f}/s"
        )
        self.debug_system.add_watch(
            "Active Rooms", lambda: len(self.resource_manager.active_rooms)
        )

    def _get_resource_rate(self, resource: str) -> float:
        """Helper to calculate current resource generation/consumption rate"""
        return self.resource_manager._calculate_net_resource_change(resource)

    def _setup_layers(self):
        """Setup rendering layers"""
        # Background layer
        self.background_layer = [self.starfield]

        # Game layer - order matters!
        self.game_layer = [
            self.grid_renderer,  # Draw tiles first
            self.room_manager,  # Draw rooms and interactables
            self.ai_system,  # Draw AI characters
            self.character_sprites,  # Draw player on top
        ]

        # System layer
        self.system_layer = [self.building_system]

        # UI layer
        self.ui_layer = [self.game_hud]

        # Setup camera references
        self.grid_renderer.set_camera(self.camera)

        # Add elements to layers in drawing order
        self.background_layer.append(self.starfield)
        self.game_layer.extend(
            [self.grid_renderer, self.room_manager, self.character_sprites]
        )
        self.system_layer.extend([self.building_system])
        self.ui_layer.append(self.game_hud)

        # Setup debug visualization
        self.room_manager.collision_system.set_camera(self.camera)
        self.debug_layer = [
            self.debug_system,
            self.room_manager.collision_system,
            self.ai_system,
        ]

        # Add player to both game and debug layers
        # self.game_layer.append(self.player)
        self.debug_layer.append(self.player)

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

        # Handle interaction system events
        if self.interaction_system.handle_event(event):
            return True

        # Add debug toggle (F3 key)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            self.debug_system.toggle()
            return True

        return False

    def update(self):
        """Update scene state"""
        # Get delta time
        dt = self.debug_system.clock.get_time() / 1000.0  # Convert to seconds

        # Update all interactable entities
        if self.interaction_system:
            for entity in self.interaction_system.interactables:
                entity.update(dt)  # This updates feedback timers

        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Update interaction system with mouse position
        self.interaction_system.update(mouse_pos)

        # Update input first
        self.input_manager.update()

        # Update camera to follow player
        self.camera.update(self.player.rect)

        # Update resource system with delta time
        dt = self.debug_system.clock.get_time() / 1000.0  # Convert to seconds
        self.resource_manager.update(dt)

        # Core game updates
        self.player.update(self.room_manager, self.input_manager)
        self.ai_system.update(dt)
        self.starfield.update(self.camera.x, self.camera.y)
        self.game_hud.update()

        # Let building system handle its own toggle
        self.building_system.update()

        super().update()
        self.debug_system.clock.tick()
        self.dialog_system.update()

    def draw(self, screen):
        # Use the parent Scene's draw method which will handle all layers
        super().draw(screen)
        # Draw dialog on top of everything
        self.dialog_system.draw(screen)

    def _start_tutorial_sequence(self):
        """Start the tutorial dialog sequence (Scenes 5-7)"""
        initial_dialog = [
            # Scene 5: Boarding Your Ship
            DialogEntry(
                character="MAX",
                text="There she is—the 'Starbreeze'! Isn't she a beauty? Sleek, efficient, and... compact. Perfect for someone who values simplicity. And hey, less space means fewer places for things to go wrong, right?",
            ),
            DialogEntry(
                character="MAX",
                text="Now, I know what you're thinking: 'Didn't he promise me a state-of-the-art vessel?' Think of this as... a hands-on opportunity. After all, what's a journey without a few challenges? You'll be fine! Probably.",
            ),
            # Scene 6: Stepping Inside
            DialogEntry(
                character="EVA",
                text="Greetings, Overseer. Welcome aboard the 'Starbreeze'—NovaForge's finest example of minimalism in space travel.",
            ),
            DialogEntry(
                character="EVA",
                text="Current status report: Battery reserves at 20% and depleting. Oxygen levels are sufficient for approximately... 2 hours and 47 minutes. Recommend immediate attention to life support systems—unless, of course, you're practicing for a record in breath-holding.",
            ),
            # Scene 7: Assessing the Situation
            DialogEntry(
                character="EVA",
                text="You'll notice the battery unit is flashing red—a universally recognized sign of 'bad.' Perhaps you might consider recharging it? There's a hand-crank generator stored under your cot. Manual labor builds character, or so I've been told.",
            ),
        ]

        later_dialog = [
            # Scene 8: Max's Message
            DialogEntry(
                character="MAX",
                text="Hey there, just wanted to check in! How's the 'Starbreeze' treating you? I imagine you're settling in nicely. Now, I won't keep you long—I know you're eager to get started. Just remember: the journey of a thousand light-years begins with a single step... or in your case, a single room. Cheers!",
            ),
            # Scene 9: The First Build
            DialogEntry(
                character="EVA",
                text="Overseer, while the 'Starbreeze' offers the charm of compact living, expanding the ship might increase our survival prospects. I recommend constructing a generator room to stabilize power or an oxygen garden for sustainable air supply.",
            ),
            DialogEntry(
                character="EVA",
                text="Please note, our current materials are limited. Choose wisely—or don't. I'm merely an AI with a vested interest in not floating aimlessly through space.",
            ),
        ]

        # Start initial dialog sequence - remove the callback
        self.dialog_system.start_dialog_sequence(initial_dialog)

        # Schedule the later dialog sequence to start after 60 seconds
        self.dialog_system.schedule_dialog_sequence(later_dialog, delay=30)
