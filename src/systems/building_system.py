from typing import Tuple

import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager
from systems.debug_system import DebugSystem
from systems.event_system import GameEvent
from systems.game_state_manager import GameState
from systems.room_manager import RoomManager
from ui.components.button import Button
from ui.components.toggle_button import ToggleButton
from ui.layouts.build_menu import BuildMenu


class BuildingSystem:
    def __init__(self, room_manager: RoomManager, resource_manager, screen):
        self.room_manager = room_manager
        self.resource_manager = resource_manager
        self.asset_manager = AssetManager()
        self.grid = room_manager.grid
        self.active = False
        self.camera = None
        self.state_manager = None
        self.input_manager = None
        self.debug = DebugSystem()

        # Building state
        self.selected_category = None
        self.selected_type = None
        self.ghost_position = None
        self.valid_placement = False

        # Initialize UI elements right away
        self.init_ui(screen)

    def set_state_manager(self, state_manager):
        self.state_manager = state_manager
        self.state_manager.subscribe(GameState.BUILDING, self._handle_state_change)

    def set_input_manager(self, input_manager):
        self.input_manager = input_manager

    def set_camera(self, camera):
        self.camera = camera

    def select_build_item(self, category: str, item_type: str):
        """Select an item to build"""
        if category != self.selected_category:
            self.clear_selection()

        self.selected_category = category
        self.selected_type = item_type
        self.ghost_position = None
        self.valid_placement = False

    def toggle_building_mode(self):
        """Toggle building mode on/off"""
        if not hasattr(self, "build_menu") or self.build_menu is None:
            self.debug.log("Error: Build menu not initialized")
            return

        self.active = not self.active
        self.build_menu.visible = self.active

        if self.state_manager:
            new_state = GameState.BUILDING if self.active else GameState.PLAYING
            self.state_manager.set_state(new_state)

    def update(self):
        if not self.active or not self.selected_type:
            return

        mouse_pos = pygame.mouse.get_pos()
        world_pos = self.camera.screen_to_world(*mouse_pos)
        grid_x = world_pos[0] // self.grid.cell_size
        grid_y = world_pos[1] // self.grid.cell_size

        if self.selected_category == "rooms":
            # Center the room on cursor
            room_size = self.grid.room_config["room_types"][self.selected_type][
                "grid_size"
            ]
            grid_x -= room_size[0] // 2
            grid_y -= room_size[1] // 2
            self.valid_placement = self.grid.is_valid_room_placement(
                grid_x, grid_y, self.selected_type
            )
        elif self.selected_category == "platforms":
            # Center the platform horizontally
            grid_x -= 1  # Center 3-tile wide platform
            self.valid_placement = self.grid.is_valid_platform_placement(grid_x, grid_y)
        else:
            # Handle other tile groups
            group_name = self.selected_type
            if group_name in self.grid.tile_groups:
                group = self.grid.tile_groups[group_name]
                # Center the group on cursor
                grid_x -= group["width"] // 2
                self.valid_placement = self.grid.is_valid_group_placement(
                    grid_x, grid_y, group_name
                )
            else:
                self.valid_placement = self.grid.is_valid_tile_placement(grid_x, grid_y)

        self.ghost_position = (grid_x, grid_y)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle building-related events"""
        if not self.active or not self.selected_type:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.valid_placement and self.ghost_position:
                if self.selected_category == "rooms":
                    return self._place_room()
                else:
                    return self._place_item()
        return False

    def _place_room(self) -> bool:
        """Place a room at the ghost position"""
        room_id = f"room_{len(self.room_manager.rooms)}"
        success = self.room_manager.add_room(
            self.selected_type,
            self.ghost_position[0] * self.grid.cell_size,
            self.ghost_position[1] * self.grid.cell_size,
            room_id,
        )
        return success

    def _place_item(self) -> bool:
        """Place a non-room item at the ghost position"""
        if self.selected_category == "platforms":
            return self.grid.place_platform(
                self.ghost_position[0], self.ghost_position[1]
            )

        group_name = self.selected_type
        if group_name in self.grid.tile_groups:
            return self.grid.place_tile_group(
                self.ghost_position[0], self.ghost_position[1], group_name
            )
        else:
            # Handle single-tile items
            tile_type = TileType.EMPTY  # Default or determine based on category
            self.grid.set_tile(
                self.ghost_position[0], self.ghost_position[1], tile_type
            )
            return True

    def draw(self, screen: pygame.Surface):
        if not self.active or not self.selected_type or not self.ghost_position:
            return

        if self.selected_category == "rooms":
            self._draw_room_ghost(screen)
        elif self.selected_category == "structures":
            self._draw_door_ghost(screen)
        else:
            self._draw_item_ghost(screen)

    def _draw_room_ghost(self, screen: pygame.Surface):
        """Draw ghost for room placement"""
        room_size = self.grid.room_config["room_types"][self.selected_type]["grid_size"]
        width, height = room_size
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

    def _draw_item_ghost(self, screen: pygame.Surface):
        """Draw ghost for items (including platforms)"""
        world_x = self.ghost_position[0] * self.grid.cell_size
        world_y = self.ghost_position[1] * self.grid.cell_size

        if self.selected_category == "platforms":
            # Get platform texture from asset manager
            platform_data = self.asset_manager.get_tilemap_group("platform")
            if platform_data:
                ghost = platform_data["surface"].copy()
                if not self.valid_placement:
                    # Add red tint for invalid placement
                    tint = pygame.Surface(ghost.get_size(), pygame.SRCALPHA)
                    pygame.draw.rect(tint, (255, 0, 0, 128), tint.get_rect())
                    ghost.blit(tint, (0, 0))
            else:
                # Fallback if texture not found
                ghost = pygame.Surface(
                    (self.grid.cell_size * 3, self.grid.cell_size * 2), pygame.SRCALPHA
                )
                color = (100, 100, 100, 128)
                pygame.draw.rect(ghost, color, ghost.get_rect())
                if not self.valid_placement:
                    pygame.draw.rect(ghost, (255, 0, 0, 64), ghost.get_rect())

        else:
            # Original single-tile ghost drawing
            ghost = pygame.Surface(
                (self.grid.cell_size, self.grid.cell_size), pygame.SRCALPHA
            )
            color = (0, 255, 0, 128) if self.valid_placement else (255, 0, 0, 128)
            pygame.draw.rect(ghost, color, ghost.get_rect())

        screen_pos = self.camera.world_to_screen(world_x, world_y)
        screen.blit(ghost, screen_pos)

    def _draw_door_ghost(self, screen: pygame.Surface):
        """Draw ghost for door placement"""
        world_x = self.ghost_position[0] * self.grid.cell_size
        world_y = self.ghost_position[1] * self.grid.cell_size

        # Get door texture from asset manager
        door_data = self.asset_manager.get_tilemap_group(self.selected_type)
        if door_data:
            ghost = door_data["surface"].copy()
            if not self.valid_placement:
                # Add red tint for invalid placement
                tint = pygame.Surface(ghost.get_size(), pygame.SRCALPHA)
                pygame.draw.rect(tint, (255, 0, 0, 128), tint.get_rect())
                ghost.blit(tint, (0, 0))
        else:
            # Fallback if texture not found
            ghost = pygame.Surface(
                (self.grid.cell_size * 2, self.grid.cell_size * 3), pygame.SRCALPHA
            )
            color = (0, 255, 0, 128) if self.valid_placement else (255, 0, 0, 128)
            pygame.draw.rect(ghost, color, ghost.get_rect())

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
            self.selected_category = None
            self.selected_type = None
            self.ghost_position = None

    def init_ui(self, screen: pygame.Surface):
        """Initialize UI elements that need screen reference"""
        try:
            self.toggle_button = ToggleButton(
                rect=pygame.Rect(20, 20, 60, 60),
                text="Build",
                action=self.toggle_building_mode,
                image_path="assets/images/ui/build_icon.png",
            )

            self.build_menu = BuildMenu(
                screen=screen,
                room_manager=self.room_manager,
                on_select=self.select_build_item,
            )
            self.build_menu.visible = False  # Start hidden

            self.debug.log("Building system UI initialized successfully")
        except Exception as e:
            self.debug.log(f"Error initializing building system UI: {e}")
            raise

    def clear_selection(self):
        """Clear current building selection"""
        self.selected_category = None
        self.selected_type = None
        self.ghost_position = None
        self.valid_placement = False

        # Clear button states in build menu
        if self.build_menu:
            for element in self.build_menu.ui_system.elements:
                if isinstance(element, Button):
                    element.active = False

    def try_build_room(self, room_type: str, position: Tuple[int, int]) -> bool:
        """Attempt to build a room if resources are available"""
        # Get room costs from config
        room_config = self.room_manager.grid.room_config["room_types"][room_type]
        resource_costs = room_config.get("build_costs", {})

        # Check if we have enough resources
        for resource, cost in resource_costs.items():
            if self.resource_manager.resources[resource] < cost:
                self.debug.log(f"Not enough {resource} to build {room_type}")
                return False

        # Deduct resources if we can build
        if self.room_manager.add_room(room_type, position[0], position[1]):
            for resource, cost in resource_costs.items():
                self.resource_manager.resources[resource] -= cost
                self.resource_manager.event_system.emit(
                    GameEvent.RESOURCE_UPDATED,
                    resource=resource,
                    amount=self.resource_manager.resources[resource],
                )
            return True
        return False
