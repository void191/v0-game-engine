"""
Example player controller script
"""

import numpy as np
from core.scripting import ScriptBehavior
from core.input import KeyCode


class PlayerController(ScriptBehavior):
    """First-person player controller"""
    
    def __init__(self):
        super().__init__()
        self.move_speed = 5.0
        self.jump_force = 10.0
        self.mouse_sensitivity = 2.0
        self.is_grounded = False
    
    def start(self):
        """Initialize player"""
        self.api.log("Player controller started")
        
        # Get rigidbody component
        self.rigidbody = self.api.get_component('rigidbody')
        if not self.rigidbody:
            self.api.log("Warning: No rigidbody component found")
    
    def update(self, delta_time: float):
        """Update player movement"""
        # Get input
        horizontal = self.api.input.get_axis("Horizontal")
        vertical = self.api.input.get_axis("Vertical")
        
        # Calculate movement direction
        forward = np.array([0.0, 0.0, 1.0])
        right = np.array([1.0, 0.0, 0.0])
        
        # Rotate by player rotation
        rotation = self.api.transform.rotation
        # TODO: Apply rotation to forward/right vectors
        
        # Calculate velocity
        move_direction = forward * vertical + right * horizontal
        if np.linalg.norm(move_direction) > 0:
            move_direction = move_direction / np.linalg.norm(move_direction)
        
        # Apply movement
        if self.rigidbody:
            self.rigidbody.velocity[0] = move_direction[0] * self.move_speed
            self.rigidbody.velocity[2] = move_direction[2] * self.move_speed
        else:
            self.api.transform.position += move_direction * self.move_speed * delta_time
        
        # Jump
        if self.api.input.get_key_down(KeyCode.SPACE) and self.is_grounded:
            if self.rigidbody:
                self.rigidbody.velocity[1] = self.jump_force
        
        # Mouse look
        mouse_delta = self.api.input.mouse_delta
        self.api.transform.rotation[1] += mouse_delta[0] * self.mouse_sensitivity * delta_time
        # TODO: Clamp vertical rotation
    
    def on_collision_enter(self, collision):
        """Handle collision"""
        # Check if grounded
        if collision.normal[1] > 0.7:  # Roughly pointing up
            self.is_grounded = True
    
    def on_collision_exit(self, collision):
        """Handle collision exit"""
        self.is_grounded = False
