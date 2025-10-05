"""
Voxel grid data structure
"""

import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class VoxelColor:
    """RGBA color for voxel"""
    r: int = 255
    g: int = 255
    b: int = 255
    a: int = 255
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)
    
    @classmethod
    def from_tuple(cls, rgba: Tuple[int, int, int, int]) -> 'VoxelColor':
        return cls(*rgba)


class VoxelGrid:
    """3D voxel grid with color palette"""
    
    def __init__(self, size: int = 64):
        self.size = size
        # Grid stores palette indices (0 = empty)
        self.grid = np.zeros((size, size, size), dtype=np.uint8)
        
        # Color palette (index 0 is reserved for empty)
        self.palette: List[VoxelColor] = [VoxelColor(0, 0, 0, 0)]  # Empty
        self._init_default_palette()
        
        self.layers: List[bool] = [True] * size  # Layer visibility
    
    def _init_default_palette(self):
        """Initialize default color palette"""
        # Add some basic colors
        default_colors = [
            (255, 255, 255, 255),  # White
            (255, 0, 0, 255),      # Red
            (0, 255, 0, 255),      # Green
            (0, 0, 255, 255),      # Blue
            (255, 255, 0, 255),    # Yellow
            (255, 0, 255, 255),    # Magenta
            (0, 255, 255, 255),    # Cyan
            (128, 128, 128, 255),  # Gray
        ]
        
        for color in default_colors:
            self.palette.append(VoxelColor.from_tuple(color))
    
    def set_voxel(self, x: int, y: int, z: int, color_index: int):
        """Set voxel at position to color index"""
        if self._is_valid_pos(x, y, z) and 0 <= color_index < len(self.palette):
            self.grid[x, y, z] = color_index
    
    def get_voxel(self, x: int, y: int, z: int) -> int:
        """Get voxel color index at position"""
        if self._is_valid_pos(x, y, z):
            return self.grid[x, y, z]
        return 0
    
    def get_voxel_color(self, x: int, y: int, z: int) -> Optional[VoxelColor]:
        """Get voxel color at position"""
        index = self.get_voxel(x, y, z)
        if index > 0 and index < len(self.palette):
            return self.palette[index]
        return None
    
    def clear(self):
        """Clear all voxels"""
        self.grid.fill(0)
    
    def fill_region(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, color_index: int):
        """Fill rectangular region with color"""
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        z1, z2 = min(z1, z2), max(z1, z2)
        
        x1 = max(0, min(x1, self.size - 1))
        x2 = max(0, min(x2, self.size - 1))
        y1 = max(0, min(y1, self.size - 1))
        y2 = max(0, min(y2, self.size - 1))
        z1 = max(0, min(z1, self.size - 1))
        z2 = max(0, min(z2, self.size - 1))
        
        self.grid[x1:x2+1, y1:y2+1, z1:z2+1] = color_index
    
    def add_color(self, color: VoxelColor) -> int:
        """Add color to palette, return index"""
        self.palette.append(color)
        return len(self.palette) - 1
    
    def _is_valid_pos(self, x: int, y: int, z: int) -> bool:
        """Check if position is valid"""
        return 0 <= x < self.size and 0 <= y < self.size and 0 <= z < self.size
    
    def get_filled_voxels(self) -> List[Tuple[int, int, int, VoxelColor]]:
        """Get list of all filled voxels with positions and colors"""
        voxels = []
        indices = np.argwhere(self.grid > 0)
        
        for idx in indices:
            x, y, z = idx
            color_index = self.grid[x, y, z]
            if color_index < len(self.palette):
                voxels.append((x, y, z, self.palette[color_index]))
        
        return voxels
    
    def bake_to_mesh(self):
        """Convert voxel grid to optimized mesh"""
        # TODO: Implement greedy meshing algorithm
        # For now, return basic cube per voxel
        vertices = []
        colors = []
        indices = []
        
        voxels = self.get_filled_voxels()
        
        for i, (x, y, z, color) in enumerate(voxels):
            # Add cube vertices for this voxel
            base_idx = len(vertices)
            
            # Cube vertices (8 corners)
            cube_verts = [
                (x, y, z), (x+1, y, z), (x+1, y+1, z), (x, y+1, z),
                (x, y, z+1), (x+1, y, z+1), (x+1, y+1, z+1), (x, y+1, z+1)
            ]
            
            vertices.extend(cube_verts)
            colors.extend([color.to_tuple()] * 8)
            
            # Cube indices (12 triangles, 6 faces)
            cube_indices = [
                # Front
                0, 1, 2, 0, 2, 3,
                # Back
                5, 4, 7, 5, 7, 6,
                # Left
                4, 0, 3, 4, 3, 7,
                # Right
                1, 5, 6, 1, 6, 2,
                # Top
                3, 2, 6, 3, 6, 7,
                # Bottom
                4, 5, 1, 4, 1, 0
            ]
            
            indices.extend([base_idx + idx for idx in cube_indices])
        
        return {
            'vertices': np.array(vertices, dtype=np.float32),
            'colors': np.array(colors, dtype=np.uint8),
            'indices': np.array(indices, dtype=np.uint32)
        }
