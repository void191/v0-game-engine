"""
Resource loading API for user scripts
"""


class ResourceLoader:
    """Resource loading API for user scripts"""
    
    _engine = None
    
    @classmethod
    def set_engine(cls, engine):
        """Set the engine instance (called internally)"""
        cls._engine = engine
    
    @classmethod
    def load_mesh(cls, path: str):
        """Load a mesh resource"""
        if cls._engine and cls._engine.asset_manager:
            return cls._engine.asset_manager.load_obj(path)
        return None
    
    @classmethod
    def load_texture(cls, path: str):
        """Load a texture resource"""
        if cls._engine and cls._engine.asset_manager:
            return cls._engine.asset_manager.load_texture(path)
        return None
