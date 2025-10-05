"""
Example pickup item script
"""

from core.scripting import ScriptBehavior


class PickupItem(ScriptBehavior):
    """Collectible item that destroys on pickup"""
    
    def __init__(self):
        super().__init__()
        self.pickup_sound = None
        self.points = 10
    
    def start(self):
        """Initialize pickup"""
        # Make collider a trigger
        collider = self.api.get_component('collider')
        if collider:
            collider.is_trigger = True
    
    def on_trigger_enter(self, other):
        """Handle pickup"""
        # Check if player picked up
        if other.name == "Player":
            self.api.log(f"Picked up item worth {self.points} points!")
            
            # TODO: Play sound
            # TODO: Add points to player
            
            # Destroy this item
            self.api.destroy(self.entity)
