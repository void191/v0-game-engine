"""
Build/Export API for user scripts
"""


class Build:
    """Build API for user scripts"""
    
    _engine = None
    
    @classmethod
    def set_engine(cls, engine):
        """Set the engine instance (called internally)"""
        cls._engine = engine
    
    @classmethod
    def export_game(cls, output_path: str, platform: str = 'windows', options: dict = None):
        """Export game to standalone build"""
        # This would trigger the export system
        pass
