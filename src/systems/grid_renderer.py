from typing import Optional

import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager


class GridRenderer:
    def __init__(self, grid, tile_size=16):
        self.grid = grid
        self.tile_size = tile_size
        self.asset_manager = AssetManager()
        self.camera = None

        self.textures = {
            TileType.WALL: self._init_wall_textures(),
            TileType.CORNER: self._init_corner_textures(),
            TileType.DOOR: self._init_door_textures(),
            TileType.INTERIOR_BACKGROUND: self._init_interior_background_textures(),
        }

        self.tile_cache = {}
        self.rendered_groups = set()

        self.grid.add_tile_change_callback(self._on_tiles_changed)

    def _init_wall_textures(self):
        """Initialize wall textures"""
        return {
            "exterior": {
                "top": self.asset_manager.get_tilemap_group("exterior_top_center_1")[
                    "surface"
                ],
                "bottom": self.asset_manager.get_tilemap_group(
                    "exterior_bottom_center_1"
                )["surface"],
                "left": self.asset_manager.get_tilemap_group("exterior_left_1")[
                    "surface"
                ],
                "right": self.asset_manager.get_tilemap_group("exterior_right_1")[
                    "surface"
                ],
                "center": self.asset_manager.get_tilemap_group("exterior_connected")[
                    "surface"
                ],
            },
        }

    def _init_corner_textures(self):
        """Initialize corner textures"""
        return {
            "exterior": {
                "top_left": self.asset_manager.get_tilemap_group("exterior_top_left")[
                    "surface"
                ],
                "top_right": self.asset_manager.get_tilemap_group("exterior_top_right")[
                    "surface"
                ],
                "bottom_left": self.asset_manager.get_tilemap_group(
                    "exterior_bottom_left"
                )["surface"],
                "bottom_right": self.asset_manager.get_tilemap_group(
                    "exterior_bottom_right"
                )["surface"],
            },
        }

    def _init_door_textures(self):
        """Initialize door textures"""
        return {
            "light_closed": self.asset_manager.get_tilemap_group("door_light_closed")[
                "surface"
            ],
            "light_open": self.asset_manager.get_tilemap_group("door_light_open")[
                "surface"
            ],
        }

    def _init_interior_background_textures(self):
        """Initialize interior background textures"""
        return {
            "light": self._load_textures(
                {
                    "top_left": "light_top_left",
                    "top_center": "light_top_center",
                    "top_right": "light_top_right",
                    "left": "light_left",
                    "center": "light_center",
                    "right": "light_right",
                }
            ),
            "dark": self._load_textures(
                {
                    "bottom_left": "dark_bottom_left",
                    "bottom_center": "dark_bottom_center",
                    "bottom_right": "dark_bottom_right",
                    "left": "dark_left",
                    "center": "dark_center",
                    "right": "dark_right",
                }
            ),
        }

    def _load_textures(self, texture_map):
        """Helper to load multiple textures"""
        return {
            key: self.asset_manager.get_tilemap_group(group_name)["surface"]
            for key, group_name in texture_map.items()
        }

    def _is_exterior_wall(self, x: int, y: int) -> bool:
        """Determine if a wall is on the exterior of the structure"""
        # Check if any adjacent tile is empty
        adjacent = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return any(pos not in self.grid.cells for pos in adjacent)

    def _is_in_top_half(self, x: int, y: int) -> bool:
        """Determine if a position is in the top half of its room"""
        for room_id, room in self.grid.rooms.items():
            room_x, room_y = room["grid_pos"]
            width, height = room["grid_size"]

            # Check if position is within this room's bounds
            if room_x <= x < room_x + width and room_y <= y < room_y + height:
                # Calculate if we're in the top half of the room
                room_mid_y = room_y + (height // 2)
                return y < room_mid_y

        return False  # Default to bottom half if not in any room

    def _check_adjacent_tile(
        self, x: int, y: int, tile_type: Optional[TileType] = None
    ) -> dict:
        """Helper to check adjacent tiles for a specific type or existence"""
        adjacent = {
            "up": (x, y - 1) in self.grid.cells,
            "down": (x, y + 1) in self.grid.cells,
            "left": (x - 1, y) in self.grid.cells,
            "right": (x + 1, y) in self.grid.cells,
        }

        if tile_type:
            return {
                dir: exists and self.grid.cells[(x + dx, y + dy)] == tile_type
                for dir, exists, (dx, dy) in [
                    ("up", adjacent["up"], (0, -1)),
                    ("down", adjacent["down"], (0, 1)),
                    ("left", adjacent["left"], (-1, 0)),
                    ("right", adjacent["right"], (1, 0)),
                ]
            }
        return adjacent

    def _get_wall_context(self, x: int, y: int) -> dict:
        """Get detailed wall context including position and lighting"""
        adjacent = self._check_adjacent_tile(x, y)

        if not adjacent["up"]:
            return {"type": "exterior", "position": "top"}
        if not adjacent["down"]:
            return {"type": "exterior", "position": "bottom"}
        if not adjacent["left"]:
            return {"type": "exterior", "position": "left"}
        if not adjacent["right"]:
            return {"type": "exterior", "position": "right"}

        return {"type": "exterior", "position": "center"}

    def _get_corner_context(self, x: int, y: int) -> dict:
        """Get detailed corner context including position and if it's exterior"""
        adjacent = self._check_adjacent_tile(x, y)

        # Determine exterior corner position
        if not adjacent["up"] and not adjacent["left"]:
            return {"type": "exterior", "position": "top_left"}
        if not adjacent["up"] and not adjacent["right"]:
            return {"type": "exterior", "position": "top_right"}
        if not adjacent["down"] and not adjacent["left"]:
            return {"type": "exterior", "position": "bottom_left"}
        if not adjacent["down"] and not adjacent["right"]:
            return {"type": "exterior", "position": "bottom_right"}

        # Interior corner context
        bg_adjacent = self._check_adjacent_tile(x, y, TileType.INTERIOR_BACKGROUND)
        wall_adjacent = self._check_adjacent_tile(x, y, TileType.WALL)

        is_top = bg_adjacent["up"]
        is_left = wall_adjacent["left"]

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

    def _get_background_context(self, x: int, y: int) -> dict:
        """Get context for interior background tiles"""
        lighting = "light" if self._is_in_top_half(x, y) else "dark"

        # Check adjacent walls
        wall_adjacent = self._check_adjacent_tile(x, y, TileType.WALL)

        # Determine position based on adjacent walls
        if wall_adjacent["up"] and wall_adjacent["left"]:
            position = "top_left"
        elif wall_adjacent["up"] and wall_adjacent["right"]:
            position = "top_right"
        elif wall_adjacent["up"]:
            position = "top_center"
        elif wall_adjacent["down"] and wall_adjacent["left"]:
            position = "bottom_left"
        elif wall_adjacent["down"] and wall_adjacent["right"]:
            position = "bottom_right"
        elif wall_adjacent["down"]:
            position = "bottom_center"
        elif wall_adjacent["left"]:
            position = "left"
        elif wall_adjacent["right"]:
            position = "right"
        else:
            position = "center"

        return {"lighting": lighting, "position": position}

    def _on_tiles_changed(self):
        """Clear the tile cache when tiles change"""
        self.tile_cache.clear()

    def render(self, surface: pygame.Surface, camera):
        """Render the grid using tilemap assets with caching"""
        # Get visible area in grid coordinates
        visible_area = camera.get_visible_area()
        min_x = visible_area.left
        min_y = visible_area.top
        max_x = visible_area.right + 1
        max_y = visible_area.bottom + 1

        self.rendered_groups.clear()

        # Only process tiles within camera bounds
        for pos, tile_type in self.grid.cells.items():
            x, y = pos

            if not (min_x <= x <= max_x and min_y <= y <= max_y):
                continue

            if pos in self.rendered_groups:
                continue

            # Check if this is part of a tile group
            group_info = self._find_group_at_position(x, y, tile_type)
            if group_info:
                self._render_tile_group(surface, *group_info, camera)
                continue

            screen_pos = camera.world_to_screen(x * self.tile_size, y * self.tile_size)

            # Check cache first
            if pos in self.tile_cache:
                surface.blit(self.tile_cache[pos], screen_pos)
                continue

            # Create a new surface for this tile
            tile_surface = pygame.Surface(
                (self.tile_size, self.tile_size), pygame.SRCALPHA
            )

            if tile_type == TileType.DOOR:
                self._render_door_tile(tile_surface)
            elif tile_type == TileType.WALL:
                self._render_wall_tile(tile_surface, x, y)
            elif tile_type == TileType.CORNER:
                self._render_corner_tile(tile_surface, x, y)
            elif tile_type == TileType.FLOOR:
                self._render_floor_tile(tile_surface, x, y)
            elif tile_type == TileType.INTERIOR_BACKGROUND:
                self._render_background_tile(tile_surface, x, y)

            # Store in cache
            self.tile_cache[pos] = tile_surface
            # Render to main surface
            surface.blit(tile_surface, screen_pos)

    def _find_group_at_position(
        self, x: int, y: int, tile_type: TileType
    ) -> Optional[tuple]:
        """Find if position is part of a tile group"""
        for group_name, group in self.grid.tile_groups.items():
            # Skip single-tile groups
            if group["width"] == 1 and group["height"] == 1:
                continue

            if group["tile_type"] != tile_type:
                continue

            # Check if this could be the top-left of a group
            is_group = True
            for dx in range(group["width"]):
                for dy in range(group["height"]):
                    check_pos = (x + dx, y + dy)
                    if (
                        check_pos not in self.grid.cells
                        or self.grid.cells[check_pos] != tile_type
                    ):
                        is_group = False
                        break
                if not is_group:
                    break

            if is_group:
                return (group_name, x, y)
        return None

    def _render_tile_group(
        self, surface: pygame.Surface, group_name: str, x: int, y: int, camera
    ):
        """Render a complete tile group"""
        group = self.grid.tile_groups[group_name]
        screen_pos = camera.world_to_screen(x * self.tile_size, y * self.tile_size)

        # Get group texture
        group_data = self.asset_manager.get_tilemap_group(group_name)
        if group_data and "surface" in group_data:
            surface.blit(group_data["surface"], screen_pos)

        # Mark all tiles in group as rendered
        for dx in range(group["width"]):
            for dy in range(group["height"]):
                self.rendered_groups.add((x + dx, y + dy))

    def _render_door_tile(self, tile_surface):
        """Render a single door tile"""
        texture = self.textures[TileType.DOOR]["light_closed"]
        tile_surface.blit(texture, (0, 0))

    def _render_wall_tile(self, tile_surface, x, y):
        """Render a single wall tile"""
        context = self._get_wall_context(x, y)
        texture = self.textures[TileType.WALL]["exterior"][context["position"]]
        tile_surface.blit(texture, (0, 0))

    def _render_corner_tile(self, tile_surface, x, y):
        """Render a single corner tile"""
        context = self._get_corner_context(x, y)
        texture = self.textures[TileType.CORNER]["exterior"][context["position"]]
        tile_surface.blit(texture, (0, 0))

    def _render_floor_tile(self, tile_surface, x, y):
        """Render a single floor tile"""
        position = self._get_floor_context(x, y)
        texture = self.textures[TileType.FLOOR][position]
        tile_surface.blit(texture, (0, 0))

    def _render_background_tile(self, tile_surface, x, y):
        """Render a single background tile"""
        context = self._get_background_context(x, y)
        texture = self.textures[TileType.INTERIOR_BACKGROUND][context["lighting"]][
            context["position"]
        ]
        tile_surface.blit(texture, (0, 0))

    def set_camera(self, camera):
        """Set camera reference"""
        self.camera = camera
