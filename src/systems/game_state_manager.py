from enum import Enum, auto

from systems.event_system import EventSystem, GameEvent


class GameState(Enum):
    NORMAL = auto()
    BUILDING = auto()
    PAUSED = auto()
    # Add more states as needed


class GameStateManager:
    def __init__(self):
        self.current_state = GameState.NORMAL
        self.previous_state = None
        self.event_system = EventSystem()

    def set_state(self, new_state: GameState):
        """Change the current game state"""
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state

            # Emit state change event
            self.event_system.emit(
                GameEvent.GAME_STATE_CHANGED,
                new_state=new_state,
                previous_state=self.previous_state,
            )

    def revert_state(self):
        """Revert to previous state"""
        if self.previous_state:
            self.set_state(self.previous_state)
