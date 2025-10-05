"""
Core engine runtime and coordination
"""

import logging
from typing import Optional
from pathlib import Path

from .config import EngineConfig
from .scene import SceneManager
from .physics import PhysicsEngine
from .scripting import ScriptManager
from .input import InputManager
from .time import TimeManager

# Import runtime modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from runtime.renderer import Renderer
from runtime.asset import AssetManager


logger = logging.getLogger(__name__)


class EngineCore:
    """Main engine coordinator"""
    
    def __init__(self, config: EngineConfig):
        self.config = config
        self.renderer: Optional[Renderer] = None
        self.scene_manager: Optional[SceneManager] = None
        self.asset_manager: Optional[AssetManager] = None
        self.physics_engine: Optional[PhysicsEngine] = None
        self.script_manager: Optional[ScriptManager] = None
        self.input_manager: Optional[InputManager] = None
        self.time_manager: Optional[TimeManager] = None
        self.is_initialized = False
        self.is_playing = False
        self.is_running = True
        
    def initialize(self, gl_context=None):
        """Initialize engine subsystems"""
        logger.info("Initializing PolyForge Engine...")
        
        # Initialize renderer with moderngl context
        if gl_context:
            self.renderer = Renderer(gl_context)
        
        # Initialize scene manager
        self.scene_manager = SceneManager(self)
        
        # Initialize asset manager
        self.asset_manager = AssetManager()
        self.asset_manager.scan_assets()
        
        # Initialize physics engine with pybullet
        self.physics_engine = PhysicsEngine()
        
        # Initialize script manager
        self.script_manager = ScriptManager(self)
        
        # Initialize input manager
        self.input_manager = InputManager()
        
        # Initialize time manager
        self.time_manager = TimeManager()
        
        self.is_initialized = True
        logger.info("Engine initialized successfully")
    
    def shutdown(self):
        """Shutdown engine subsystems"""
        logger.info("Shutting down engine...")
        
        if self.physics_engine:
            self.physics_engine.shutdown()
        
        self.is_initialized = False
        logger.info("Engine shutdown complete")
    
    def play(self):
        """Start runtime/play mode"""
        if not self.is_initialized:
            logger.error("Cannot play: engine not initialized")
            return
        
        logger.info("Starting play mode...")
        self.is_playing = True
    
    def stop(self):
        """Stop runtime/play mode"""
        logger.info("Stopping play mode...")
        self.is_playing = False
    
    def update(self, delta_time: float):
        """Update engine (called each frame)"""
        if not self.is_playing:
            return
        
        self.time_manager.update(delta_time)
        
        self.script_manager.update_scripts(delta_time)
        
        while self.time_manager.should_fixed_update():
            self.script_manager.fixed_update_scripts(self.time_manager.fixed_delta_time)
            self.physics_engine.update(self.scene_manager, self.time_manager.fixed_delta_time)
        
        self.input_manager.update()
    
    def render(self, view_matrix, projection_matrix):
        """Render the scene"""
        if not self.renderer or not self.scene_manager:
            return
        
        self.renderer.clear()
        
        # Render all entities with mesh components
        for entity in self.scene_manager.get_all_entities():
            if 'mesh' in entity.components:
                mesh_component = entity.components['mesh']
                if hasattr(mesh_component, 'mesh_handle') and mesh_component.mesh_handle:
                    model_matrix = entity.transform.get_matrix()
                    self.renderer.render_mesh(
                        mesh_component.mesh_handle,
                        model_matrix,
                        view_matrix,
                        projection_matrix
                    )
