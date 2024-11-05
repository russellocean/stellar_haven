import pygame


class TilemapRenderer:
    def __init__(self, helper):
        self.helper = helper
        self.screen = helper.screen

    def render(self):
        """Main render method"""
        self.screen.fill((40, 44, 52))  # Dark background

        if self.helper.current_tilemap:
            self.helper._update_transform()
            self.render_tilemap()
            if self.helper.grid_visible:
                self.render_grid()
            self.render_selections()
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
            pygame.draw.line(self.screen, (255, 255, 255, 128), start_pos, end_pos, 1)

        # Draw horizontal lines
        for y in range(0, self.helper.scaled_size[1] + 1, self.helper.scaled_tile_size):
            start_pos = (self.helper.image_pos[0], y + self.helper.image_pos[1])
            end_pos = (
                self.helper.image_pos[0] + self.helper.scaled_size[0],
                y + self.helper.image_pos[1],
            )
            pygame.draw.line(self.screen, (255, 255, 255, 128), start_pos, end_pos, 1)

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
