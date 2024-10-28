import os

from PIL import Image, ImageDraw


def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_player_sprite():
    # Create a 32x32 sprite with a blue rectangle
    size = (32, 32)
    image = Image.new("RGBA", size, (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(image)

    # Draw a blue rectangle with a white border
    draw.rectangle([4, 4, 27, 27], fill=(0, 0, 255), outline=(255, 255, 255))

    return image


def create_room(name, size, color):
    """Create a room with specific dimensions and color"""
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw room with border
    draw.rectangle(
        [0, 0, size[0] - 1, size[1] - 1], fill=color, outline=(100, 100, 100)
    )

    # Add room name text
    draw.text((10, 10), name, fill=(255, 255, 255))

    return image


def create_room_layout():
    """Calculate room sizes and positions relative to ship size"""
    GRID_SIZE = 32  # Match the grid size from RoomBuilder

    # Make ship size multiple of grid size (no border needed)
    SHIP_WIDTH = GRID_SIZE * 20  # 640px
    SHIP_HEIGHT = GRID_SIZE * 15  # 480px

    # Define room sizes as multiples of grid size
    ROOM_WIDTH = GRID_SIZE * 6  # 192px
    ROOM_HEIGHT = GRID_SIZE * 4  # 128px

    room_layouts = {
        "bridge": {
            "size": (ROOM_WIDTH, ROOM_HEIGHT),
            "position": (0, 0),
            "color": (70, 70, 90),
        },
        "engine_room": {
            "size": (ROOM_WIDTH, ROOM_HEIGHT),
            "position": (0.7, 0),  # Top right
            "color": (90, 70, 70),
        },
        "life_support": {
            "size": (ROOM_WIDTH, ROOM_HEIGHT),
            "position": (0, 0.6),  # Bottom left
            "color": (70, 90, 70),
        },
        "medical_bay": {
            "size": (ROOM_WIDTH, ROOM_HEIGHT),
            "position": (0.35, 0.6),  # Bottom middle
            "color": (70, 90, 90),
        },
    }

    # Convert relative positions to absolute positions
    for room_data in room_layouts.values():
        rel_x, rel_y = room_data["position"]
        # Ensure positions snap to grid
        room_data["position"] = (
            int((rel_x * (SHIP_WIDTH - ROOM_WIDTH)) // GRID_SIZE) * GRID_SIZE,
            int((rel_y * (SHIP_HEIGHT - ROOM_HEIGHT)) // GRID_SIZE) * GRID_SIZE,
        )

    return room_layouts


def create_build_icon():
    """Create a build mode icon with a wrench and hammer"""
    size = (32, 32)
    image = Image.new("RGBA", size, (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(image)

    # Draw a simplified wrench shape
    wrench_color = (200, 200, 200)  # Light gray
    wrench_points = [
        (8, 24),
        (12, 20),  # Handle
        (16, 16),
        (20, 20),
        (16, 24),  # Head
        (12, 20),
        (8, 24),  # Complete the shape
    ]
    draw.polygon(wrench_points, fill=wrench_color, outline=(100, 100, 100))

    # Draw a simplified hammer shape
    hammer_color = (180, 180, 180)  # Slightly darker gray
    hammer_points = [
        (16, 8),
        (24, 8),  # Head
        (24, 12),
        (20, 12),  # Head bottom
        (18, 24),
        (14, 24),  # Handle
        (16, 12),
        (16, 8),  # Complete the shape
    ]
    draw.polygon(hammer_points, fill=hammer_color, outline=(100, 100, 100))

    return image


def main():
    # Ensure assets directories exist
    ensure_directory_exists("assets/images")
    ensure_directory_exists("assets/images/rooms")
    ensure_directory_exists("assets/images/ui")

    GRID_SIZE = 32  # Base grid size
    ROOM_WIDTH = GRID_SIZE * 6  # 192px - base room width
    ROOM_HEIGHT = GRID_SIZE * 4  # 128px - base room height

    # Make ship interior 3x3 rooms in size
    ship_size = (
        ROOM_WIDTH * 3,  # 576px width (3 rooms wide)
        ROOM_HEIGHT * 3,  # 384px height (3 rooms tall)
    )
    ship_image = create_room("ship_interior", ship_size, (50, 50, 50))
    ship_image.save("assets/images/ship_interior.png")
    print(f"Ship interior: size={ship_size}")

    # Define standard room size
    room_layouts = {
        "bridge": {
            "size": (ROOM_WIDTH, ROOM_HEIGHT),
            "color": (70, 70, 90),
        },
        "engine_room": {
            "size": (ROOM_WIDTH, ROOM_HEIGHT),
            "color": (90, 70, 70),
        },
        "life_support": {
            "size": (ROOM_WIDTH, ROOM_HEIGHT),
            "color": (70, 90, 70),
        },
        "medical_bay": {
            "size": (ROOM_WIDTH, ROOM_HEIGHT),
            "color": (70, 90, 90),
        },
    }

    # Generate room images
    for room_name, layout in room_layouts.items():
        image = create_room(room_name, layout["size"], layout["color"])
        image.save(f"assets/images/rooms/{room_name}.png")
        print(f"{room_name}: size={layout['size']}")

    # Generate player sprite
    player = create_player_sprite()
    player.save("assets/images/player.png")

    # Generate build icon
    build_icon = create_build_icon()
    build_icon.save("assets/images/ui/build_icon.png")

    print("Placeholder art generated successfully!")


if __name__ == "__main__":
    main()
