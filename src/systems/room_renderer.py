from typing import List, Optional, Tuple

import pygame

from systems.asset_manager import AssetManager
from systems.debug_system import DebugSystem


class RoomRenderer:
    TILE_SIZE = 32

    def __init__(self):
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
        connected_sides: List[bool],
        connection_points: List[Optional[int]] = None,
    ):
        """Render a complete room"""
        size = (rect.width, rect.height)
        surface.fill((0, 0, 0, 0))  # Clear surface

        # Render layers in order
        self._render_interior(surface, size)
        self._render_framework(surface, size, connected_sides, connection_points)
        self._render_decorations(
            surface, room_type, self.get_decoration_positions(room_type, size)
        )

    def _render_framework(
        self,
        surface: pygame.Surface,
        size: Tuple[int, int],
        connected_sides: List[bool],
        connection_points: List[Optional[int]],
    ):
        """Render walls, corners, and doors"""
        width, height = size

        # Render walls and corners
        self._render_walls(surface, width, height)
        self._render_corners(surface, width, height)

        # Render doors at connection points
        if connection_points:
            self._render_doors(
                surface, width, height, connected_sides, connection_points
            )

    def _render_doors(
        self,
        surface: pygame.Surface,
        width: int,
        height: int,
        connected_sides: List[bool],
        connection_points: List[Optional[int]],
    ):
        """Render doors at connection points"""
        door_positions = [
            (lambda x: (x, 0), "horizontal"),  # Top
            (lambda y: (width - self.TILE_SIZE, y), "vertical"),  # Right
            (lambda x: (x, height - self.TILE_SIZE), "horizontal"),  # Bottom
            (lambda y: (0, y), "vertical"),  # Left
        ]

        for i, (pos_func, door_type) in enumerate(door_positions):
            if connected_sides[i] and connection_points[i] is not None:
                self._place_door(
                    surface, pos_func(connection_points[i] * self.TILE_SIZE), door_type
                )

    def _place_door(
        self, surface: pygame.Surface, pos: Tuple[int, int], door_type: str
    ):
        """Place a door at the specified position"""
        if door_type == "horizontal":
            surface.blit(self.framework["door_horizontal_left"], pos)
            surface.blit(
                self.framework["door_horizontal_right"],
                (pos[0] + self.TILE_SIZE, pos[1]),
            )
        else:  # vertical
            surface.blit(self.framework["door_vertical_top"], pos)
            surface.blit(
                self.framework["door_vertical_bottom"],
                (pos[0], pos[1] + self.TILE_SIZE),
            )

    def _render_decorations(
        self, surface: pygame.Surface, room_type: str, positions: List[Tuple[int, int]]
    ):
        """Render decorations for a room"""
        if room_type not in self.room_config["room_types"]:
            return

        room_config = self.room_config["room_types"][room_type]
        if "decorations" not in room_config:
            return

        for decoration, pos in zip(room_config["decorations"], positions):
            key = f"{room_type}_{decoration}"
            if key in self.decorations:
                surface.blit(self.decorations[key], pos)

    def get_decoration_positions(
        self, room_type: str, size: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Get positions for room decorations"""
        if room_type not in self.room_config["room_types"]:
            return []

        room_config = self.room_config["room_types"][room_type]
        if "decorations" not in room_config:
            return []

        width, height = size
        positions = []

        # For now, just place decorations in a grid pattern
        num_decorations = len(room_config["decorations"])
        grid_size = int(num_decorations**0.5) + 1
        spacing_x = width // (grid_size + 1)
        spacing_y = height // (grid_size + 1)

        for i in range(num_decorations):
            x = spacing_x * ((i % grid_size) + 1)
            y = spacing_y * ((i // grid_size) + 1)
            positions.append((x, y))

        return positions

    def _render_interior(self, surface: pygame.Surface, size: Tuple[int, int]):
        """Render the interior floor and basic walls"""
        width, height = size

        # Fill with floor tiles
        for y in range(self.TILE_SIZE, height - self.TILE_SIZE, self.TILE_SIZE):
            for x in range(self.TILE_SIZE, width - self.TILE_SIZE, self.TILE_SIZE):
                surface.blit(self.interiors["floor"], (x, y))

    def _render_walls(self, surface: pygame.Surface, width: int, height: int):
        """Render the basic walls"""
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

    def _render_corners(self, surface: pygame.Surface, width: int, height: int):
        """Render the corner pieces"""
        # Place corner pieces
        surface.blit(self.framework["corner_top_left"], (0, 0))
        surface.blit(self.framework["corner_top_right"], (width - self.TILE_SIZE, 0))
        surface.blit(self.framework["corner_bottom_left"], (0, height - self.TILE_SIZE))
        surface.blit(
            self.framework["corner_bottom_right"],
            (width - self.TILE_SIZE, height - self.TILE_SIZE),
        )
