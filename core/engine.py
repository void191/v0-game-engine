"""
Core engine runtime and coordination
"""

import logging
from typing import Optional
from pathlib import Path

from .config import EngineConfig
from .scene import SceneManager
from .godot_bridge import GodotBridge
from .physics import PhysicsEngine
from .scripting import ScriptManager
from .input import InputManager
from .time import TimeManager
from .asset import AssetManager


logger = logging.getLogger(__name__)


class EngineCore:
    """Main engine coordinator"""
    
    def __init__(self, config: EngineConfig):
        self.config = config
        self.godot_bridge: Optional[GodotBridge] = None
        self.scene_manager: Optional[SceneManager] = None
        self.asset_manager: Optional[AssetManager] = None
        self.physics_engine: Optional[PhysicsEngine] = None
        self.script_manager: Optional[ScriptManager] = None
        self.input_manager: Optional[InputManager] = None
        self.time_manager: Optional[TimeManager] = None
        self.renderer = None
        self.is_initialized = False
        self.is_playing = False
        self.is_running = True
        
    def initialize(self):
        """Initialize engine subsystems"""
        logger.info("Initializing PolyForge Engine...")
        
        # Initialize Godot bridge
        self.godot_bridge = GodotBridge(self.config)
        self.godot_bridge.initialize()
        
        # Initialize scene manager
        self.scene_manager = SceneManager(self)
        
        # Initialize asset manager
        self.asset_manager = AssetManager()
        self.asset_manager.scan_assets()
        
        # Initialize physics engine
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
        
        if self.godot_bridge:
            self.godot_bridge.shutdown()
        
        self.is_initialized = False
        logger.info("Engine shutdown complete")
    
    def play(self):
        """Start runtime/play mode"""
        if not self.is_initialized:
            logger.error("Cannot play: engine not initialized")
            return
        
        logger.info("Starting play mode...")
        self.is_playing = True
        if self.godot_bridge:
            self.godot_bridge.start_runtime()
    
    def stop(self):
        """Stop runtime/play mode"""
        logger.info("Stopping play mode...")
        self.is_playing = False
        if self.godot_bridge:
            self.godot_bridge.stop_runtime()
    
    def update(self, delta_time: float):
        """Update engine (called each frame)"""
        if self.is_playing and self.godot_bridge:
            self.godot_bridge.update(delta_time)
        
        if not self.is_playing:
            return
        
        self.time_manager.update(delta_time)
        
        self.script_manager.update_scripts(delta_time)
        
        while self.time_manager.should_fixed_update():
            self.script_manager.fixed_update_scripts(self.time_manager.fixed_delta_time)
            self.physics_engine.update(self.scene_manager, self.time_manager.fixed_delta_time)
        
        self.input_manager.update()
