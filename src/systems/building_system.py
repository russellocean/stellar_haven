from typing import Optional

import pygame

from systems.room_manager import RoomManager
from ui.build_menu import BuildMenu
from ui.room_builder import RoomBuilder
from ui.toggle_button import ToggleButton


class BuildingSystem:
    def __init__(self, screen: pygame.Surface, room_manager: RoomManager):
        self.screen = screen
        self.room_manager = room_manager
        self.building_mode = False

        # Initialize UI components
        self.build_menu = BuildMenu(screen, self.on_room_selected)
        self.room_builder = RoomBuilder(screen)
        # Pass ship room rect to room builder instead of ship_rect
        self.room_builder.ship_rect = room_manager.ship_room.rect

        # Create build mode toggle button with action callback
        button_size = 40
        self.toggle_button = ToggleButton(
            10,  # x position
            10,  # y position
            button_size,  # size
            "Build",  # text shown below button
            self.toggle_building_mode,  # action callback
            "assets/images/ui/build_icon.png",  # icon
        )

    def on_room_selected(self, room_type: str):
        """Handle room selection from the build menu"""
        self.room_builder.select_room_type(room_type)

    def toggle_building_mode(self, force_state: Optional[bool] = None):
        print("toggle_building_mode", force_state)
        """Toggle or set building mode"""
        if force_state is not None:
            self.building_mode = force_state
        else:
            self.building_mode = not self.building_mode

        self.build_menu.visible = self.building_mode
        self.toggle_button.toggled = self.building_mode

        if not self.building_mode:
            self.room_builder.selected_room_type = None

    def handle_event(self, event: pygame.event.Event):
        """Handle building-related events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:  # Keyboard shortcut
                self.toggle_building_mode()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check for room placement if in building mode and have selected room
            if self.building_mode and self.room_builder.selected_room_type:
                if self.room_builder.valid_placement:
                    print(
                        "Placing room at:", self.room_builder.ghost_room.rect.topleft
                    )  # Debug
                    new_room = self.room_manager.add_room(
                        self.room_builder.selected_room_type,
                        *self.room_builder.ghost_room.rect.topleft
                    )
                    if new_room:
                        print("Room placed successfully")  # Debug
                    else:
                        print("Failed to place room")  # Debug
            else:
                # Handle toggle button click
                self.toggle_button.update(mouse_pos, True)

                # Handle build menu clicks if visible
                if self.building_mode:
                    self.build_menu.update(mouse_pos, True)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            self.toggle_button.update(mouse_pos, False)

    def update(self):
        """Update building system state"""
        mouse_pos = pygame.mouse.get_pos()

        # Update toggle button hover state
        self.toggle_button.update(mouse_pos, False)

        # Update room builder with current mouse position
        if self.building_mode and self.room_builder.selected_room_type:
            self.room_builder.update(mouse_pos, self.room_manager.get_rooms())

    def draw(self):
        """Draw all building-related UI"""
        # Draw the build menu and room builder first
        if self.building_mode:
            self.build_menu.draw()
            self.room_builder.draw()  # This will draw the ghost room

        # Draw the toggle button on top
        self.toggle_button.draw(self.screen)

        # Draw the cursor circle
        pygame.draw.circle(self.screen, (255, 255, 255), pygame.mouse.get_pos(), 5)
