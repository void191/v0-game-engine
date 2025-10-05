"""
Build configuration for game exports
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional


class BuildPlatform(Enum):
    """Target build platforms"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"


class BuildMode(Enum):
    """Build modes"""
    DEBUG = "debug"
    RELEASE = "release"


@dataclass
class BuildConfig:
    """Build configuration"""
    
    # Project info
    project_name: str = "MyGame"
    project_path: Path = None
    version: str = "1.0.0"
    
    # Build settings
    platform: BuildPlatform = BuildPlatform.WINDOWS
    mode: BuildMode = BuildMode.RELEASE
    output_path: Path = None
    
    # Scene settings
    main_scene: Path = None
    included_scenes: List[Path] = None
    
    # Asset settings
    compress_textures: bool = True
    compress_audio: bool = True
    optimize_meshes: bool = True
    
    # Code settings
    strip_debug_symbols: bool = True
    obfuscate_scripts: bool = False
    
    # Window settings
    window_width: int = 1280
    window_height: int = 720
    fullscreen: bool = False
    resizable: bool = True
    
    # Icon and splash
    icon_path: Optional[Path] = None
    splash_screen: Optional[Path] = None
    
    def __post_init__(self):
        if self.included_scenes is None:
            self.included_scenes = []
        
        if self.output_path is None:
            self.output_path = Path("./builds")
