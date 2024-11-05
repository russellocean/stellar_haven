import json
import os
from typing import Tuple

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

        self.ui.show()

    def setup_pygame(self):
        """Initialize Pygame components"""
        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size)
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
            self.current_tilemap = pygame.image.load(path).convert_alpha()
            self.tilemap_path = path
            self.selected_tiles = []
            return True
        except (pygame.error, FileNotFoundError) as e:
            QMessageBox.critical(self.ui, "Error", f"Failed to load tilemap: {e}")
            return False

    def save_config(self, filename: str):
        """Save current configuration to file"""
        if not self.current_tilemap:
            QMessageBox.warning(self.ui, "Warning", "No tilemap loaded")
            return

        config = {
            "tilemap": os.path.relpath(self.tilemap_path, AssetManager().asset_path),
            "tile_size": self.tile_size,
            "tiles": self.tile_configs,
        }

        try:
            config_path = os.path.join(AssetManager().config_path, filename)
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
            QMessageBox.information(
                self.ui, "Success", "Configuration saved successfully"
            )
        except Exception as e:
            QMessageBox.critical(self.ui, "Error", f"Failed to save configuration: {e}")

    def load_config(self, filename: str):
        """Load configuration from file"""
        try:
            config_path = os.path.join(AssetManager().config_path, filename)
            with open(config_path, "r") as f:
                config = json.load(f)

            # Load tilemap
            tilemap_path = os.path.join(AssetManager().asset_path, config["tilemap"])
            if self.load_tilemap(tilemap_path):
                self.tile_size = config["tile_size"]
                self.tile_configs = config["tiles"]
                self.ui.tile_size_input.setValue(self.tile_size)
                QMessageBox.information(
                    self.ui, "Success", "Configuration loaded successfully"
                )
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
            running = self.input_handler.handle_input()
            self.renderer.render()
            self.clock.tick(60)

        # Cleanup
        pygame.quit()
        self.ui.close()
