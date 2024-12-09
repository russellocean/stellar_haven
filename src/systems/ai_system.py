import json
import random
from typing import List

import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager
from systems.event_system import EventSystem, GameEvent


class AICharacter:
    def __init__(self, x: int, y: int, room_bounds, room_type: str):
        # Physics constants
        self.GRAVITY = 0.5
        self.WALK_SPEED = 1

        # Initialize position and movement
        self.rect = pygame.Rect(x, y, 20, 30)
        self.velocity = pygame.Vector2(0, 0)
        self.room_bounds = room_bounds
        self.on_ground = False
        self.facing_right = True

        # State management
        self.state = "idle"
        self.state_timer = random.uniform(2.0, 4.0)
        self.IDLE_TIME = random.uniform(2.0, 4.0)
        self.WALK_TIME = random.uniform(1.5, 3.0)

        # Load AI character config
        self.asset_manager = AssetManager()
        with open("assets/config/ai_characters.json", "r") as f:
            self.ai_config = json.load(f)
        with open("assets/config/ai_dialogue.json", "r") as f:
            self.dialogue_config = json.load(f)

        # Generate character identity
        self.room_type = room_type
        self.generate_identity()

        # Animation properties
        self.animation_frame = 0
        self.animation_timer = 0
        self.ANIMATION_SPEED = 0.1
        self.last_update = pygame.time.get_ticks()
        self.current_animation = "idle"

        # Load animations
        self.load_animations()

        # Initialize sprite
        self.image = self.animations["idle"][0]
        self.image_rect = self.image.get_rect()
        self.sprite_offset_x = 0
        self.sprite_offset_y = 0

        # Create name tag surface
        self.create_name_tag()

        # Dialogue system
        self.dialogue_timer = 0
        self.dialogue_display_timer = 0
        self.DIALOGUE_DISPLAY_TIME = 4.0
        self.current_dialogue = None
        self.dialogue_surface = None
        self.dialogue_alpha = 0  # For fade effect
        self.name_tag_visible = True
        self.name_tag_alpha = 255
        self.set_next_dialogue_time("idle")

        # Work efficiency
        self.efficiency = self.dialogue_config["behavior"]["work_efficiency"][
            "base_rate"
        ]
        self.mood = "normal"  # Can be "happy", "normal", or "stressed"

    def generate_identity(self):
        """Generate a unique identity for the AI character"""
        room_roles = self.ai_config["room_specific_roles"][self.room_type]
        self.title = random.choice(room_roles["titles"])
        self.first_name = random.choice(self.ai_config["first_names"])
        self.last_name = random.choice(self.ai_config["last_names"])
        self.full_name = f"{self.first_name} {self.last_name}"

    def load_animations(self):
        """Load animations"""
        self.animations = {
            "idle": [
                self.asset_manager.get_image(
                    f"characters/with-helm/idle/sprites/idle{i}.png"
                )
                for i in range(1, 5)
            ],
            "run": [
                self.asset_manager.get_image(
                    f"characters/with-helm/run/sprites/run{i}.png"
                )
                for i in range(1, 11)
            ],
            "jump": [
                self.asset_manager.get_image(
                    f"characters/with-helm/jump-no-gun/sprites/jump-no-gun{i}.png"
                )
                for i in range(1, 7)
            ],
        }

    def create_name_tag(self):
        """Create the name tag surface"""
        style = self.ai_config["name_tag_style"]

        # Create fonts for name and title
        try:
            name_font = pygame.font.SysFont(style["font"], style["name_size"])
            title_font = pygame.font.SysFont(style["font"], style["title_size"])
        except:
            name_font = pygame.font.Font(None, style["name_size"])
            title_font = pygame.font.Font(None, style["title_size"])

        # Create text surfaces with different colors for name and title
        name_surface = name_font.render(self.full_name, True, style["text_color"])
        title_surface = title_font.render(self.title, True, style["title_color"])

        # Calculate background size
        padding = style["padding"]
        width = max(name_surface.get_width(), title_surface.get_width()) + padding * 2
        height = (
            name_surface.get_height()
            + title_surface.get_height()
            + padding * 2
            + style["vertical_spacing"]
        )

        # Create background surface with alpha
        self.name_tag = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw background with outline
        background_color = (*style["background_color"], style["background_alpha"])
        outline_color = (*style["outline_color"], style["background_alpha"])

        # Draw outline
        pygame.draw.rect(
            self.name_tag,
            outline_color,
            (0, 0, width, height),
            border_radius=style["border_radius"],
        )

        # Draw inner background
        pygame.draw.rect(
            self.name_tag,
            background_color,
            (
                style["outline_thickness"],
                style["outline_thickness"],
                width - 2 * style["outline_thickness"],
                height - 2 * style["outline_thickness"],
            ),
            border_radius=style["border_radius"],
        )

        # Blit text onto background
        name_x = (width - name_surface.get_width()) // 2
        title_x = (width - title_surface.get_width()) // 2

        self.name_tag.blit(name_surface, (name_x, padding))
        self.name_tag.blit(
            title_surface,
            (title_x, padding + name_surface.get_height() + style["vertical_spacing"]),
        )

    def set_next_dialogue_time(self, state="idle"):
        """Set the timer for the next dialogue based on state"""
        freq = self.dialogue_config["behavior"]["dialogue_frequency"][
            "alert" if state == "alert" else "idle"
        ]
        self.dialogue_timer = random.uniform(freq["min_time"], freq["max_time"])

    def update_dialogue(self, dt: float, resource_manager):
        """Update dialogue timer and handle transitions"""
        # Update display timer and handle transitions
        if self.dialogue_display_timer > 0:
            self.dialogue_display_timer -= dt

            # Fade in during first 0.3 seconds
            if self.dialogue_display_timer > self.DIALOGUE_DISPLAY_TIME - 0.3:
                self.dialogue_alpha = min(255, self.dialogue_alpha + (dt * 850))
            # Fade out during last 0.3 seconds
            elif self.dialogue_display_timer < 0.3:
                self.dialogue_alpha = max(0, self.dialogue_alpha - (dt * 850))

            if self.dialogue_display_timer <= 0:
                self.dialogue_surface = None
                self.current_dialogue = None
                self.dialogue_alpha = 0

        # Update dialogue generation timer
        if self.dialogue_timer > 0:
            self.dialogue_timer -= dt
            return

        # Time to generate new dialogue
        dialogue_options = []

        # Check resource states for relevant dialogue
        power_level = resource_manager.get_resource_percentage("power")
        oxygen_level = resource_manager.get_resource_percentage("oxygen")

        if (
            power_level < 30
            and "resource_low_power"
            in self.dialogue_config["room_specific_dialogue"][self.room_type]
        ):
            dialogue_options.extend(
                self.dialogue_config["room_specific_dialogue"][self.room_type][
                    "resource_low_power"
                ]
            )
            self.set_next_dialogue_time("alert")
        elif (
            oxygen_level < 30
            and "resource_low_oxygen"
            in self.dialogue_config["room_specific_dialogue"][self.room_type]
        ):
            dialogue_options.extend(
                self.dialogue_config["room_specific_dialogue"][self.room_type][
                    "resource_low_oxygen"
                ]
            )
            self.set_next_dialogue_time("alert")
        else:
            # Use idle dialogue
            dialogue_options.extend(
                self.dialogue_config["room_specific_dialogue"][self.room_type]["idle"]
            )
            self.set_next_dialogue_time("idle")

        if dialogue_options:
            # Select and format dialogue
            dialogue = random.choice(dialogue_options)
            dialogue = dialogue.format(
                power_efficiency=int(power_level), oxygen_level=int(oxygen_level)
            )

            # Create dialogue surface and set display timer
            self.create_dialogue_surface(dialogue)
            self.dialogue_display_timer = self.DIALOGUE_DISPLAY_TIME

    def create_dialogue_surface(self, text: str):
        """Create a surface for the dialogue bubble with alpha channel"""
        font = pygame.font.Font(None, 20)
        padding = 5

        # Create text surface
        text_surface = font.render(text, True, (255, 255, 255))

        # Create bubble surface with padding
        width = text_surface.get_width() + padding * 2
        height = text_surface.get_height() + padding * 2

        # Create main surface and temporary surface for alpha
        self.dialogue_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw background on temp surface
        pygame.draw.rect(
            temp_surface, (0, 0, 0, 180), (0, 0, width, height), border_radius=5
        )

        # Add text to temp surface
        temp_surface.blit(text_surface, (padding, padding))

        # Start with 0 alpha
        self.dialogue_alpha = 0
        self.dialogue_surface = temp_surface
        self.current_dialogue = text

    def get_work_efficiency(self) -> float:
        """Get the current work efficiency of the character"""
        if self.mood == "happy":
            return (
                self.efficiency
                * self.dialogue_config["behavior"]["work_efficiency"][
                    "happy_multiplier"
                ]
            )
        elif self.mood == "stressed":
            return (
                self.efficiency
                * self.dialogue_config["behavior"]["work_efficiency"][
                    "stressed_multiplier"
                ]
            )
        return self.efficiency


class AISystem:
    def __init__(self, room_manager, collision_system):
        self.room_manager = room_manager
        self.collision_system = collision_system
        self.characters: List[AICharacter] = []
        self.camera = None
        self.event_system = EventSystem()
        self.player = None  # Will store reference to player
        self.name_tag_fade_distance = 150  # Distance at which name tags start fading

        # Load room config to determine AI counts
        with open("assets/config/rooms.json", "r") as f:
            self.room_config = json.load(f)

        # Register for room creation events
        room_manager.on_room_added = self.handle_room_added

        # Register for resource events
        self.event_system.subscribe(GameEvent.RESOURCE_LOW, self._handle_resource_low)
        self.event_system.subscribe(
            GameEvent.RESOURCE_CRITICAL, self._handle_resource_critical
        )
        self.event_system.subscribe(
            GameEvent.RESOURCE_RESTORED, self._handle_resource_restored
        )

        # Spawn AIs in existing rooms
        for room_id, room in room_manager.rooms.items():
            self.populate_room(room)

    def set_player(self, player):
        """Set the player reference for distance calculations"""
        self.player = player

    def _handle_resource_low(self, event_data):
        """Handle low resource event"""
        resource = event_data.resource if hasattr(event_data, "resource") else None
        if resource:
            for character in self.characters:
                if character.room_type in ["engine_room", "life_support", "bridge"]:
                    character.mood = "stressed"
                    character.set_next_dialogue_time("alert")

    def _handle_resource_critical(self, event_data):
        """Handle critical resource event"""
        resource = event_data.resource if hasattr(event_data, "resource") else None
        if resource:
            for character in self.characters:
                character.mood = "stressed"
                character.set_next_dialogue_time("alert")

    def _handle_resource_restored(self, event_data):
        """Handle resource restored event"""
        resource = event_data.resource if hasattr(event_data, "resource") else None
        if resource:
            for character in self.characters:
                character.mood = "happy"
                character.set_next_dialogue_time("idle")

    def handle_room_added(self, room):
        """Called when a new room is added to the ship"""
        self.populate_room(room)

    def populate_room(self, room):
        """Populate a room with appropriate number of AIs"""
        # Get room data from grid
        room_data = self.room_manager.grid.rooms[room.room_id]
        grid_pos = room_data["grid_pos"]
        grid_size = room_data["grid_size"]

        # Calculate room boundaries in world coordinates
        left = grid_pos[0] * self.room_manager.grid.cell_size
        right = (grid_pos[0] + grid_size[0]) * self.room_manager.grid.cell_size

        # Add margin to keep AI away from walls
        margin = self.room_manager.grid.cell_size * 1.5
        room_bounds = {"left": left + margin, "right": right - margin}

        # Determine number of AIs based on room type
        num_ais = self._get_ai_count_for_room(room.room_type)

        if num_ais > 0:
            # Calculate spawn positions spread across the room
            room_width = right - left - (2 * margin)
            spacing = room_width / (num_ais + 1)

            for i in range(num_ais):
                spawn_x = left + margin + spacing * (i + 1)
                spawn_y = self.room_manager.get_room_center(room)[1]
                self.spawn_character(spawn_x, spawn_y, room_bounds, room.room_type)

    def _get_ai_count_for_room(self, room_type: str) -> int:
        """Determine how many AIs should be in each room type"""
        room_config = self.room_config["room_types"][room_type]
        grid_size = room_config["grid_size"]
        room_area = grid_size[0] * grid_size[1]

        # Define AI counts based on room type and size
        if room_type == "bridge":
            # Bridge is restricted - no AI characters
            return 0
        elif room_type == "engine_room":
            # Engine room needs a few engineers
            return min(3, max(1, room_area // 48))
        elif room_type == "life_support":
            # Life support needs 1-2 technicians
            return min(2, max(1, room_area // 64))
        elif room_type == "starting_quarters":
            # Quarters should have a few crew members
            return min(3, max(1, room_area // 48))
        elif room_type == "research_lab":
            # Research lab needs scientists
            return min(3, max(1, room_area // 40))
        elif room_type == "medical_bay":
            # Medical bay needs medical staff
            return min(3, max(1, room_area // 48))
        elif room_type == "cargo_bay":
            # Cargo bay needs workers
            return min(2, max(1, room_area // 64))
        else:
            return 0  # No AIs for other room types

    def set_camera(self, camera):
        self.camera = camera

    def spawn_character(self, x: int, y: int, room_bounds, room_type: str):
        character = AICharacter(x, y, room_bounds, room_type)
        self.characters.append(character)
        return character

    def update(self, delta_time: float):
        """Update all AI characters"""
        resource_manager = self.room_manager.resource_manager

        if not self.player:
            return

        # First update all character states and physics
        for character in self.characters:
            # Update character state
            if character.state_timer > 0:
                character.state_timer -= delta_time
                if character.state_timer <= 0:
                    if character.state == "idle":
                        character.state = "walking"
                        character.state_timer = character.WALK_TIME
                        character.facing_right = random.choice([True, False])
                        character.velocity.x = (
                            character.WALK_SPEED
                            if character.facing_right
                            else -character.WALK_SPEED
                        )
                    else:
                        character.state = "idle"
                        character.state_timer = character.IDLE_TIME
                        character.velocity.x = 0

            # Update dialogue
            character.update_dialogue(delta_time, resource_manager)

            # Apply character efficiency to room resources
            if character.room_type in ["engine_room", "life_support"]:
                matching_rooms = [
                    room
                    for room in self.room_manager.rooms.values()
                    if room.room_type == character.room_type
                ]
                if matching_rooms and hasattr(matching_rooms[0], "resource_generators"):
                    room = matching_rooms[0]
                    efficiency = character.get_work_efficiency()
                    for resource, base_rate in room.resource_generators.items():
                        if not hasattr(room, "_original_rates"):
                            room._original_rates = {}
                        if resource not in room._original_rates:
                            room._original_rates[resource] = base_rate
                        room.resource_generators[resource] = (
                            room._original_rates[resource] * efficiency
                        )

            # Update physics
            if not character.on_ground:
                character.velocity.y += character.GRAVITY

            # Check room bounds
            if character.rect.centerx >= character.room_bounds["right"]:
                character.rect.centerx = character.room_bounds["right"]
                character.facing_right = False
                character.velocity.x = (
                    -character.WALK_SPEED if character.state == "walking" else 0
                )
            elif character.rect.centerx <= character.room_bounds["left"]:
                character.rect.centerx = character.room_bounds["left"]
                character.facing_right = True
                character.velocity.x = (
                    character.WALK_SPEED if character.state == "walking" else 0
                )

            # Update position with collision detection
            can_move, new_pos = self.collision_system.check_movement(
                character.rect, character.velocity, dropping=False
            )

            if can_move:
                character.rect.centerx = new_pos.x
                character.rect.bottom = new_pos.y
            else:
                if abs(character.velocity.x) > 0:
                    character.facing_right = not character.facing_right
                    character.velocity.x = (
                        character.WALK_SPEED
                        if character.facing_right
                        else -character.WALK_SPEED
                    )
                if character.velocity.y > 0:
                    character.velocity.y = 0
                    character.on_ground = True

            self._check_ground_state(character)
            self._update_character_animation(character, delta_time)

        # Then handle name tag visibility separately
        characters_with_distance = []
        for character in self.characters:
            dist = (
                (character.rect.centerx - self.player.rect.centerx) ** 2
                + (character.rect.centery - self.player.rect.centery) ** 2
            ) ** 0.5
            characters_with_distance.append((character, dist))

        # Sort by distance
        characters_with_distance.sort(key=lambda x: x[1])

        # Update name tag visibility based on distance and overlap
        visible_tags = []
        for character, dist in characters_with_distance:
            # Calculate target alpha based on distance
            if dist < self.name_tag_fade_distance:
                target_alpha = 255
            else:
                fade_factor = min(1.0, (dist - self.name_tag_fade_distance) / 150.0)
                target_alpha = max(0, int(255 * (1 - fade_factor)))

            # Check for overlap with visible tags
            tag_rect = pygame.Rect(
                character.rect.centerx - character.name_tag.get_width() // 2,
                character.rect.top - character.name_tag.get_height() - 5,
                character.name_tag.get_width(),
                character.name_tag.get_height(),
            )

            overlapping = False
            for visible_tag in visible_tags:
                if tag_rect.colliderect(visible_tag):
                    overlapping = True
                    break

            if overlapping:
                target_alpha = 0
            else:
                visible_tags.append(tag_rect)

            # Smoothly transition alpha
            if target_alpha > character.name_tag_alpha:
                character.name_tag_alpha = min(
                    target_alpha, character.name_tag_alpha + (delta_time * 510)
                )
            elif target_alpha < character.name_tag_alpha:
                character.name_tag_alpha = max(
                    target_alpha, character.name_tag_alpha - (delta_time * 510)
                )

    def _check_ground_state(self, character: AICharacter):
        if character.velocity.y < 0:
            character.on_ground = False
            return

        grid_x, grid_y = self.room_manager.grid.world_to_grid(
            character.rect.centerx, character.rect.bottom + 1
        )
        tile = self.room_manager.grid.get_tile(grid_x, grid_y)

        if tile and (tile.blocks_movement or tile == TileType.PLATFORM):
            character.on_ground = True
        else:
            character.on_ground = False

    def _update_character_animation(self, character: AICharacter, delta_time: float):
        now = pygame.time.get_ticks()
        elapsed = (now - character.last_update) / 1000.0
        character.animation_timer += elapsed
        character.last_update = now

        if not character.on_ground:
            character.current_animation = "jump"
            if character.velocity.y < 0:
                character.animation_frame = 0
            else:
                character.animation_frame = 3
        elif character.state == "walking":
            character.current_animation = "run"
            if character.animation_timer >= character.ANIMATION_SPEED:
                character.animation_frame = (character.animation_frame + 1) % len(
                    character.animations["run"]
                )
                character.animation_timer = 0
        else:
            character.current_animation = "idle"
            if character.animation_timer >= character.ANIMATION_SPEED:
                character.animation_frame = (character.animation_frame + 1) % len(
                    character.animations["idle"]
                )
                character.animation_timer = 0

        max_frames = len(character.animations[character.current_animation]) - 1
        character.animation_frame = min(character.animation_frame, max_frames)

        current_frame = character.animations[character.current_animation][
            character.animation_frame
        ]
        if not character.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        character.image = current_frame

        character.image_rect = character.image.get_rect()
        character.image_rect.centerx = (
            character.rect.centerx + character.sprite_offset_x
        )
        character.image_rect.bottom = character.rect.bottom + character.sprite_offset_y

    def draw(self, screen: pygame.Surface):
        if not self.camera:
            return

        debug_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        for character in self.characters:
            # Draw character sprite
            screen_pos = self.camera.world_to_screen(
                character.image_rect.x, character.image_rect.y
            )
            screen.blit(character.image, screen_pos)

            # Draw name tag with alpha
            if character.name_tag_alpha > 0:
                name_tag_with_alpha = character.name_tag.copy()
                name_tag_with_alpha.set_alpha(character.name_tag_alpha)
                name_tag_pos = self.camera.world_to_screen(
                    character.rect.centerx - character.name_tag.get_width() // 2,
                    character.rect.top - character.name_tag.get_height() - 5,
                )
                screen.blit(name_tag_with_alpha, name_tag_pos)

            # Draw dialogue bubble with alpha
            if character.dialogue_surface and character.dialogue_alpha > 0:
                dialogue_with_alpha = character.dialogue_surface.copy()
                dialogue_with_alpha.set_alpha(character.dialogue_alpha)
                dialogue_pos = self.camera.world_to_screen(
                    character.rect.centerx
                    - character.dialogue_surface.get_width() // 2,
                    character.rect.top
                    - character.name_tag.get_height()
                    - character.dialogue_surface.get_height()
                    - 10,
                )
                screen.blit(dialogue_with_alpha, dialogue_pos)

        screen.blit(debug_surface, (0, 0))
