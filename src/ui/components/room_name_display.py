import pygame


class RoomNameDisplay:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.current_text = ""
        self.target_text = ""
        self.display_time = 0
        self.fade_duration = 1000  # 1 second fade
        self.display_duration = 2000  # 2 seconds display
        self.alpha = 0
        self.rect = pygame.Rect(0, 0, 200, 50)

    def show_room_name(self, room_name: str):
        """Show a new room name"""
        self.target_text = room_name
        self.current_text = room_name
        self.display_time = pygame.time.get_ticks()
        self.alpha = 255

    def update(self):
        """Update the display animation"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.display_time

        if elapsed < self.fade_duration:
            # Fade in
            self.alpha = int(255 * (elapsed / self.fade_duration))
        elif elapsed < self.display_duration:
            # Full display
            self.alpha = 255
        elif elapsed < self.display_duration + self.fade_duration:
            # Fade out
            fade_progress = (elapsed - self.display_duration) / self.fade_duration
            self.alpha = int(255 * (1 - fade_progress))
        else:
            # Hidden
            self.alpha = 0

    def draw(self, surface: pygame.Surface):
        """Draw the room name"""
        if self.alpha > 0:
            text_surface = self.font.render(self.current_text, True, (255, 255, 255))
            text_surface.set_alpha(self.alpha)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
