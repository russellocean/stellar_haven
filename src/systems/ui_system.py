from typing import List

import pygame


class UISystem:
    def __init__(self):
        self.elements: List = []
        self.active = True

    def add_element(self, element):
        self.elements.append(element)

    def remove_element(self, element):
        if element in self.elements:
            self.elements.remove(element)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for all UI elements, return True if handled"""
        if not self.active:
            return False

        # Handle events in reverse order (top-most first)
        for element in reversed(self.elements):
            if element.handle_event(event):
                return True
        return False

    def draw(self, surface: pygame.Surface):
        """Draw all UI elements"""
        if not self.active:
            return

        for element in self.elements:
            element.draw(surface)
