from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple

import pygame

from systems.event_system import EventSystem, GameEvent
from ui.components.dialog_box import DialogBox


class DialogState(Enum):
    INACTIVE = auto()
    PLAYING = auto()
    WAITING = auto()
    COMPLETE = auto()


@dataclass
class DialogEntry:
    character: str
    text: str
    delay: float = 0


class DialogSystem:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DialogSystem, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.event_system = EventSystem()
            self.dialog_box = None
            self.dialog_queue: List[DialogEntry] = []
            self.current_dialog: Optional[DialogEntry] = None
            self.state = DialogState.INACTIVE
            self.delayed_dialogs: List[Tuple[float, List[DialogEntry]]] = []
            self.timer: float = 0
            self._initialized = True
            self.on_complete_callback = None

    def initialize(self, screen):
        """Initialize the dialog box"""
        self.dialog_box = DialogBox(screen)

    def start_dialog_sequence(self, dialogs: List[DialogEntry], on_complete=None):
        """Start a new dialog sequence"""
        self.dialog_queue = dialogs.copy()
        self.state = DialogState.PLAYING
        self.on_complete_callback = on_complete
        self._show_next_dialog()

    def _show_next_dialog(self):
        """Show the next dialog in the queue"""
        if not self.dialog_queue:
            self.state = DialogState.INACTIVE
            self.event_system.emit(GameEvent.DIALOG_ENDED)
            if self.on_complete_callback:
                self.on_complete_callback()
            return

        self.current_dialog = self.dialog_queue.pop(0)
        self.dialog_box.show_dialog(
            self.current_dialog.character, self.current_dialog.text
        )
        self.state = DialogState.PLAYING
        self.event_system.emit(GameEvent.DIALOG_STARTED, dialog=self.current_dialog)

    def update(self):
        """Update the dialog system"""
        if self.state != DialogState.INACTIVE and self.dialog_box:
            self.dialog_box.update()

            # Check if current dialog is complete
            if self.state == DialogState.PLAYING and not self.dialog_box.is_animating:
                self.state = DialogState.WAITING

        # Handle delayed dialog sequences
        if self.delayed_dialogs:
            self.timer += 1 / 60  # Assuming 60 FPS, adjust as needed
            delay, dialogs = self.delayed_dialogs[0]
            if self.timer >= delay:
                self.start_dialog_sequence(dialogs)
                self.delayed_dialogs.pop(0)
                self.timer = 0

    def handle_event(self, event) -> bool:
        """Handle input events"""
        if self.state == DialogState.INACTIVE:
            return False

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            if self.state == DialogState.PLAYING:
                # Skip current dialog animation
                self.dialog_box.skip_animation()
                self.state = DialogState.WAITING
                return True
            elif self.state == DialogState.WAITING:
                # Move to next dialog
                self._show_next_dialog()
                return True

        return False

    def draw(self, surface):
        """Draw the dialog box"""
        if self.state != DialogState.INACTIVE and self.dialog_box:
            self.dialog_box.draw(surface)

    def is_active(self) -> bool:
        """Check if dialog system is currently active"""
        return self.state != DialogState.INACTIVE

    def schedule_dialog_sequence(self, dialogs: List[DialogEntry], delay: float):
        """Schedule a dialog sequence to start after a delay (in seconds)"""
        self.delayed_dialogs.append((delay, dialogs))
