from typing import Dict, List, Optional, Tuple

import pygame

from systems.asset_manager import AssetManager


class RoomRenderer:
    TILE_SIZE = 32  # Base size for tiles

    def __init__(self):
        self.asset_manager = AssetManager()
        self.framework = {}
        self.interiors = {}
        self.decorations = {}

        # Load room config first
        self.room_config = self.asset_manager.get_config("rooms")
        if not self.room_config or "room_types" not in self.room_config:
            print("Warning: Room config not found or invalid")
            self.room_config = {"room_types": {}}

        # Load all room assets
        self.load_assets()

    def load_assets(self):
        """Load all room-related assets using AssetManager"""
        # Load framework pieces
        framework_pieces = [
            "wall_horizontal",
            "wall_vertical",
            "corner_top_left",
            "corner_top_right",
            "corner_bottom_left",
            "corner_bottom_right",
            "door_horizontal",
            "door_vertical",
        ]

        for piece in framework_pieces:
            image_path = f"rooms/framework/{piece}.png"
            self.framework[piece] = self.asset_manager.get_image(image_path)
            if not self.framework[piece]:
                print(f"Warning: Failed to load framework piece: {piece}")
                # Create a default colored rectangle as fallback
                surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
                surf.fill((255, 0, 255))  # Magenta for missing textures
                self.framework[piece] = surf

        # Load interior tiles
        interior_pieces = ["floor", "wall"]
        for piece in interior_pieces:
            image_path = f"rooms/interiors/{piece}_base.png"
            self.interiors[piece] = self.asset_manager.get_image(image_path)
            if not self.interiors[piece]:
                print(f"Warning: Failed to load interior piece: {piece}")
                # Create a default colored rectangle as fallback
                surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
                surf.fill((128, 128, 128))  # Gray for missing textures
                self.interiors[piece] = surf

        # Load decorations for each room type
        for room_type in self.room_config.get("room_types", {}):
            self.decorations[room_type] = {}
            room_decorations = self.room_config["room_types"][room_type].get(
                "decorations", {}
            )

            for decoration_name in room_decorations:
                image_path = f"rooms/decorations/{room_type}/{decoration_name}.png"
                decoration_image = self.asset_manager.get_image(image_path)

                if decoration_image:
                    self.decorations[room_type][decoration_name] = decoration_image
                else:
                    print(f"Warning: Failed to load decoration: {image_path}")
                    # Create a default colored rectangle as fallback
                    size = room_decorations[decoration_name].get("size", (1, 1))
                    surf = pygame.Surface(
                        (size[0] * self.TILE_SIZE, size[1] * self.TILE_SIZE)
                    )
                    surf.fill((0, 255, 0))  # Green for missing textures
                    self.decorations[room_type][decoration_name] = surf

    def get_valid_room_size(
        self, room_type: str, desired_size: Tuple[int, int]
    ) -> Tuple[int, int]:
        """Validate and adjust room size based on configuration"""
        config = self.room_config["room_types"][room_type]
        min_size = config["min_size"]
        max_size = config["max_size"]

        return (
            max(min_size[0], min(max_size[0], desired_size[0])),
            max(min_size[1], min(max_size[1], desired_size[1])),
        )

    def get_decoration_positions(
        self, room_type: str, room_size: Tuple[int, int]
    ) -> Dict[str, List[Tuple[int, int]]]:
        """Calculate valid positions for decorations based on room configuration"""
        config = self.room_config["room_types"][room_type]["decorations"]
        positions = {}

        for decoration_name, decoration_config in config.items():
            positions[decoration_name] = self._calculate_valid_positions(
                room_size,
                decoration_config["size"],
                decoration_config["valid_positions"],
                decoration_config["min_count"],
            )

        return positions

    def _calculate_valid_positions(
        self,
        room_size: Tuple[int, int],
        decoration_size: Tuple[int, int],
        valid_positions: List[str],
        min_count: int,
    ) -> List[Tuple[int, int]]:
        """Calculate valid positions for a decoration based on rules"""
        positions = []
        tile_size = 32  # Our base tile size

        # Convert sizes from tiles to pixels
        room_width = room_size[0] * tile_size
        room_height = room_size[1] * tile_size
        dec_width = decoration_size[0] * tile_size
        dec_height = decoration_size[1] * tile_size

        # Calculate positions based on placement rules
        if "wall" in valid_positions:
            # Add wall positions
            for x in range(tile_size, room_width - dec_width, tile_size):
                positions.append((x, tile_size))  # Top wall
                positions.append(
                    (x, room_height - dec_height - tile_size)
                )  # Bottom wall

            for y in range(tile_size, room_height - dec_height, tile_size):
                positions.append((tile_size, y))  # Left wall
                positions.append((room_width - dec_width - tile_size, y))  # Right wall

        if "center" in valid_positions:
            # Add center positions
            center_x = (room_width - dec_width) // 2
            center_y = (room_height - dec_height) // 2
            positions.append((center_x, center_y))

        if "corner" in valid_positions:
            # Add corner positions
            positions.extend(
                [
                    (tile_size, tile_size),  # Top-left
                    (room_width - dec_width - tile_size, tile_size),  # Top-right
                    (tile_size, room_height - dec_height - tile_size),  # Bottom-left
                    (
                        room_width - dec_width - tile_size,
                        room_height - dec_height - tile_size,
                    ),  # Bottom-right
                ]
            )

        return positions[:min_count]  # Return at least the minimum required positions

    def render_room(
        self,
        surface: pygame.Surface,
        room_type: str,
        rect: pygame.Rect,
        connected_sides: Optional[List[bool]] = None,
    ):
        """Render a complete room using configuration"""
        if connected_sides is None:
            connected_sides = [False, False, False, False]

        # Validate room size
        room_size = self.get_valid_room_size(
            room_type, (rect.width // 32, rect.height // 32)
        )

        # Create room surface
        room_surface = pygame.Surface(rect.size, pygame.SRCALPHA)

        # Get room theme colors
        theme = self.room_config["room_types"][room_type]["color_theme"]

        # Render base elements
        self._render_floor(room_surface, rect.size, theme["floor"])
        self._render_framework(room_surface, rect.size, connected_sides)

        # Get and render decorations
        decoration_positions = self.get_decoration_positions(room_type, room_size)
        self._render_decorations(room_surface, room_type, decoration_positions)

        # Blit to main surface
        surface.blit(room_surface, rect.topleft)

    def _render_floor(
        self, surface: pygame.Surface, size: Tuple[int, int], color: List[int]
    ):
        """Render the floor tiles"""
        width, height = size
        floor_tile = self.interiors.get("floor")

        # Tint the floor tile with the room's color
        tinted_tile = floor_tile.copy()
        tinted_tile.fill(
            (color[0], color[1], color[2], 128), special_flags=pygame.BLEND_RGBA_MULT
        )

        # Tile the floor
        for y in range(0, height, self.TILE_SIZE):
            for x in range(0, width, self.TILE_SIZE):
                surface.blit(tinted_tile, (x, y))

    def _render_framework(
        self,
        surface: pygame.Surface,
        size: Tuple[int, int],
        connected_sides: List[bool],
    ):
        """Render walls and corners"""
        width, height = size

        # Draw corners
        surface.blit(self.framework["corner_top_left"], (0, 0))
        surface.blit(self.framework["corner_top_right"], (width - self.TILE_SIZE, 0))
        surface.blit(self.framework["corner_bottom_left"], (0, height - self.TILE_SIZE))
        surface.blit(
            self.framework["corner_bottom_right"],
            (width - self.TILE_SIZE, height - self.TILE_SIZE),
        )

        # Draw horizontal walls
        for x in range(self.TILE_SIZE, width - self.TILE_SIZE, self.TILE_SIZE):
            surface.blit(self.framework["wall_horizontal"], (x, 0))  # Top wall
            surface.blit(
                self.framework["wall_horizontal"], (x, height - self.TILE_SIZE)
            )  # Bottom wall

        # Draw vertical walls
        for y in range(self.TILE_SIZE, height - self.TILE_SIZE, self.TILE_SIZE):
            surface.blit(self.framework["wall_vertical"], (0, y))  # Left wall
            surface.blit(
                self.framework["wall_vertical"], (width - self.TILE_SIZE, y)
            )  # Right wall

        # Add doors where rooms are connected
        if connected_sides[0]:  # Top
            surface.blit(
                self.framework["door_horizontal"], (width // 2 - self.TILE_SIZE, 0)
            )
        if connected_sides[1]:  # Right
            surface.blit(
                self.framework["door_vertical"],
                (width - self.TILE_SIZE, height // 2 - self.TILE_SIZE),
            )
        if connected_sides[2]:  # Bottom
            surface.blit(
                self.framework["door_horizontal"],
                (width // 2 - self.TILE_SIZE, height - self.TILE_SIZE),
            )
        if connected_sides[3]:  # Left
            surface.blit(
                self.framework["door_vertical"], (0, height // 2 - self.TILE_SIZE)
            )

    def _render_decorations(
        self,
        surface: pygame.Surface,
        room_type: str,
        decoration_positions: Dict[str, List[Tuple[int, int]]],
    ):
        """Render room decorations at their designated positions"""
        if room_type not in self.decorations:
            return

        for decoration_name, positions in decoration_positions.items():
            if decoration_name in self.decorations[room_type]:
                decoration_image = self.decorations[room_type][decoration_name]
                for pos in positions:
                    surface.blit(decoration_image, pos)
