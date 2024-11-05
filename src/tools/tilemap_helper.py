import json
import os
from typing import Dict, List, Optional, Tuple

import pygame
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDockWidget,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from systems.asset_manager import AssetManager


class TilemapUI(QMainWindow):
    def __init__(self, tilemap_helper):
        super().__init__()
        self.helper = tilemap_helper
        self.setWindowTitle("Tilemap Helper Controls")

        # Create dock widget
        dock = QDockWidget("Controls", self)
        dock.setFeatures(
            QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable
        )

        # Create widget to hold controls
        controls = QWidget()
        layout = QVBoxLayout()

        # Toggle Grid Button
        grid_btn = QPushButton("Toggle Grid")
        grid_btn.clicked.connect(self.toggle_grid)
        layout.addWidget(grid_btn)
        layout.addWidget(QLabel("Hotkey: G"))

        # Save Config Button
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)
        layout.addWidget(QLabel("Hotkey: Ctrl+S"))

        # Load Config Button
        load_btn = QPushButton("Load Configuration")
        load_btn.clicked.connect(self.load_config)
        layout.addWidget(load_btn)
        layout.addWidget(QLabel("Hotkey: Ctrl+L"))

        # Navigation hints
        layout.addWidget(QLabel("\nNavigation:"))
        layout.addWidget(QLabel("Left Click: Select/deselect tiles"))
        layout.addWidget(QLabel("Middle Click + Drag: Pan view"))
        layout.addWidget(QLabel("Mouse Wheel: Zoom in/out"))

        # Add stretch to push everything to the top
        layout.addStretch()

        controls.setLayout(layout)
        dock.setWidget(controls)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        # Set a reasonable size and position for the UI window
        self.resize(250, 400)
        self.move(100, 100)

    def toggle_grid(self):
        self.helper.grid_visible = not self.helper.grid_visible

    def save_config(self):
        self.helper.save_config("tilemap_config.json")

    def load_config(self):
        self.helper.load_config("tilemap_config.json")


class TilemapHelper:
    def __init__(self, qt_app, window_size: Tuple[int, int] = (1920, 1080)):
        # Store the existing QApplication
        self.qt_app = qt_app

        # Initialize Pygame
        pygame.init()
        self.window_size = window_size
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Tilemap Helper")

        # Create UI window
        self.ui = TilemapUI(self)
        self.ui.show()

        self.asset_manager = AssetManager()
        self.clock = pygame.time.Clock()

        # Tilemap properties
        self.current_tilemap: Optional[pygame.Surface] = None
        self.tilemap_path: Optional[str] = None
        self.tile_size: int = 32
        self.grid_visible: bool = True

        # Selection and editing
        self.selected_tiles: List[Tuple[int, int]] = []
        self.current_metadata: Dict = {}
        self.tile_configs: Dict = {}

        # UI state
        self.scroll_offset = [0, 0]
        self.zoom_level = 1.0
        self.dragging = False
        self.last_mouse_pos = None

        # Add new properties for cached calculations
        self.scale = 1.0
        self.scaled_size = (0, 0)
        self.image_pos = (0, 0)
        self.scaled_tile_size = self.tile_size

    def load_tilemap(self, path: str) -> bool:
        """Load a tilemap image"""
        try:
            print(f"Attempting to load tilemap from: {path}")
            # Try to load the image directly first
            try:
                self.current_tilemap = pygame.image.load(path)
            except pygame.error:
                # If direct loading fails, try through asset manager
                self.current_tilemap = self.asset_manager.get_image(path)

            if self.current_tilemap is None:
                print("Failed to load tilemap: Image is None")
                return False

            print(
                f"Tilemap loaded successfully. Size: {self.current_tilemap.get_size()}"
            )
            self.tilemap_path = path
            self.scroll_offset = [0, 0]  # Reset view
            return True
        except Exception as e:
            print(f"Failed to load tilemap: {e}")
            return False

    def save_config(self, filename: str):
        """Save the current tile configurations"""
        config = {
            "tilemap": self.tilemap_path,
            "tile_size": self.tile_size,
            "tiles": self.tile_configs,
        }

        config_path = os.path.join(self.asset_manager.config_path, filename)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    def load_config(self, filename: str):
        """Load existing tile configurations"""
        config = self.asset_manager.get_config(filename)
        if config:
            self.tile_configs = config.get("tiles", {})
            self.tile_size = config.get("tile_size", 32)
            if config.get("tilemap"):
                self.load_tilemap(config["tilemap"])

    def handle_input(self):
        """Handle user input"""
        # Process PyQt events
        self.qt_app.processEvents()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_selection(event.pos)
                elif event.button == 2:  # Middle click
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                elif event.button == 4:  # Mouse wheel up
                    self._adjust_zoom(1.1)
                elif event.button == 5:  # Mouse wheel down
                    self._adjust_zoom(0.9)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:  # Middle click release
                    self.dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self._handle_drag(event.pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    self.grid_visible = not self.grid_visible
                elif event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                    self.save_config("tilemap_config.json")
                elif event.key == pygame.K_l and event.mod & pygame.KMOD_CTRL:
                    self.load_config("tilemap_config.json")

        return True

    def _handle_selection(self, pos: Tuple[int, int]):
        """Handle tile selection"""
        if not self.current_tilemap:
            return

        # Convert screen position to tilemap position
        rel_x = pos[0] - self.image_pos[0]
        rel_y = pos[1] - self.image_pos[1]

        # Convert to tile coordinates
        tile_x = int(rel_x / self.scaled_tile_size)
        tile_y = int(rel_y / self.scaled_tile_size)

        # Check if the click is within the image bounds
        max_tiles_x = self.current_tilemap.get_width() // self.tile_size
        max_tiles_y = self.current_tilemap.get_height() // self.tile_size

        if 0 <= tile_x < max_tiles_x and 0 <= tile_y < max_tiles_y:
            tile_pos = (tile_x, tile_y)
            if tile_pos in self.selected_tiles:
                self.selected_tiles.remove(tile_pos)
            else:
                self.selected_tiles.append(tile_pos)

    def _handle_drag(self, pos: Tuple[int, int]):
        """Handle map dragging"""
        if self.last_mouse_pos:
            dx = pos[0] - self.last_mouse_pos[0]
            dy = pos[1] - self.last_mouse_pos[1]
            self.scroll_offset[0] += dx
            self.scroll_offset[1] += dy
        self.last_mouse_pos = pos

    def _adjust_zoom(self, factor: float):
        """Adjust zoom level"""
        new_zoom = self.zoom_level * factor
        if 0.25 <= new_zoom <= 4.0:
            self.zoom_level = new_zoom

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

    def render(self):
        """Render the current view"""
        self.screen.fill((40, 44, 52))  # Dark background

        if self.current_tilemap:
            self._update_transform()  # Update calculations once per frame

            # Draw tilemap
            scaled_map = pygame.transform.scale(self.current_tilemap, self.scaled_size)
            self.screen.blit(scaled_map, self.image_pos)

            # Draw grid and selections
            if self.grid_visible:
                self._draw_grid()
            self._draw_selections()
        else:
            # Draw some text if no tilemap is loaded
            font = pygame.font.Font(None, 36)
            text = font.render("No tilemap loaded", True, (255, 255, 255))
            text_rect = text.get_rect(
                center=(self.window_size[0] / 2, self.window_size[1] / 2)
            )
            self.screen.blit(text, text_rect)

        pygame.display.flip()

    def _draw_grid(self):
        """Draw the tile grid"""
        if not self.current_tilemap:
            return

        # Draw vertical lines
        for x in range(0, self.scaled_size[0] + 1, self.scaled_tile_size):
            start_pos = (x + self.image_pos[0], self.image_pos[1])
            end_pos = (x + self.image_pos[0], self.image_pos[1] + self.scaled_size[1])
            pygame.draw.line(self.screen, (255, 255, 255, 128), start_pos, end_pos, 1)

        # Draw horizontal lines
        for y in range(0, self.scaled_size[1] + 1, self.scaled_tile_size):
            start_pos = (self.image_pos[0], y + self.image_pos[1])
            end_pos = (self.image_pos[0] + self.scaled_size[0], y + self.image_pos[1])
            pygame.draw.line(self.screen, (255, 255, 255, 128), start_pos, end_pos, 1)

    def _draw_selections(self):
        """Draw selected tiles"""
        if not self.current_tilemap:
            return

        for tile_pos in self.selected_tiles:
            rect = pygame.Rect(
                self.image_pos[0] + tile_pos[0] * self.scaled_tile_size,
                self.image_pos[1] + tile_pos[1] * self.scaled_tile_size,
                self.scaled_tile_size,
                self.scaled_tile_size,
            )
            pygame.draw.rect(self.screen, (255, 255, 0, 128), rect, 2)

    def run(self):
        """Main application loop"""
        running = True
        while running:
            running = self.handle_input()
            self.render()
            self.clock.tick(60)

        # Cleanup
        pygame.quit()
        self.ui.close()


if __name__ == "__main__":
    app = TilemapHelper()
    app.run()
