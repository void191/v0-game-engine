"""
Example player controller script
"""

from python_api import Scene, Input, PhysicsBody

# Get player entity
player = Scene.find_entity("player")

def update(dt):
    """Called every frame"""
    speed = 5.0
    
    # Movement
    if Input.is_key_down("W"):
        player.transform.position[2] -= speed * dt
    if Input.is_key_down("S"):
        player.transform.position[2] += speed * dt
    if Input.is_key_down("A"):
        player.transform.position[0] -= speed * dt
    if Input.is_key_down("D"):
        player.transform.position[0] += speed * dt
    
    # Jump
    if Input.is_key_down("Space"):
        PhysicsBody.apply_force(player, (0, 100, 0))
