from systems.ui_system import UISystem


class Scene:
    def __init__(self, game):
        self.game = game
        self.ui_system = UISystem()
        self.camera = None

        # Define drawing layers
        self.background_layer = []  # Stars, parallax, etc.
        self.game_layer = []  # Game objects, sprites
        self.system_layer = []  # Game systems (building, etc.)
        self.ui_layer = []  # UI elements
        self.debug_layer = []  # Debug visuals

    def handle_event(self, event):
        """Handle input events"""
        # Handle dialog system events first if dialog system exists
        if hasattr(self, "dialog_system") and self.dialog_system.is_active():
            if self.dialog_system.handle_event(event):
                return True

        # Handle UI events
        if self.ui_system.handle_event(event):
            return True

        return False

    def update(self):
        pass

    def draw(self, screen):
        """Draw all layers in order"""
        # Draw background (not affected by camera)
        for element in self.background_layer:
            element.draw(screen)

        # Draw game objects with camera offset
        if self.camera:
            for element in self.game_layer:
                if hasattr(element, "sprites"):  # If it's a sprite group
                    for s in element.sprites():
                        # Use image_rect if available, otherwise fall back to regular rect
                        source_rect = getattr(s, "image_rect", s.rect)
                        screen_rect = self.camera.apply(source_rect)
                        screen.blit(s.image, screen_rect)
                elif hasattr(element, "render"):  # For tile-based renderers
                    element.render(screen, self.camera)
                elif hasattr(element, "rect"):  # For traditional sprites
                    screen_rect = self.camera.apply(element.rect)
                    screen.blit(element.image, screen_rect)
                else:  # Fallback for other elements
                    element.draw(screen)
        else:
            # Fallback for no camera
            for element in self.game_layer:
                element.draw(screen)

        # Draw systems (might need camera offset depending on system)
        for element in self.system_layer:
            element.draw(screen)

        # Draw UI elements (not affected by camera)
        self.ui_system.draw(screen)
        for element in self.ui_layer:
            element.draw(screen)

        # Debug layer (elements handle their own camera offset)
        for element in self.debug_layer:
            if hasattr(element, "draw_debug"):
                element.draw_debug(screen)
            else:
                element.draw(screen)
