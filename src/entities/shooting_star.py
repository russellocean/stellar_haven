import math
import random

import pygame


class ShootingStar:
    # Class-level surface cache
    _trail_surface = None
    _trail_size = (0, 0)

    def __init__(self, screen_width, screen_height):
        # Initialize shared surface if needed
        if ShootingStar._trail_surface is None or ShootingStar._trail_size != (
            screen_width,
            screen_height,
        ):
            ShootingStar._trail_surface = pygame.Surface(
                (screen_width, screen_height), pygame.SRCALPHA
            )
            ShootingStar._trail_size = (screen_width, screen_height)

        # Optimized initialization
        self.length = random.randint(10, 20)  # Reduced length
        self.speed = random.uniform(15, 25)
        self.thickness = random.uniform(1.5, 3)
        self.x = random.randint(-100, 0)
        self.y = random.randint(0, screen_height)

        # Precalculate angle calculations
        angle = random.uniform(-30, 30)
        self.dx = self.speed * math.cos(math.radians(angle))
        self.dy = self.speed * math.sin(math.radians(angle))

        # Use deque for better performance with fixed length
        from collections import deque

        self.points = deque([(self.x, self.y)], maxlen=self.length)

        self.alive = True

        # Simplified color (reduce random calls)
        base_color = random.randint(200, 255)
        self.color = (base_color, base_color, 255)

        # Optimized fade
        self.alpha = 255
        self.fade_speed = random.uniform(5, 10)  # Slightly faster fade

    def update(self):
        # Move the shooting star
        self.x += self.dx
        self.y += self.dy
        self.points.append((self.x, self.y))

        # Simplified fade
        self.alpha -= self.fade_speed
        self.alive = self.alpha > 0

    def draw(self, screen):
        if len(self.points) < 2:
            return

        # Clear the shared surface
        ShootingStar._trail_surface.fill((0, 0, 0, 0))

        # Draw fewer segments with optimized alpha
        points = list(self.points)  # Convert deque to list for indexing
        num_segments = min(len(points) - 1, 8)  # Limit number of segments
        step = max(1, (len(points) - 1) // num_segments)

        for i in range(0, len(points) - 1, step):
            segment_alpha = int(self.alpha * (i / len(points)))
            if segment_alpha <= 0:
                continue

            pygame.draw.line(
                ShootingStar._trail_surface,
                (*self.color, segment_alpha),
                points[i],
                points[i + 1],
                int(self.thickness * (i / len(points) + 0.5)),
            )

        screen.blit(ShootingStar._trail_surface, (0, 0))
