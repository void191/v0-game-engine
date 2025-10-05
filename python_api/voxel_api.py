"""
Voxel API for user scripts
"""

import numpy as np


class VoxelGrid:
    """Voxel grid for user scripts"""
    
    def __init__(self, size_x: int, size_y: int, size_z: int):
        self.size = (size_x, size_y, size_z)
        self.data = np.zeros(self.size, dtype=np.uint8)
    
    def set(self, x: int, y: int, z: int, value: int):
        """Set voxel value"""
        if 0 <= x < self.size[0] and 0 <= y < self.size[1] and 0 <= z < self.size[2]:
            self.data[x, y, z] = value
    
    def get(self, x: int, y: int, z: int) -> int:
        """Get voxel value"""
        if 0 <= x < self.size[0] and 0 <= y < self.size[1] and 0 <= z < self.size[2]:
            return self.data[x, y, z]
        return 0
    
    def bake_mesh(self):
        """Convert voxel grid to mesh"""
        # This would call the asset manager's bake function
        pass


class VoxelAPI:
    """Voxel API for user scripts"""
    
    @staticmethod
    def create_grid(size_x: int, size_y: int, size_z: int) -> VoxelGrid:
        """Create a new voxel grid"""
        return VoxelGrid(size_x, size_y, size_z)
