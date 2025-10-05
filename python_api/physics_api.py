"""
Physics API for user scripts
"""

import numpy as np


class PhysicsBody:
    """Physics body API for user scripts"""
    
    _engine = None
    
    @classmethod
    def set_engine(cls, engine):
        """Set the engine instance (called internally)"""
        cls._engine = engine
    
    @classmethod
    def add_rigidbody(cls, entity, mass: float = 1.0, shape: str = 'box'):
        """Add a rigidbody to an entity"""
        if cls._engine and cls._engine.physics_engine:
            cls._engine.physics_engine.add_rigidbody(
                entity._internal,
                mass=mass,
                shape_type=shape
            )
    
    @classmethod
    def apply_force(cls, entity, force: tuple):
        """Apply force to an entity"""
        if cls._engine and cls._engine.physics_engine:
            cls._engine.physics_engine.apply_force(
                entity._internal,
                np.array(force, dtype=np.float32)
            )
