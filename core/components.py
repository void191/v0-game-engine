"""
Entity component system
"""

import numpy as np
from typing import Optional
from dataclasses import dataclass


@dataclass
class MeshComponent:
    """Mesh renderer component"""
    mesh_path: str
    material: Optional[str] = None
    cast_shadows: bool = True
    receive_shadows: bool = True


@dataclass
class LightComponent:
    """Light component"""
    light_type: str = "point"  # point, directional, spot
    color: np.ndarray = None
    intensity: float = 1.0
    range: float = 10.0
    spot_angle: float = 45.0
    
    def __post_init__(self):
        if self.color is None:
            self.color = np.array([1.0, 1.0, 1.0])


@dataclass
class CameraComponent:
    """Camera component"""
    fov: float = 60.0
    near_plane: float = 0.1
    far_plane: float = 1000.0
    is_main: bool = False


@dataclass
class RigidbodyComponent:
    """Physics rigidbody component"""
    mass: float = 1.0
    use_gravity: bool = True
    is_kinematic: bool = False
    linear_drag: float = 0.0
    angular_drag: float = 0.05
    velocity: np.ndarray = None
    angular_velocity: np.ndarray = None
    
    def __post_init__(self):
        if self.velocity is None:
            self.velocity = np.array([0.0, 0.0, 0.0])
        if self.angular_velocity is None:
            self.angular_velocity = np.array([0.0, 0.0, 0.0])


@dataclass
class ColliderComponent:
    """Physics collider component"""
    collider_type: str = "box"  # box, sphere, capsule, mesh
    size: np.ndarray = None
    radius: float = 0.5
    height: float = 2.0
    is_trigger: bool = False
    
    def __post_init__(self):
        if self.size is None:
            self.size = np.array([1.0, 1.0, 1.0])


@dataclass
class ScriptComponent:
    """Python script component"""
    script_path: str
    enabled: bool = True
