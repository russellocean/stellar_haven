import pygame

DEFAULT_CONTROLS = {
    "move_left": [pygame.K_LEFT, pygame.K_a],
    "move_right": [pygame.K_RIGHT, pygame.K_d],
    "jump": [pygame.K_UP, pygame.K_w, pygame.K_SPACE],
    "move_down": [pygame.K_DOWN, pygame.K_s],  # New control for dropping down
}
