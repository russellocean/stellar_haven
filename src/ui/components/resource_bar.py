from typing import Optional, Tuple

import pygame


class ResourceBar:
    def __init__(
        self,
        name: str,
        position: Tuple[int, int],
        width: int = 200,
        height: int = 25,
        color: Tuple[int, int, int] = (255, 255, 255),
        icon_path: Optional[str] = None,
        animation_speed: float = 0.1,
        show_rate: bool = False,
    ):
        self.name = name
        self.x, self.y = position
        self.width = width
        self.height = height
        self.color = color
        self.current_width = 0  # For animation
        self.target_width = 0
        self.animation_speed = animation_speed
        self.show_rate = show_rate
        self.current_rate = 0
        self.target_rate = 0
        self.rate_font = pygame.font.Font(None, height - 8)

        # Setup font
        self.font = pygame.font.Font(None, height - 4)

        # Load and scale icon if provided
        self.icon = None
        self.icon_size = height
        self.icon_padding = 5
        if icon_path:
            try:
                self.icon = pygame.image.load(icon_path).convert_alpha()
                self.icon = pygame.transform.scale(
                    self.icon, (self.icon_size, self.icon_size)
                )
            except pygame.error:
                print(f"Warning: Could not load icon {icon_path}")

        # Calculate bar offset if we have an icon
        self.bar_x_offset = self.icon_size + self.icon_padding if self.icon else 0

        # Visual effects
        self.glow_color = self._lighten_color(color, 50)
        self.dark_color = self._darken_color(color, 50)
        self.flash_alpha = 0
        self.flash_duration = 255
        self.flash_timer = 0

    def _lighten_color(
        self, color: Tuple[int, int, int], amount: int
    ) -> Tuple[int, int, int]:
        """Lighten a color by a given amount"""
        return tuple(min(255, c + amount) for c in color)

    def _darken_color(
        self, color: Tuple[int, int, int], amount: int
    ) -> Tuple[int, int, int]:
        """Darken a color by a given amount"""
        return tuple(max(0, c - amount) for c in color)

    def update(self):
        """Update animations"""
        # Smooth bar width animation
        if self.current_width != self.target_width:
            diff = self.target_width - self.current_width
            self.current_width += diff * self.animation_speed

        # Update flash effect
        if self.flash_timer > 0:
            self.flash_timer -= 1
            self.flash_alpha = int((self.flash_timer / self.flash_duration) * 255)

    def trigger_flash(self):
        """Trigger a flash effect"""
        self.flash_timer = self.flash_duration
        self.flash_alpha = 255

    def update_rate(self, rate: float):
        """Update the resource change rate"""
        self.target_rate = rate
        # Smooth rate changes
        rate_diff = self.target_rate - self.current_rate
        self.current_rate += rate_diff * self.animation_speed

    def draw(self, surface: pygame.Surface, current: float, maximum: float):
        """Draw the resource bar with all effects"""
        # Calculate the target width based on current value
        self.target_width = (current / maximum) * (self.width - self.bar_x_offset)

        # Draw background (darker version of bar color)
        pygame.draw.rect(
            surface,
            self.dark_color,
            (
                self.x + self.bar_x_offset,
                self.y,
                self.width - self.bar_x_offset,
                self.height,
            ),
            border_radius=3,
        )

        # Draw the main bar
        if self.current_width > 0:
            pygame.draw.rect(
                surface,
                self.color,
                (self.x + self.bar_x_offset, self.y, self.current_width, self.height),
                border_radius=3,
            )

            # Draw glow effect
            glow_surface = pygame.Surface(
                (self.current_width, self.height), pygame.SRCALPHA
            )
            pygame.draw.rect(
                glow_surface,
                (*self.glow_color, 100),
                (0, 0, self.current_width, self.height // 2),
                border_radius=3,
            )
            surface.blit(glow_surface, (self.x + self.bar_x_offset, self.y))

        # Draw icon if available
        if self.icon:
            surface.blit(self.icon, (self.x, self.y))

        # Draw text
        text = f"{self.name.title()}: {int(current)}/{int(maximum)}"
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(
            centery=self.y + self.height // 2, x=self.x + self.bar_x_offset + 5
        )
        surface.blit(text_surface, text_rect)

        # Draw flash effect if active
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(
                flash_surface,
                (*self.glow_color, self.flash_alpha),
                (0, 0, self.width, self.height),
                border_radius=3,
            )
            surface.blit(flash_surface, (self.x, self.y))

        # Draw rate if enabled
        if self.show_rate:
            rate_text = f"{self.current_rate:+.1f}/s"
            rate_color = (0, 255, 0) if self.current_rate > 0 else (255, 100, 100)
            if abs(self.current_rate) < 0.01:  # If rate is very close to 0
                rate_color = (200, 200, 200)  # Gray for stable
            rate_surface = self.rate_font.render(rate_text, True, rate_color)
            rate_rect = rate_surface.get_rect(
                midright=(self.x + self.width - 5, self.y + self.height // 2)
            )
            surface.blit(rate_surface, rate_rect)
