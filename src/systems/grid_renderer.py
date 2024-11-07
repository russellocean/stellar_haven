from typing import Optional

import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager


class GridRenderer:
    """
    Handles the rendering of grid-based tiles and tile groups with texture caching.
    Supports walls, corners, doors, and interior backgrounds with contextual rendering.
    """

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
        """Get corner context for exterior corners"""
        adjacent = self._check_adjacent_tile(x, y)

        # Determine exterior corner position
        if not adjacent["up"] and not adjacent["left"]:
            return {"position": "top_left"}
        if not adjacent["up"] and not adjacent["right"]:
            return {"position": "top_right"}
        if not adjacent["down"] and not adjacent["left"]:
            return {"position": "bottom_left"}
        if not adjacent["down"] and not adjacent["right"]:
            return {"position": "bottom_right"}

        # Default case (shouldn't happen if corner placement is correct)
        return {"position": "top_left"}

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

        # First render all background tiles
        for pos, tiles in self.grid.cells.items():
            x, y = pos
            if not (min_x <= x <= max_x and min_y <= y <= max_y):
                continue

            background_tile = self.grid.get_background_tile(x, y)
            if background_tile:
                screen_pos = camera.world_to_screen(
                    x * self.tile_size, y * self.tile_size
                )
                if pos in self.tile_cache:
                    surface.blit(self.tile_cache[pos + ("bg",)], screen_pos)
                else:
                    tile_surface = pygame.Surface(
                        (self.tile_size, self.tile_size), pygame.SRCALPHA
                    )
                    if background_tile == TileType.INTERIOR_BACKGROUND:
                        self._render_background_tile(tile_surface, x, y)
                    self.tile_cache[pos + ("bg",)] = tile_surface
                    surface.blit(tile_surface, screen_pos)

        # Then render all foreground tiles
        for pos, tiles in self.grid.cells.items():
            x, y = pos
            if not (min_x <= x <= max_x and min_y <= y <= max_y):
                continue

            # Skip if already rendered as part of a group
            if (x, y) in self.rendered_groups:
                continue

            primary_tile = self.grid.get_tile(x, y)
            if primary_tile in [TileType.PLATFORM, TileType.DOOR]:
                # Check cache first
                cache_key = (x, y, "group")
                if cache_key in self.tile_cache:
                    group_name, group_x, group_y = self.tile_cache[cache_key]
                    self._render_tile_group(
                        surface, group_name, group_x, group_y, camera
                    )
                else:
                    # Only check for groups if not in cache
                    group_info = self._find_group_at_position(x, y, primary_tile)
                    if group_info:
                        group_name, group_x, group_y = group_info
                        # Cache for all tiles in the group
                        group = self.grid.tile_groups[group_name]
                        for dx in range(group["width"]):
                            for dy in range(group["height"]):
                                group_cache_key = (group_x + dx, group_y + dy, "group")
                                self.tile_cache[group_cache_key] = (
                                    group_name,
                                    group_x,
                                    group_y,
                                )

                        self._render_tile_group(
                            surface, group_name, group_x, group_y, camera
                        )

            elif primary_tile not in [
                TileType.INTERIOR_BACKGROUND,
                TileType.BACKGROUND,
            ]:
                # Handle other foreground tiles
                screen_pos = camera.world_to_screen(
                    x * self.tile_size, y * self.tile_size
                )
                if pos in self.tile_cache:
                    surface.blit(self.tile_cache[pos], screen_pos)
                    continue

                # Create a new surface for this tile
                tile_surface = pygame.Surface(
                    (self.tile_size, self.tile_size), pygame.SRCALPHA
                )

                if primary_tile == TileType.WALL:
                    self._render_wall_tile(tile_surface, x, y)
                elif primary_tile == TileType.CORNER:
                    self._render_corner_tile(tile_surface, x, y)

                # Store in cache and render
                self.tile_cache[pos] = tile_surface
                surface.blit(tile_surface, screen_pos)

    def _find_group_at_position(
        self, x: int, y: int, tile_type: TileType
    ) -> Optional[tuple]:
        """Find if position is part of a tile group"""
        # Add debug output
        print(f"Checking for group at {x}, {y} with type {tile_type}")

        for group_name, group in self.grid.tile_groups.items():
            # Debug output for each group being checked
            print(f"Checking group: {group_name}, type: {group['tile_type']}")

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
                        or self.grid.get_tile(*check_pos) != tile_type
                    ):  # Use get_tile instead of direct access
                        is_group = False
                        break
                if not is_group:
                    break

            if is_group:
                print(f"Found group: {group_name} at {x}, {y}")
                return (group_name, x, y)
        return None

    def _render_tile_group(
        self, surface: pygame.Surface, group_name: str, x: int, y: int, camera
    ):
        """Render a complete tile group"""
        # Skip if already rendered this frame
        if (x, y) in self.rendered_groups:
            return

        screen_pos = camera.world_to_screen(x * self.tile_size, y * self.tile_size)
        group = self.grid.tile_groups[group_name]

        # Get group texture from cache or create it
        cache_key = (group_name, "texture")
        if cache_key in self.tile_cache:
            surface.blit(self.tile_cache[cache_key], screen_pos)
        else:
            # Get group texture
            group_data = self.asset_manager.get_tilemap_group(group_name)
            if group_data and "surface" in group_data:
                self.tile_cache[cache_key] = group_data["surface"]
                surface.blit(group_data["surface"], screen_pos)

        # Mark all tiles in group as rendered for this frame
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

    def _render_corner_tile(self, tile_surface: pygame.Surface, x: int, y: int) -> None:
        """Render a single corner tile"""
        context = self._get_corner_context(x, y)
        texture = self.textures[TileType.CORNER]["exterior"][context["position"]]
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
