import random

import pygame

from entities.celestial_object import CelestialObject
from entities.shooting_star import ShootingStar


class StarfieldSystem:
    def __init__(self, screen_size):
        self.background = pygame.Surface(screen_size)
        self.background.fill((0, 0, 0))
        self.objects = []

        # Load sprite sheet
        spritesheet = pygame.image.load("assets/CelestialObjects.png").convert_alpha()

        # Extract sprites
        self.planets = [
            spritesheet.subsurface((i * 64, j * 64, 64, 64))
            for j in range(3)
            for i in range(4)
        ]
        self.moons = [
            spritesheet.subsurface((i * 32, 3 * 64, 32, 32)) for i in range(4)
        ]
        self.dwarf_stars = [
            spritesheet.subsurface((i * 32, 3 * 64 + 32, 32, 32)) for i in range(4)
        ]
        self.stars = [
            spritesheet.subsurface(((4 + i) * 32, 3 * 64 + 32, 32, 32))
            for i in range(4)
        ]
        # Add black holes and nebulae (rightmost column)
        # Black hole is 128x96 at position (384, 0)
        self.black_hole = spritesheet.subsurface((256, 0, 128, 96))
        self.nebulae = spritesheet.subsurface((256, 96, 128, 128))

        self.create_celestial_objects()

        self.camera_x = 0
        self.camera_y = 0
        self.last_camera_x = 0
        self.last_camera_y = 0

        self.shooting_stars = []
        self.shooting_star_timer = 0
        self.shooting_star_delay = random.uniform(1, 3)  # Time between shooting stars
        self.screen_size = screen_size

    def create_celestial_objects(self):
        screen_w = self.background.get_width()
        screen_h = self.background.get_height()

        # Add black holes (very slow rotation, dramatic scale)
        for _ in range(2):
            x = random.randint(0, screen_w)
            y = random.randint(-screen_h, screen_h)
            speed = random.uniform(0.05, 0.1)  # Very slow movement
            self.objects.append(
                CelestialObject(
                    self.black_hole,
                    x,
                    y,
                    speed,
                    scale=3,
                    can_rotate=True,
                    rotation_speed=random.uniform(-0.02, 0.02),  # Slow rotation
                )
            )

        # Add nebulae (large, very slow, slight rotation)
        for _ in range(3):
            x = random.randint(0, screen_w)
            y = random.randint(-screen_h, screen_h)
            speed = random.uniform(0.02, 0.08)  # Extremely slow movement
            self.objects.append(
                CelestialObject(
                    self.nebulae,
                    x,
                    y,
                    speed,
                    scale=4,
                    can_rotate=True,
                    rotation_speed=random.uniform(-0.05, 0.05),  # Very slow rotation
                )
            )

        # Add fast-moving background stars (smallest, fastest)
        for _ in range(145):
            star = random.choice(self.stars)
            x = random.randint(0, screen_w)
            y = random.randint(-screen_h, screen_h)
            # 80% chance of slower speed, 20% chance of very fast speed
            if random.random() < 0.8:
                speed = random.uniform(1.5, 3.0)  # More common slower speed
            else:
                speed = random.uniform(6.0, 12.0)  # Rare but very fast
            self.objects.append(
                CelestialObject(
                    star,
                    x,
                    y,
                    speed,
                    scale=0.4,
                    can_rotate=True,
                    rotation_speed=random.uniform(-2.0, 2.0),  # Fast rotation
                )
            )

        # Add planets (larger, slower, no rotation) (Closer)
        for _ in range(5):
            planet = random.choice(self.planets)
            x = random.randint(0, screen_w)
            y = random.randint(-screen_h, screen_h)
            speed = random.uniform(0.1, 0.3)
            self.objects.append(
                CelestialObject(planet, x, y, speed, scale=0.8, can_rotate=False)
            )

        # Add planets (larger, slower, no rotation) (Farther)
        for _ in range(30):
            planet = random.choice(self.planets)
            x = random.randint(0, screen_w * 3)
            y = random.randint(-screen_h, screen_h)
            speed = random.uniform(0.05, 0.8)
            self.objects.append(
                CelestialObject(planet, x, y, speed, scale=0.2, can_rotate=False)
            )

        # Add moons (medium, medium speed, with rotation)
        for _ in range(8):
            moon = random.choice(self.moons)
            x = random.randint(0, screen_w)
            y = random.randint(-screen_h, screen_h)
            speed = random.uniform(0.3, 0.5)
            self.objects.append(
                CelestialObject(
                    moon,
                    x,
                    y,
                    speed,
                    scale=1.0,
                    can_rotate=True,
                    rotation_speed=random.uniform(-0.8, 0.8),  # Medium rotation
                )
            )

        # Add dwarf stars (small, faster, with rotation)
        for _ in range(12):
            star = random.choice(self.dwarf_stars)
            x = random.randint(0, screen_w)
            y = random.randint(-screen_h, screen_h)
            speed = random.uniform(0.4, 0.6)
            self.objects.append(
                CelestialObject(
                    star,
                    x,
                    y,
                    speed,
                    scale=0.7,
                    can_rotate=True,
                    rotation_speed=random.uniform(-1.5, 1.5),  # Fast rotation
                )
            )

    def update(self, camera_x=0, camera_y=0):
        screen_w = self.background.get_width()

        # Calculate camera movement delta
        dx = camera_x - self.last_camera_x
        dy = camera_y - self.last_camera_y

        for obj in self.objects:
            # Update horizontal position for scrolling
            obj.x += obj.speed
            if obj.x > screen_w:
                obj.x = -obj.image.get_width()

            # Apply parallax effect based on camera movement
            obj.x -= dx * obj.parallax_factor
            obj.y -= dy * obj.parallax_factor

            # Update rotation if applicable
            obj.update()

        # Store camera position for next frame
        self.last_camera_x = camera_x
        self.last_camera_y = camera_y

        # Update shooting star timer
        self.shooting_star_timer -= 1 / 60  # Assuming 60 FPS

        # Create new shooting stars
        if self.shooting_star_timer <= 0:
            # Small chance for a burst of shooting stars
            if random.random() < 0.1:  # 10% chance
                num_stars = random.randint(2, 4)
                for _ in range(num_stars):
                    self.shooting_stars.append(ShootingStar(*self.screen_size))
            else:
                self.shooting_stars.append(ShootingStar(*self.screen_size))

            # Reset timer with random delay
            self.shooting_star_timer = random.uniform(1, 3)

        # Update existing shooting stars
        for star in self.shooting_stars[:]:
            star.update()
            if not star.alive:
                self.shooting_stars.remove(star)

    def draw(self, screen):
        # Draw regular background first
        screen.blit(self.background, (0, 0))

        # Draw celestial objects
        for obj in self.objects:
            rect = obj.image.get_rect(center=(obj.x, obj.y))
            screen.blit(obj.image, rect)

        # Draw shooting stars on top
        for star in self.shooting_stars:
            star.draw(screen)
