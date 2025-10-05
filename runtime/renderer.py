"""
ModernGL-based renderer for PolyForge Engine
"""

import logging
import numpy as np
import moderngl
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MeshHandle:
    """Handle to a loaded mesh"""
    vao: moderngl.VertexArray
    vertex_count: int
    index_count: int
    material_id: Optional[int] = None


@dataclass
class Material:
    """Material properties"""
    diffuse_color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    specular_color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    shininess: float = 32.0
    texture_id: Optional[int] = None


class Renderer:
    """ModernGL-based renderer"""
    
    def __init__(self, ctx: moderngl.Context):
        self.ctx = ctx
        self.meshes: Dict[str, MeshHandle] = {}
        self.materials: Dict[int, Material] = {}
        self.textures: Dict[int, moderngl.Texture] = {}
        self.shaders: Dict[str, moderngl.Program] = {}
        
        self._init_shaders()
        self._init_default_material()
        
        logger.info("Renderer initialized")
    
    def _init_shaders(self):
        """Initialize default shaders"""
        # Basic shader
        vertex_shader = """
        #version 330
        
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        
        in vec3 in_position;
        in vec3 in_normal;
        in vec2 in_texcoord;
        in vec4 in_color;
        
        out vec3 v_position;
        out vec3 v_normal;
        out vec2 v_texcoord;
        out vec4 v_color;
        
        void main() {
            vec4 world_pos = model * vec4(in_position, 1.0);
            v_position = world_pos.xyz;
            v_normal = mat3(model) * in_normal;
            v_texcoord = in_texcoord;
            v_color = in_color;
            gl_Position = projection * view * world_pos;
        }
        """
        
        fragment_shader = """
        #version 330
        
        uniform vec4 diffuse_color;
        uniform vec3 light_dir;
        uniform vec3 camera_pos;
        uniform bool use_texture;
        uniform sampler2D tex;
        
        in vec3 v_position;
        in vec3 v_normal;
        in vec2 v_texcoord;
        in vec4 v_color;
        
        out vec4 fragColor;
        
        void main() {
            vec3 normal = normalize(v_normal);
            vec3 light = normalize(light_dir);
            
            // Ambient
            vec3 ambient = vec3(0.3);
            
            // Diffuse
            float diff = max(dot(normal, light), 0.0);
            vec3 diffuse = diff * vec3(1.0);
            
            // Specular
            vec3 view_dir = normalize(camera_pos - v_position);
            vec3 reflect_dir = reflect(-light, normal);
            float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);
            vec3 specular = spec * vec3(0.5);
            
            vec4 base_color = diffuse_color * v_color;
            if (use_texture) {
                base_color *= texture(tex, v_texcoord);
            }
            
            vec3 result = (ambient + diffuse + specular) * base_color.rgb;
            fragColor = vec4(result, base_color.a);
        }
        """
        
        self.shaders['basic'] = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        
        # Flat shader for voxels
        flat_vertex = """
        #version 330
        
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        
        in vec3 in_position;
        in vec4 in_color;
        
        out vec4 v_color;
        
        void main() {
            v_color = in_color;
            gl_Position = projection * view * model * vec4(in_position, 1.0);
        }
        """
        
        flat_fragment = """
        #version 330
        
        in vec4 v_color;
        out vec4 fragColor;
        
        void main() {
            fragColor = v_color;
        }
        """
        
        self.shaders['flat'] = self.ctx.program(
            vertex_shader=flat_vertex,
            fragment_shader=flat_fragment
        )
    
    def _init_default_material(self):
        """Initialize default material"""
        self.materials[0] = Material()
    
    def load_mesh(self, vertices: np.ndarray, indices: Optional[np.ndarray] = None,
                  normals: Optional[np.ndarray] = None, texcoords: Optional[np.ndarray] = None,
                  colors: Optional[np.ndarray] = None) -> MeshHandle:
        """Load mesh data into GPU"""
        # Prepare vertex data
        vertex_data = vertices.astype('f4').tobytes()
        
        # Create vertex buffer
        vbo = self.ctx.buffer(vertex_data)
        
        # Prepare attributes
        attributes = [('in_position', 3, 'f4')]
        
        if normals is not None:
            normal_data = normals.astype('f4').tobytes()
            vbo_normal = self.ctx.buffer(normal_data)
            attributes.append(('in_normal', 3, 'f4'))
        
        if texcoords is not None:
            texcoord_data = texcoords.astype('f4').tobytes()
            vbo_texcoord = self.ctx.buffer(texcoord_data)
            attributes.append(('in_texcoord', 2, 'f4'))
        
        if colors is not None:
            color_data = colors.astype('f4').tobytes()
            vbo_color = self.ctx.buffer(color_data)
            attributes.append(('in_color', 4, 'f4'))
        
        # Create VAO
        if indices is not None:
            ibo = self.ctx.buffer(indices.astype('i4').tobytes())
            vao = self.ctx.vertex_array(
                self.shaders['basic'],
                [(vbo, '3f', 'in_position')],
                index_buffer=ibo
            )
            index_count = len(indices)
        else:
            vao = self.ctx.vertex_array(
                self.shaders['basic'],
                [(vbo, '3f', 'in_position')]
            )
            index_count = 0
        
        return MeshHandle(
            vao=vao,
            vertex_count=len(vertices),
            index_count=index_count
        )
    
    def render_mesh(self, mesh_handle: MeshHandle, model_matrix: np.ndarray,
                   view_matrix: np.ndarray, projection_matrix: np.ndarray):
        """Render a mesh"""
        shader = self.shaders['basic']
        shader['model'].write(model_matrix.astype('f4').tobytes())
        shader['view'].write(view_matrix.astype('f4').tobytes())
        shader['projection'].write(projection_matrix.astype('f4').tobytes())
        shader['diffuse_color'].value = (1.0, 1.0, 1.0, 1.0)
        shader['light_dir'].value = (0.5, 1.0, 0.3)
        shader['camera_pos'].value = (0.0, 0.0, 5.0)
        shader['use_texture'].value = False
        
        mesh_handle.vao.render()
    
    def clear(self, color: Tuple[float, float, float, float] = (0.1, 0.1, 0.1, 1.0)):
        """Clear the framebuffer"""
        self.ctx.clear(*color)
    
    def set_viewport(self, width: int, height: int):
        """Set viewport size"""
        self.ctx.viewport = (0, 0, width, height)
