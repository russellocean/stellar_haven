import json
import os
from typing import List, Optional, Tuple

import pygame
from PyQt5.QtWidgets import QMessageBox

from systems.asset_manager import AssetManager
from tools.tilemap_helper.input_handler import InputHandler
from tools.tilemap_helper.renderer import TilemapRenderer
from tools.tilemap_helper.ui import TilemapUI


class TilemapHelper:
    def __init__(self, qt_app, window_size: Tuple[int, int] = (1920, 1080)):
        self.qt_app = qt_app
        self.window_size = window_size

        # Initialize subsystems
        self.setup_pygame()
        self.setup_state()

        # Create UI and subsystems
        self.ui = TilemapUI(self)
        self.renderer = TilemapRenderer(self)
        self.input_handler = InputHandler(self)

        # Load previous state
        self.load_state()

        self.ui.show()

    def setup_pygame(self):
        """Initialize Pygame components"""
        pygame.init()
        self.screen = pygame.display.set_mode(
            self.window_size, pygame.RESIZABLE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Tilemap Helper")
        self.clock = pygame.time.Clock()

    def setup_state(self):
        """Initialize state variables"""
        # Tilemap state
        self.current_tilemap = None
        self.tilemap_path = None
        self.tile_size = 32
        self.selected_tiles = []
        self.tile_configs = {}
        self.tile_types = [
            "ground",
            "wall",
            "decoration",
            "planet",
            "star",
            "door",
            "floor",
            "window",
            "furniture",
        ]  # Default types

        # View state
        self.grid_visible = True
        self.zoom_level = 1.0
        self.scroll_offset = [0, 0]
        self.dragging = False
        self.last_mouse_pos = None

        # Multi-tile state
        self.multi_tile_width = 1
        self.multi_tile_height = 1

        # Transform state
        self.scale = 1.0
        self.scaled_size = (0, 0)
        self.image_pos = (0, 0)
        self.scaled_tile_size = self.tile_size

    def load_tilemap(self, path: str) -> bool:
        """Load a tilemap from file"""
        try:
            new_tilemap = pygame.image.load(path).convert_alpha()

            # If load successful, reset state
            self.current_tilemap = new_tilemap
            self.tilemap_path = path
            self.selected_tiles = []
            self.tile_configs = {}  # Clear existing configurations

            # Reset view
            self.zoom_level = 1.0
            self.scroll_offset = [0, 0]
            self.dragging = False
            self.last_mouse_pos = None

            # Reset multi-tile state
            self.multi_tile_width = 1
            self.multi_tile_height = 1

            # Automatically load configuration for this tilemap
            self.load_config("tilemap_config.json")

            return True
        except (pygame.error, FileNotFoundError) as e:
            QMessageBox.critical(self.ui, "Error", f"Failed to load tilemap: {e}")
            return False

    def save_config(self, filename: str):
        """Save current configuration to file"""
        if not hasattr(self, "tilemap_configs"):
            print("No config to save")
            return

        try:
            print(f"Saving config to {AssetManager().config_path}/{filename}")
            config_path = os.path.join(AssetManager().config_path, filename)
            with open(config_path, "w") as f:
                json.dump(self.tilemap_configs, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self.ui, "Error", f"Failed to save configuration: {e}")

    def load_config(self, filename: str):
        """Load configuration from file"""
        try:
            config_path = os.path.join(AssetManager().config_path, filename)

            # Create default config if file doesn't exist
            if not os.path.exists(config_path):
                default_config = {"global": {"tile_types": self.tile_types}}
                # Ensure config directory exists
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                # Write default config
                with open(config_path, "w") as f:
                    json.dump(default_config, f, indent=4)
                self.tilemap_configs = default_config
                return

            # Load existing config
            with open(config_path, "r") as f:
                self.tilemap_configs = json.load(f)

            # Load global tile types if they exist
            if "global" in self.tilemap_configs:
                self.tile_types = self.tilemap_configs["global"].get(
                    "tile_types", self.tile_types
                )
                self.ui.update_tile_types(self.tile_types)

            # Update tile_configs for current tilemap
            if self.tilemap_path:
                rel_path = os.path.relpath(self.tilemap_path, AssetManager().asset_path)
                if rel_path in self.tilemap_configs:
                    # Load tile size from config
                    self.tile_size = self.tilemap_configs[rel_path].get("tile_size", 16)
                    self.ui.tile_size_input.setValue(self.tile_size)  # Update UI

                    # Load tile configurations
                    self.tile_configs.clear()
                    for group in self.tilemap_configs[rel_path]["groups"]:
                        for tile in group["tiles"]:
                            self.tile_configs[str((tile["x"], tile["y"]))] = group[
                                "metadata"
                            ]
        except Exception as e:
            QMessageBox.critical(self.ui, "Error", f"Failed to load configuration: {e}")

    def set_multi_tile_size(self, width: int, height: int):
        """Set the size for multi-tile selections"""
        self.multi_tile_width = width
        self.multi_tile_height = height

    def _update_transform(self):
        """Update all transformation calculations for the current frame"""
        if not self.current_tilemap:
            return

        # Calculate the scaling factor to fit the image to the screen
        image_width = self.current_tilemap.get_width()
        image_height = self.current_tilemap.get_height()

        # Calculate scaling factors for both dimensions
        scale_x = self.window_size[0] / image_width
        scale_y = self.window_size[1] / image_height

        # Use the smaller scaling factor to ensure the image fits
        self.scale = min(scale_x, scale_y) * self.zoom_level

        # Calculate the scaled dimensions
        self.scaled_size = (
            int(image_width * self.scale),
            int(image_height * self.scale),
        )

        # Calculate position to center the image
        self.image_pos = (
            (self.window_size[0] - self.scaled_size[0]) // 2 + self.scroll_offset[0],
            (self.window_size[1] - self.scaled_size[1]) // 2 + self.scroll_offset[1],
        )

        # Calculate scaled tile size
        self.scaled_tile_size = int(self.tile_size * self.scale)

    def _adjust_zoom(self, factor: float):
        """Adjust zoom level"""
        new_zoom = self.zoom_level * factor
        if 0.25 <= new_zoom <= 4.0:
            self.zoom_level = new_zoom

    def run(self):
        """Main application loop"""
        running = True
        while running:
            # Process events and update
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                self.input_handler.handle_event(event)

            # Process Qt events
            self.qt_app.processEvents()

            # Render and maintain framerate
            self.renderer.render()
            self.clock.tick(60)

        # Save state before cleanup
        self.save_state()
        pygame.quit()
        self.ui.close()

    def get_tile_config(self, pos: Tuple[int, int]) -> Optional[dict]:
        """Get configuration for a tile position"""
        return self.tile_configs.get(str(pos))

    def add_tile_group(self, tiles: List[Tuple[int, int]], metadata: dict):
        """Add a new tile group to the configuration"""
        if not self.tilemap_path:
            return

        # Create config entry for this tilemap if it doesn't exist
        if not hasattr(self, "tilemap_configs"):
            self.tilemap_configs = {}

        # Get relative path for the tilemap
        rel_path = os.path.relpath(self.tilemap_path, AssetManager().asset_path)

        # Initialize config for this tilemap if needed
        if rel_path not in self.tilemap_configs:
            self.tilemap_configs[rel_path] = {"tile_size": self.tile_size, "groups": []}

        # Add the new tile group
        tile_group = {
            "tiles": [{"x": x, "y": y} for x, y in tiles],
            "metadata": metadata,
        }

        self.tilemap_configs[rel_path]["groups"].append(tile_group)

        # Update the tile_configs for rendering
        for tile_pos in tiles:
            self.tile_configs[str(tile_pos)] = metadata

        # Auto-save the configuration
        self.save_config("tilemap_config.json")

    def save_state(self):
        """Save current application state"""
        state = {
            "last_file": self.tilemap_path,
            "grid_visible": self.grid_visible,
            "tile_size": self.tile_size,
            "zoom_level": self.zoom_level,
            "scroll_offset": self.scroll_offset,
            "window_position": (self.ui.pos().x(), self.ui.pos().y()),
            "window_size": (self.ui.size().width(), self.ui.size().height()),
        }

        try:
            state_path = os.path.join(
                AssetManager().config_path, "tilemap_helper_state.json"
            )
            with open(state_path, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Failed to save state: {e}")

    def load_state(self):
        """Load previous application state"""
        try:
            state_path = os.path.join(
                AssetManager().config_path, "tilemap_helper_state.json"
            )
            if os.path.exists(state_path):
                with open(state_path, "r") as f:
                    state = json.load(f)

                # Restore window state
                self.ui.resize(
                    state.get("window_size", (250, 400))[0],
                    state.get("window_size", (250, 400))[1],
                )
                self.ui.move(
                    state.get("window_position", (100, 100))[0],
                    state.get("window_position", (100, 100))[1],
                )

                # Restore view state
                self.grid_visible = state.get("grid_visible", True)
                self.zoom_level = state.get("zoom_level", 1.0)
                self.scroll_offset = state.get("scroll_offset", [0, 0])

                # Restore tile size
                self.tile_size = state.get("tile_size", 32)
                self.ui.tile_size_input.setValue(self.tile_size)

                # Load last opened file
                last_file = state.get("last_file")
                if last_file and os.path.exists(last_file):
                    self.load_tilemap(last_file)

        except Exception as e:
            print(f"Failed to load state: {e}")

    def save_tile_types(self, types: list):
        """Save tile types to configuration"""
        if not hasattr(self, "tilemap_configs"):
            self.tilemap_configs = {}

        # Add/update global tile types
        self.tilemap_configs["global"] = {"tile_types": types}
        self.tile_types = types

        # Ensure config directory exists
        os.makedirs(
            os.path.dirname(
                os.path.join(AssetManager().config_path, "tilemap_config.json")
            ),
            exist_ok=True,
        )

        # Save to file
        self.save_config("tilemap_config.json")
