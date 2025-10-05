"""
Low-poly mesh editor window
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QLabel, QPushButton, QComboBox,
    QDoubleSpinBox, QFileDialog, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QMouseEvent
import logging
import numpy as np

from .mesh_data import Mesh
from .mesh_operations import MeshOperations

logger = logging.getLogger(__name__)


class MeshViewport(QWidget):
    """3D mesh viewport"""
    
    def __init__(self, mesh: Mesh):
        super().__init__()
        self.mesh = mesh
        
        self.setMinimumSize(600, 600)
        self.setMouseTracking(True)
        
        # Camera
        self.camera_rotation = [30, 45]
        self.camera_distance = 5
        
        # Interaction
        self.last_mouse_pos = QPoint()
    
    def paintEvent(self, event):
        """Render mesh"""
        painter = QPainter(self)
        
        # Background
        painter.fillRect(self.rect(), QColor(40, 40, 45))
        
        # Draw mesh (simple wireframe for now)
        # TODO: Implement proper 3D rendering with OpenGL
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        scale = 50
        
        if not self.mesh.vertices:
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignCenter, "No mesh loaded\nAdd a primitive to start")
            return
        
        # Simple orthographic projection
        painter.setPen(QColor(100, 200, 255))
        
        # Draw edges
        for face in self.mesh.faces:
            points = []
            for idx in face.vertex_indices:
                if idx < len(self.mesh.vertices):
                    pos = self.mesh.vertices[idx].position
                    # Simple 2D projection
                    x = center_x + int(pos[0] * scale)
                    y = center_y - int(pos[1] * scale)
                    points.append(QPoint(x, y))
            
            # Draw face edges
            for i in range(len(points)):
                next_i = (i + 1) % len(points)
                painter.drawLine(points[i], points[next_i])
        
        # Draw vertices
        painter.setPen(QColor(255, 255, 100))
        for i, vertex in enumerate(self.mesh.vertices):
            pos = vertex.position
            x = center_x + int(pos[0] * scale)
            y = center_y - int(pos[1] * scale)
            
            if i in self.mesh.selected_vertices:
                painter.setBrush(QColor(255, 200, 0))
            else:
                painter.setBrush(QColor(100, 200, 255))
            
            painter.drawEllipse(QPoint(x, y), 4, 4)
        
        # Draw info
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(10, 20, f"Vertices: {len(self.mesh.vertices)}")
        painter.drawText(10, 40, f"Faces: {len(self.mesh.faces)}")
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.RightButton:
            self.last_mouse_pos = event.pos()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        if event.buttons() & Qt.RightButton:
            delta = event.pos() - self.last_mouse_pos
            self.camera_rotation[1] += delta.x() * 0.5
            self.camera_rotation[0] += delta.y() * 0.5
            self.last_mouse_pos = event.pos()
            self.update()
    
    def wheelEvent(self, event):
        """Handle mouse wheel"""
        delta = event.angleDelta().y()
        self.camera_distance -= delta * 0.01
        self.camera_distance = max(1, min(20, self.camera_distance))
        self.update()


class MeshEditorWindow(QMainWindow):
    """Low-poly mesh editor window"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
        self.mesh = Mesh()
        
        self.setWindowTitle("Mesh Editor")
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
        self.viewport = MeshViewport(self.mesh)
        layout.addWidget(self.viewport, stretch=1)
        
        # Side panel
        side_panel = self._create_side_panel()
        layout.addWidget(side_panel)
    
    def _create_side_panel(self) -> QWidget:
        """Create side panel"""
        panel = QWidget()
        panel.setMaximumWidth(250)
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Primitives
        primitives_group = QGroupBox("Primitives")
        primitives_layout = QVBoxLayout()
        primitives_group.setLayout(primitives_layout)
        
        cube_btn = QPushButton("Add Cube")
        cube_btn.clicked.connect(lambda: self._add_primitive("cube"))
        primitives_layout.addWidget(cube_btn)
        
        sphere_btn = QPushButton("Add Sphere")
        sphere_btn.clicked.connect(lambda: self._add_primitive("sphere"))
        primitives_layout.addWidget(sphere_btn)
        
        cylinder_btn = QPushButton("Add Cylinder")
        cylinder_btn.clicked.connect(lambda: self._add_primitive("cylinder"))
        primitives_layout.addWidget(cylinder_btn)
        
        plane_btn = QPushButton("Add Plane")
        plane_btn.clicked.connect(lambda: self._add_primitive("plane"))
        primitives_layout.addWidget(plane_btn)
        
        layout.addWidget(primitives_group)
        
        # Operations
        ops_group = QGroupBox("Operations")
        ops_layout = QVBoxLayout()
        ops_group.setLayout(ops_layout)
        
        extrude_btn = QPushButton("Extrude")
        extrude_btn.clicked.connect(self._on_extrude)
        ops_layout.addWidget(extrude_btn)
        
        subdivide_btn = QPushButton("Subdivide")
        subdivide_btn.clicked.connect(self._on_subdivide)
        ops_layout.addWidget(subdivide_btn)
        
        layout.addWidget(ops_group)
        
        # Transform
        transform_group = QGroupBox("Transform")
        transform_layout = QVBoxLayout()
        transform_group.setLayout(transform_layout)
        
        transform_layout.addWidget(QLabel("Scale:"))
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.1, 10.0)
        self.scale_spin.setValue(1.0)
        self.scale_spin.setSingleStep(0.1)
        transform_layout.addWidget(self.scale_spin)
        
        scale_btn = QPushButton("Apply Scale")
        scale_btn.clicked.connect(self._on_scale)
        transform_layout.addWidget(scale_btn)
        
        layout.addWidget(transform_group)
        
        # Export
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout()
        export_group.setLayout(export_layout)
        
        export_gltf_btn = QPushButton("Export GLTF")
        export_gltf_btn.clicked.connect(self._on_export_gltf)
        export_layout.addWidget(export_gltf_btn)
        
        export_obj_btn = QPushButton("Export OBJ")
        export_obj_btn.clicked.connect(self._on_export_obj)
        export_layout.addWidget(export_obj_btn)
        
        layout.addWidget(export_group)
        
        layout.addStretch()
        
        return panel
    
    def _setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        new_action = toolbar.addAction("New")
        new_action.triggered.connect(self._on_new)
        
        open_action = toolbar.addAction("Open")
        open_action.triggered.connect(self._on_open)
        
        save_action = toolbar.addAction("Save")
        save_action.triggered.connect(self._on_save)
    
    def _add_primitive(self, primitive_type: str):
        """Add primitive to mesh"""
        if primitive_type == "cube":
            self.mesh = MeshOperations.create_cube(1.0)
        elif primitive_type == "sphere":
            self.mesh = MeshOperations.create_sphere(1.0, 16, 8)
        elif primitive_type == "cylinder":
            self.mesh = MeshOperations.create_cylinder(1.0, 2.0, 16)
        elif primitive_type == "plane":
            self.mesh = MeshOperations.create_plane(2.0, 1)
        
        self.viewport.mesh = self.mesh
        self.viewport.update()
        logger.info(f"Added {primitive_type} primitive")
    
    def _on_extrude(self):
        """Extrude selected faces"""
        if self.mesh.selected_faces:
            MeshOperations.extrude_faces(self.mesh, list(self.mesh.selected_faces), 0.5)
            self.viewport.update()
            logger.info("Extruded faces")
        else:
            QMessageBox.information(self, "Extrude", "No faces selected")
    
    def _on_subdivide(self):
        """Subdivide mesh"""
        MeshOperations.subdivide_mesh(self.mesh)
        self.viewport.update()
        logger.info("Subdivided mesh")
    
    def _on_scale(self):
        """Scale selected vertices"""
        scale_value = self.scale_spin.value()
        
        if self.mesh.selected_vertices:
            center = self.mesh.get_center()
            scale = np.array([scale_value, scale_value, scale_value])
            MeshOperations.scale_vertices(
                self.mesh,
                list(self.mesh.selected_vertices),
                scale,
                center
            )
            self.viewport.update()
            logger.info(f"Scaled vertices by {scale_value}")
        else:
            QMessageBox.information(self, "Scale", "No vertices selected")
    
    def _on_export_gltf(self):
        """Export as GLTF"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export GLTF", "", "GLTF Files (*.gltf);;GLB Files (*.glb)"
        )
        
        if filename:
            logger.info(f"Exporting to {filename}")
            # TODO: Implement GLTF export using pygltflib
            QMessageBox.information(self, "Export", "GLTF export not yet implemented")
    
    def _on_export_obj(self):
        """Export as OBJ"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export OBJ", "", "OBJ Files (*.obj)"
        )
        
        if filename:
            logger.info(f"Exporting to {filename}")
            # TODO: Implement OBJ export
            QMessageBox.information(self, "Export", "OBJ export not yet implemented")
    
    def _on_new(self):
        """Create new mesh"""
        self.mesh = Mesh()
        self.viewport.mesh = self.mesh
        self.viewport.update()
    
    def _on_open(self):
        """Open mesh file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Mesh", "", "All Files (*.*)"
        )
        
        if filename:
            logger.info(f"Opening {filename}")
            # TODO: Implement mesh loading
    
    def _on_save(self):
        """Save mesh file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Mesh", "", "All Files (*.*)"
        )
        
        if filename:
            logger.info(f"Saving to {filename}")
            # TODO: Implement mesh saving
