"""
Scene serialization and deserialization
"""

import json
from pathlib import Path
from typing import Dict, Any
import numpy as np

from core.scene import SceneManager, Entity


class SceneSerializer:
    """Serialize and deserialize scenes"""
    
    @staticmethod
    def save_scene(scene_manager: SceneManager, path: Path):
        """Save scene to file"""
        scene_data = {
            'entities': []
        }
        
        # Serialize root entities
        for entity in scene_manager.root_entities:
            entity_data = SceneSerializer._serialize_entity(entity)
            scene_data['entities'].append(entity_data)
        
        with open(path, 'w') as f:
            json.dump(scene_data, f, indent=2)
    
    @staticmethod
    def load_scene(scene_manager: SceneManager, path: Path):
        """Load scene from file"""
        with open(path, 'r') as f:
            scene_data = json.load(f)
        
        # Clear existing scene
        scene_manager.clear()
        
        # Deserialize entities
        for entity_data in scene_data['entities']:
            SceneSerializer._deserialize_entity(scene_manager, entity_data, None)
    
    @staticmethod
    def _serialize_entity(entity: Entity) -> Dict[str, Any]:
        """Serialize entity to dict"""
        data = {
            'name': entity.name,
            'active': entity.active,
            'transform': {
                'position': entity.transform.position.tolist(),
                'rotation': entity.transform.rotation.tolist(),
                'scale': entity.transform.scale.tolist()
            },
            'components': {},
            'children': []
        }
        
        # Serialize components
        for comp_type, comp in entity.components.items():
            data['components'][comp_type] = SceneSerializer._serialize_component(comp)
        
        # Serialize children
        for child in entity.children:
            data['children'].append(SceneSerializer._serialize_entity(child))
        
        return data
    
    @staticmethod
    def _deserialize_entity(scene_manager: SceneManager, data: Dict[str, Any], parent: Entity):
        """Deserialize entity from dict"""
        entity = scene_manager.create_entity(data['name'], parent)
        entity.active = data['active']
        
        # Restore transform
        transform_data = data['transform']
        entity.transform.position = np.array(transform_data['position'])
        entity.transform.rotation = np.array(transform_data['rotation'])
        entity.transform.scale = np.array(transform_data['scale'])
        
        # Restore components
        for comp_type, comp_data in data['components'].items():
            component = SceneSerializer._deserialize_component(comp_type, comp_data)
            if component:
                entity.add_component(comp_type, component)
        
        # Deserialize children
        for child_data in data['children']:
            SceneSerializer._deserialize_entity(scene_manager, child_data, entity)
        
        return entity
    
    @staticmethod
    def _serialize_component(component) -> Dict[str, Any]:
        """Serialize component"""
        if hasattr(component, '__dict__'):
            data = {}
            for key, value in component.__dict__.items():
                if isinstance(value, np.ndarray):
                    data[key] = value.tolist()
                else:
                    data[key] = value
            return data
        return {}
    
    @staticmethod
    def _deserialize_component(comp_type: str, data: Dict[str, Any]):
        """Deserialize component"""
        from core.components import (
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
            # Convert lists back to numpy arrays
            for key, value in data.items():
                if isinstance(value, list) and key in ['position', 'rotation', 'scale', 'color', 'velocity', 'angular_velocity', 'size']:
                    data[key] = np.array(value)
            
            return component_classes[comp_type](**data)
        
        return None
