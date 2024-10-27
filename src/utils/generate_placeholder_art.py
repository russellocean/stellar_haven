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


def create_ship_interior():
    # Create an 800x400 ship interior
    size = (800, 400)
    image = Image.new("RGBA", size, (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(image)

    # Draw main ship outline
    draw.rectangle([0, 0, 799, 399], fill=(50, 50, 50), outline=(100, 100, 100))

    # Draw some basic room divisions
    draw.line([(200, 0), (200, 399)], fill=(100, 100, 100), width=2)
    draw.line([(400, 0), (400, 399)], fill=(100, 100, 100), width=2)
    draw.line([(600, 0), (600, 399)], fill=(100, 100, 100), width=2)

    return image


def main():
    # Ensure assets directory exists
    assets_path = "assets/images"
    ensure_directory_exists(assets_path)

    # Generate and save player sprite
    player = create_player_sprite()
    player.save(f"{assets_path}/player.png")

    # Generate and save ship interior
    ship = create_ship_interior()
    ship.save(f"{assets_path}/ship_interior.png")

    print("Placeholder art generated successfully!")


if __name__ == "__main__":
    main()
