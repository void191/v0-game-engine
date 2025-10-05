"""
Standalone game player/runtime
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent

from core.config import EngineConfig
from core.engine import EngineCore
from editor.viewport import ViewportWidget
from editor.scene_serializer import SceneSerializer

logger = logging.getLogger(__name__)


class RuntimePlayer(QMainWindow):
    """Standalone runtime player window"""
    
    def __init__(self, project_path: Path, scene_path: Path = None):
        super().__init__()
        
        self.project_path = project_path
        self.scene_path = scene_path
        
        # Initialize engine
        config = EngineConfig()
        config.project_path = project_path
        self.engine = EngineCore(config)
        self.engine.initialize()
        
        self._setup_ui()
        self._load_scene()
        self._setup_update_timer()
        
        # Start playing immediately
        self.engine.play()
    
    def _setup_ui(self):
        """Setup UI"""
        self.setWindowTitle("PolyForge Runtime")
        self.setGeometry(100, 100, 1280, 720)
        
        # Hide cursor for game mode
        self.setCursor(Qt.BlankCursor)
        
        # Central widget - viewport only
        self.viewport = ViewportWidget(self.engine)
        self.setCentralWidget(self.viewport)
        
        # Fullscreen option
        # self.showFullScreen()
    
    def _load_scene(self):
        """Load game scene"""
        if self.scene_path and self.scene_path.exists():
            logger.info(f"Loading scene: {self.scene_path}")
            SceneSerializer.load_scene(self.engine.scene_manager, self.scene_path)
        else:
            logger.warning("No scene specified or scene not found")
    
    def _setup_update_timer(self):
        """Setup game loop timer"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._on_update)
        self.update_timer.start(16)  # ~60 FPS
    
    def _on_update(self):
        """Game loop update"""
        delta_time = 0.016  # TODO: Calculate actual delta
        self.engine.update(delta_time)
        self.viewport.update()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press"""
        # ESC to quit
        if event.key() == Qt.Key_Escape:
            self.close()
            return
        
        # Forward to input manager
        # TODO: Map Qt keys to KeyCode enum
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release"""
        # Forward to input manager
        super().keyReleaseEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        # Forward to input manager
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        # Forward to input manager
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        # Forward to input manager
        super().mouseMoveEvent(event)
    
    def closeEvent(self, event):
        """Handle window close"""
        self.engine.stop()
        self.engine.shutdown()
        event.accept()


def run_game(project_path: Path, scene_path: Path = None):
    """Run game in standalone player"""
    app = QApplication(sys.argv)
    
    player = RuntimePlayer(project_path, scene_path)
    player.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    # Example usage
    project_path = Path("./projects/my_game")
    scene_path = project_path / "scenes" / "main.scene.json"
    
    run_game(project_path, scene_path)
