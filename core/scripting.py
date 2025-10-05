"""
Python scripting API for game logic
"""

import numpy as np
from typing import Optional, Any
from pathlib import Path
import importlib.util
import sys


class ScriptAPI:
    """API exposed to user scripts"""
    
    def __init__(self, entity, engine):
        self.entity = entity
        self.engine = engine
        self.transform = entity.transform
        self.scene = engine.scene_manager
        self.input = engine.input_manager
        self.time = engine.time_manager
    
    def get_component(self, component_type: str):
        """Get component from entity"""
        return self.entity.components.get(component_type)
    
    def add_component(self, component_type: str, component):
        """Add component to entity"""
        self.entity.add_component(component_type, component)
    
    def remove_component(self, component_type: str):
        """Remove component from entity"""
        self.entity.remove_component(component_type)
    
    def find_entity(self, name: str) -> Optional[Any]:
        """Find entity by name"""
        return self.scene.find_entity_by_name(name)
    
    def instantiate(self, prefab_path: str, position: np.ndarray = None, rotation: np.ndarray = None):
        """Instantiate prefab"""
        from .prefab import Prefab
        
        prefab = Prefab.load_from_file(Path(prefab_path))
        entity = prefab.instantiate(self.scene)
        
        if position is not None:
            entity.transform.position = position
        if rotation is not None:
            entity.transform.rotation = rotation
        
        return entity
    
    def destroy(self, entity):
        """Destroy entity"""
        self.scene.destroy_entity(entity)
    
    def log(self, message: str):
        """Log message"""
        print(f"[Script] {message}")


class ScriptBehavior:
    """Base class for user scripts"""
    
    def __init__(self):
        self.api: Optional[ScriptAPI] = None
        self.enabled = True
    
    def awake(self):
        """Called when script is first loaded"""
        pass
    
    def start(self):
        """Called before first update"""
        pass
    
    def update(self, delta_time: float):
        """Called every frame"""
        pass
    
    def fixed_update(self, delta_time: float):
        """Called at fixed intervals for physics"""
        pass
    
    def on_collision_enter(self, collision):
        """Called when collision starts"""
        pass
    
    def on_collision_stay(self, collision):
        """Called while collision persists"""
        pass
    
    def on_collision_exit(self, collision):
        """Called when collision ends"""
        pass
    
    def on_trigger_enter(self, other):
        """Called when trigger is entered"""
        pass
    
    def on_trigger_exit(self, other):
        """Called when trigger is exited"""
        pass
    
    def on_destroy(self):
        """Called when entity is destroyed"""
        pass


class ScriptManager:
    """Manages script loading and execution"""
    
    def __init__(self, engine):
        self.engine = engine
        self.loaded_scripts = {}
        self.script_instances = {}
    
    def load_script(self, script_path: Path) -> type:
        """Load script from file"""
        if script_path in self.loaded_scripts:
            return self.loaded_scripts[script_path]
        
        # Load module
        spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[script_path.stem] = module
        spec.loader.exec_module(module)
        
        # Find ScriptBehavior subclass
        script_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, ScriptBehavior) and obj != ScriptBehavior:
                script_class = obj
                break
        
        if script_class:
            self.loaded_scripts[script_path] = script_class
            return script_class
        
        return None
    
    def create_script_instance(self, entity, script_path: Path) -> Optional[ScriptBehavior]:
        """Create script instance for entity"""
        script_class = self.load_script(script_path)
        
        if not script_class:
            return None
        
        # Create instance
        instance = script_class()
        instance.api = ScriptAPI(entity, self.engine)
        
        # Store instance
        if entity.id not in self.script_instances:
            self.script_instances[entity.id] = []
        self.script_instances[entity.id].append(instance)
        
        # Call awake
        instance.awake()
        
        return instance
    
    def update_scripts(self, delta_time: float):
        """Update all script instances"""
        for entity_id, scripts in self.script_instances.items():
            for script in scripts:
                if script.enabled:
                    script.update(delta_time)
    
    def fixed_update_scripts(self, delta_time: float):
        """Fixed update for physics"""
        for entity_id, scripts in self.script_instances.items():
            for script in scripts:
                if script.enabled:
                    script.fixed_update(delta_time)
    
    def remove_entity_scripts(self, entity_id: int):
        """Remove all scripts for entity"""
        if entity_id in self.script_instances:
            for script in self.script_instances[entity_id]:
                script.on_destroy()
            del self.script_instances[entity_id]
