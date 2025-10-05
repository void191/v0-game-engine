"""
Mesh editing operations
"""

import numpy as np
from typing import List
from .mesh_data import Mesh


class MeshOperations:
    """Mesh editing operations"""
    
    @staticmethod
    def create_cube(size: float = 1.0) -> Mesh:
        """Create cube primitive"""
        mesh = Mesh("Cube")
        
        half = size / 2
        
        # 8 vertices
        vertices = [
            np.array([-half, -half, -half]),
            np.array([half, -half, -half]),
            np.array([half, half, -half]),
            np.array([-half, half, -half]),
            np.array([-half, -half, half]),
            np.array([half, -half, half]),
            np.array([half, half, half]),
            np.array([-half, half, half]),
        ]
        
        for v in vertices:
            mesh.add_vertex(v)
        
        # 6 faces (quads)
        faces = [
            [0, 1, 2, 3],  # Front
            [5, 4, 7, 6],  # Back
            [4, 0, 3, 7],  # Left
            [1, 5, 6, 2],  # Right
            [3, 2, 6, 7],  # Top
            [4, 5, 1, 0],  # Bottom
        ]
        
        for f in faces:
            mesh.add_face(f)
        
        mesh.calculate_normals()
        return mesh
    
    @staticmethod
    def create_sphere(radius: float = 1.0, segments: int = 16, rings: int = 8) -> Mesh:
        """Create sphere primitive"""
        mesh = Mesh("Sphere")
        
        # Generate vertices
        for ring in range(rings + 1):
            theta = np.pi * ring / rings
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)
            
            for seg in range(segments + 1):
                phi = 2 * np.pi * seg / segments
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)
                
                x = radius * sin_theta * cos_phi
                y = radius * cos_theta
                z = radius * sin_theta * sin_phi
                
                mesh.add_vertex(np.array([x, y, z]))
        
        # Generate faces
        for ring in range(rings):
            for seg in range(segments):
                v0 = ring * (segments + 1) + seg
                v1 = v0 + 1
                v2 = (ring + 1) * (segments + 1) + seg
                v3 = v2 + 1
                
                mesh.add_face([v0, v1, v3, v2])
        
        mesh.calculate_normals()
        return mesh
    
    @staticmethod
    def create_cylinder(radius: float = 1.0, height: float = 2.0, segments: int = 16) -> Mesh:
        """Create cylinder primitive"""
        mesh = Mesh("Cylinder")
        
        half_height = height / 2
        
        # Bottom center
        bottom_center = mesh.add_vertex(np.array([0, -half_height, 0]))
        
        # Bottom ring
        bottom_ring = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            z = radius * np.sin(angle)
            idx = mesh.add_vertex(np.array([x, -half_height, z]))
            bottom_ring.append(idx)
        
        # Top ring
        top_ring = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            z = radius * np.sin(angle)
            idx = mesh.add_vertex(np.array([x, half_height, z]))
            top_ring.append(idx)
        
        # Top center
        top_center = mesh.add_vertex(np.array([0, half_height, 0]))
        
        # Bottom cap
        for i in range(segments):
            next_i = (i + 1) % segments
            mesh.add_face([bottom_center, bottom_ring[next_i], bottom_ring[i]])
        
        # Side faces
        for i in range(segments):
            next_i = (i + 1) % segments
            mesh.add_face([bottom_ring[i], bottom_ring[next_i], top_ring[next_i], top_ring[i]])
        
        # Top cap
        for i in range(segments):
            next_i = (i + 1) % segments
            mesh.add_face([top_center, top_ring[i], top_ring[next_i]])
        
        mesh.calculate_normals()
        return mesh
    
    @staticmethod
    def create_plane(size: float = 1.0, subdivisions: int = 1) -> Mesh:
        """Create plane primitive"""
        mesh = Mesh("Plane")
        
        half = size / 2
        step = size / subdivisions
        
        # Generate vertices
        for y in range(subdivisions + 1):
            for x in range(subdivisions + 1):
                px = -half + x * step
                pz = -half + y * step
                mesh.add_vertex(np.array([px, 0, pz]))
        
        # Generate faces
        for y in range(subdivisions):
            for x in range(subdivisions):
                v0 = y * (subdivisions + 1) + x
                v1 = v0 + 1
                v2 = (y + 1) * (subdivisions + 1) + x
                v3 = v2 + 1
                
                mesh.add_face([v0, v1, v3, v2])
        
        mesh.calculate_normals()
        return mesh
    
    @staticmethod
    def extrude_faces(mesh: Mesh, face_indices: List[int], distance: float):
        """Extrude selected faces"""
        for face_idx in face_indices:
            if face_idx >= len(mesh.faces):
                continue
            
            face = mesh.faces[face_idx]
            
            # Calculate face normal
            v0 = mesh.vertices[face.vertex_indices[0]].position
            v1 = mesh.vertices[face.vertex_indices[1]].position
            v2 = mesh.vertices[face.vertex_indices[2]].position
            
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = np.cross(edge1, edge2)
            length = np.linalg.norm(normal)
            if length > 0:
                normal = normal / length
            
            # Create new vertices
            new_indices = []
            for old_idx in face.vertex_indices:
                old_pos = mesh.vertices[old_idx].position
                new_pos = old_pos + normal * distance
                new_idx = mesh.add_vertex(new_pos)
                new_indices.append(new_idx)
            
            # Update face to use new vertices
            face.vertex_indices = new_indices
            
            # Create side faces
            for i in range(len(face.vertex_indices)):
                next_i = (i + 1) % len(face.vertex_indices)
                old_i = face_idx * len(face.vertex_indices) + i
                old_next = face_idx * len(face.vertex_indices) + next_i
                
                # This is simplified - proper implementation would track original vertices
        
        mesh.calculate_normals()
    
    @staticmethod
    def scale_vertices(mesh: Mesh, vertex_indices: List[int], scale: np.ndarray, pivot: np.ndarray):
        """Scale selected vertices around pivot"""
        for idx in vertex_indices:
            if idx < len(mesh.vertices):
                vertex = mesh.vertices[idx]
                offset = vertex.position - pivot
                vertex.position = pivot + offset * scale
        
        mesh.calculate_normals()
    
    @staticmethod
    def translate_vertices(mesh: Mesh, vertex_indices: List[int], translation: np.ndarray):
        """Translate selected vertices"""
        for idx in vertex_indices:
            if idx < len(mesh.vertices):
                mesh.vertices[idx].position += translation
    
    @staticmethod
    def rotate_vertices(mesh: Mesh, vertex_indices: List[int], axis: np.ndarray, angle: float, pivot: np.ndarray):
        """Rotate selected vertices around axis"""
        # Rodrigues' rotation formula
        axis = axis / np.linalg.norm(axis)
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        
        for idx in vertex_indices:
            if idx < len(mesh.vertices):
                vertex = mesh.vertices[idx]
                offset = vertex.position - pivot
                
                rotated = (
                    offset * cos_angle +
                    np.cross(axis, offset) * sin_angle +
                    axis * np.dot(axis, offset) * (1 - cos_angle)
                )
                
                vertex.position = pivot + rotated
        
        mesh.calculate_normals()
    
    @staticmethod
    def subdivide_mesh(mesh: Mesh):
        """Subdivide all faces"""
        new_faces = []
        
        for face in mesh.faces:
            if face.is_triangle():
                # Subdivide triangle into 4 triangles
                v0, v1, v2 = face.vertex_indices
                
                # Create midpoint vertices
                p0 = mesh.vertices[v0].position
                p1 = mesh.vertices[v1].position
                p2 = mesh.vertices[v2].position
                
                m01 = mesh.add_vertex((p0 + p1) / 2)
                m12 = mesh.add_vertex((p1 + p2) / 2)
                m20 = mesh.add_vertex((p2 + p0) / 2)
                
                # Create 4 new triangles
                new_faces.append([v0, m01, m20])
                new_faces.append([v1, m12, m01])
                new_faces.append([v2, m20, m12])
                new_faces.append([m01, m12, m20])
        
        # Replace faces
        mesh.faces = [mesh.faces[0].__class__(vertex_indices=f) for f in new_faces]
        mesh.calculate_normals()
