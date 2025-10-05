"""
Engine configuration management
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class EngineConfig:
    """Engine configuration settings"""
    
    # Paths
    project_path: Optional[Path] = None
    assets_path: Path = Path("assets")
    cache_path: Path = Path(".cache")
    
    # Rendering
    viewport_width: int = 1280
    viewport_height: int = 720
    target_fps: int = 60
    vsync: bool = True
    msaa_samples: int = 4
    
    # Voxel editor
    voxel_grid_size: int = 64
    voxel_default_palette_size: int = 256
    
    # Physics
    physics_fps: int = 60
    gravity: tuple = (0.0, -9.81, 0.0)
    
    # Scripting
    enable_hot_reload: bool = True
    python_path: Optional[Path] = None
    
    def load_defaults(self):
        """Load default configuration"""
        self.assets_path.mkdir(parents=True, exist_ok=True)
        self.cache_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, path: Path):
        """Save configuration to JSON file"""
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2, default=str)
    
    @classmethod
    def load(cls, path: Path) -> 'EngineConfig':
        """Load configuration from JSON file"""
        with open(path, 'r') as f:
            data = json.load(f)
            # Convert string paths back to Path objects
            for key in ['project_path', 'assets_path', 'cache_path', 'python_path']:
                if data.get(key):
                    data[key] = Path(data[key])
            return cls(**data)
