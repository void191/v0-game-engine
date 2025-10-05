"""
Scene hierarchy panel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QPushButton, QHBoxLayout, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction


class HierarchyPanel(QWidget):
    """Scene hierarchy tree view"""
    
    entity_selected = Signal(int)  # entity_id
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Scene")
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self.tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("+ Entity")
        add_btn.clicked.connect(self._on_add_entity)
        button_layout.addWidget(add_btn)
        
        add_light_btn = QPushButton("+ Light")
        add_light_btn.clicked.connect(self._on_add_light)
        button_layout.addWidget(add_light_btn)
        
        add_camera_btn = QPushButton("+ Camera")
        add_camera_btn.clicked.connect(self._on_add_camera)
        button_layout.addWidget(add_camera_btn)
        
        layout.addLayout(button_layout)
        
        self._refresh_tree()
    
    def _refresh_tree(self):
        """Refresh hierarchy tree"""
        self.tree.clear()
        
        if not self.engine.scene_manager:
            return
        
        # Add root entities
        for entity in self.engine.scene_manager.root_entities:
            self._add_entity_to_tree(entity, None)
        
        # Expand all items
        self.tree.expandAll()
    
    def _add_entity_to_tree(self, entity, parent_item):
        """Recursively add entity and children to tree"""
        if parent_item is None:
            item = QTreeWidgetItem(self.tree)
        else:
            item = QTreeWidgetItem(parent_item)
        
        # Set display text with icon based on components
        display_name = entity.name
        if 'light' in entity.components:
            display_name = f"💡 {entity.name}"
        elif 'camera' in entity.components:
            display_name = f"📷 {entity.name}"
        elif 'mesh' in entity.components:
            display_name = f"🔷 {entity.name}"
        
        item.setText(0, display_name)
        item.setData(0, Qt.UserRole, entity.id)
        
        # Gray out if inactive
        if not entity.active:
            item.setForeground(0, Qt.gray)
        
        # Add children
        for child in entity.children:
            self._add_entity_to_tree(child, item)
    
    def _on_selection_changed(self):
        """Handle selection change"""
        selected = self.tree.selectedItems()
        if selected:
            entity_id = selected[0].data(0, Qt.UserRole)
            self.entity_selected.emit(entity_id)
    
    def _on_add_entity(self):
        """Add new empty entity"""
        if self.engine.scene_manager:
            entity = self.engine.scene_manager.create_entity("Entity")
            self._refresh_tree()
    
    def _on_add_light(self):
        """Add new light entity"""
        if self.engine.scene_manager:
            from core.components import LightComponent
            
            entity = self.engine.scene_manager.create_entity("Light")
            entity.add_component('light', LightComponent())
            self._refresh_tree()
    
    def _on_add_camera(self):
        """Add new camera entity"""
        if self.engine.scene_manager:
            from core.components import CameraComponent
            
            entity = self.engine.scene_manager.create_entity("Camera")
            entity.add_component('camera', CameraComponent())
            self._refresh_tree()
    
    def _on_context_menu(self, position):
        """Show context menu"""
        item = self.tree.itemAt(position)
        if not item:
            return
        
        entity_id = item.data(0, Qt.UserRole)
        entity = self.engine.scene_manager.get_entity(entity_id)
        
        if not entity:
            return
        
        menu = QMenu(self)
        
        # Duplicate action
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(lambda: self._duplicate_entity(entity))
        menu.addAction(duplicate_action)
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self._delete_entity(entity))
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # Toggle active
        toggle_text = "Deactivate" if entity.active else "Activate"
        toggle_action = QAction(toggle_text, self)
        toggle_action.triggered.connect(lambda: self._toggle_active(entity))
        menu.addAction(toggle_action)
        
        menu.exec_(self.tree.viewport().mapToGlobal(position))
    
    def _duplicate_entity(self, entity):
        """Duplicate entity"""
        # TODO: Implement entity duplication
        self._refresh_tree()
    
    def _delete_entity(self, entity):
        """Delete entity"""
        self.engine.scene_manager.destroy_entity(entity)
        self._refresh_tree()
    
    def _toggle_active(self, entity):
        """Toggle entity active state"""
        entity.active = not entity.active
        self._refresh_tree()
