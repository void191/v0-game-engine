"""
Mesh data structures
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Vertex:
    """Mesh vertex"""
    position: np.ndarray
    normal: np.ndarray = field(default_factory=lambda: np.array([0.0, 1.0, 0.0]))
    uv: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0]))
    color: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0, 1.0]))


@dataclass
class Face:
    """Mesh face (triangle or quad)"""
    vertex_indices: List[int]
    
    def is_triangle(self) -> bool:
        return len(self.vertex_indices) == 3
    
    def is_quad(self) -> bool:
        return len(self.vertex_indices) == 4


class Mesh:
    """Low-poly mesh data"""
    
    def __init__(self, name: str = "Mesh"):
        self.name = name
        self.vertices: List[Vertex] = []
        self.faces: List[Face] = []
        self.selected_vertices: set = set()
        self.selected_faces: set = set()
    
    def add_vertex(self, position: np.ndarray) -> int:
        """Add vertex and return index"""
        vertex = Vertex(position=position.copy())
        self.vertices.append(vertex)
        return len(self.vertices) - 1
    
    def add_face(self, vertex_indices: List[int]) -> int:
        """Add face and return index"""
        if len(vertex_indices) < 3:
            raise ValueError("Face must have at least 3 vertices")
        
        face = Face(vertex_indices=vertex_indices)
        self.faces.append(face)
        return len(self.faces) - 1
    
    def remove_vertex(self, index: int):
        """Remove vertex and update faces"""
        if 0 <= index < len(self.vertices):
            # Remove faces that use this vertex
            self.faces = [f for f in self.faces if index not in f.vertex_indices]
            
            # Update vertex indices in remaining faces
            for face in self.faces:
                face.vertex_indices = [
                    (i - 1 if i > index else i) for i in face.vertex_indices
                ]
            
            del self.vertices[index]
    
    def remove_face(self, index: int):
        """Remove face"""
        if 0 <= index < len(self.faces):
            del self.faces[index]
    
    def calculate_normals(self):
        """Calculate vertex normals from face normals"""
        # Reset normals
        for vertex in self.vertices:
            vertex.normal = np.array([0.0, 0.0, 0.0])
        
        # Accumulate face normals
        for face in self.faces:
            if len(face.vertex_indices) >= 3:
                # Get face vertices
                v0 = self.vertices[face.vertex_indices[0]].position
                v1 = self.vertices[face.vertex_indices[1]].position
                v2 = self.vertices[face.vertex_indices[2]].position
                
                # Calculate face normal
                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = np.cross(edge1, edge2)
                
                # Normalize
                length = np.linalg.norm(normal)
                if length > 0:
                    normal = normal / length
                
                # Add to vertex normals
                for idx in face.vertex_indices:
                    self.vertices[idx].normal += normal
        
        # Normalize vertex normals
        for vertex in self.vertices:
            length = np.linalg.norm(vertex.normal)
            if length > 0:
                vertex.normal = vertex.normal / length
    
    def get_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get mesh bounding box"""
        if not self.vertices:
            return np.zeros(3), np.zeros(3)
        
        positions = np.array([v.position for v in self.vertices])
        min_bounds = np.min(positions, axis=0)
        max_bounds = np.max(positions, axis=0)
        
        return min_bounds, max_bounds
    
    def get_center(self) -> np.ndarray:
        """Get mesh center"""
        if not self.vertices:
            return np.zeros(3)
        
        positions = np.array([v.position for v in self.vertices])
        return np.mean(positions, axis=0)
    
    def to_arrays(self) -> dict:
        """Convert to numpy arrays for rendering"""
        if not self.vertices or not self.faces:
            return {
                'positions': np.array([], dtype=np.float32),
                'normals': np.array([], dtype=np.float32),
                'colors': np.array([], dtype=np.float32),
                'indices': np.array([], dtype=np.uint32)
            }
        
        positions = []
        normals = []
        colors = []
        indices = []
        
        for face in self.faces:
            # Triangulate if quad
            if face.is_quad():
                triangles = [
                    [face.vertex_indices[0], face.vertex_indices[1], face.vertex_indices[2]],
                    [face.vertex_indices[0], face.vertex_indices[2], face.vertex_indices[3]]
                ]
            else:
                triangles = [face.vertex_indices]
            
            for tri in triangles:
                for idx in tri:
                    vertex = self.vertices[idx]
                    positions.append(vertex.position)
                    normals.append(vertex.normal)
                    colors.append(vertex.color)
                    indices.append(len(positions) - 1)
        
        return {
            'positions': np.array(positions, dtype=np.float32),
            'normals': np.array(normals, dtype=np.float32),
            'colors': np.array(colors, dtype=np.float32),
            'indices': np.array(indices, dtype=np.uint32)
        }
