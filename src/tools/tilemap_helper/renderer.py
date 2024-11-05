import pygame


class TilemapRenderer:
    def __init__(self, helper):
        self.helper = helper
        self.screen = helper.screen
        self.hover_pos = None  # Add hover position tracking

    def render(self):
        """Main render method"""
        self.screen.fill((40, 44, 52))  # Dark background

        if self.helper.current_tilemap:
            self.helper._update_transform()
            self.render_tilemap()
            if self.helper.grid_visible:
                self.render_grid()
            self.render_configured_tiles()  # New method for configured tiles
            self.render_selections()
            self.render_hover()  # New method for hover effects
            self.render_tooltip()  # New method for property display
        else:
            self.render_empty_state()

        pygame.display.flip()

    def render_tilemap(self):
        """Render the tilemap"""
        # Round the scaled size to prevent floating point errors
        scaled_size = (
            round(self.helper.scaled_size[0]),
            round(self.helper.scaled_size[1]),
        )

        # Round the image position to ensure pixel-perfect alignment
        image_pos = (round(self.helper.image_pos[0]), round(self.helper.image_pos[1]))

        scaled_map = pygame.transform.scale(self.helper.current_tilemap, scaled_size)
        self.screen.blit(scaled_map, image_pos)

    def render_grid(self):
        """Draw the tile grid"""
        if not self.helper.current_tilemap:
            return

        # Get the number of tiles in each dimension
        tiles_x = self.helper.current_tilemap.get_width() // self.helper.tile_size
        tiles_y = self.helper.current_tilemap.get_height() // self.helper.tile_size

        # Draw vertical lines
        for i in range(tiles_x + 1):
            x = self.helper.image_pos[0] + (i * self.helper.scaled_tile_size)
            pygame.draw.line(
                self.screen,
                (255, 255, 255, 64),
                (x, self.helper.image_pos[1]),
                (x, self.helper.image_pos[1] + self.helper.scaled_size[1]),
                1,
            )

        # Draw horizontal lines
        for i in range(tiles_y + 1):
            y = self.helper.image_pos[1] + (i * self.helper.scaled_tile_size)
            pygame.draw.line(
                self.screen,
                (255, 255, 255, 64),
                (self.helper.image_pos[0], y),
                (self.helper.image_pos[0] + self.helper.scaled_size[0], y),
                1,
            )

    def render_selections(self):
        """Draw selected tiles"""
        for tile_pos in self.helper.selected_tiles:
            rect = pygame.Rect(
                self.helper.image_pos[0] + tile_pos[0] * self.helper.scaled_tile_size,
                self.helper.image_pos[1] + tile_pos[1] * self.helper.scaled_tile_size,
                self.helper.scaled_tile_size,
                self.helper.scaled_tile_size,
            )
            pygame.draw.rect(self.screen, (255, 255, 0, 128), rect, 2)

    def render_empty_state(self):
        """Draw message when no tilemap is loaded"""
        font = pygame.font.Font(None, 36)
        text = font.render("No tilemap loaded", True, (255, 255, 255))
        text_rect = text.get_rect(
            center=(self.helper.window_size[0] / 2, self.helper.window_size[1] / 2)
        )
        self.screen.blit(text, text_rect)

    def render_configured_tiles(self):
        """Draw green grid lines for configured tiles"""
        # Get all configured tile groups
        for pos_str, config in self.helper.tile_configs.items():
            try:
                x, y = eval(pos_str)  # Convert string position back to tuple

                # Draw green rectangle around the individual tile
                rect = pygame.Rect(
                    self.helper.image_pos[0] + x * self.helper.scaled_tile_size,
                    self.helper.image_pos[1] + y * self.helper.scaled_tile_size,
                    self.helper.scaled_tile_size,
                    self.helper.scaled_tile_size,
                )
                pygame.draw.rect(self.screen, (0, 255, 0, 128), rect, 2)
            except (ValueError, SyntaxError):
                continue

    def render_hover(self):
        """Draw hover effect for tile groups"""
        if self.hover_pos:
            # Find the tile group that contains the hovered position
            hover_group = None
            for pos_str, config in self.helper.tile_configs.items():
                try:
                    x, y = eval(pos_str)
                    # Get all tiles in this group
                    tiles = []
                    for tile_pos_str in self.helper.tile_configs:
                        tile_x, tile_y = eval(tile_pos_str)
                        if self.helper.tile_configs[tile_pos_str] == config:
                            tiles.append((tile_x, tile_y))

                    # Check if hover_pos matches any tile in this group
                    if (self.hover_pos[0], self.hover_pos[1]) in tiles:
                        hover_group = tiles
                        break

                except (ValueError, SyntaxError):
                    continue

            if hover_group:
                # Find bounds of the tile group
                min_x = min(x for x, y in hover_group)
                min_y = min(y for x, y in hover_group)
                max_x = max(x for x, y in hover_group)
                max_y = max(y for x, y in hover_group)

                # Draw rectangle around the entire group
                rect = pygame.Rect(
                    self.helper.image_pos[0] + min_x * self.helper.scaled_tile_size,
                    self.helper.image_pos[1] + min_y * self.helper.scaled_tile_size,
                    self.helper.scaled_tile_size * (max_x - min_x + 1),
                    self.helper.scaled_tile_size * (max_y - min_y + 1),
                )
                pygame.draw.rect(self.screen, (100, 200, 255, 128), rect, 2)

    def render_tooltip(self):
        """Display tile properties on hover"""
        if self.hover_pos:
            hover_config = self.helper.get_tile_config(self.hover_pos)
            if hover_config:
                # Create tooltip text
                lines = [
                    f"Name: {hover_config.get('name', 'Unnamed')}",
                    f"Type: {hover_config.get('type', 'Unknown')}",
                    f"Size: {hover_config.get('width', 1)}x{hover_config.get('height', 1)}",
                ]

                # Add custom properties
                props = hover_config.get("properties", {})
                if props:
                    lines.append("Properties:")
                    for key, value in props.items():
                        lines.append(f"  {key}: {value}")

                # Render tooltip
                font = pygame.font.Font(None, 24)
                line_height = 25
                padding = 5

                # Calculate tooltip size
                max_width = max(font.size(line)[0] for line in lines)
                height = line_height * len(lines)

                # Create tooltip background
                tooltip_surf = pygame.Surface(
                    (max_width + padding * 2, height + padding * 2)
                )
                tooltip_surf.fill((40, 44, 52))
                pygame.draw.rect(
                    tooltip_surf, (100, 100, 100), tooltip_surf.get_rect(), 1
                )

                # Add text
                for i, line in enumerate(lines):
                    text_surf = font.render(line, True, (255, 255, 255))
                    tooltip_surf.blit(text_surf, (padding, padding + i * line_height))

                # Position tooltip near mouse but ensure it stays on screen
                mouse_pos = pygame.mouse.get_pos()
                tooltip_x = min(
                    mouse_pos[0] + 20,
                    self.helper.window_size[0] - max_width - padding * 2,
                )
                tooltip_y = min(
                    mouse_pos[1] + 20, self.helper.window_size[1] - height - padding * 2
                )

                self.screen.blit(tooltip_surf, (tooltip_x, tooltip_y))
