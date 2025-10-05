"""
Input management system
"""

import numpy as np
from enum import Enum
from typing import Set


class KeyCode(Enum):
    """Key codes"""
    # Letters
    A = 'a'
    B = 'b'
    C = 'c'
    D = 'd'
    E = 'e'
    F = 'f'
    G = 'g'
    H = 'h'
    I = 'i'
    J = 'j'
    K = 'k'
    L = 'l'
    M = 'm'
    N = 'n'
    O = 'o'
    P = 'p'
    Q = 'q'
    R = 'r'
    S = 's'
    T = 't'
    U = 'u'
    V = 'v'
    W = 'w'
    X = 'x'
    Y = 'y'
    Z = 'z'
    
    # Numbers
    NUM_0 = '0'
    NUM_1 = '1'
    NUM_2 = '2'
    NUM_3 = '3'
    NUM_4 = '4'
    NUM_5 = '5'
    NUM_6 = '6'
    NUM_7 = '7'
    NUM_8 = '8'
    NUM_9 = '9'
    
    # Special keys
    SPACE = 'space'
    ENTER = 'enter'
    ESCAPE = 'escape'
    SHIFT = 'shift'
    CTRL = 'ctrl'
    ALT = 'alt'
    TAB = 'tab'
    
    # Arrow keys
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'


class MouseButton(Enum):
    """Mouse buttons"""
    LEFT = 0
    RIGHT = 1
    MIDDLE = 2


class InputManager:
    """Manages keyboard and mouse input"""
    
    def __init__(self):
        self.keys_down: Set[KeyCode] = set()
        self.keys_pressed: Set[KeyCode] = set()
        self.keys_released: Set[KeyCode] = set()
        
        self.mouse_buttons_down: Set[MouseButton] = set()
        self.mouse_buttons_pressed: Set[MouseButton] = set()
        self.mouse_buttons_released: Set[MouseButton] = set()
        
        self.mouse_position = np.array([0.0, 0.0])
        self.mouse_delta = np.array([0.0, 0.0])
        self.mouse_scroll = 0.0
    
    def update(self):
        """Update input state (call at end of frame)"""
        self.keys_pressed.clear()
        self.keys_released.clear()
        self.mouse_buttons_pressed.clear()
        self.mouse_buttons_released.clear()
        self.mouse_delta = np.array([0.0, 0.0])
        self.mouse_scroll = 0.0
    
    def on_key_press(self, key: KeyCode):
        """Handle key press event"""
        if key not in self.keys_down:
            self.keys_pressed.add(key)
            self.keys_down.add(key)
    
    def on_key_release(self, key: KeyCode):
        """Handle key release event"""
        if key in self.keys_down:
            self.keys_released.add(key)
            self.keys_down.remove(key)
    
    def on_mouse_press(self, button: MouseButton):
        """Handle mouse press event"""
        if button not in self.mouse_buttons_down:
            self.mouse_buttons_pressed.add(button)
            self.mouse_buttons_down.add(button)
    
    def on_mouse_release(self, button: MouseButton):
        """Handle mouse release event"""
        if button in self.mouse_buttons_down:
            self.mouse_buttons_released.add(button)
            self.mouse_buttons_down.remove(button)
    
    def on_mouse_move(self, position: np.ndarray, delta: np.ndarray):
        """Handle mouse move event"""
        self.mouse_position = position
        self.mouse_delta = delta
    
    def on_mouse_scroll(self, delta: float):
        """Handle mouse scroll event"""
        self.mouse_scroll = delta
    
    def get_key(self, key: KeyCode) -> bool:
        """Check if key is currently held down"""
        return key in self.keys_down
    
    def get_key_down(self, key: KeyCode) -> bool:
        """Check if key was pressed this frame"""
        return key in self.keys_pressed
    
    def get_key_up(self, key: KeyCode) -> bool:
        """Check if key was released this frame"""
        return key in self.keys_released
    
    def get_mouse_button(self, button: MouseButton) -> bool:
        """Check if mouse button is currently held down"""
        return button in self.mouse_buttons_down
    
    def get_mouse_button_down(self, button: MouseButton) -> bool:
        """Check if mouse button was pressed this frame"""
        return button in self.mouse_buttons_pressed
    
    def get_mouse_button_up(self, button: MouseButton) -> bool:
        """Check if mouse button was released this frame"""
        return button in self.mouse_buttons_released
    
    def get_axis(self, axis_name: str) -> float:
        """Get axis value (-1 to 1)"""
        if axis_name == "Horizontal":
            value = 0.0
            if self.get_key(KeyCode.D) or self.get_key(KeyCode.RIGHT):
                value += 1.0
            if self.get_key(KeyCode.A) or self.get_key(KeyCode.LEFT):
                value -= 1.0
            return value
        
        elif axis_name == "Vertical":
            value = 0.0
            if self.get_key(KeyCode.W) or self.get_key(KeyCode.UP):
                value += 1.0
            if self.get_key(KeyCode.S) or self.get_key(KeyCode.DOWN):
                value -= 1.0
            return value
        
        return 0.0
