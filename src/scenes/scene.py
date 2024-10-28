from systems.ui_system import UISystem


class Scene:
    def __init__(self, game):
        self.game = game
        self.ui_system = UISystem()

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
        # Draw each layer in order
        for element in self.background_layer:
            element.draw(screen)

        for element in self.game_layer:
            element.draw(screen)

        for element in self.system_layer:
            element.draw(screen)

        # UI system handles its own elements
        self.ui_system.draw(screen)

        for element in self.debug_layer:
            element.draw(screen)
