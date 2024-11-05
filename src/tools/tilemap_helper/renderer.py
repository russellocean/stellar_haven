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
        scaled_map = pygame.transform.scale(
            self.helper.current_tilemap, self.helper.scaled_size
        )
        self.screen.blit(scaled_map, self.helper.image_pos)

    def render_grid(self):
        """Draw the tile grid"""
        # Draw vertical lines
        for x in range(0, self.helper.scaled_size[0] + 1, self.helper.scaled_tile_size):
            start_pos = (x + self.helper.image_pos[0], self.helper.image_pos[1])
            end_pos = (
                x + self.helper.image_pos[0],
                self.helper.image_pos[1] + self.helper.scaled_size[1],
            )
            pygame.draw.line(self.screen, (255, 255, 255, 64), start_pos, end_pos, 1)

        # Draw horizontal lines
        for y in range(0, self.helper.scaled_size[1] + 1, self.helper.scaled_tile_size):
            start_pos = (self.helper.image_pos[0], y + self.helper.image_pos[1])
            end_pos = (
                self.helper.image_pos[0] + self.helper.scaled_size[0],
                y + self.helper.image_pos[1],
            )
            pygame.draw.line(self.screen, (255, 255, 255, 64), start_pos, end_pos, 1)

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
        for pos_str, config in self.helper.tile_configs.items():
            try:
                x, y = eval(pos_str)  # Convert string position back to tuple
                width = config.get("width", 1)
                height = config.get("height", 1)

                # Draw green rectangle around configured tiles
                rect = pygame.Rect(
                    self.helper.image_pos[0] + x * self.helper.scaled_tile_size,
                    self.helper.image_pos[1] + y * self.helper.scaled_tile_size,
                    self.helper.scaled_tile_size * width,
                    self.helper.scaled_tile_size * height,
                )
                pygame.draw.rect(self.screen, (0, 255, 0, 128), rect, 2)
            except (ValueError, SyntaxError):
                continue

    def render_hover(self):
        """Draw hover effect for tile groups"""
        if self.hover_pos:
            # Find the base tile of the group by checking all configured tiles
            base_tile = None
            base_config = None

            for pos_str, config in self.helper.tile_configs.items():
                try:
                    x, y = eval(pos_str)
                    width = config.get("width", 1)
                    height = config.get("height", 1)

                    # Check if hover_pos is within this tile group's bounds
                    if (
                        x <= self.hover_pos[0] < x + width
                        and y <= self.hover_pos[1] < y + height
                    ):
                        base_tile = (x, y)
                        base_config = config
                        break
                except (ValueError, SyntaxError):
                    continue

            if base_tile and base_config:
                # Draw rectangle around the entire group
                rect = pygame.Rect(
                    self.helper.image_pos[0]
                    + base_tile[0] * self.helper.scaled_tile_size,
                    self.helper.image_pos[1]
                    + base_tile[1] * self.helper.scaled_tile_size,
                    self.helper.scaled_tile_size * base_config.get("width", 1),
                    self.helper.scaled_tile_size * base_config.get("height", 1),
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
