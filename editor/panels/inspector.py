"""
Entity inspector panel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QGroupBox,
    QLineEdit, QDoubleSpinBox, QCheckBox, QPushButton,
    QHBoxLayout, QComboBox
)
from PySide6.QtCore import Qt
import numpy as np


class InspectorPanel(QWidget):
    """Entity properties inspector"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.current_entity = None
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Scroll area for properties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Content widget
        self.content = QWidget()
        self.content_layout = QVBoxLayout()
        self.content.setLayout(self.content_layout)
        scroll.setWidget(self.content)
        
        # Placeholder
        self.content_layout.addWidget(QLabel("No entity selected"))
        self.content_layout.addStretch()
    
    def set_entity(self, entity):
        """Set entity to inspect"""
        self.current_entity = entity
        self._refresh_properties()
    
    def _refresh_properties(self):
        """Refresh property display"""
        # Clear existing widgets
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.current_entity:
            self.content_layout.addWidget(QLabel("No entity selected"))
            self.content_layout.addStretch()
            return
        
        # Entity name
        name_group = QGroupBox("Entity")
        name_layout = QVBoxLayout()
        name_group.setLayout(name_layout)
        
        name_edit = QLineEdit(self.current_entity.name)
        name_edit.textChanged.connect(lambda text: setattr(self.current_entity, 'name', text))
        name_layout.addWidget(QLabel("Name:"))
        name_layout.addWidget(name_edit)
        
        active_check = QCheckBox("Active")
        active_check.setChecked(self.current_entity.active)
        active_check.toggled.connect(lambda checked: setattr(self.current_entity, 'active', checked))
        name_layout.addWidget(active_check)
        
        self.content_layout.addWidget(name_group)
        
        # Transform
        transform_group = self._create_transform_group()
        self.content_layout.addWidget(transform_group)
        
        # Components
        for comp_type, component in self.current_entity.components.items():
            comp_group = self._create_component_group(comp_type, component)
            self.content_layout.addWidget(comp_group)
        
        # Add component button
        add_comp_btn = QPushButton("+ Add Component")
        add_comp_btn.clicked.connect(self._on_add_component)
        self.content_layout.addWidget(add_comp_btn)
        
        self.content_layout.addStretch()
    
    def _create_transform_group(self) -> QGroupBox:
        """Create transform property group"""
        group = QGroupBox("Transform")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        transform = self.current_entity.transform
        
        # Position
        layout.addWidget(QLabel("Position:"))
        pos_layout = QHBoxLayout()
        for i, axis in enumerate(['X', 'Y', 'Z']):
            spin = QDoubleSpinBox()
            spin.setRange(-1000, 1000)
            spin.setValue(transform.position[i])
            spin.valueChanged.connect(lambda val, idx=i: self._update_transform_position(idx, val))
            pos_layout.addWidget(QLabel(axis))
            pos_layout.addWidget(spin)
        layout.addLayout(pos_layout)
        
        # Rotation
        layout.addWidget(QLabel("Rotation:"))
        rot_layout = QHBoxLayout()
        for i, axis in enumerate(['X', 'Y', 'Z']):
            spin = QDoubleSpinBox()
            spin.setRange(-360, 360)
            spin.setValue(np.degrees(transform.rotation[i]))
            spin.valueChanged.connect(lambda val, idx=i: self._update_transform_rotation(idx, val))
            rot_layout.addWidget(QLabel(axis))
            rot_layout.addWidget(spin)
        layout.addLayout(rot_layout)
        
        # Scale
        layout.addWidget(QLabel("Scale:"))
        scale_layout = QHBoxLayout()
        for i, axis in enumerate(['X', 'Y', 'Z']):
            spin = QDoubleSpinBox()
            spin.setRange(0.01, 100)
            spin.setValue(transform.scale[i])
            spin.valueChanged.connect(lambda val, idx=i: self._update_transform_scale(idx, val))
            scale_layout.addWidget(QLabel(axis))
            scale_layout.addWidget(spin)
        layout.addLayout(scale_layout)
        
        return group
    
    def _create_component_group(self, comp_type: str, component) -> QGroupBox:
        """Create component property group"""
        group = QGroupBox(comp_type.capitalize())
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Display component properties
        if hasattr(component, '__dict__'):
            for key, value in component.__dict__.items():
                layout.addWidget(QLabel(f"{key}: {value}"))
        
        # Remove button
        remove_btn = QPushButton("Remove Component")
        remove_btn.clicked.connect(lambda: self._remove_component(comp_type))
        layout.addWidget(remove_btn)
        
        return group
    
    def _update_transform_position(self, index: int, value: float):
        """Update transform position"""
        if self.current_entity:
            self.current_entity.transform.position[index] = value
    
    def _update_transform_rotation(self, index: int, value: float):
        """Update transform rotation"""
        if self.current_entity:
            self.current_entity.transform.rotation[index] = np.radians(value)
    
    def _update_transform_scale(self, index: int, value: float):
        """Update transform scale"""
        if self.current_entity:
            self.current_entity.transform.scale[index] = value
    
    def _on_add_component(self):
        """Add component to entity"""
        # TODO: Show component selection dialog
        pass
    
    def _remove_component(self, comp_type: str):
        """Remove component from entity"""
        if self.current_entity:
            self.current_entity.remove_component(comp_type)
            self._refresh_properties()
