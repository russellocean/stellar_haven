from typing import List, Tuple

import pygame

from systems.asset_manager import AssetManager
from systems.debug_system import DebugSystem


class RoomRenderer:
    TILE_SIZE = 32

    def __init__(self, room_manager):
        self.room_manager = room_manager
        self.asset_manager = AssetManager()
        self.debug = DebugSystem()

        # Initialize asset containers
        self.framework = {}
        self.interiors = {}
        self.decorations = {}

        # Load room config and assets
        self._load_room_config()
        self._load_assets()

    def _load_room_config(self):
        """Load room configuration file"""
        self.room_config = self.asset_manager.get_config("rooms")
        if not self.room_config or "room_types" not in self.room_config:
            self.debug.log("Warning: Room config not found or invalid")
            self.room_config = {"room_types": {}}

    def _load_assets(self):
        """Load all room assets"""
        self._load_framework_assets()
        self._load_interior_assets()
        self._load_decoration_assets()

    def _load_framework_assets(self):
        """Load wall and door assets"""
        framework_pieces = [
            "wall_horizontal",
            "wall_vertical",
            "corner_top_left",
            "corner_top_right",
            "corner_bottom_left",
            "corner_bottom_right",
            "door_horizontal_left",
            "door_horizontal_right",
            "door_vertical_top",
            "door_vertical_bottom",
        ]

        for piece in framework_pieces:
            self.framework[piece] = self._load_or_create_fallback(
                f"rooms/framework/{piece}.png", (255, 0, 255)  # Magenta fallback
            )

    def _load_interior_assets(self):
        """Load floor and wall assets"""
        for piece in ["floor", "wall"]:
            self.interiors[piece] = self._load_or_create_fallback(
                f"rooms/interiors/{piece}_base.png", (128, 128, 128)  # Gray fallback
            )

    def _load_decoration_assets(self):
        """Load decoration assets for each room type"""
        for room_type, config in self.room_config["room_types"].items():
            if "decorations" in config:
                for decoration in config["decorations"]:
                    key = f"{room_type}_{decoration}"
                    self.decorations[key] = self._load_or_create_fallback(
                        f"rooms/decorations/{room_type}/{decoration}.png",
                        (0, 255, 0),  # Green fallback
                    )

    def _load_or_create_fallback(
        self, path: str, fallback_color: Tuple[int, int, int]
    ) -> pygame.Surface:
        """Load image or create fallback surface"""
        image = self.asset_manager.get_image(path)
        if not image:
            self.debug.log(f"Warning: Failed to load asset: {path}")
            fallback = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
            fallback.fill(fallback_color)
            return fallback
        return image

    def render_room(
        self,
        surface: pygame.Surface,
        room_type: str,
        rect: pygame.Rect,
        doors: List[dict],
    ):
        """Render a complete room"""
        size = rect.size
        surface.fill((0, 0, 0, 0))

        # Get room theme
        theme = self.room_config["room_types"][room_type]["color_theme"]

        # Render layers
        self._render_interior(surface, size, theme)
        self._render_walls(surface, size, theme)

        # Render doors
        for door in doors:
            pixel_x = door["x"] * self.TILE_SIZE
            pixel_y = door["y"] * self.TILE_SIZE

            if door["horizontal"]:
                surface.blit(self.framework["door_horizontal_left"], (pixel_x, pixel_y))
                surface.blit(
                    self.framework["door_horizontal_right"],
                    (pixel_x + self.TILE_SIZE, pixel_y),
                )
            else:
                surface.blit(self.framework["door_vertical_top"], (pixel_x, pixel_y))
                surface.blit(
                    self.framework["door_vertical_bottom"],
                    (pixel_x, pixel_y + self.TILE_SIZE),
                )

        # Render corners last
        self._render_corners(surface, size)

    def _render_interior(
        self, surface: pygame.Surface, size: Tuple[int, int], theme: str
    ):
        """Render the interior floor and basic walls"""
        width, height = size

        # Fill with floor tiles
        for y in range(self.TILE_SIZE, height - self.TILE_SIZE, self.TILE_SIZE):
            for x in range(self.TILE_SIZE, width - self.TILE_SIZE, self.TILE_SIZE):
                surface.blit(self.interiors["floor"], (x, y))

    def _render_walls(self, surface: pygame.Surface, size: Tuple[int, int], theme: str):
        """Render the basic walls"""
        width, height = size

        # Top and bottom walls
        for x in range(self.TILE_SIZE, width - self.TILE_SIZE, self.TILE_SIZE):
            surface.blit(self.framework["wall_horizontal"], (x, 0))  # Top
            surface.blit(
                self.framework["wall_horizontal"], (x, height - self.TILE_SIZE)
            )  # Bottom

        # Left and right walls
        for y in range(self.TILE_SIZE, height - self.TILE_SIZE, self.TILE_SIZE):
            surface.blit(self.framework["wall_vertical"], (0, y))  # Left
            surface.blit(
                self.framework["wall_vertical"], (width - self.TILE_SIZE, y)
            )  # Right

    def _render_corners(self, surface: pygame.Surface, size: Tuple[int, int]):
        """Render the corner pieces"""
        width, height = size

        # Place corner pieces
        surface.blit(self.framework["corner_top_left"], (0, 0))
        surface.blit(self.framework["corner_top_right"], (width - self.TILE_SIZE, 0))
        surface.blit(self.framework["corner_bottom_left"], (0, height - self.TILE_SIZE))
        surface.blit(
            self.framework["corner_bottom_right"],
            (width - self.TILE_SIZE, height - self.TILE_SIZE),
        )
