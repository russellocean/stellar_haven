from typing import Tuple

import pygame


class InputHandler:
    def __init__(self, helper):
        self.helper = helper

    def handle_input(self) -> bool:
        """Process all input events"""
        self.helper.qt_app.processEvents()

        for event in pygame.event.get():
            if not self.handle_event(event):
                return False
        return True

    def handle_event(self, event) -> bool:
        """Handle a single pygame event"""
        if event.type == pygame.QUIT:
            return False

        handlers = {
            pygame.MOUSEBUTTONDOWN: self.handle_mouse_down,
            pygame.MOUSEBUTTONUP: self.handle_mouse_up,
            pygame.MOUSEMOTION: self.handle_mouse_motion,
            pygame.KEYDOWN: self.handle_keydown,
        }

        if event.type in handlers:
            handlers[event.type](event)

        return True

    def handle_mouse_down(self, event):
        """Handle mouse button down events"""
        if event.button == 1:  # Left click
            self.handle_selection(event.pos)
        elif event.button == 2:  # Middle click
            self.helper.dragging = True
            self.helper.last_mouse_pos = event.pos
        elif event.button == 4:  # Mouse wheel up
            self.helper._adjust_zoom(1.1)
        elif event.button == 5:  # Mouse wheel down
            self.helper._adjust_zoom(0.9)

    def handle_mouse_up(self, event):
        """Handle mouse button up events"""
        if event.button == 2:  # Middle click release
            self.helper.dragging = False

    def handle_mouse_motion(self, event):
        """Handle mouse motion events"""
        if self.helper.dragging:
            self.handle_drag(event.pos)

    def handle_keydown(self, event):
        """Handle keyboard events"""
        if event.key == pygame.K_g:
            self.helper.grid_visible = not self.helper.grid_visible
        elif event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
            self.helper.save_config("tilemap_config.json")
        elif event.key == pygame.K_l and event.mod & pygame.KMOD_CTRL:
            self.helper.load_config("tilemap_config.json")

    def handle_selection(self, pos: Tuple[int, int]):
        """Handle tile selection with multi-tile support"""
        if not self.helper.current_tilemap:
            return

        # Convert screen position to tilemap position
        rel_x = pos[0] - self.helper.image_pos[0]
        rel_y = pos[1] - self.helper.image_pos[1]

        # Convert to tile coordinates
        base_x = int(rel_x / self.helper.scaled_tile_size)
        base_y = int(rel_y / self.helper.scaled_tile_size)

        # Check if the click is within the image bounds
        max_tiles_x = self.helper.current_tilemap.get_width() // self.helper.tile_size
        max_tiles_y = self.helper.current_tilemap.get_height() // self.helper.tile_size

        # Generate all tiles in the multi-tile selection
        tiles_to_toggle = []
        for y in range(
            base_y, min(base_y + self.helper.multi_tile_height, max_tiles_y)
        ):
            for x in range(
                base_x, min(base_x + self.helper.multi_tile_width, max_tiles_x)
            ):
                if 0 <= x < max_tiles_x and 0 <= y < max_tiles_y:
                    tiles_to_toggle.append((x, y))

        # Toggle all tiles in the selection
        for tile_pos in tiles_to_toggle:
            if tile_pos in self.helper.selected_tiles:
                self.helper.selected_tiles.remove(tile_pos)
            else:
                self.helper.selected_tiles.append(tile_pos)

    def handle_drag(self, pos: Tuple[int, int]):
        """Handle map dragging"""
        if self.helper.last_mouse_pos:
            dx = pos[0] - self.helper.last_mouse_pos[0]
            dy = pos[1] - self.helper.last_mouse_pos[1]
            self.helper.scroll_offset[0] += dx
            self.helper.scroll_offset[1] += dy
        self.helper.last_mouse_pos = pos
