import json
import random
from typing import List

import pygame

from grid.tile_type import TileType
from systems.asset_manager import AssetManager


class AICharacter:
    def __init__(self, x: int, y: int, room_bounds, room_type: str):
        # Physics constants
        self.GRAVITY = 0.5
        self.WALK_SPEED = 1  # Very slow, casual walking speed

        # Initialize position and movement
        self.rect = pygame.Rect(x, y, 20, 30)
        self.velocity = pygame.Vector2(0, 0)
        self.room_bounds = room_bounds
        self.on_ground = False
        self.facing_right = True

        # State management
        self.state = "idle"
        self.state_timer = 0
        self.IDLE_TIME = random.uniform(2.0, 4.0)
        self.WALK_TIME = random.uniform(1.5, 3.0)

        # Load AI character config
        self.asset_manager = AssetManager()
        with open("assets/config/ai_characters.json", "r") as f:
            self.ai_config = json.load(f)

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


class AISystem:
    def __init__(self, room_manager, collision_system):
        self.room_manager = room_manager
        self.collision_system = collision_system
        self.characters: List[AICharacter] = []
        self.camera = None

        # Load room config to determine AI counts
        with open("assets/config/rooms.json", "r") as f:
            self.room_config = json.load(f)

        # Register for room creation events
        room_manager.on_room_added = self.handle_room_added

        # Spawn AIs in existing rooms
        for room_id, room in room_manager.rooms.items():
            self.populate_room(room)

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
            # Bridge needs several officers
            return min(4, max(2, room_area // 32))
        elif room_type == "engine_room":
            # Engine room needs a few engineers
            return min(3, max(1, room_area // 48))
        elif room_type == "life_support":
            # Life support needs 1-2 technicians
            return min(2, max(1, room_area // 64))
        elif room_type == "starting_quarters":
            # Quarters should have a few crew members
            return min(3, max(1, room_area // 48))
        else:
            return 0  # No AIs for other room types

    def set_camera(self, camera):
        self.camera = camera

    def spawn_character(self, x: int, y: int, room_bounds, room_type: str):
        character = AICharacter(x, y, room_bounds, room_type)
        self.characters.append(character)
        return character

    def update(self, delta_time: float):
        for character in self.characters:
            # Update state timer and handle state changes
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

            # Apply gravity if not on ground
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

            # Draw name tag above character
            name_tag_pos = self.camera.world_to_screen(
                character.rect.centerx - character.name_tag.get_width() // 2,
                character.rect.top - character.name_tag.get_height() - 5,
            )
            screen.blit(character.name_tag, name_tag_pos)

        screen.blit(debug_surface, (0, 0))
