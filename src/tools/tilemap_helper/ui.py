from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDockWidget,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class TilemapUI(QMainWindow):
    def __init__(self, tilemap_helper):
        super().__init__()
        self.helper = tilemap_helper
        self.setup_ui()

    def setup_ui(self):
        """Initialize all UI elements"""
        self.setWindowTitle("Tilemap Helper Controls")
        self.setup_controls()
        self.setup_metadata()
        self.setup_window()

    def setup_controls(self):
        """Setup the controls dock"""
        self.controls_dock = QDockWidget("Controls", self)
        controls = QWidget()
        controls_layout = QVBoxLayout()

        # Load Tilemap Button
        load_tilemap_btn = QPushButton("Load Tilemap")
        load_tilemap_btn.clicked.connect(self.load_new_tilemap)
        controls_layout.addWidget(load_tilemap_btn)
        controls_layout.addWidget(QLabel("Load a different tilemap"))

        # Toggle Grid Button
        grid_btn = QPushButton("Toggle Grid")
        grid_btn.clicked.connect(self.toggle_grid)
        controls_layout.addWidget(grid_btn)
        controls_layout.addWidget(QLabel("Hotkey: G"))

        # Navigation hints
        controls_layout.addWidget(QLabel("\nNavigation:"))
        controls_layout.addWidget(QLabel("Left Click: Select/deselect tiles"))
        controls_layout.addWidget(QLabel("Middle Click + Drag: Pan view"))
        controls_layout.addWidget(QLabel("Mouse Wheel: Zoom in/out"))

        # Add tile size controls
        size_group = QGroupBox("Tile Size")
        size_layout = QFormLayout()
        self.tile_size_input = QSpinBox()
        self.tile_size_input.setRange(8, 256)
        self.tile_size_input.setValue(32)
        self.tile_size_input.valueChanged.connect(self.update_tile_size)
        size_layout.addRow("Tile Size (px):", self.tile_size_input)
        size_group.setLayout(size_layout)
        controls_layout.addWidget(size_group)

        controls.setLayout(controls_layout)
        self.controls_dock.setWidget(controls)
        self.addDockWidget(Qt.RightDockWidgetArea, self.controls_dock)

    def setup_metadata(self):
        """Setup the metadata dock"""
        self.metadata_dock = QDockWidget("Tile Properties", self)
        metadata = QWidget()
        metadata_layout = QFormLayout()

        # Tile position info
        self.pos_label = QLabel("No tile selected")
        metadata_layout.addRow("Position:", self.pos_label)

        # Tile name
        self.tile_name = QLineEdit()
        metadata_layout.addRow("Name:", self.tile_name)

        # Tile type
        self.tile_type = QComboBox()
        self.tile_type.addItems(["ground", "wall", "decoration", "planet", "custom"])
        manage_types_btn = QPushButton("Manage Types")
        manage_types_btn.clicked.connect(self.manage_types)
        metadata_layout.addRow("", manage_types_btn)
        metadata_layout.addRow("Type:", self.tile_type)

        # Multi-tile size
        self.multi_tile_width = QSpinBox()
        self.multi_tile_height = QSpinBox()
        self.multi_tile_width.setRange(1, 16)
        self.multi_tile_height.setRange(1, 16)

        multi_size = QWidget()
        multi_layout = QHBoxLayout()
        multi_layout.addWidget(QLabel("W:"))
        multi_layout.addWidget(self.multi_tile_width)
        multi_layout.addWidget(QLabel("H:"))
        multi_layout.addWidget(self.multi_tile_height)
        metadata_layout.addRow("Multi-tile:", multi_size)

        # Custom properties
        self.custom_props = QLineEdit()
        self.custom_props.setPlaceholderText("key1:value1,key2:value2")
        metadata_layout.addRow("Properties:", self.custom_props)

        # Add Tile Group Button
        save_group_btn = QPushButton("Add Tile Group")
        save_group_btn.clicked.connect(self.save_tile_group)
        metadata_layout.addRow("", save_group_btn)

        metadata.setLayout(metadata_layout)
        self.metadata_dock.setWidget(metadata)
        self.addDockWidget(Qt.RightDockWidgetArea, self.metadata_dock)

    def setup_window(self):
        """Setup window properties"""
        self.resize(250, 400)
        self.move(100, 100)

    def toggle_grid(self):
        """Toggle grid visibility"""
        self.helper.grid_visible = not self.helper.grid_visible
        self.helper.save_state()  # Save state when grid visibility changes

    def update_tile_size(self):
        """Update the tile size in the helper"""
        self.helper.tile_size = self.tile_size_input.value()

    def update_metadata(self):
        """Update metadata for selected tiles"""
        if not self.helper.selected_tiles:
            return

        metadata = {
            "name": self.tile_name.text(),
            "type": self.tile_type.currentText(),
            "width": self.multi_tile_width.value(),
            "height": self.multi_tile_height.value(),
            "properties": self._parse_custom_props(),
        }

        # Update all selected tiles with the same metadata
        for tile_pos in self.helper.selected_tiles:
            self.helper.tile_configs[str(tile_pos)] = metadata

    def _parse_custom_props(self):
        """Parse custom properties string into dictionary"""
        props = {}
        text = self.custom_props.text().strip()
        if text:
            try:
                pairs = text.split(",")
                for pair in pairs:
                    key, value = pair.split(":")
                    props[key.strip()] = value.strip()
            except ValueError:
                QMessageBox.warning(self, "Warning", "Invalid property format")
        return props

    def update_multi_tile(self):
        """Handle multi-tile selection changes"""
        width = self.multi_tile_width.value()
        height = self.multi_tile_height.value()
        self.helper.set_multi_tile_size(width, height)

    def update_selected_position(self, pos=None):
        """Update the position label for selected tile"""
        if pos:
            self.pos_label.setText(f"({pos[0]}, {pos[1]})")
        else:
            self.pos_label.setText("No tile selected")

    def load_new_tilemap(self):
        """Open file dialog to load a new tilemap"""
        # Get the assets directory
        project_root = (
            Path(self.helper.tilemap_path).parent.parent.parent
            if self.helper.tilemap_path
            else None
        )
        assets_dir = project_root / "assets" / "tilemaps" if project_root else None

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Tilemap",
            str(assets_dir) if assets_dir else "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)",
        )

        if file_path:
            # Load the new tilemap
            if self.helper.load_tilemap(file_path):
                # Reset UI elements
                self.tile_size_input.setValue(32)  # Reset to default tile size
                self.multi_tile_width.setValue(1)  # Reset multi-tile size
                self.multi_tile_height.setValue(1)
                self.tile_name.clear()  # Clear metadata fields
                self.custom_props.clear()
                self.tile_type.setCurrentIndex(0)

                QMessageBox.information(
                    self, "Success", "New tilemap loaded successfully!"
                )
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to load the selected tilemap!"
                )

    def save_tile_group(self):
        """Save the current selection as a tile group"""
        if not self.helper.selected_tiles:
            QMessageBox.warning(self, "Warning", "No tiles selected!")
            return

        if not self.tile_name.text().strip():
            QMessageBox.warning(
                self, "Warning", "Please provide a name for the tile group!"
            )
            return

        # Create metadata for the tile group
        metadata = {
            "name": self.tile_name.text(),
            "type": self.tile_type.currentText(),
            "width": self.multi_tile_width.value(),
            "height": self.multi_tile_height.value(),
            "properties": self._parse_custom_props(),
        }

        # Add the tile group to configuration
        self.helper.add_tile_group(self.helper.selected_tiles.copy(), metadata)

        # Clear selection and form
        self.helper.selected_tiles.clear()
        self.clear_metadata_form()

        QMessageBox.information(self, "Success", "Tile group added successfully!")

    def clear_metadata_form(self):
        """Clear all metadata form fields"""
        self.tile_name.clear()
        self.tile_type.setCurrentIndex(0)
        self.multi_tile_width.setValue(1)
        self.multi_tile_height.setValue(1)
        self.custom_props.clear()
        self.pos_label.setText("No tile selected")

    def manage_types(self):
        """Open type manager dialog"""
        dialog = TypeManagerDialog(self, self.helper.tile_types)
        if dialog.exec_():
            new_types = dialog.get_types()
            if new_types:  # Don't allow empty type list
                print(f"New types: {new_types}")
                # Update helper's types and save to config
                self.helper.save_tile_types(new_types)
                # Update UI combobox
                self.update_tile_types(new_types)

    def update_tile_types(self, types: list):
        """Update the tile type combo box"""
        current = self.tile_type.currentText()
        self.tile_type.clear()
        self.tile_type.addItems(types)

        # Try to restore previous selection
        index = self.tile_type.findText(current)
        if index >= 0:
            self.tile_type.setCurrentIndex(index)


class TypeManagerDialog(QDialog):
    def __init__(self, parent=None, current_types=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Tile Types")
        self.setModal(True)
        self.setup_ui(current_types or [])

    def setup_ui(self, current_types):
        layout = QVBoxLayout()

        # Type list
        self.type_list = QListWidget()
        self.type_list.addItems(current_types)
        layout.addWidget(self.type_list)

        # Action buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Type")
        add_btn.clicked.connect(self.add_type)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove Type")
        remove_btn.clicked.connect(self.remove_type)
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)

        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        ok_btn = QPushButton("Done")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        dialog_buttons.addWidget(ok_btn)
        dialog_buttons.addWidget(cancel_btn)
        layout.addLayout(dialog_buttons)

        self.setLayout(layout)

    def add_type(self):
        new_type, ok = QInputDialog.getText(self, "Add Type", "Enter new tile type:")
        if ok and new_type:
            if new_type not in [
                self.type_list.item(i).text() for i in range(self.type_list.count())
            ]:
                item = QListWidgetItem(new_type)
                self.type_list.addItem(item)
            else:
                QMessageBox.warning(self, "Warning", "Type already exists!")

    def remove_type(self):
        current = self.type_list.currentItem()
        if current:
            self.type_list.takeItem(self.type_list.row(current))

    def get_types(self):
        return [self.type_list.item(i).text() for i in range(self.type_list.count())]
