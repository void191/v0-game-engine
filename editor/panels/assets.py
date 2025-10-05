"""
Asset browser panel
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel


class AssetBrowserPanel(QWidget):
    """Asset browser and manager"""
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel("Assets"))
        
        # Asset list
        self.asset_list = QListWidget()
        layout.addWidget(self.asset_list)
        
        self._refresh_assets()
    
    def _refresh_assets(self):
        """Refresh asset list"""
        self.asset_list.clear()
        # TODO: Scan assets directory and populate list
        self.asset_list.addItem("(No assets)")
