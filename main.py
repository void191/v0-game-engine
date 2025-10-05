"""
PolyForge Engine - Main entry point
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication

from core.config import EngineConfig
from core.engine import EngineCore
from editor.main_window import MainWindow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    logger.info("Starting PolyForge Engine...")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("PolyForge Engine")
    
    # Create engine config
    config = EngineConfig()
    config.project_path = Path("./projects/default")
    
    # Initialize engine
    engine = EngineCore(config)
    engine.initialize()
    
    # Create and show main window
    window = MainWindow(engine)
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
