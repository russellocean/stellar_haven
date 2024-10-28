import pygame

from systems.event_system import EventSystem, GameEvent
from systems.game_state_manager import GameState
from systems.room_manager import RoomManager
from ui.components.toggle_button import ToggleButton
from ui.layouts.build_menu import BuildMenu
from ui.layouts.room_builder_layout import RoomBuilderLayout


class BuildingSystem:
    def __init__(self, screen: pygame.Surface, room_manager: RoomManager):
        self.screen = screen
        self.room_manager = room_manager
        self.active = False
        self.state_manager = None
        self.input_manager = None
        self.camera = None

        # Initialize components
        self.room_builder = RoomBuilderLayout(screen)
        self.room_builder.ship_rect = room_manager.ship_room.rect

        # Create build mode toggle button
        toggle_rect = pygame.Rect(20, 20, 60, 60)
        self.toggle_button = ToggleButton(
            rect=toggle_rect,
            text="Build",
            action=self.toggle_building_mode,
            image_path="assets/images/ui/build_icon.png",
        )

        # Initialize UI layouts
        self.build_menu = BuildMenu(screen=screen, on_select=self.select_room_type)

        # Subscribe to relevant events
        self.event_system = EventSystem()
        self.event_system.subscribe(
            GameEvent.GAME_STATE_CHANGED, self._handle_state_change
        )

    def set_state_manager(self, state_manager):
        """Set the state manager reference"""
        self.state_manager = state_manager

    def toggle_building_mode(self):
        """Toggle building mode on/off"""
        if self.active:
            self.disable()
        else:
            self.enable()

        # Update game state after toggling
        if self.state_manager:
            from systems.game_state_manager import GameState

            new_state = GameState.BUILDING if self.active else GameState.NORMAL
            self.state_manager.set_state(new_state)

    def enable(self):
        """Enable building mode"""
        self.active = True
        self.build_menu.visible = True
        self.toggle_button.set_toggled(True)
        self.room_builder.visible = True

    def disable(self):
        """Disable building mode"""
        self.active = False
        self.build_menu.visible = False
        self.room_builder.selected_room_type = None
        self.toggle_button.set_toggled(False)
        self.room_builder.visible = False

    def select_room_type(self, room_type: str):
        """Handle room selection from build menu"""
        self.room_builder.select_room_type(room_type)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle building-related events"""
        if not self.active:
            return False

        # Handle room placement
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if (
                self.room_builder.selected_room_type
                and self.room_builder.valid_placement
            ):
                self.room_manager.add_room(
                    self.room_builder.selected_room_type,
                    *self.room_builder.ghost_room.rect.topleft
                )
                return True
        return False

    def update(self):
        """Update building system state"""
        if not self.active:
            return

        if self.room_builder.selected_room_type:
            # Add camera offset to mouse position
            mouse_pos = pygame.mouse.get_pos()
            world_pos = (
                mouse_pos[0] + self.camera.offset_x,
                mouse_pos[1] + self.camera.offset_y,
            )
            self.room_builder.update(world_pos, self.room_manager.get_rooms())

    def draw(self, screen: pygame.Surface):
        """Draw building-specific elements"""
        if not self.active:
            return

        if self.room_builder.selected_room_type:
            # Apply camera offset to ghost room
            ghost_rect = self.camera.apply(self.room_builder.ghost_room.rect)
            screen.blit(self.room_builder.ghost_room.image, ghost_rect)

    def set_input_manager(self, input_manager):
        """Set the input manager reference"""
        self.input_manager = input_manager

    def set_camera(self, camera):
        """Set the camera reference"""
        self.camera = camera

    def _handle_state_change(self, event_data):
        """Handle game state changes"""
        new_state = event_data.data["new_state"]
        if new_state == GameState.BUILDING:
            self.active = True
        else:
            self.active = False

    def place_room(self, room_type: str, position: tuple):
        """Place a room and emit event"""
        room = self.room_builder.build_room(room_type, position)
        if room:
            self.room_manager.add_room(room)
            self.event_system.emit(
                GameEvent.ROOM_BUILT, room=room, room_type=room_type, position=position
            )
