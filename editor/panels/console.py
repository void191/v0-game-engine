"""
Console/log panel
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide6.QtGui import QTextCursor
import logging


class ConsolePanel(QWidget):
    """Console output and Python REPL"""
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.console_output)
        
        # Setup logging handler
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging to console"""
        handler = ConsoleHandler(self)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
    
    def append_log(self, message: str):
        """Append log message to console"""
        self.console_output.append(message)
        self.console_output.moveCursor(QTextCursor.End)


class ConsoleHandler(logging.Handler):
    """Logging handler that outputs to console panel"""
    
    def __init__(self, console_panel):
        super().__init__()
        self.console_panel = console_panel
    
    def emit(self, record):
        msg = self.format(record)
        self.console_panel.append_log(msg)
