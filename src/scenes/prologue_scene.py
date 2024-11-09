from enum import Enum, auto

import pygame

from scenes.scene import Scene
from systems.asset_manager import AssetManager
from systems.dialog_system import DialogEntry, DialogSystem
from systems.event_system import EventSystem, GameEvent
from ui.components.button import Button


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
        self.dialog_system = DialogSystem()
        self.dialog_system.initialize(game.screen)

        # Subscribe to dialog events to trigger scene transitions
        self.event_system.subscribe(GameEvent.DIALOG_STARTED, self._on_dialog_started)

        # Transition properties
        self.fade_alpha = 255  # Start fully black
        self.fade_surface = pygame.Surface(game.screen.get_size())
        self.fade_surface.fill((0, 0, 0))
        self.is_fading = True
        self.fade_speed = 5
        self.fade_in = True
        self.transitioning = False
        self.next_state = None

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
            if bg:
                self.backgrounds[state] = pygame.transform.scale(bg, screen_size)

        self.current_state = PrologueState.BROADCAST
        self.dialog_sequence = self._init_dialog_sequence()

        # Start the dialog sequence
        self.dialog_system.start_dialog_sequence(
            self.dialog_sequence, on_complete=self._on_prologue_complete
        )

        # Add skip button
        button_width = 100
        button_height = 40
        self.skip_button = Button(
            rect=pygame.Rect(
                game.screen.get_width() - button_width - 20,  # 20px from right edge
                20,  # 20px from top
                button_width,
                button_height,
            ),
            text="Skip",
            action=self._skip_prologue,
            tooltip="Skip the prologue",
        )

    def _init_dialog_sequence(self):
        """Initialize the dialog sequence for the prologue"""
        return [
            DialogEntry(
                character="MAX",
                text="Ladies and gentlemen, visionaries and adventurers, welcome! I'm Maxwell Remington, CEO of NovaForge Industries—the fine folks turning the impossible into yesterday's news.",
            ),
            DialogEntry(
                character="MAX",
                text="Today, I'm thrilled to announce our most ambitious venture yet! We're pushing beyond the final frontier, setting up shop in the great unknown. And guess what? One of you lucky souls has been chosen to lead this glorious expedition!",
            ),
            DialogEntry(
                character="MAX",
                text="Yes, you there! Don't look so surprised. Pack your bags, say your goodbyes, and prepare for the adventure of several lifetimes. Trust me; it's gonna be a blast!",
            ),
            DialogEntry(
                character="EVA",
                text="Greetings, Overseer. I am E.V.A., your Enhanced Virtual Associate. I'll be assisting you on this... 'adventure' mandated by Mr. Remington.",
            ),
            DialogEntry(
                character="EVA",
                text="Your assignment: to establish and manage NovaForge's newest trading outpost on the fringes of known space. Objectives include expansion, resource management, and settler welfare. Survival rate: statistically improbable.",
            ),
            DialogEntry(
                character="EVA",
                text="But don't worry; I'm programmed to increase your odds by approximately 2.7%.",
            ),
            DialogEntry(
                character="MAX",
                text="Ah, there's my favorite Overseer! Ready to make history—or at least a decent footnote? Remember, the universe is your oyster, and we've supplied you with the knife. Well, maybe a spoon. Budget cuts, you understand.",
            ),
            DialogEntry(
                character="MAX",
                text="Anyway, safe travels! And if you stumble upon any priceless artifacts or groundbreaking discoveries, you know who to call!",
            ),
            DialogEntry(
                character="EVA",
                text="Calculating fastest route to designated coordinates.",
            ),
            DialogEntry(
                character="EVA",
                text="Warning: Minor hull damage detected. Cause: Micrometeorite impact. Probability of catastrophic failure: Low. Probability of annoyance: High.",
            ),
            DialogEntry(
                character="EVA",
                text="Entering the Haven Sector. Scans indicate minimal activity—a perfect place for a fresh start or an unmarked grave.",
            ),
            DialogEntry(
                character="MAX",
                text="There she is—the 'Starbreeze'! Isn't she a beauty? Sleek, efficient, and... compact. Perfect for someone who values simplicity. And hey, less space means fewer places for things to go wrong, right?",
            ),
            DialogEntry(
                character="MAX",
                text="Now, I know what you're thinking: 'Didn't he promise me a state-of-the-art vessel?' Think of this as... a hands-on opportunity. After all, what's a journey without a few challenges? You'll be fine! Probably.",
            ),
        ]

    def _on_prologue_complete(self):
        """Handle prologue completion"""
        self.event_system.emit(GameEvent.PROLOGUE_COMPLETED)
        self.event_system.emit(GameEvent.GAME_STATE_CHANGED, new_state="GAMEPLAY")

    def _on_dialog_started(self, event_data):
        """Handle dialog started event"""
        dialog = event_data.data.get("dialog")
        if dialog:
            # Determine which background to show based on dialog progress
            if self.dialog_system.dialog_queue:
                if len(self.dialog_system.dialog_queue) > 10:
                    new_state = PrologueState.BROADCAST
                elif len(self.dialog_system.dialog_queue) > 7:
                    new_state = PrologueState.BRIEFING
                elif len(self.dialog_system.dialog_queue) > 4:
                    new_state = PrologueState.DEPARTURE
                else:
                    new_state = PrologueState.JOURNEY

                if new_state != self.current_state:
                    self.transitioning = True
                    self.fade_in = False
                    self.next_state = new_state

    def _skip_prologue(self):
        """Skip to the end of the prologue"""
        self.event_system.emit(GameEvent.PROLOGUE_COMPLETED)
        self.event_system.emit(GameEvent.GAME_STATE_CHANGED, new_state="GAMEPLAY")

    def update(self):
        """Update scene state"""
        super().update()

        # Handle fade transitions
        if self.is_fading or self.transitioning:
            if self.fade_in:
                self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)
                if self.fade_alpha <= 0:
                    self.is_fading = False
                    self.transitioning = False
            else:
                self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
                if self.fade_alpha >= 255 and self.transitioning:
                    # Complete state transition
                    self.current_state = self.next_state
                    self.fade_in = True

        self.dialog_system.update()

    def handle_event(self, event):
        """Handle input events"""
        # Handle skip button first
        if self.skip_button.handle_event(event):
            return True

        if super().handle_event(event):
            return True
        return self.dialog_system.handle_event(event)

    def draw(self, screen):
        """Draw the current scene"""
        # Draw current background
        if self.current_state in self.backgrounds:
            screen.blit(self.backgrounds[self.current_state], (0, 0))

        # Draw dialog
        self.dialog_system.draw(screen)

        # Draw skip button
        self.skip_button.draw(screen)

        # Draw fade overlay
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            screen.blit(self.fade_surface, (0, 0))
