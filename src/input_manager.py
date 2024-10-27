import pygame


class InputManager:
    def __init__(self):
        self.actions = {"move_left": False, "move_right": False, "jump": False}

    def update(self):
        keys = pygame.key.get_pressed()

        # Update action states based on key presses
        self.actions["move_left"] = keys[pygame.K_LEFT] or keys[pygame.K_a]
        self.actions["move_right"] = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        self.actions["jump"] = (
            keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
        )

    def is_action_pressed(self, action):
        return self.actions.get(action, False)
