# PolyForge Engine

A Python-based game engine with integrated voxel and low-poly modeling tools, powered by Godot for rendering.

## Features

- **Integrated Editors**
  - Voxel Editor with painting, sculpting, and terrain tools
  - Low-Poly Mesh Editor with vertex/edge/face manipulation
  - Visual Effects Editor for particles and shaders
  - Level Editor with scene hierarchy and entity management

- **Entity Component System**
  - Transform, Mesh, Light, Camera components
  - Physics with Rigidbody and Collider components
  - Python scripting with lifecycle callbacks

- **Physics Engine**
  - Collision detection (AABB, sphere, mixed)
  - Rigidbody dynamics with gravity and drag
  - Trigger volumes for game logic

- **Python Scripting API**
  - Easy-to-use scripting interface
  - Input management (keyboard, mouse)
  - Scene management and entity manipulation
  - Lifecycle methods (awake, start, update, fixed_update)

- **Export System**
  - Multi-platform builds (Windows, Linux, macOS, Web)
  - Asset optimization and compression
  - Standalone runtime player

## Installation

\`\`\`bash
# Install dependencies
pip install PySide6 numpy pillow

# Install Godot (for rendering)
# Download from https://godotengine.org/
\`\`\`

## Quick Start

\`\`\`bash
# Run the editor
python main.py

# Run a game build
python runtime/player.py --project ./projects/my_game --scene main.scene.json
\`\`\`

## Project Structure

\`\`\`
polyforge/
├── core/              # Core engine systems
│   ├── engine.py      # Main engine coordinator
│   ├── scene.py       # Scene and entity management
│   ├── physics.py     # Physics engine
│   ├── scripting.py   # Python scripting API
│   └── components.py  # Entity components
├── editor/            # Editor UI
│   ├── main_window.py # Main editor window
│   ├── viewport.py    # 3D viewport
│   └── panels/        # Editor panels
├── tools/             # Modeling tools
│   ├── voxel/         # Voxel editor
│   └── mesh/          # Mesh editor
├── runtime/           # Standalone player
│   └── player.py      # Runtime player
├── export/            # Build export system
│   ├── exporter.py    # Game exporter
│   └── build_dialog.py # Export UI
└── examples/          # Example scripts
    ├── player_controller.py
    └── rotating_object.py
\`\`\`

## Creating a Game Script

\`\`\`python
from core.scripting import ScriptBehavior
from core.input import KeyCode

class PlayerController(ScriptBehavior):
    def __init__(self):
        super().__init__()
        self.move_speed = 5.0
    
    def start(self):
        self.api.log("Player started!")
    
    def update(self, delta_time):
        # Get input
        horizontal = self.api.input.get_axis("Horizontal")
        vertical = self.api.input.get_axis("Vertical")
        
        # Move player
        self.api.transform.position[0] += horizontal * self.move_speed * delta_time
        self.api.transform.position[2] += vertical * self.move_speed * delta_time
\`\`\`

## Exporting Your Game

1. Open the editor
2. Go to Build > Export Build...
3. Configure platform and settings
4. Click Export

## License

MIT License
