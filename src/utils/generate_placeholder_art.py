import os

from PIL import Image, ImageDraw, ImageFont


def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_tile(size, color, text="", border_color=(100, 100, 100)):
    """Create a basic tile with text"""
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw filled rectangle with border
    draw.rectangle([0, 0, size[0] - 1, size[1] - 1], fill=color, outline=border_color)

    # Add text if provided
    if text:
        font = ImageFont.load_default()
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        draw.text((x, y), text, fill=(255, 255, 255), font=font)

    return image


def main():
    TILE_SIZE = 32

    # Create directory structure
    ensure_directory_exists("assets/rooms/framework")
    ensure_directory_exists("assets/rooms/interiors")
    ensure_directory_exists("assets/rooms/decorations/bridge")
    ensure_directory_exists("assets/rooms/decorations/engine_room")
    ensure_directory_exists("assets/rooms/decorations/life_support")
    ensure_directory_exists("assets/characters")

    # Generate framework pieces - all single tile size for consistency
    framework_pieces = {
        "wall_horizontal.png": ((TILE_SIZE, TILE_SIZE), (80, 80, 80), "═"),
        "wall_vertical.png": ((TILE_SIZE, TILE_SIZE), (80, 80, 80), "║"),
        "corner_top_left.png": ((TILE_SIZE, TILE_SIZE), (90, 90, 90), "╔"),
        "corner_top_right.png": ((TILE_SIZE, TILE_SIZE), (90, 90, 90), "╗"),
        "corner_bottom_left.png": ((TILE_SIZE, TILE_SIZE), (90, 90, 90), "╚"),
        "corner_bottom_right.png": ((TILE_SIZE, TILE_SIZE), (90, 90, 90), "╝"),
        "door_horizontal_left.png": ((TILE_SIZE, TILE_SIZE), (100, 70, 70), "D═"),
        "door_horizontal_right.png": ((TILE_SIZE, TILE_SIZE), (100, 70, 70), "═D"),
        "door_vertical_top.png": ((TILE_SIZE, TILE_SIZE), (100, 70, 70), "D"),
        "door_vertical_bottom.png": ((TILE_SIZE, TILE_SIZE), (100, 70, 70), "D"),
    }

    for filename, (size, color, text) in framework_pieces.items():
        image = create_tile(size, color, text)
        image.save(f"assets/rooms/framework/{filename}")
        print(f"Generated: framework/{filename}")

    # Generate interior pieces
    interior_pieces = {
        "floor_base.png": ((TILE_SIZE, TILE_SIZE), (50, 50, 50), "·"),
        "wall_base.png": ((TILE_SIZE, TILE_SIZE), (70, 70, 70), "#"),
    }

    for filename, (size, color, text) in interior_pieces.items():
        image = create_tile(size, color, text)
        image.save(f"assets/rooms/interiors/{filename}")
        print(f"Generated: interiors/{filename}")

    # Generate bridge decorations
    bridge_pieces = {
        "console_left.png": ((TILE_SIZE, TILE_SIZE), (70, 70, 100), "CO"),
        "console_right.png": ((TILE_SIZE, TILE_SIZE), (70, 70, 100), "NS"),
        "captain_chair.png": ((TILE_SIZE, TILE_SIZE), (100, 100, 70), "CAP"),
    }

    for filename, (size, color, text) in bridge_pieces.items():
        image = create_tile(size, color, text)
        image.save(f"assets/rooms/decorations/bridge/{filename}")
        print(f"Generated: decorations/bridge/{filename}")

    # Generate engine room decorations
    engine_pieces = {
        "engine_top_left.png": ((TILE_SIZE, TILE_SIZE), (100, 70, 70), "E1"),
        "engine_top_right.png": ((TILE_SIZE, TILE_SIZE), (100, 70, 70), "E2"),
        "engine_bottom_left.png": ((TILE_SIZE, TILE_SIZE), (100, 70, 70), "E3"),
        "engine_bottom_right.png": ((TILE_SIZE, TILE_SIZE), (100, 70, 70), "E4"),
        "console_left.png": ((TILE_SIZE, TILE_SIZE), (70, 70, 100), "CO"),
        "console_right.png": ((TILE_SIZE, TILE_SIZE), (70, 70, 100), "NS"),
        "pipes_top.png": ((TILE_SIZE, TILE_SIZE), (100, 70, 100), "P1"),
        "pipes_bottom.png": ((TILE_SIZE, TILE_SIZE), (100, 70, 100), "P2"),
    }

    for filename, (size, color, text) in engine_pieces.items():
        image = create_tile(size, color, text)
        image.save(f"assets/rooms/decorations/engine_room/{filename}")
        print(f"Generated: decorations/engine_room/{filename}")

    # Generate life support decorations
    life_support_pieces = {
        "oxygen_generator_left.png": ((TILE_SIZE, TILE_SIZE), (70, 100, 70), "O2"),
        "oxygen_generator_right.png": ((TILE_SIZE, TILE_SIZE), (70, 100, 70), "GN"),
        "filter_top.png": ((TILE_SIZE, TILE_SIZE), (70, 100, 100), "F1"),
        "filter_bottom.png": ((TILE_SIZE, TILE_SIZE), (70, 100, 100), "F2"),
    }

    for filename, (size, color, text) in life_support_pieces.items():
        image = create_tile(size, color, text)
        image.save(f"assets/rooms/decorations/life_support/{filename}")
        print(f"Generated: decorations/life_support/{filename}")

    # Generate player character
    player_states = {
        "idle.png": ((TILE_SIZE, TILE_SIZE), (0, 255, 0), "P"),
        "walk_1.png": ((TILE_SIZE, TILE_SIZE), (0, 240, 0), "P1"),
        "walk_2.png": ((TILE_SIZE, TILE_SIZE), (0, 240, 0), "P2"),
        "interact.png": ((TILE_SIZE, TILE_SIZE), (0, 220, 0), "PI"),
    }

    for filename, (size, color, text) in player_states.items():
        image = create_tile(size, color, text)
        image.save(f"assets/characters/{filename}")
        print(f"Generated: characters/{filename}")

    print("\nPlaceholder art generated successfully!")
    print("Note: Framework pieces use ASCII box-drawing characters for clarity")
    print("Note: Player character is represented by green 'P' tiles")


if __name__ == "__main__":
    main()
