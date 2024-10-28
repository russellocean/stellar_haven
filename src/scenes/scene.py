from systems.ui_system import UISystem


class Scene:
    def __init__(self, game):
        self.game = game
        self.ui_system = UISystem()
        self.camera = None  # Add camera reference

        # Define drawing layers
        self.background_layer = []  # Stars, parallax, etc.
        self.game_layer = []  # Game objects, sprites
        self.system_layer = []  # Game systems (building, etc.)
        self.ui_layer = []  # UI elements
        self.debug_layer = []  # Debug visuals

    def handle_event(self, event):
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
            for sprite in self.game_layer:
                if hasattr(sprite, "sprites"):  # If it's a sprite group
                    for s in sprite.sprites():
                        screen_rect = self.camera.apply(s.rect)
                        screen.blit(s.image, screen_rect)
                else:  # Single sprite/element
                    screen_rect = self.camera.apply(sprite.rect)
                    screen.blit(sprite.image, screen_rect)
        else:
            # Fallback for no camera
            for element in self.game_layer:
                element.draw(screen)

        # Draw systems (might need camera offset depending on system)
        for element in self.system_layer:
            element.draw(screen)

        # Draw UI elements (not affected by camera)
        self.ui_system.draw(screen)
        for element in self.ui_layer:  # Add this line to draw UI layer elements
            element.draw(screen)

        # Debug layer (might need camera offset depending on debug visuals)
        for element in self.debug_layer:
            element.draw(screen)
