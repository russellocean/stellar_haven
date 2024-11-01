import pygame

from systems.game_state_manager import GameState
from systems.room_manager import RoomManager
from ui.components.toggle_button import ToggleButton
from ui.layouts.build_menu import BuildMenu


class BuildingSystem:
    def __init__(self, room_manager: RoomManager):
        self.room_manager = room_manager
        self.grid = room_manager.grid
        self.active = False
        self.camera = None
        self.state_manager = None
        self.input_manager = None

        # Building state
        self.selected_room_type = None
        self.ghost_position = None
        self.valid_placement = False

        # UI elements will be initialized later
        self.toggle_button = None
        self.build_menu = None

    def set_state_manager(self, state_manager):
        self.state_manager = state_manager
        self.state_manager.subscribe(GameState.BUILDING, self._handle_state_change)

    def set_input_manager(self, input_manager):
        self.input_manager = input_manager

    def set_camera(self, camera):
        self.camera = camera

    def select_room_type(self, room_type: str):
        self.selected_room_type = room_type
        self.ghost_position = None
        self.valid_placement = False

    def toggle_building_mode(self):
        self.active = not self.active
        self.build_menu.visible = self.active
        if self.state_manager:
            new_state = GameState.BUILDING if self.active else GameState.PLAYING
            self.state_manager.set_state(new_state)

    def update(self):
        if not self.active or not self.selected_room_type:
            return

        # Get mouse position in world coordinates
        mouse_pos = pygame.mouse.get_pos()
        world_pos = self.camera.screen_to_world(*mouse_pos)

        # Convert to grid coordinates
        grid_x = world_pos[0] // self.grid.cell_size
        grid_y = world_pos[1] // self.grid.cell_size

        # Center the room on cursor
        room_size = self.grid.room_config["room_types"][self.selected_room_type][
            "grid_size"
        ]
        grid_x -= room_size[0] // 2
        grid_y -= room_size[1] // 2

        # Update placement state
        self.ghost_position = (grid_x, grid_y)
        self.valid_placement = self.grid.is_valid_room_placement(
            grid_x, grid_y, self.selected_room_type
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle building-related events"""
        if not self.active or not self.selected_room_type:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.valid_placement and self.ghost_position:
                print(f"Placing room at {self.ghost_position}")  # Debug print

                # Generate room ID
                room_id = f"room_{len(self.room_manager.rooms)}"

                # Add room through room manager
                success = self.room_manager.add_room(
                    self.selected_room_type,
                    self.ghost_position[0] * self.grid.cell_size,
                    self.ghost_position[1] * self.grid.cell_size,
                    room_id,
                )

                if success:
                    print(f"Room placed successfully: {room_id}")  # Debug print
                    return True
                else:
                    print("Room placement failed")  # Debug print
            else:
                print(
                    f"Invalid placement: valid={self.valid_placement}, pos={self.ghost_position}"
                )
        return False

    def draw(self, screen: pygame.Surface):
        if not self.active or not self.selected_room_type or not self.ghost_position:
            return

        room_size = self.grid.room_config["room_types"][self.selected_room_type][
            "grid_size"
        ]
        width, height = room_size
        grid_x, grid_y = self.ghost_position

        # Create ghost surface
        world_width = width * self.grid.cell_size
        world_height = height * self.grid.cell_size
        ghost = pygame.Surface((world_width, world_height), pygame.SRCALPHA)

        # Draw each tile type with different colors but same opacity
        opacity = 128
        for dx in range(width):
            for dy in range(height):
                tile_x = dx * self.grid.cell_size
                tile_y = dy * self.grid.cell_size
                tile_rect = pygame.Rect(
                    tile_x, tile_y, self.grid.cell_size, self.grid.cell_size
                )

                # Determine tile type based on position (similar to _add_room_tiles logic)
                if dx in (0, width - 1) and dy in (0, height - 1):
                    # Corners
                    color = (255, 255, 0, opacity)  # Yellow for corners
                elif dx in (0, width - 1) or dy in (0, height - 1):
                    # Walls
                    color = (128, 128, 128, opacity)  # Gray for walls
                elif dy == height - 2:
                    # Floor
                    color = (0, 255, 255, opacity)  # Cyan for floor
                else:
                    # Background
                    color = (50, 50, 50, opacity)  # Dark gray for background

                pygame.draw.rect(ghost, color, tile_rect)

        # Apply red tint if invalid placement
        if not self.valid_placement:
            tint = pygame.Surface((world_width, world_height), pygame.SRCALPHA)
            pygame.draw.rect(tint, (255, 0, 0, 64), tint.get_rect())
            ghost.blit(tint, (0, 0))

        # Draw ghost at world position
        world_x = self.ghost_position[0] * self.grid.cell_size
        world_y = self.ghost_position[1] * self.grid.cell_size
        screen_pos = self.camera.world_to_screen(world_x, world_y)
        screen.blit(ghost, screen_pos)

    def _handle_state_change(self, event_data: dict):
        """Handle game state changes"""
        new_state = event_data["new_state"]  # Access dictionary directly
        if new_state == GameState.BUILDING:
            self.active = True
            self.build_menu.visible = True
        else:
            self.active = False
            self.build_menu.visible = False
            self.selected_room_type = None
            self.ghost_position = None

    def init_ui(self, screen: pygame.Surface):
        """Initialize UI elements that need screen reference"""
        self.toggle_button = ToggleButton(
            rect=pygame.Rect(20, 20, 60, 60),
            text="Build",
            action=self.toggle_building_mode,
            image_path="assets/images/ui/build_icon.png",
        )
        self.build_menu = BuildMenu(
            screen=screen,
            room_manager=self.room_manager,
            on_select=self.select_room_type,
        )
