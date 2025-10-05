"""
Example rotating object script
"""

import numpy as np
from core.scripting import ScriptBehavior


class RotatingObject(ScriptBehavior):
    """Simple rotating object"""
    
    def __init__(self):
        super().__init__()
        self.rotation_speed = np.array([0.0, 1.0, 0.0])  # Radians per second
    
    def update(self, delta_time: float):
        """Rotate object"""
        self.api.transform.rotation += self.rotation_speed * delta_time
