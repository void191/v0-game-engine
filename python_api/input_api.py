"""
Input API for user scripts
"""


class Input:
    """Input API for user scripts"""
    
    _engine = None
    
    @classmethod
    def set_engine(cls, engine):
        """Set the engine instance (called internally)"""
        cls._engine = engine
    
    @classmethod
    def is_key_down(cls, key: str) -> bool:
        """Check if a key is currently pressed"""
        if cls._engine and cls._engine.input_manager:
            return cls._engine.input_manager.is_key_down(key)
        return False
    
    @classmethod
    def get_mouse_pos(cls) -> tuple:
        """Get mouse position"""
        if cls._engine and cls._engine.input_manager:
            return cls._engine.input_manager.get_mouse_position()
        return (0, 0)
