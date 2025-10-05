"""
Voxel brush tools
"""

from enum import Enum
from typing import List, Tuple
import numpy as np


class BrushType(Enum):
    """Brush types"""
    POINT = "point"
    SPHERE = "sphere"
    CUBE = "cube"
    CYLINDER = "cylinder"


class BrushMode(Enum):
    """Brush modes"""
    PAINT = "paint"
    ERASE = "erase"
    FILL = "fill"
    PICK = "pick"


class VoxelBrush:
    """Voxel painting brush"""
    
    def __init__(self):
        self.brush_type = BrushType.SPHERE
        self.brush_mode = BrushMode.PAINT
        self.size = 1
        self.color_index = 1
    
    def get_affected_voxels(self, x: int, y: int, z: int) -> List[Tuple[int, int, int]]:
        """Get list of voxel positions affected by brush at given position"""
        if self.brush_type == BrushType.POINT:
            return [(x, y, z)]
        
        elif self.brush_type == BrushType.SPHERE:
            return self._get_sphere_voxels(x, y, z)
        
        elif self.brush_type == BrushType.CUBE:
            return self._get_cube_voxels(x, y, z)
        
        elif self.brush_type == BrushType.CYLINDER:
            return self._get_cylinder_voxels(x, y, z)
        
        return [(x, y, z)]
    
    def _get_sphere_voxels(self, cx: int, cy: int, cz: int) -> List[Tuple[int, int, int]]:
        """Get voxels in sphere"""
        voxels = []
        radius = self.size
        
        for x in range(cx - radius, cx + radius + 1):
            for y in range(cy - radius, cy + radius + 1):
                for z in range(cz - radius, cz + radius + 1):
                    dist_sq = (x - cx)**2 + (y - cy)**2 + (z - cz)**2
                    if dist_sq <= radius**2:
                        voxels.append((x, y, z))
        
        return voxels
    
    def _get_cube_voxels(self, cx: int, cy: int, cz: int) -> List[Tuple[int, int, int]]:
        """Get voxels in cube"""
        voxels = []
        half_size = self.size // 2
        
        for x in range(cx - half_size, cx + half_size + 1):
            for y in range(cy - half_size, cy + half_size + 1):
                for z in range(cz - half_size, cz + half_size + 1):
                    voxels.append((x, y, z))
        
        return voxels
    
    def _get_cylinder_voxels(self, cx: int, cy: int, cz: int) -> List[Tuple[int, int, int]]:
        """Get voxels in cylinder (Y-axis aligned)"""
        voxels = []
        radius = self.size
        height = self.size * 2
        
        for x in range(cx - radius, cx + radius + 1):
            for y in range(cy - height // 2, cy + height // 2 + 1):
                for z in range(cz - radius, cz + radius + 1):
                    dist_sq = (x - cx)**2 + (z - cz)**2
                    if dist_sq <= radius**2:
                        voxels.append((x, y, z))
        
        return voxels
    
    def apply(self, grid, x: int, y: int, z: int):
        """Apply brush to grid at position"""
        affected = self.get_affected_voxels(x, y, z)
        
        if self.brush_mode == BrushMode.PAINT:
            for vx, vy, vz in affected:
                grid.set_voxel(vx, vy, vz, self.color_index)
        
        elif self.brush_mode == BrushMode.ERASE:
            for vx, vy, vz in affected:
                grid.set_voxel(vx, vy, vz, 0)
        
        elif self.brush_mode == BrushMode.FILL:
            # Flood fill from starting position
            self._flood_fill(grid, x, y, z)
    
    def _flood_fill(self, grid, start_x: int, start_y: int, start_z: int):
        """Flood fill algorithm"""
        target_color = grid.get_voxel(start_x, start_y, start_z)
        if target_color == self.color_index:
            return
        
        stack = [(start_x, start_y, start_z)]
        visited = set()
        
        while stack and len(visited) < 10000:  # Limit to prevent infinite loops
            x, y, z = stack.pop()
            
            if (x, y, z) in visited:
                continue
            
            if not grid._is_valid_pos(x, y, z):
                continue
            
            if grid.get_voxel(x, y, z) != target_color:
                continue
            
            visited.add((x, y, z))
            grid.set_voxel(x, y, z, self.color_index)
            
            # Add neighbors
            stack.extend([
                (x+1, y, z), (x-1, y, z),
                (x, y+1, z), (x, y-1, z),
                (x, y, z+1), (x, y, z-1)
            ])
