import json
import os
from typing import Dict, Optional

import pygame


class AssetManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetManager, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        """Initialize asset dictionaries"""
        self.images: Dict[str, pygame.Surface] = {}
        self.fonts: Dict[str, Dict[int, pygame.font.Font]] = {}
        self.configs: Dict[str, dict] = {}

        # Define base paths - now pointing to root directory
        self.base_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.asset_path = os.path.join(self.base_path, "assets")
        self.config_path = os.path.join(
            self.asset_path, "config"
        )  # Move configs into assets

        # Ensure directories exist
        os.makedirs(self.asset_path, exist_ok=True)
        os.makedirs(self.config_path, exist_ok=True)

    def get_image(self, path: str) -> Optional[pygame.Surface]:
        """Get or load an image"""
        if path not in self.images:
            try:
                full_path = os.path.join(self.asset_path, path)
                self.images[path] = pygame.image.load(full_path).convert_alpha()
                print(f"Loaded image: {path}")
            except pygame.error as e:
                print(f"Failed to load image: {path} - {e}")
                return None
        return self.images[path]

    def get_font(self, name: str = None, size: int = 24) -> pygame.font.Font:
        """Get or load a font"""
        if name is None:
            return pygame.font.Font(None, size)

        if name not in self.fonts:
            self.fonts[name] = {}

        if size not in self.fonts[name]:
            try:
                full_path = os.path.join(self.asset_path, "fonts", name)
                self.fonts[name][size] = pygame.font.Font(full_path, size)
            except pygame.error:
                print(f"Failed to load font: {name}, falling back to default")
                self.fonts[name][size] = pygame.font.Font(None, size)

        return self.fonts[name][size]

    def get_config(self, name: str) -> dict:
        """Get or load a config file"""
        if name not in self.configs:
            try:
                full_path = os.path.join(self.config_path, f"{name}.json")
                with open(full_path, "r") as f:
                    self.configs[name] = json.load(f)
                print(f"Loaded config: {name}")
            except FileNotFoundError:
                print(f"Config file not found: {name}")
                self.configs[name] = {}
        return self.configs[name]

    def preload_images(self, directory: str):
        """Preload all images from a directory"""
        dir_path = os.path.join(self.asset_path, directory)
        if not os.path.exists(dir_path):
            print(f"Directory not found: {dir_path}")
            return

        for filename in os.listdir(dir_path):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(directory, filename)
                self.get_image(path)

    def clear_cache(self):
        """Clear all cached assets"""
        self.images.clear()
        self.fonts.clear()
        self.configs.clear()
