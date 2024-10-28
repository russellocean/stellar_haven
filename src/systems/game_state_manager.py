from enum import Enum, auto
from typing import Callable, Dict


class GameState(Enum):
    NORMAL = auto()
    BUILDING = auto()
    PAUSED = auto()
    # Add more states as needed


class GameStateManager:
    def __init__(self):
        self.current_state = GameState.NORMAL
        self.previous_state = None
        self.state_handlers: Dict[GameState, Callable] = {}
        self.on_state_change_callbacks = []

    def register_state_handler(self, state: GameState, handler: Callable):
        """Register a handler function for a specific state"""
        self.state_handlers[state] = handler

    def on_state_change(self, callback: Callable):
        """Register a callback for state changes"""
        self.on_state_change_callbacks.append(callback)

    def set_state(self, new_state: GameState):
        """Change the current game state"""
        if new_state != self.current_state:
            self.current_state = new_state

        # Notify all callbacks
        for callback in self.on_state_change_callbacks:
            callback(new_state, self.previous_state)

        # Execute state handler if exists
        if new_state in self.state_handlers:
            self.state_handlers[new_state]()

    def revert_state(self):
        """Revert to previous state"""
        if self.previous_state:
            self.set_state(self.previous_state)
