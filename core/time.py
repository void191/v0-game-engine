"""
Time management system
"""

import time


class TimeManager:
    """Manages game time and delta time"""
    
    def __init__(self):
        self.time = 0.0
        self.delta_time = 0.0
        self.fixed_delta_time = 0.02  # 50 FPS for physics
        self.time_scale = 1.0
        
        self._last_frame_time = time.time()
        self._fixed_accumulator = 0.0
    
    def update(self):
        """Update time (call at start of frame)"""
        current_time = time.time()
        self.delta_time = (current_time - self._last_frame_time) * self.time_scale
        self._last_frame_time = current_time
        self.time += self.delta_time
        
        self._fixed_accumulator += self.delta_time
    
    def should_fixed_update(self) -> bool:
        """Check if fixed update should run"""
        if self._fixed_accumulator >= self.fixed_delta_time:
            self._fixed_accumulator -= self.fixed_delta_time
            return True
        return False
    
    def reset(self):
        """Reset time"""
        self.time = 0.0
        self.delta_time = 0.0
        self._last_frame_time = time.time()
        self._fixed_accumulator = 0.0
