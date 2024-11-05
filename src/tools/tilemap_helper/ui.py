from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDockWidget,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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

        # Toggle Grid Button
        grid_btn = QPushButton("Toggle Grid")
        grid_btn.clicked.connect(self.toggle_grid)
        controls_layout.addWidget(grid_btn)
        controls_layout.addWidget(QLabel("Hotkey: G"))

        # Save Config Button
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_config)
        controls_layout.addWidget(save_btn)
        controls_layout.addWidget(QLabel("Hotkey: Ctrl+S"))

        # Load Config Button
        load_btn = QPushButton("Load Configuration")
        load_btn.clicked.connect(self.load_config)
        controls_layout.addWidget(load_btn)
        controls_layout.addWidget(QLabel("Hotkey: Ctrl+L"))

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
        self.tile_name.textChanged.connect(self.update_metadata)
        metadata_layout.addRow("Name:", self.tile_name)

        # Tile type
        self.tile_type = QComboBox()
        self.tile_type.addItems(["ground", "wall", "decoration", "planet", "custom"])
        self.tile_type.currentTextChanged.connect(self.update_metadata)
        metadata_layout.addRow("Type:", self.tile_type)

        # Multi-tile size
        self.multi_tile_width = QSpinBox()
        self.multi_tile_height = QSpinBox()
        self.multi_tile_width.setRange(1, 16)
        self.multi_tile_height.setRange(1, 16)
        self.multi_tile_width.valueChanged.connect(self.update_multi_tile)
        self.multi_tile_height.valueChanged.connect(self.update_multi_tile)

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
        self.custom_props.textChanged.connect(self.update_metadata)
        metadata_layout.addRow("Properties:", self.custom_props)

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

    def save_config(self):
        """Save current configuration"""
        self.helper.save_config("tilemap_config.json")

    def load_config(self):
        """Load configuration"""
        self.helper.load_config("tilemap_config.json")

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
