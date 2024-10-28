import pygame


class InputManager:
    def __init__(self):
        self.actions = {
            "move_left": False,
            "move_right": False,
            "jump": False,
            "move_down": False,
        }

    def handle_event(self, event: pygame.event.Event):
        """Handle keyboard events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                return "toggle_build"
        return None

    def update(self):
        """Update continuous movement actions"""
        keys = pygame.key.get_pressed()

        # Update continuous movement actions
        self.actions["move_left"] = keys[pygame.K_LEFT] or keys[pygame.K_a]
        self.actions["move_right"] = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        self.actions["jump"] = (
            keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
        )
        self.actions["move_down"] = keys[pygame.K_DOWN] or keys[pygame.K_s]

    def is_action_pressed(self, action):
        """Returns True while the action is held down"""
        return self.actions.get(action, False)
