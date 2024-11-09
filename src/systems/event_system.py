from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List


class GameEvent(Enum):
    # Room Events
    ROOM_BUILT = auto()
    ROOM_DESTROYED = auto()
    ROOM_ENTERED = auto()
    ROOM_EXITED = auto()
    ROOM_DAMAGED = auto()
    ROOM_REPAIRED = auto()

    # Resource Events
    RESOURCE_DEPLETED = auto()
    RESOURCE_RESTORED = auto()
    RESOURCE_UPDATED = auto()

    # Game State Events
    GAME_STATE_CHANGED = auto()
    BUILD_MODE_TOGGLED = auto()

    # Player Events
    PLAYER_MOVED = auto()
    PLAYER_INTERACTED = auto()

    # Alert Events
    ALERT_TRIGGERED = auto()
    RESOURCE_CRITICAL = auto()
    RESOURCE_WARNING = auto()
    RESOURCE_LOW = auto()

    # Dialog Events
    DIALOG_STARTED = auto()
    DIALOG_ENDED = auto()
    PROLOGUE_COMPLETED = auto()


@dataclass
class EventData:
    """Container for event data"""

    event_type: GameEvent
    data: Dict[str, Any]


class EventSystem:
    _instance = None

    def __new__(cls):
        # Singleton pattern
        if cls._instance is None:
            cls._instance = super(EventSystem, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not self._initialized:
            self._handlers: Dict[GameEvent, List[Callable]] = {}
            self._initialized = True

    def subscribe(self, event: GameEvent, handler: Callable) -> None:
        """Subscribe to an event"""
        if event not in self._handlers:
            self._handlers[event] = []
        if handler not in self._handlers[event]:
            self._handlers[event].append(handler)

    def unsubscribe(self, event: GameEvent, handler: Callable) -> None:
        """Unsubscribe from an event"""
        if event in self._handlers and handler in self._handlers[event]:
            self._handlers[event].remove(handler)

    def emit(self, event: GameEvent, **kwargs) -> None:
        """Emit an event with optional data"""
        if event in self._handlers:
            event_data = EventData(event_type=event, data=kwargs)
            for handler in self._handlers[event]:
                handler(event_data)

    def clear_event(self, event: GameEvent) -> None:
        """Clear all handlers for an event"""
        if event in self._handlers:
            self._handlers[event] = []

    def clear_all(self) -> None:
        """Clear all event handlers"""
        self._handlers = {}
