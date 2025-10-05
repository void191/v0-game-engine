"""
Physics engine with collision detection and response
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

from .scene import Entity
from .components import RigidbodyComponent, ColliderComponent


@dataclass
class CollisionInfo:
    """Collision information"""
    entity_a: Entity
    entity_b: Entity
    point: np.ndarray
    normal: np.ndarray
    penetration: float


class PhysicsEngine:
    """Simple physics engine"""
    
    def __init__(self):
        self.gravity = np.array([0.0, -9.81, 0.0])
        self.collision_pairs: List[CollisionInfo] = []
    
    def update(self, scene_manager, delta_time: float):
        """Update physics simulation"""
        self.collision_pairs.clear()
        
        # Get all entities with rigidbodies
        rigidbody_entities = []
        for entity in scene_manager.get_all_entities():
            if 'rigidbody' in entity.components:
                rigidbody_entities.append(entity)
        
        # Apply forces and integrate
        for entity in rigidbody_entities:
            self._integrate(entity, delta_time)
        
        # Detect collisions
        self._detect_collisions(rigidbody_entities)
        
        # Resolve collisions
        for collision in self.collision_pairs:
            self._resolve_collision(collision)
    
    def _integrate(self, entity: Entity, delta_time: float):
        """Integrate rigidbody motion"""
        rigidbody = entity.components['rigidbody']
        
        if rigidbody.is_kinematic:
            return
        
        # Apply gravity
        if rigidbody.use_gravity:
            acceleration = self.gravity
        else:
            acceleration = np.array([0.0, 0.0, 0.0])
        
        # Update velocity
        rigidbody.velocity += acceleration * delta_time
        
        # Apply drag
        rigidbody.velocity *= (1.0 - rigidbody.linear_drag * delta_time)
        rigidbody.angular_velocity *= (1.0 - rigidbody.angular_drag * delta_time)
        
        # Update position
        entity.transform.position += rigidbody.velocity * delta_time
        
        # Update rotation
        entity.transform.rotation += rigidbody.angular_velocity * delta_time
    
    def _detect_collisions(self, entities: List[Entity]):
        """Detect collisions between entities"""
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                entity_a = entities[i]
                entity_b = entities[j]
                
                if 'collider' not in entity_a.components or 'collider' not in entity_b.components:
                    continue
                
                collision = self._check_collision(entity_a, entity_b)
                if collision:
                    self.collision_pairs.append(collision)
    
    def _check_collision(self, entity_a: Entity, entity_b: Entity) -> Optional[CollisionInfo]:
        """Check collision between two entities"""
        collider_a = entity_a.components['collider']
        collider_b = entity_b.components['collider']
        
        # Box-Box collision
        if collider_a.collider_type == 'box' and collider_b.collider_type == 'box':
            return self._check_box_box(entity_a, entity_b)
        
        # Sphere-Sphere collision
        elif collider_a.collider_type == 'sphere' and collider_b.collider_type == 'sphere':
            return self._check_sphere_sphere(entity_a, entity_b)
        
        # Box-Sphere collision
        elif collider_a.collider_type == 'box' and collider_b.collider_type == 'sphere':
            return self._check_box_sphere(entity_a, entity_b)
        elif collider_a.collider_type == 'sphere' and collider_b.collider_type == 'box':
            return self._check_box_sphere(entity_b, entity_a)
        
        return None
    
    def _check_box_box(self, entity_a: Entity, entity_b: Entity) -> Optional[CollisionInfo]:
        """AABB collision detection"""
        collider_a = entity_a.components['collider']
        collider_b = entity_b.components['collider']
        
        pos_a = entity_a.transform.position
        pos_b = entity_b.transform.position
        
        size_a = collider_a.size * entity_a.transform.scale
        size_b = collider_b.size * entity_b.transform.scale
        
        # Calculate half extents
        half_a = size_a / 2
        half_b = size_b / 2
        
        # Calculate overlap on each axis
        overlap_x = (half_a[0] + half_b[0]) - abs(pos_a[0] - pos_b[0])
        overlap_y = (half_a[1] + half_b[1]) - abs(pos_a[1] - pos_b[1])
        overlap_z = (half_a[2] + half_b[2]) - abs(pos_a[2] - pos_b[2])
        
        # Check if overlapping on all axes
        if overlap_x > 0 and overlap_y > 0 and overlap_z > 0:
            # Find minimum overlap axis
            min_overlap = min(overlap_x, overlap_y, overlap_z)
            
            # Calculate normal
            normal = np.array([0.0, 0.0, 0.0])
            if min_overlap == overlap_x:
                normal[0] = 1.0 if pos_a[0] < pos_b[0] else -1.0
            elif min_overlap == overlap_y:
                normal[1] = 1.0 if pos_a[1] < pos_b[1] else -1.0
            else:
                normal[2] = 1.0 if pos_a[2] < pos_b[2] else -1.0
            
            # Calculate contact point
            point = (pos_a + pos_b) / 2
            
            return CollisionInfo(
                entity_a=entity_a,
                entity_b=entity_b,
                point=point,
                normal=normal,
                penetration=min_overlap
            )
        
        return None
    
    def _check_sphere_sphere(self, entity_a: Entity, entity_b: Entity) -> Optional[CollisionInfo]:
        """Sphere-sphere collision detection"""
        collider_a = entity_a.components['collider']
        collider_b = entity_b.components['collider']
        
        pos_a = entity_a.transform.position
        pos_b = entity_b.transform.position
        
        radius_a = collider_a.radius * max(entity_a.transform.scale)
        radius_b = collider_b.radius * max(entity_b.transform.scale)
        
        # Calculate distance
        delta = pos_b - pos_a
        distance = np.linalg.norm(delta)
        
        # Check if overlapping
        if distance < radius_a + radius_b:
            normal = delta / distance if distance > 0 else np.array([0.0, 1.0, 0.0])
            penetration = (radius_a + radius_b) - distance
            point = pos_a + normal * radius_a
            
            return CollisionInfo(
                entity_a=entity_a,
                entity_b=entity_b,
                point=point,
                normal=normal,
                penetration=penetration
            )
        
        return None
    
    def _check_box_sphere(self, box_entity: Entity, sphere_entity: Entity) -> Optional[CollisionInfo]:
        """Box-sphere collision detection"""
        box_collider = box_entity.components['collider']
        sphere_collider = sphere_entity.components['collider']
        
        box_pos = box_entity.transform.position
        sphere_pos = sphere_entity.transform.position
        
        box_size = box_collider.size * box_entity.transform.scale
        sphere_radius = sphere_collider.radius * max(sphere_entity.transform.scale)
        
        # Find closest point on box to sphere
        half_size = box_size / 2
        closest = np.clip(
            sphere_pos - box_pos,
            -half_size,
            half_size
        )
        closest += box_pos
        
        # Calculate distance
        delta = sphere_pos - closest
        distance = np.linalg.norm(delta)
        
        # Check if overlapping
        if distance < sphere_radius:
            normal = delta / distance if distance > 0 else np.array([0.0, 1.0, 0.0])
            penetration = sphere_radius - distance
            
            return CollisionInfo(
                entity_a=box_entity,
                entity_b=sphere_entity,
                point=closest,
                normal=normal,
                penetration=penetration
            )
        
        return None
    
    def _resolve_collision(self, collision: CollisionInfo):
        """Resolve collision with impulse"""
        entity_a = collision.entity_a
        entity_b = collision.entity_b
        
        rigidbody_a = entity_a.components.get('rigidbody')
        rigidbody_b = entity_b.components.get('rigidbody')
        
        if not rigidbody_a or not rigidbody_b:
            return
        
        # Skip if both are kinematic
        if rigidbody_a.is_kinematic and rigidbody_b.is_kinematic:
            return
        
        # Separate objects
        correction = collision.normal * collision.penetration * 0.5
        
        if not rigidbody_a.is_kinematic:
            entity_a.transform.position -= correction
        if not rigidbody_b.is_kinematic:
            entity_b.transform.position += correction
        
        # Calculate relative velocity
        rel_velocity = rigidbody_b.velocity - rigidbody_a.velocity
        
        # Calculate impulse
        velocity_along_normal = np.dot(rel_velocity, collision.normal)
        
        # Don't resolve if velocities are separating
        if velocity_along_normal > 0:
            return
        
        # Calculate restitution (bounciness)
        restitution = 0.5
        
        # Calculate impulse scalar
        impulse_scalar = -(1 + restitution) * velocity_along_normal
        impulse_scalar /= (1 / rigidbody_a.mass + 1 / rigidbody_b.mass)
        
        # Apply impulse
        impulse = collision.normal * impulse_scalar
        
        if not rigidbody_a.is_kinematic:
            rigidbody_a.velocity -= impulse / rigidbody_a.mass
        if not rigidbody_b.is_kinematic:
            rigidbody_b.velocity += impulse / rigidbody_b.mass
    
    def raycast(self, origin: np.ndarray, direction: np.ndarray, max_distance: float = 1000.0) -> Optional[Tuple[Entity, np.ndarray, float]]:
        """Cast a ray and return hit information"""
        # TODO: Implement raycasting
        return None
