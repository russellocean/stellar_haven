from enum import Enum, auto
from typing import Callable, Dict, List


class GameState(Enum):
    PLAYING = auto()
    BUILDING = auto()
    PAUSED = auto()
    # Add more states as needed


class GameStateManager:
    def __init__(self):
        self.current_state = GameState.PLAYING
        self.previous_state = None
        self.subscribers: Dict[GameState, List[Callable]] = {
            state: [] for state in GameState
        }

    def set_state(self, new_state: GameState):
        """Change the current game state"""
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state

            # Notify subscribers
            for callback in self.subscribers[new_state]:
                callback(
                    {"new_state": new_state, "previous_state": self.previous_state}
                )

    def subscribe(self, state: GameState, callback: Callable):
        """Subscribe to state changes"""
        self.subscribers[state].append(callback)

    def unsubscribe(self, state: GameState, callback: Callable):
        """Unsubscribe from state changes"""
        if callback in self.subscribers[state]:
            self.subscribers[state].remove(callback)

    def get_state(self) -> GameState:
        """Get the current game state"""
        return self.current_state
