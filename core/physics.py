"""
Physics engine using PyBullet
"""

import numpy as np
import pybullet as p
import pybullet_data
from typing import Dict, Optional
import logging

from .scene import Entity
from .components import RigidbodyComponent, ColliderComponent

logger = logging.getLogger(__name__)


class PhysicsEngine:
    """PyBullet-based physics engine"""
    
    def __init__(self):
        # Initialize PyBullet in DIRECT mode (no GUI)
        self.client_id = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, -9.81, 0, physicsClientId=self.client_id)
        
        # Map entities to PyBullet body IDs
        self.entity_to_body: Dict[int, int] = {}
        self.body_to_entity: Dict[int, Entity] = {}
        
        logger.info("PyBullet physics engine initialized")
    
    def shutdown(self):
        """Shutdown physics engine"""
        p.disconnect(physicsClientId=self.client_id)
        logger.info("Physics engine shutdown")
    
    def add_rigidbody(self, entity: Entity, mass: float = 1.0, 
                     shape_type: str = 'box', size: tuple = (1, 1, 1)):
        """Add a rigidbody to an entity"""
        pos = entity.transform.position
        rot = entity.transform.rotation
        
        # Create collision shape
        if shape_type == 'box':
            half_extents = [s/2 for s in size]
            collision_shape = p.createCollisionShape(
                p.GEOM_BOX,
                halfExtents=half_extents,
                physicsClientId=self.client_id
            )
        elif shape_type == 'sphere':
            radius = size[0] if isinstance(size, (list, tuple)) else size
            collision_shape = p.createCollisionShape(
                p.GEOM_SPHERE,
                radius=radius,
                physicsClientId=self.client_id
            )
        elif shape_type == 'cylinder':
            radius = size[0]
            height = size[1]
            collision_shape = p.createCollisionShape(
                p.GEOM_CYLINDER,
                radius=radius,
                height=height,
                physicsClientId=self.client_id
            )
        else:
            collision_shape = p.createCollisionShape(
                p.GEOM_BOX,
                halfExtents=[0.5, 0.5, 0.5],
                physicsClientId=self.client_id
            )
        
        # Create multi-body
        body_id = p.createMultiBody(
            baseMass=mass,
            baseCollisionShapeIndex=collision_shape,
            basePosition=pos.tolist(),
            baseOrientation=p.getQuaternionFromEuler(rot.tolist()),
            physicsClientId=self.client_id
        )
        
        # Store mapping
        self.entity_to_body[id(entity)] = body_id
        self.body_to_entity[body_id] = entity
        
        logger.debug(f"Added rigidbody to entity {entity.name}")
    
    def remove_rigidbody(self, entity: Entity):
        """Remove rigidbody from entity"""
        entity_id = id(entity)
        if entity_id in self.entity_to_body:
            body_id = self.entity_to_body[entity_id]
            p.removeBody(body_id, physicsClientId=self.client_id)
            del self.entity_to_body[entity_id]
            del self.body_to_entity[body_id]
    
    def update(self, scene_manager, delta_time: float):
        """Update physics simulation"""
        # Step simulation
        p.stepSimulation(physicsClientId=self.client_id)
        
        # Sync entity transforms with physics bodies
        for entity_id, body_id in self.entity_to_body.items():
            entity = self.body_to_entity[body_id]
            
            # Get position and orientation from PyBullet
            pos, orn = p.getBasePositionAndOrientation(
                body_id,
                physicsClientId=self.client_id
            )
            
            # Update entity transform
            entity.transform.position = np.array(pos, dtype=np.float32)
            euler = p.getEulerFromQuaternion(orn)
            entity.transform.rotation = np.array(euler, dtype=np.float32)
    
    def apply_force(self, entity: Entity, force: np.ndarray):
        """Apply force to entity"""
        entity_id = id(entity)
        if entity_id in self.entity_to_body:
            body_id = self.entity_to_body[entity_id]
            p.applyExternalForce(
                body_id,
                -1,
                force.tolist(),
                [0, 0, 0],
                p.WORLD_FRAME,
                physicsClientId=self.client_id
            )
    
    def apply_impulse(self, entity: Entity, impulse: np.ndarray):
        """Apply impulse to entity"""
        entity_id = id(entity)
        if entity_id in self.entity_to_body:
            body_id = self.entity_to_body[entity_id]
            p.applyExternalForce(
                body_id,
                -1,
                impulse.tolist(),
                [0, 0, 0],
                p.WORLD_FRAME,
                physicsClientId=self.client_id
            )
    
    def raycast(self, origin: np.ndarray, direction: np.ndarray, 
                max_distance: float = 1000.0) -> Optional[tuple]:
        """Cast a ray and return hit information"""
        end = origin + direction * max_distance
        
        result = p.rayTest(
            origin.tolist(),
            end.tolist(),
            physicsClientId=self.client_id
        )
        
        if result and result[0][0] != -1:
            body_id = result[0][0]
            hit_pos = np.array(result[0][3])
            hit_normal = np.array(result[0][4])
            
            if body_id in self.body_to_entity:
                entity = self.body_to_entity[body_id]
                return (entity, hit_pos, hit_normal)
        
        return None
