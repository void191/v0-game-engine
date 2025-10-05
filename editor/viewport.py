"""
3D viewport widget
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
import logging

logger = logging.getLogger(__name__)


class ViewportWidget(QWidget):
    """3D viewport for scene rendering"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setMinimumSize(800, 600)
        self.setFocusPolicy(Qt.StrongFocus)
    
    def paintEvent(self, event):
        """Render viewport"""
        painter = QPainter(self)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(45, 45, 48))
        
        # TODO: Render Godot scene here
        # For now, draw placeholder grid
        painter.setPen(QColor(80, 80, 80))
        
        width = self.width()
        height = self.height()
        grid_size = 50
        
        # Draw vertical lines
        for x in range(0, width, grid_size):
            painter.drawLine(x, 0, x, height)
        
        # Draw horizontal lines
        for y in range(0, height, grid_size):
            painter.drawLine(0, y, width, y)
        
        # Draw center text
        painter.setPen(QColor(150, 150, 150))
        painter.drawText(self.rect(), Qt.AlignCenter, "3D Viewport\n(Godot integration pending)")
