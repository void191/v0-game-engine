"""
Scene graph and entity management
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Transform:
    """3D transformation"""
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    scale: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))


class Entity:
    """Scene entity/game object"""
    
    def __init__(self, name: str, entity_id: int):
        self.name = name
        self.id = entity_id
        self.transform = Transform()
        self.parent: Optional[Entity] = None
        self.children: List[Entity] = []
        self.components: Dict[str, object] = {}
        self.active = True
    
    def add_component(self, component_type: str, component: object):
        """Add a component to this entity"""
        self.components[component_type] = component
    
    def get_component(self, component_type: str) -> Optional[object]:
        """Get a component by type"""
        return self.components.get(component_type)
    
    def remove_component(self, component_type: str):
        """Remove a component"""
        if component_type in self.components:
            del self.components[component_type]
    
    def add_child(self, child: 'Entity'):
        """Add a child entity"""
        child.parent = self
        self.children.append(child)
    
    def remove_child(self, child: 'Entity'):
        """Remove a child entity"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)


class SceneManager:
    """Manages scenes and entities"""
    
    def __init__(self, engine):
        self.engine = engine
        self.entities: Dict[int, Entity] = {}
        self.root_entities: List[Entity] = []
        self._next_entity_id = 1
    
    def create_entity(self, name: str, parent: Optional[Entity] = None) -> Entity:
        """Create a new entity"""
        entity = Entity(name, self._next_entity_id)
        self._next_entity_id += 1
        
        self.entities[entity.id] = entity
        
        if parent:
            parent.add_child(entity)
        else:
            self.root_entities.append(entity)
        
        return entity
    
    def destroy_entity(self, entity: Entity):
        """Destroy an entity and its children"""
        # Recursively destroy children
        for child in list(entity.children):
            self.destroy_entity(child)
        
        # Remove from parent
        if entity.parent:
            entity.parent.remove_child(entity)
        elif entity in self.root_entities:
            self.root_entities.remove(entity)
        
        # Remove from entities dict
        if entity.id in self.entities:
            del self.entities[entity.id]
    
    def get_entity(self, entity_id: int) -> Optional[Entity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)
    
    def clear(self):
        """Clear all entities"""
        self.entities.clear()
        self.root_entities.clear()
        self._next_entity_id = 1
