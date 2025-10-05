"""
Level editor tools and gizmos
"""

import numpy as np
from enum import Enum
from typing import Optional

from core.scene import Entity


class GizmoMode(Enum):
    """Gizmo transformation mode"""
    TRANSLATE = "translate"
    ROTATE = "rotate"
    SCALE = "scale"


class TransformGizmo:
    """3D transformation gizmo"""
    
    def __init__(self):
        self.mode = GizmoMode.TRANSLATE
        self.space = "world"  # world or local
        self.snap_enabled = False
        self.snap_value = 0.5
    
    def set_mode(self, mode: GizmoMode):
        """Set gizmo mode"""
        self.mode = mode
    
    def apply_transform(self, entity: Entity, axis: str, delta: float):
        """Apply transformation to entity"""
        if self.mode == GizmoMode.TRANSLATE:
            self._apply_translation(entity, axis, delta)
        elif self.mode == GizmoMode.ROTATE:
            self._apply_rotation(entity, axis, delta)
        elif self.mode == GizmoMode.SCALE:
            self._apply_scale(entity, axis, delta)
    
    def _apply_translation(self, entity: Entity, axis: str, delta: float):
        """Apply translation"""
        if self.snap_enabled:
            delta = round(delta / self.snap_value) * self.snap_value
        
        if axis == 'x':
            entity.transform.position[0] += delta
        elif axis == 'y':
            entity.transform.position[1] += delta
        elif axis == 'z':
            entity.transform.position[2] += delta
    
    def _apply_rotation(self, entity: Entity, axis: str, delta: float):
        """Apply rotation"""
        if self.snap_enabled:
            delta = round(delta / self.snap_value) * self.snap_value
        
        if axis == 'x':
            entity.transform.rotation[0] += delta
        elif axis == 'y':
            entity.transform.rotation[1] += delta
        elif axis == 'z':
            entity.transform.rotation[2] += delta
    
    def _apply_scale(self, entity: Entity, axis: str, delta: float):
        """Apply scale"""
        if axis == 'x':
            entity.transform.scale[0] += delta
        elif axis == 'y':
            entity.transform.scale[1] += delta
        elif axis == 'z':
            entity.transform.scale[2] += delta
        elif axis == 'uniform':
            entity.transform.scale += delta


class GridHelper:
    """Grid rendering helper"""
    
    def __init__(self, size: int = 20, spacing: float = 1.0):
        self.size = size
        self.spacing = spacing
        self.visible = True
    
    def get_grid_lines(self):
        """Get grid line positions"""
        lines = []
        half_size = self.size / 2
        
        # Lines along X axis
        for i in range(-self.size // 2, self.size // 2 + 1):
            z = i * self.spacing
            lines.append([
                (-half_size * self.spacing, 0, z),
                (half_size * self.spacing, 0, z)
            ])
        
        # Lines along Z axis
        for i in range(-self.size // 2, self.size // 2 + 1):
            x = i * self.spacing
            lines.append([
                (x, 0, -half_size * self.spacing),
                (x, 0, half_size * self.spacing)
            ])
        
        return lines
