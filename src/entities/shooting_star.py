import math
import random

import pygame


class ShootingStar:
    def __init__(self, screen_width, screen_height):
        # Create a trail of points
        self.length = random.randint(20, 40)
        self.speed = random.uniform(15, 25)
        self.thickness = random.uniform(1.5, 3)
        # Randomize starting position (always start from left side of screen)
        self.x = random.randint(-100, 0)
        self.y = random.randint(0, screen_height)

        # Random angle (mostly rightward)
        self.angle = random.uniform(-30, 30)  # -30 to 30 degrees for rightward motion
        self.dx = self.speed * math.cos(math.radians(self.angle))
        self.dy = self.speed * math.sin(math.radians(self.angle))

        # Trail effect
        self.points = [(self.x, self.y)]
        self.alive = True

        # Add subtle color variation
        base_color = random.randint(200, 255)
        self.color = (base_color, base_color, random.randint(220, 255))

        # Fade effect
        self.alpha = 255
        self.fade_speed = random.uniform(3, 7)

    def update(self):
        # Move the shooting star
        self.x += self.dx
        self.y += self.dy

        # Add new point to trail
        self.points.append((self.x, self.y))

        # Remove old points to maintain trail length
        if len(self.points) > self.length:
            self.points.pop(0)

        # Fade out
        self.alpha -= self.fade_speed
        if self.alpha <= 0:
            self.alive = False

    def draw(self, screen):
        if len(self.points) < 2:
            return

        # Create a surface for the trail with alpha support
        trail_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        # Draw the trail with fade effect
        for i in range(len(self.points) - 1):
            start_pos = self.points[i]
            end_pos = self.points[i + 1]

            # Calculate alpha for this segment
            segment_alpha = int(self.alpha * (i / len(self.points)))

            # Draw the trail segment with alpha
            pygame.draw.line(
                trail_surface,
                (*self.color, segment_alpha),
                start_pos,
                end_pos,
                int(self.thickness * (i / len(self.points) + 0.5)),
            )

        screen.blit(trail_surface, (0, 0))
