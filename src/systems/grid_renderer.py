import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager


class GridRenderer:
    def __init__(self, grid, tile_size=16):
        self.grid = grid
        self.tile_size = tile_size
        self.asset_manager = AssetManager()
        self.camera = None

        # Initialize texture mappings with more specific contexts
        self.textures = {
            TileType.WALL: {
                "exterior": {
                    "top": self.asset_manager.get_tilemap_group(
                        "exterior_top_center_1"
                    )["surface"],
                    "bottom": self.asset_manager.get_tilemap_group(
                        "exterior_bottom_center_1"
                    )["surface"],
                    "left": self.asset_manager.get_tilemap_group("exterior_left_1")[
                        "surface"
                    ],
                    "right": self.asset_manager.get_tilemap_group("exterior_right_1")[
                        "surface"
                    ],
                },
                "interior": {
                    "light": {
                        "top": self.asset_manager.get_tilemap_group("light_top_center")[
                            "surface"
                        ],
                        "center": self.asset_manager.get_tilemap_group("light_center")[
                            "surface"
                        ],
                        "left": self.asset_manager.get_tilemap_group("light_left")[
                            "surface"
                        ],
                        "right": self.asset_manager.get_tilemap_group("light_right")[
                            "surface"
                        ],
                    },
                    "dark": {
                        "center": self.asset_manager.get_tilemap_group("dark_center")[
                            "surface"
                        ],
                        "left": self.asset_manager.get_tilemap_group("dark_left")[
                            "surface"
                        ],
                        "right": self.asset_manager.get_tilemap_group("dark_right")[
                            "surface"
                        ],
                        "bottom": self.asset_manager.get_tilemap_group(
                            "dark_bottom_center"
                        )["surface"],
                    },
                },
            },
            TileType.CORNER: {
                "exterior": {
                    "top_left": self.asset_manager.get_tilemap_group(
                        "exterior_top_left"
                    )["surface"],
                    "top_right": self.asset_manager.get_tilemap_group(
                        "exterior_top_right"
                    )["surface"],
                    "bottom_left": self.asset_manager.get_tilemap_group(
                        "exterior_bottom_left"
                    )["surface"],
                    "bottom_right": self.asset_manager.get_tilemap_group(
                        "exterior_bottom_right"
                    )["surface"],
                },
                "interior": {
                    "light": {
                        "top_left": self.asset_manager.get_tilemap_group(
                            "light_top_left"
                        )["surface"],
                        "top_right": self.asset_manager.get_tilemap_group(
                            "light_top_right"
                        )["surface"],
                    },
                    "dark": {
                        "bottom_left": self.asset_manager.get_tilemap_group(
                            "dark_bottom_left"
                        )["surface"],
                        "bottom_right": self.asset_manager.get_tilemap_group(
                            "dark_bottom_right"
                        )["surface"],
                    },
                },
            },
            TileType.FLOOR: {
                "left": self.asset_manager.get_tilemap_group("platform_left")[
                    "surface"
                ],
                "center": self.asset_manager.get_tilemap_group("platform_center")[
                    "surface"
                ],
                "right": self.asset_manager.get_tilemap_group("platform_right")[
                    "surface"
                ],
            },
            TileType.DOOR: {
                "light": {
                    "closed": self.asset_manager.get_tilemap_group("door_light_closed")[
                        "surface"
                    ],
                    "open": self.asset_manager.get_tilemap_group("door_light_open")[
                        "surface"
                    ],
                },
                "special": {
                    "closed": self.asset_manager.get_tilemap_group(
                        "door_special_closed"
                    )["surface"],
                    "open": self.asset_manager.get_tilemap_group("door_special_open")[
                        "surface"
                    ],
                },
            },
            TileType.BACKGROUND: self.asset_manager.get_tilemap_group("dark_center")[
                "surface"
            ],
        }

        # Store metadata for multi-tile textures
        self.texture_metadata = {
            "door_light_closed": self.asset_manager.get_tilemap_group(
                "door_light_closed"
            ),
            "door_light_open": self.asset_manager.get_tilemap_group("door_light_open"),
            "door_special_closed": self.asset_manager.get_tilemap_group(
                "door_special_closed"
            ),
            "door_special_open": self.asset_manager.get_tilemap_group(
                "door_special_open"
            ),
        }

    def _is_exterior_wall(self, x: int, y: int) -> bool:
        """Determine if a wall is on the exterior of the structure"""
        # Check if any adjacent tile is empty
        adjacent = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return any(pos not in self.grid.cells for pos in adjacent)

    def _get_wall_context(self, x: int, y: int) -> dict:
        """Get detailed wall context including position and lighting"""
        is_exterior = self._is_exterior_wall(x, y)

        if is_exterior:
            # Determine exterior wall position
            up = (x, y - 1) not in self.grid.cells
            down = (x, y + 1) not in self.grid.cells
            left = (x - 1, y) not in self.grid.cells
            right = (x + 1, y) not in self.grid.cells

            if up:
                return {"type": "exterior", "position": "top"}
            if down:
                return {"type": "exterior", "position": "bottom"}
            if left:
                return {"type": "exterior", "position": "left"}
            if right:
                return {"type": "exterior", "position": "right"}

        # Interior wall context
        is_top = (x, y - 1) in self.grid.cells and self.grid.cells[
            (x, y - 1)
        ] == TileType.BACKGROUND
        return {
            "type": "interior",
            "lighting": "light" if is_top else "dark",
            "position": "top" if is_top else "center",
        }

    def _get_corner_context(self, x: int, y: int) -> dict:
        """Get detailed corner context including position and if it's exterior"""
        is_exterior = self._is_exterior_wall(x, y)

        if is_exterior:
            # Determine exterior corner position
            up = (x, y - 1) not in self.grid.cells
            down = (x, y + 1) not in self.grid.cells
            left = (x - 1, y) not in self.grid.cells
            right = (x + 1, y) not in self.grid.cells

            if up and left:
                return {"type": "exterior", "position": "top_left"}
            if up and right:
                return {"type": "exterior", "position": "top_right"}
            if down and left:
                return {"type": "exterior", "position": "bottom_left"}
            if down and right:
                return {"type": "exterior", "position": "bottom_right"}

        # Interior corner context
        is_top = (x, y - 1) in self.grid.cells and self.grid.cells[
            (x, y - 1)
        ] == TileType.BACKGROUND
        is_left = (x - 1, y) in self.grid.cells and self.grid.cells[
            (x - 1, y)
        ] == TileType.WALL

        return {
            "type": "interior",
            "lighting": "light" if is_top else "dark",
            "position": f"{'top' if is_top else 'bottom'}_{'left' if is_left else 'right'}",
        }

    def _get_floor_context(self, x: int, y: int) -> str:
        """Determine floor piece type (left, center, right)"""
        left = (x - 1, y) in self.grid.cells and self.grid.cells[
            (x - 1, y)
        ] == TileType.FLOOR
        right = (x + 1, y) in self.grid.cells and self.grid.cells[
            (x + 1, y)
        ] == TileType.FLOOR

        if not left and right:
            return "left"
        if left and not right:
            return "right"
        return "center"

    def render(self, surface: pygame.Surface, camera):
        """Render the grid using tilemap assets"""
        for pos, tile_type in self.grid.cells.items():
            x, y = pos
            screen_pos = camera.world_to_screen(x * self.tile_size, y * self.tile_size)

            texture = None
            if tile_type == TileType.DOOR:
                # Get door metadata
                door_data = self.texture_metadata["door_light_closed"]
                if door_data:
                    texture = door_data["surface"]
                    # Calculate the full door rectangle
                    door_rect = pygame.Rect(
                        screen_pos[0],
                        screen_pos[1] - (door_data["height"] - 1) * self.tile_size,
                        door_data["width"] * self.tile_size,
                        door_data["height"] * self.tile_size,
                    )
                    surface.blit(texture, door_rect)
                    continue  # Skip the normal blit below

            elif tile_type == TileType.WALL:
                context = self._get_wall_context(x, y)
                if context["type"] == "exterior":
                    texture = self.textures[TileType.WALL]["exterior"][
                        context["position"]
                    ]
                else:
                    texture = self.textures[TileType.WALL]["interior"][
                        context["lighting"]
                    ][context["position"]]

            elif tile_type == TileType.CORNER:
                context = self._get_corner_context(x, y)
                if context["type"] == "exterior":
                    texture = self.textures[TileType.CORNER]["exterior"][
                        context["position"]
                    ]
                else:
                    texture = self.textures[TileType.CORNER]["interior"][
                        context["lighting"]
                    ][context["position"]]

            elif tile_type == TileType.FLOOR:
                position = self._get_floor_context(x, y)
                texture = self.textures[TileType.FLOOR][position]

            elif tile_type == TileType.BACKGROUND:
                texture = self.textures[TileType.BACKGROUND]

            if texture:
                if isinstance(texture, dict):  # If it's a multi-tile texture
                    surface.blit(texture["surface"], screen_pos)
                else:  # Single-tile texture
                    surface.blit(texture, screen_pos)

    def set_camera(self, camera):
        """Set camera reference"""
        self.camera = camera
