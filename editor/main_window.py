"""
Main editor window
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QDockWidget,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
import logging
from pathlib import Path

from .viewport import ViewportWidget
from .panels.hierarchy import HierarchyPanel
from .panels.inspector import InspectorPanel
from .panels.assets import AssetBrowserPanel
from .panels.console import ConsolePanel
from .scene_serializer import SceneSerializer

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main editor window"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.current_scene_path = None
        
        self.setWindowTitle("PolyForge Engine")
        self.setGeometry(100, 100, 1600, 900)
        
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbars()
        self._setup_docks()
        self._setup_update_timer()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup main UI layout"""
        # Central widget - viewport
        self.viewport = ViewportWidget(self.engine)
        self.setCentralWidget(self.viewport)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _setup_menus(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Project", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Project", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._on_open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Project", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._on_save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        save_scene_action = QAction("Save &Scene", self)
        save_scene_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_scene_action.triggered.connect(self._on_save_scene)
        file_menu.addAction(save_scene_action)
        
        load_scene_action = QAction("&Load Scene", self)
        load_scene_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        load_scene_action.triggered.connect(self._on_load_scene)
        file_menu.addAction(load_scene_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        voxel_action = QAction("&Voxel Editor", self)
        voxel_action.triggered.connect(self._on_open_voxel_editor)
        tools_menu.addAction(voxel_action)
        
        mesh_action = QAction("&Mesh Editor", self)
        mesh_action.triggered.connect(self._on_open_mesh_editor)
        tools_menu.addAction(mesh_action)
        
        vfx_action = QAction("&VFX Editor", self)
        vfx_action.triggered.connect(self._on_open_vfx_editor)
        tools_menu.addAction(vfx_action)
        
        # Build menu
        build_menu = menubar.addMenu("&Build")
        
        play_action = QAction("&Play", self)
        play_action.setShortcut(Qt.Key_F5)
        play_action.triggered.connect(self._on_play)
        build_menu.addAction(play_action)
        
        stop_action = QAction("&Stop", self)
        stop_action.setShortcut(Qt.Key_F6)
        stop_action.triggered.connect(self._on_stop)
        build_menu.addAction(stop_action)
        
        build_menu.addSeparator()
        
        export_action = QAction("&Export Build...", self)
        export_action.triggered.connect(self._on_export_build)
        build_menu.addAction(export_action)
    
    def _setup_toolbars(self):
        """Setup toolbars"""
        # Main toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        play_action = QAction("Play", self)
        play_action.triggered.connect(self._on_play)
        toolbar.addAction(play_action)
        
        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self._on_stop)
        toolbar.addAction(stop_action)
    
    def _setup_docks(self):
        """Setup dock panels"""
        # Hierarchy panel (left)
        self.hierarchy_dock = QDockWidget("Hierarchy", self)
        self.hierarchy_panel = HierarchyPanel(self.engine)
        self.hierarchy_dock.setWidget(self.hierarchy_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.hierarchy_dock)
        
        # Inspector panel (right)
        self.inspector_dock = QDockWidget("Inspector", self)
        self.inspector_panel = InspectorPanel(self.engine)
        self.inspector_dock.setWidget(self.inspector_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inspector_dock)
        
        # Asset browser (bottom)
        self.assets_dock = QDockWidget("Assets", self)
        self.assets_panel = AssetBrowserPanel(self.engine)
        self.assets_dock.setWidget(self.assets_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.assets_dock)
        
        # Console (bottom, tabbed with assets)
        self.console_dock = QDockWidget("Console", self)
        self.console_panel = ConsolePanel()
        self.console_dock.setWidget(self.console_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)
        self.tabifyDockWidget(self.assets_dock, self.console_dock)
    
    def _setup_update_timer(self):
        """Setup update timer for engine"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._on_update)
        self.update_timer.start(16)  # ~60 FPS
    
    def _connect_signals(self):
        """Connect panel signals"""
        self.hierarchy_panel.entity_selected.connect(self._on_entity_selected)
    
    def _on_update(self):
        """Update engine each frame"""
        delta_time = 0.016  # TODO: Calculate actual delta
        self.engine.update(delta_time)
        self.viewport.update()
    
    def _on_entity_selected(self, entity_id: int):
        """Handle entity selection"""
        entity = self.engine.scene_manager.get_entity(entity_id)
        if entity:
            self.inspector_panel.set_entity(entity)
    
    def _on_new_project(self):
        """Create new project"""
        logger.info("New project")
        # TODO: Implement project creation dialog
    
    def _on_open_project(self):
        """Open existing project"""
        logger.info("Open project")
        # TODO: Implement project open dialog
    
    def _on_save_project(self):
        """Save current project"""
        logger.info("Save project")
        # TODO: Implement project save
    
    def _on_save_scene(self):
        """Save current scene"""
        if self.current_scene_path:
            SceneSerializer.save_scene(self.engine.scene_manager, self.current_scene_path)
            logger.info(f"Scene saved to {self.current_scene_path}")
            self.status_bar.showMessage(f"Scene saved", 3000)
        else:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Scene", "", "Scene Files (*.scene.json)"
            )
            if filename:
                self.current_scene_path = Path(filename)
                SceneSerializer.save_scene(self.engine.scene_manager, self.current_scene_path)
                logger.info(f"Scene saved to {filename}")
                self.status_bar.showMessage(f"Scene saved", 3000)
    
    def _on_load_scene(self):
        """Load scene"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Scene", "", "Scene Files (*.scene.json)"
        )
        if filename:
            self.current_scene_path = Path(filename)
            SceneSerializer.load_scene(self.engine.scene_manager, self.current_scene_path)
            self.hierarchy_panel._refresh_tree()
            logger.info(f"Scene loaded from {filename}")
            self.status_bar.showMessage(f"Scene loaded", 3000)
    
    def _on_open_voxel_editor(self):
        """Open voxel editor"""
        from tools.voxel.voxel_editor import VoxelEditorWindow
        
        logger.info("Opening voxel editor")
        self.voxel_editor = VoxelEditorWindow(self.engine)
        self.voxel_editor.show()
    
    def _on_open_mesh_editor(self):
        """Open mesh editor"""
        from tools.mesh.mesh_editor import MeshEditorWindow
        
        logger.info("Opening mesh editor")
        self.mesh_editor = MeshEditorWindow(self.engine)
        self.mesh_editor.show()
    
    def _on_open_vfx_editor(self):
        """Open VFX editor"""
        logger.info("Opening VFX editor")
        # TODO: Open VFX editor window
    
    def _on_play(self):
        """Start play mode"""
        self.engine.play()
        self.status_bar.showMessage("Playing")
    
    def _on_stop(self):
        """Stop play mode"""
        self.engine.stop()
        self.status_bar.showMessage("Ready")
    
    def _on_export_build(self):
        """Export game build"""
        from export.build_dialog import BuildDialog
        
        logger.info("Opening export dialog")
        dialog = BuildDialog(self.engine, self)
        dialog.exec()
    
    def closeEvent(self, event):
        """Handle window close"""
        self.engine.shutdown()
        event.accept()
