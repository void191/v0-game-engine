"""
Renderer API for user scripts
"""

from typing import Optional


class Renderer:
    """Renderer API for user scripts"""
    
    _engine = None
    
    @classmethod
    def set_engine(cls, engine):
        """Set the engine instance (called internally)"""
        cls._engine = engine
    
    @classmethod
    def load_mesh(cls, path: str):
        """Load a mesh from file"""
        if cls._engine and cls._engine.asset_manager:
            # Load mesh using asset manager
            return cls._engine.asset_manager.load_obj(path)
        return None
