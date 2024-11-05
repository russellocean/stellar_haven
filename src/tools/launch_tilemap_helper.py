#!/usr/bin/env python3

import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QFileDialog

# Get the absolute path to src directory
src_dir = Path(__file__).parent.parent.absolute()
project_root = src_dir.parent
assets_dir = project_root / "assets" / "tilemaps"

sys.path.insert(0, str(src_dir))

from tools.tilemap_helper import TilemapHelper


def print_controls():
    """Print control information to console"""
    print("Tilemap loaded successfully!")
    print("\nControls:")
    print("- Left click: Select/deselect tiles")
    print("- Middle click + drag: Pan view")
    print("- Mouse wheel: Zoom in/out")
    print("- G: Toggle grid")


def select_tilemap() -> str:
    """Open a file dialog to select a tilemap"""
    # Create the tilemaps directory if it doesn't exist
    assets_dir.mkdir(parents=True, exist_ok=True)

    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select Tilemap",
        str(assets_dir),
        "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)",
    )

    return file_path


def main():
    # Create QApplication first
    app = QApplication(sys.argv)

    # Show file dialog before creating helper
    file_path = select_tilemap()

    # Create helper with the existing QApplication
    helper = TilemapHelper(app)

    if file_path:
        if helper.load_tilemap(file_path):
            print_controls()
        else:
            print("Failed to load selected tilemap!")
    else:
        print("No tilemap selected. Starting with empty canvas.")

    helper.run()


if __name__ == "__main__":
    main()
