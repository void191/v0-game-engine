"""
Prefab system for reusable entity templates
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

from .scene import Entity, Transform


class Prefab:
    """Prefab template for entities"""
    
    def __init__(self, name: str):
        self.name = name
        self.template_data: Dict[str, Any] = {}
    
    def save_from_entity(self, entity: Entity):
        """Save prefab from entity"""
        self.template_data = {
            'name': entity.name,
            'transform': {
                'position': entity.transform.position.tolist(),
                'rotation': entity.transform.rotation.tolist(),
                'scale': entity.transform.scale.tolist()
            },
            'components': {},
            'children': []
        }
        
        # Save components
        for comp_type, comp in entity.components.items():
            self.template_data['components'][comp_type] = self._serialize_component(comp)
        
        # Save children recursively
        for child in entity.children:
            child_prefab = Prefab(child.name)
            child_prefab.save_from_entity(child)
            self.template_data['children'].append(child_prefab.template_data)
    
    def instantiate(self, scene_manager, parent: Optional[Entity] = None) -> Entity:
        """Instantiate prefab as entity"""
        entity = scene_manager.create_entity(self.template_data['name'], parent)
        
        # Restore transform
        transform_data = self.template_data['transform']
        entity.transform.position = np.array(transform_data['position'])
        entity.transform.rotation = np.array(transform_data['rotation'])
        entity.transform.scale = np.array(transform_data['scale'])
        
        # Restore components
        for comp_type, comp_data in self.template_data['components'].items():
            component = self._deserialize_component(comp_type, comp_data)
            entity.add_component(comp_type, component)
        
        # Instantiate children
        for child_data in self.template_data['children']:
            child_prefab = Prefab(child_data['name'])
            child_prefab.template_data = child_data
            child_prefab.instantiate(scene_manager, entity)
        
        return entity
    
    def save_to_file(self, path: Path):
        """Save prefab to file"""
        with open(path, 'w') as f:
            json.dump(self.template_data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, path: Path) -> 'Prefab':
        """Load prefab from file"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        prefab = cls(data['name'])
        prefab.template_data = data
        return prefab
    
    def _serialize_component(self, component) -> Dict[str, Any]:
        """Serialize component to dict"""
        if hasattr(component, '__dict__'):
            data = {}
            for key, value in component.__dict__.items():
                if isinstance(value, np.ndarray):
                    data[key] = value.tolist()
                else:
                    data[key] = value
            return data
        return {}
    
    def _deserialize_component(self, comp_type: str, data: Dict[str, Any]):
        """Deserialize component from dict"""
        # Import component classes
        from .components import (
            MeshComponent, LightComponent, CameraComponent,
            RigidbodyComponent, ColliderComponent, ScriptComponent
        )
        
        component_classes = {
            'mesh': MeshComponent,
            'light': LightComponent,
            'camera': CameraComponent,
            'rigidbody': RigidbodyComponent,
            'collider': ColliderComponent,
            'script': ScriptComponent
        }
        
        if comp_type in component_classes:
            # Convert lists back to numpy arrays where needed
            for key, value in data.items():
                if isinstance(value, list) and key in ['position', 'rotation', 'scale', 'color', 'velocity', 'angular_velocity', 'size']:
                    data[key] = np.array(value)
            
            return component_classes[comp_type](**data)
        
        return None
