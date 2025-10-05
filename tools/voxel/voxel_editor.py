"""
Voxel editor window
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QLabel, QSpinBox, QComboBox, QPushButton,
    QColorDialog, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QMouseEvent
import logging

from .voxel_grid import VoxelGrid, VoxelColor
from .voxel_brush import VoxelBrush, BrushType, BrushMode

logger = logging.getLogger(__name__)


class VoxelViewport(QWidget):
    """3D voxel viewport"""
    
    def __init__(self, grid: VoxelGrid, brush: VoxelBrush):
        super().__init__()
        self.grid = grid
        self.brush = brush
        
        self.setMinimumSize(600, 600)
        self.setMouseTracking(True)
        
        # Camera
        self.camera_rotation = [45, 45]  # pitch, yaw
        self.camera_distance = 100
        self.camera_target = [grid.size // 2, grid.size // 2, grid.size // 2]
        
        # Interaction
        self.is_painting = False
        self.last_mouse_pos = QPoint()
    
    def paintEvent(self, event):
        """Render voxel grid"""
        painter = QPainter(self)
        
        # Background
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        # Draw grid (simple 2D projection for now)
        # TODO: Implement proper 3D rendering with OpenGL/ModernGL
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        voxel_size = 8
        
        # Draw filled voxels
        voxels = self.grid.get_filled_voxels()
        
        for x, y, z, color in voxels:
            # Simple isometric projection
            screen_x = center_x + (x - z) * voxel_size
            screen_y = center_y + (x + z) * voxel_size // 2 - y * voxel_size
            
            qcolor = QColor(color.r, color.g, color.b, color.a)
            painter.fillRect(screen_x, screen_y, voxel_size, voxel_size, qcolor)
            
            # Draw outline
            painter.setPen(QColor(0, 0, 0, 100))
            painter.drawRect(screen_x, screen_y, voxel_size, voxel_size)
        
        # Draw info
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(10, 20, f"Voxels: {len(voxels)}")
        painter.drawText(10, 40, f"Grid Size: {self.grid.size}x{self.grid.size}x{self.grid.size}")
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.is_painting = True
            self._paint_at_mouse(event.pos())
        elif event.button() == Qt.RightButton:
            self.last_mouse_pos = event.pos()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        if self.is_painting:
            self._paint_at_mouse(event.pos())
        elif event.buttons() & Qt.RightButton:
            # Rotate camera
            delta = event.pos() - self.last_mouse_pos
            self.camera_rotation[1] += delta.x() * 0.5
            self.camera_rotation[0] += delta.y() * 0.5
            self.last_mouse_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.is_painting = False
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y()
        self.camera_distance -= delta * 0.1
        self.camera_distance = max(10, min(500, self.camera_distance))
        self.update()
    
    def _paint_at_mouse(self, pos: QPoint):
        """Paint voxel at mouse position"""
        # TODO: Implement proper ray casting for 3D picking
        # For now, paint at center of grid
        center = self.grid.size // 2
        self.brush.apply(self.grid, center, center, center)
        self.update()


class VoxelEditorWindow(QMainWindow):
    """Voxel editor main window"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
        self.grid = VoxelGrid(size=32)
        self.brush = VoxelBrush()
        
        self.setWindowTitle("Voxel Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        self._setup_ui()
        self._setup_toolbar()
    
    def _setup_ui(self):
        """Setup UI"""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout()
        central.setLayout(layout)
        
        # Viewport
        self.viewport = VoxelViewport(self.grid, self.brush)
        layout.addWidget(self.viewport, stretch=1)
        
        # Side panel
        side_panel = self._create_side_panel()
        layout.addWidget(side_panel)
    
    def _create_side_panel(self) -> QWidget:
        """Create side panel with tools"""
        panel = QWidget()
        panel.setMaximumWidth(250)
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Brush settings
        layout.addWidget(QLabel("<b>Brush</b>"))
        
        # Brush type
        layout.addWidget(QLabel("Type:"))
        self.brush_type_combo = QComboBox()
        for brush_type in BrushType:
            self.brush_type_combo.addItem(brush_type.value)
        self.brush_type_combo.currentTextChanged.connect(self._on_brush_type_changed)
        layout.addWidget(self.brush_type_combo)
        
        # Brush mode
        layout.addWidget(QLabel("Mode:"))
        self.brush_mode_combo = QComboBox()
        for brush_mode in BrushMode:
            self.brush_mode_combo.addItem(brush_mode.value)
        self.brush_mode_combo.currentTextChanged.connect(self._on_brush_mode_changed)
        layout.addWidget(self.brush_mode_combo)
        
        # Brush size
        layout.addWidget(QLabel("Size:"))
        self.brush_size_spin = QSpinBox()
        self.brush_size_spin.setRange(1, 10)
        self.brush_size_spin.setValue(1)
        self.brush_size_spin.valueChanged.connect(self._on_brush_size_changed)
        layout.addWidget(self.brush_size_spin)
        
        # Color picker
        layout.addWidget(QLabel("<b>Color</b>"))
        self.color_btn = QPushButton("Pick Color")
        self.color_btn.clicked.connect(self._on_pick_color)
        layout.addWidget(self.color_btn)
        
        # Grid settings
        layout.addWidget(QLabel("<b>Grid</b>"))
        
        clear_btn = QPushButton("Clear Grid")
        clear_btn.clicked.connect(self._on_clear_grid)
        layout.addWidget(clear_btn)
        
        # Export
        layout.addWidget(QLabel("<b>Export</b>"))
        
        export_mesh_btn = QPushButton("Export Mesh")
        export_mesh_btn.clicked.connect(self._on_export_mesh)
        layout.addWidget(export_mesh_btn)
        
        export_vox_btn = QPushButton("Export .vox")
        export_vox_btn.clicked.connect(self._on_export_vox)
        layout.addWidget(export_vox_btn)
        
        layout.addStretch()
        
        return panel
    
    def _setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # File actions
        new_action = toolbar.addAction("New")
        new_action.triggered.connect(self._on_new)
        
        open_action = toolbar.addAction("Open")
        open_action.triggered.connect(self._on_open)
        
        save_action = toolbar.addAction("Save")
        save_action.triggered.connect(self._on_save)
    
    def _on_brush_type_changed(self, text: str):
        """Handle brush type change"""
        self.brush.brush_type = BrushType(text)
    
    def _on_brush_mode_changed(self, text: str):
        """Handle brush mode change"""
        self.brush.brush_mode = BrushMode(text)
    
    def _on_brush_size_changed(self, value: int):
        """Handle brush size change"""
        self.brush.size = value
    
    def _on_pick_color(self):
        """Pick brush color"""
        color = QColorDialog.getColor()
        if color.isValid():
            voxel_color = VoxelColor(color.red(), color.green(), color.blue(), 255)
            color_index = self.grid.add_color(voxel_color)
            self.brush.color_index = color_index
            
            # Update button color
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def _on_clear_grid(self):
        """Clear voxel grid"""
        reply = QMessageBox.question(
            self, "Clear Grid",
            "Are you sure you want to clear the entire grid?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.grid.clear()
            self.viewport.update()
    
    def _on_export_mesh(self):
        """Export as mesh"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Mesh", "", "GLTF Files (*.gltf);;GLB Files (*.glb)"
        )
        
        if filename:
            mesh_data = self.grid.bake_to_mesh()
            logger.info(f"Exporting mesh to {filename}")
            # TODO: Implement actual mesh export using pygltflib
            QMessageBox.information(self, "Export", "Mesh export not yet implemented")
    
    def _on_export_vox(self):
        """Export as .vox file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export VOX", "", "MagicaVoxel Files (*.vox)"
        )
        
        if filename:
            logger.info(f"Exporting .vox to {filename}")
            # TODO: Implement .vox export
            QMessageBox.information(self, "Export", ".vox export not yet implemented")
    
    def _on_new(self):
        """Create new voxel grid"""
        self.grid = VoxelGrid(size=32)
        self.viewport.grid = self.grid
        self.viewport.update()
    
    def _on_open(self):
        """Open voxel file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Voxel File", "", "All Files (*.*)"
        )
        
        if filename:
            logger.info(f"Opening {filename}")
            # TODO: Implement file loading
    
    def _on_save(self):
        """Save voxel file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Voxel File", "", "All Files (*.*)"
        )
        
        if filename:
            logger.info(f"Saving to {filename}")
            # TODO: Implement file saving
