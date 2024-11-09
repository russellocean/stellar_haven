from enum import Enum, auto

import pygame

from scenes.scene import Scene
from systems.asset_manager import AssetManager
from systems.event_system import EventSystem, GameEvent
from ui.components.dialog_box import DialogBox


class PrologueState(Enum):
    BROADCAST = auto()
    BRIEFING = auto()
    DEPARTURE = auto()
    JOURNEY = auto()
    COMPLETE = auto()


class PrologueScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.asset_manager = AssetManager()
        self.event_system = EventSystem()

        # Initialize dialog system
        self.dialog_box = DialogBox(game.screen)

        # Load background images
        self.backgrounds = {
            PrologueState.BROADCAST: self.asset_manager.get_image(
                "prologue/Stellar_Haven_Opening_Broadcast.png"
            ),
            PrologueState.BRIEFING: self.asset_manager.get_image(
                "prologue/Stellar_Haven_Briefing.png"
            ),
            PrologueState.DEPARTURE: self.asset_manager.get_image(
                "prologue/Stellar_Haven_Spaceport_Departure.png"
            ),
            PrologueState.JOURNEY: self.asset_manager.get_image(
                "prologue/Stellar_Haven_Journey_Through_Space.png"
            ),
        }

        # Scale backgrounds to fit screen
        screen_size = game.screen.get_size()
        for state, bg in self.backgrounds.items():
            self.backgrounds[state] = pygame.transform.scale(bg, screen_size)

        self.current_state = PrologueState.BROADCAST
        self.dialog_index = 0
        self.dialogs = self._init_dialog_sequence()

        # Start first dialog
        self._show_next_dialog()

    def _init_dialog_sequence(self):
        """Initialize the dialog sequence for the prologue"""
        return [
            # Scene 1: The Broadcast
            (
                PrologueState.BROADCAST,
                "MAX",
                "Ladies and gentlemen, visionaries and adventurers, welcome! I'm Maxwell Remington, CEO of NovaForge Industries—the fine folks turning the impossible into yesterday's news.",
            ),
            (
                PrologueState.BROADCAST,
                "MAX",
                "Today, I'm thrilled to announce our most ambitious venture yet! We're pushing beyond the final frontier, setting up shop in the great unknown. And guess what? One of you lucky souls has been chosen to lead this glorious expedition!",
            ),
            (
                PrologueState.BROADCAST,
                "MAX",
                "Yes, you there! Don't look so surprised. Pack your bags, say your goodbyes, and prepare for the adventure of several lifetimes. Trust me; it's gonna be a blast!",
            ),
            # Scene 2: The Briefing
            (
                PrologueState.BRIEFING,
                "EVA",
                "Greetings, Overseer. I am E.V.A., your Enhanced Virtual Associate. I'll be assisting you on this... 'adventure' mandated by Mr. Remington.",
            ),
            (
                PrologueState.BRIEFING,
                "EVA",
                "Your assignment: to establish and manage NovaForge's newest trading outpost on the fringes of known space. Objectives include expansion, resource management, and settler welfare. Survival rate: statistically improbable.",
            ),
            (
                PrologueState.BRIEFING,
                "EVA",
                "But don't worry; I'm programmed to increase your odds by approximately 2.7%.",
            ),
            # Scene 3: Departure
            (
                PrologueState.DEPARTURE,
                "MAX",
                "Ah, there's my favorite Overseer! Ready to make history—or at least a decent footnote? Remember, the universe is your oyster, and we've supplied you with the knife. Well, maybe a spoon. Budget cuts, you understand.",
            ),
            (
                PrologueState.DEPARTURE,
                "MAX",
                "Anyway, safe travels! And if you stumble upon any priceless artifacts or groundbreaking discoveries, you know who to call!",
            ),
            # Scene 4: Journey Through Space
            (
                PrologueState.JOURNEY,
                "EVA",
                "Calculating fastest route to designated coordinates.",
            ),
            (
                PrologueState.JOURNEY,
                "EVA",
                "Warning: Minor hull damage detected. Cause: Micrometeorite impact. Probability of catastrophic failure: Low. Probability of annoyance: High.",
            ),
            (
                PrologueState.JOURNEY,
                "EVA",
                "Entering the Haven Sector. Scans indicate minimal activity—a perfect place for a fresh start or an unmarked grave.",
            ),
            # Final transition to gameplay
            (
                PrologueState.JOURNEY,
                "MAX",
                "There she is—the 'Starbreeze'! Isn't she a beauty? Sleek, efficient, and... compact. Perfect for someone who values simplicity. And hey, less space means fewer places for things to go wrong, right?",
            ),
            (
                PrologueState.JOURNEY,
                "MAX",
                "Now, I know what you're thinking: 'Didn't he promise me a state-of-the-art vessel?' Think of this as... a hands-on opportunity. After all, what's a journey without a few challenges? You'll be fine! Probably.",
            ),
        ]

    def _show_next_dialog(self):
        """Show the next dialog in the sequence"""
        if self.dialog_index >= len(self.dialogs):
            self.event_system.emit(GameEvent.GAME_STATE_CHANGED, new_state="GAMEPLAY")
            return

        state, character, text = self.dialogs[self.dialog_index]
        self.current_state = state
        self.dialog_box.show_dialog(character, text)

    def handle_event(self, event):
        """Handle input events"""
        if super().handle_event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            self.dialog_index += 1
            self._show_next_dialog()
            return True

        return False

    def draw(self, screen):
        """Draw the current scene"""
        # Draw current background
        if self.current_state in self.backgrounds:
            screen.blit(self.backgrounds[self.current_state], (0, 0))

        # Draw dialog box
        self.dialog_box.draw(screen)
