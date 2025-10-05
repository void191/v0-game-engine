"""
Asset loading and management for PolyForge Engine
"""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from PIL import Image
import struct

logger = logging.getLogger(__name__)


class AssetManager:
    """Manages loading and caching of assets"""
    
    def __init__(self):
        self.loaded_meshes: Dict[str, dict] = {}
        self.loaded_textures: Dict[str, Image.Image] = {}
        self.asset_paths: List[Path] = []
        
        logger.info("AssetManager initialized")
    
    def scan_assets(self, base_path: Optional[Path] = None):
        """Scan for available assets"""
        if base_path is None:
            base_path = Path.cwd() / "assets"
        
        if not base_path.exists():
            base_path.mkdir(parents=True, exist_ok=True)
        
        self.asset_paths.append(base_path)
        logger.info(f"Scanning assets in {base_path}")
    
    def load_gltf(self, path: Path) -> dict:
        """Load GLTF/GLB file"""
        try:
            from pygltflib import GLTF2
            
            gltf = GLTF2().load(str(path))
            
            # Extract mesh data
            meshes = []
            for mesh in gltf.meshes:
                for primitive in mesh.primitives:
                    mesh_data = self._extract_gltf_primitive(gltf, primitive)
                    meshes.append(mesh_data)
            
            self.loaded_meshes[str(path)] = {
                'meshes': meshes,
                'format': 'gltf'
            }
            
            logger.info(f"Loaded GLTF: {path}")
            return self.loaded_meshes[str(path)]
        
        except Exception as e:
            logger.error(f"Failed to load GLTF {path}: {e}")
            return {}
    
    def _extract_gltf_primitive(self, gltf, primitive) -> dict:
        """Extract mesh data from GLTF primitive"""
        mesh_data = {
            'vertices': None,
            'normals': None,
            'texcoords': None,
            'indices': None
        }
        
        # Get accessor for positions
        if primitive.attributes.POSITION is not None:
            accessor = gltf.accessors[primitive.attributes.POSITION]
            buffer_view = gltf.bufferViews[accessor.bufferView]
            buffer = gltf.buffers[buffer_view.buffer]
            
            # Extract vertex data
            # This is simplified - full implementation would handle all accessor types
            mesh_data['vertices'] = np.array([[0, 0, 0]], dtype=np.float32)
        
        return mesh_data
    
    def load_obj(self, path: Path) -> dict:
        """Load OBJ file"""
        vertices = []
        normals = []
        texcoords = []
        faces = []
        
        try:
            with open(path, 'r') as f:
                for line in f:
                    if line.startswith('v '):
                        vertices.append([float(x) for x in line.split()[1:4]])
                    elif line.startswith('vn '):
                        normals.append([float(x) for x in line.split()[1:4]])
                    elif line.startswith('vt '):
                        texcoords.append([float(x) for x in line.split()[1:3]])
                    elif line.startswith('f '):
                        face = []
                        for vertex in line.split()[1:]:
                            indices = vertex.split('/')
                            face.append(int(indices[0]) - 1)
                        faces.append(face)
            
            mesh_data = {
                'vertices': np.array(vertices, dtype=np.float32),
                'normals': np.array(normals, dtype=np.float32) if normals else None,
                'texcoords': np.array(texcoords, dtype=np.float32) if texcoords else None,
                'indices': np.array(faces, dtype=np.int32).flatten()
            }
            
            self.loaded_meshes[str(path)] = {
                'meshes': [mesh_data],
                'format': 'obj'
            }
            
            logger.info(f"Loaded OBJ: {path}")
            return self.loaded_meshes[str(path)]
        
        except Exception as e:
            logger.error(f"Failed to load OBJ {path}: {e}")
            return {}
    
    def load_vox(self, path: Path) -> dict:
        """Load MagicaVoxel .vox file"""
        try:
            with open(path, 'rb') as f:
                # Read VOX header
                magic = f.read(4)
                if magic != b'VOX ':
                    raise ValueError("Not a valid VOX file")
                
                version = struct.unpack('<I', f.read(4))[0]
                
                # Parse chunks
                voxels = []
                palette = None
                size = (0, 0, 0)
                
                while True:
                    chunk_id = f.read(4)
                    if not chunk_id:
                        break
                    
                    chunk_size = struct.unpack('<I', f.read(4))[0]
                    child_size = struct.unpack('<I', f.read(4))[0]
                    
                    if chunk_id == b'SIZE':
                        size = struct.unpack('<III', f.read(12))
                    elif chunk_id == b'XYZI':
                        num_voxels = struct.unpack('<I', f.read(4))[0]
                        for _ in range(num_voxels):
                            x, y, z, c = struct.unpack('<BBBB', f.read(4))
                            voxels.append((x, y, z, c))
                    elif chunk_id == b'RGBA':
                        palette = []
                        for _ in range(256):
                            r, g, b, a = struct.unpack('<BBBB', f.read(4))
                            palette.append((r/255, g/255, b/255, a/255))
                    else:
                        f.read(chunk_size)
                
                mesh_data = {
                    'voxels': voxels,
                    'size': size,
                    'palette': palette,
                    'format': 'vox'
                }
                
                self.loaded_meshes[str(path)] = {
                    'meshes': [mesh_data],
                    'format': 'vox'
                }
                
                logger.info(f"Loaded VOX: {path}")
                return self.loaded_meshes[str(path)]
        
        except Exception as e:
            logger.error(f"Failed to load VOX {path}: {e}")
            return {}
    
    def load_texture(self, path: Path) -> Optional[Image.Image]:
        """Load texture image"""
        try:
            img = Image.open(path)
            self.loaded_textures[str(path)] = img
            logger.info(f"Loaded texture: {path}")
            return img
        except Exception as e:
            logger.error(f"Failed to load texture {path}: {e}")
            return None
    
    def bake_voxel_mesh(self, voxels: List[Tuple], size: Tuple[int, int, int],
                       palette: Optional[List[Tuple]] = None) -> dict:
        """Convert voxel data to mesh"""
        vertices = []
        colors = []
        indices = []
        
        # Create cube faces for each voxel
        cube_vertices = [
            # Front face
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
            # Back face
            [1, 0, 0], [0, 0, 0], [0, 1, 0], [1, 1, 0],
            # Top face
            [0, 1, 1], [1, 1, 1], [1, 1, 0], [0, 1, 0],
            # Bottom face
            [0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1],
            # Right face
            [1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1],
            # Left face
            [0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0]
        ]
        
        cube_indices = [
            0, 1, 2, 0, 2, 3,  # Front
            4, 5, 6, 4, 6, 7,  # Back
            8, 9, 10, 8, 10, 11,  # Top
            12, 13, 14, 12, 14, 15,  # Bottom
            16, 17, 18, 16, 18, 19,  # Right
            20, 21, 22, 20, 22, 23   # Left
        ]
        
        for x, y, z, c in voxels:
            base_index = len(vertices)
            
            # Add vertices for this voxel
            for v in cube_vertices:
                vertices.append([x + v[0], y + v[1], z + v[2]])
                
                # Add color
                if palette and c < len(palette):
                    colors.append(palette[c])
                else:
                    colors.append((1.0, 1.0, 1.0, 1.0))
            
            # Add indices
            for idx in cube_indices:
                indices.append(base_index + idx)
        
        return {
            'vertices': np.array(vertices, dtype=np.float32),
            'colors': np.array(colors, dtype=np.float32),
            'indices': np.array(indices, dtype=np.int32)
        }
