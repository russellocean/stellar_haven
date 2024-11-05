import random

import pygame


class CelestialObject:
    def __init__(
        self, image, x, y, speed, scale=1.0, can_rotate=False, rotation_speed=None
    ):
        self.original_image = image
        self.scale = scale
        self.image = pygame.transform.scale(
            image, (int(image.get_width() * scale), int(image.get_height() * scale))
        )
        self.x = x
        self.y = y
        self.speed = speed
        self.can_rotate = can_rotate
        self.angle = random.randint(0, 360) if can_rotate else 0
        # Use provided rotation speed or generate random if not provided and can rotate
        self.rotation_speed = (
            rotation_speed
            if rotation_speed is not None
            else (random.uniform(-0.5, 0.5) if can_rotate else 0)
        )
        # Add parallax offset based on speed (slower = further back)
        self.parallax_factor = (
            speed * 0.1
        )  # Objects with higher speed will move more with camera

    def update(self):
        if self.can_rotate:
            self.angle += self.rotation_speed
            # Rotate the scaled image
            self.image = pygame.transform.rotate(
                pygame.transform.scale(
                    self.original_image,
                    (
                        int(self.original_image.get_width() * self.scale),
                        int(self.original_image.get_height() * self.scale),
                    ),
                ),
                self.angle,
            )
