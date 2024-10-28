import pygame


class ResourceBar:
    def __init__(self, resource_name: str, position: tuple, size: tuple = (200, 20)):
        self.resource_name = resource_name
        self.position = position
        self.size = size
        self.font = pygame.font.Font(None, 24)

        # Color schemes for different resources
        self.colors = {
            "power": {"fill": (255, 215, 0), "bg": (64, 54, 0)},  # Gold
            "oxygen": {"fill": (0, 191, 255), "bg": (0, 48, 64)},  # Deep Sky Blue
            "health": {"fill": (50, 205, 50), "bg": (13, 51, 13)},  # Lime Green
        }

    def draw(self, surface: pygame.Surface, current: float, maximum: float):
        # Draw background
        bg_color = self.colors.get(self.resource_name, {"bg": (50, 50, 50)})["bg"]
        pygame.draw.rect(surface, bg_color, (*self.position, *self.size))

        # Draw fill
        fill_width = int((current / maximum) * self.size[0])
        fill_color = self.colors.get(self.resource_name, {"fill": (200, 200, 200)})[
            "fill"
        ]
        pygame.draw.rect(
            surface, fill_color, (*self.position, fill_width, self.size[1])
        )

        # Draw border
        pygame.draw.rect(surface, (200, 200, 200), (*self.position, *self.size), 1)

        # Draw text
        text = f"{self.resource_name.title()}: {int(current)}/{int(maximum)}"
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_pos = (
            self.position[0] + 5,
            self.position[1] + (self.size[1] - text_surface.get_height()) // 2,
        )
        surface.blit(text_surface, text_pos)
