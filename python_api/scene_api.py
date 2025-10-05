"""
Scene API for user scripts
"""

import numpy as np
from typing import Optional, Any


class Transform:
    """Transform component API"""
    
    def __init__(self, entity):
        self._entity = entity
    
    @property
    def position(self) -> np.ndarray:
        return self._entity.transform.position
    
    @position.setter
    def position(self, value: np.ndarray):
        self._entity.transform.position = np.array(value, dtype=np.float32)
    
    @property
    def rotation(self) -> np.ndarray:
        return self._entity.transform.rotation
    
    @rotation.setter
    def rotation(self, value: np.ndarray):
        self._entity.transform.rotation = np.array(value, dtype=np.float32)
    
    @property
    def scale(self) -> np.ndarray:
        return self._entity.transform.scale
    
    @scale.setter
    def scale(self, value: np.ndarray):
        self._entity.transform.scale = np.array(value, dtype=np.float32)


class Entity:
    """Entity API for user scripts"""
    
    def __init__(self, internal_entity):
        self._internal = internal_entity
        self.transform = Transform(internal_entity)
    
    @property
    def name(self) -> str:
        return self._internal.name
    
    @name.setter
    def name(self, value: str):
        self._internal.name = value
    
    def add_component(self, component_type: str, **kwargs):
        """Add a component to this entity"""
        # This would call the internal engine API
        pass
    
    def get_component(self, component_type: str) -> Optional[Any]:
        """Get a component from this entity"""
        return self._internal.components.get(component_type)
    
    def remove_component(self, component_type: str):
        """Remove a component from this entity"""
        if component_type in self._internal.components:
            del self._internal.components[component_type]


class Scene:
    """Scene API for user scripts"""
    
    _engine = None
    
    @classmethod
    def set_engine(cls, engine):
        """Set the engine instance (called internally)"""
        cls._engine = engine
    
    @classmethod
    def create_entity(cls, name: str, prefab: Optional[str] = None) -> Entity:
        """Create a new entity in the scene"""
        if cls._engine and cls._engine.scene_manager:
            internal_entity = cls._engine.scene_manager.create_entity(name)
            return Entity(internal_entity)
        return None
    
    @classmethod
    def find_entity(cls, name: str) -> Optional[Entity]:
        """Find an entity by name"""
        if cls._engine and cls._engine.scene_manager:
            for entity in cls._engine.scene_manager.get_all_entities():
                if entity.name == name:
                    return Entity(entity)
        return None
    
    @classmethod
    def destroy_entity(cls, entity: Entity):
        """Destroy an entity"""
        if cls._engine and cls._engine.scene_manager:
            cls._engine.scene_manager.remove_entity(entity._internal)
