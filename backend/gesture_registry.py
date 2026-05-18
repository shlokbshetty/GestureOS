"""
Gesture Registry Module

Manages gesture-to-action mappings and configuration persistence.
Provides centralized registry for all supported gestures with metadata.

Requirements: 2.1, 2.2, 2.7
"""

import json
import os
from typing import Dict, Optional


class GestureRegistry:
    """
    Central registry for gesture-to-action mappings.
    
    Maintains a mapping of gesture names to system actions with metadata.
    Supports loading/saving configuration from/to JSON files.
    
    Attributes:
        DEFAULT_GESTURES: Mapping of all 9 supported gestures with metadata
        config_path: Path to configuration file (gestures.json)
        gestures: Current gesture configuration dictionary
    """
    
    # Default gesture mappings with all metadata
    # Requirement 2.2: Support 9 gestures
    # Requirement 2.7: Include metadata (display_name, icon, description, cooldown_ms, enabled)
    DEFAULT_GESTURES = {
        'app_switch': {
            'action': 'keyboard_shortcut',
            'params': {'keys': ['alt', 'tab']},
            'cooldown_ms': 500,
            'enabled': True,
            'display_name': 'App Switch',
            'icon': 'app_switch.svg',
            'description': 'Switch between open applications'
        },
        'close_window': {
            'action': 'keyboard_shortcut',
            'params': {'keys': ['alt', 'F4']},
            'cooldown_ms': 500,
            'enabled': True,
            'display_name': 'Close Window',
            'icon': 'close_window.svg',
            'description': 'Close current window'
        },
        'play_pause': {
            'action': 'keyboard_key',
            'params': {'key': 'space'},
            'cooldown_ms': 300,
            'enabled': True,
            'display_name': 'Play/Pause',
            'icon': 'play_pause.svg',
            'description': 'Play or pause media'
        },
        'volume_up': {
            'action': 'media_key',
            'params': {'key': 'volume_up'},
            'cooldown_ms': 200,
            'enabled': True,
            'display_name': 'Volume Up',
            'icon': 'volume_up.svg',
            'description': 'Increase volume'
        },
        'volume_down': {
            'action': 'media_key',
            'params': {'key': 'volume_down'},
            'cooldown_ms': 200,
            'enabled': True,
            'display_name': 'Volume Down',
            'icon': 'volume_down.svg',
            'description': 'Decrease volume'
        },
        'scroll_up': {
            'action': 'mouse_scroll',
            'params': {'units': 200},
            'cooldown_ms': 100,
            'enabled': True,
            'display_name': 'Scroll Up',
            'icon': 'scroll_up.svg',
            'description': 'Scroll up'
        },
        'scroll_down': {
            'action': 'mouse_scroll',
            'params': {'units': -200},
            'cooldown_ms': 100,
            'enabled': True,
            'display_name': 'Scroll Down',
            'icon': 'scroll_down.svg',
            'description': 'Scroll down'
        },
        'screenshot': {
            'action': 'keyboard_key',
            'params': {'key': 'print'},
            'cooldown_ms': 1000,
            'enabled': True,
            'display_name': 'Screenshot',
            'icon': 'screenshot.svg',
            'description': 'Take screenshot'
        },
        'nothing': {
            'action': 'none',
            'params': {},
            'cooldown_ms': 0,
            'enabled': True,
            'display_name': 'No Gesture',
            'icon': 'nothing.svg',
            'description': 'No gesture detected'
        }
    }
    
    def __init__(self, config_path: str = 'gestures.json'):
        """
        Initialize GestureRegistry.
        
        Args:
            config_path: Path to gestures.json configuration file
        """
        self.config_path = config_path
        self.gestures = self._load_config()
    
    def _load_config(self) -> Dict:
        """
        Load gesture configuration from file.
        
        Requirement 2.3: Load gesture mappings from configuration file (gestures.json)
        
        Returns:
            Dictionary of gesture configurations, or DEFAULT_GESTURES if file not found
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Return gestures from config, or use defaults if not present
                    return config.get('gestures', self.DEFAULT_GESTURES.copy())
            else:
                # File not found, use defaults
                return self.DEFAULT_GESTURES.copy()
        except (json.JSONDecodeError, IOError) as e:
            # Error reading file, use defaults
            print(f"Warning: Could not load gesture config from {self.config_path}: {e}")
            return self.DEFAULT_GESTURES.copy()
    
    def save_config(self) -> bool:
        """
        Persist gesture configuration to file.
        
        Requirement 2.4: Persist changes to configuration file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            config = {'gestures': self.gestures}
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except IOError as e:
            print(f"Error: Could not save gesture config to {self.config_path}: {e}")
            return False
    
    def get_action(self, gesture_name: str) -> Optional[Dict]:
        """
        Get action for a gesture.
        
        Requirement 2.5: Return action type, parameters, and cooldown period
        Requirement 2.6: Ignore disabled gestures
        
        Args:
            gesture_name: Name of the gesture
        
        Returns:
            Dictionary with 'action', 'params', and 'cooldown_ms', or None if gesture
            not found or disabled
        """
        if gesture_name not in self.gestures:
            return None
        
        gesture = self.gestures[gesture_name]
        
        # Check if gesture is enabled (Requirement 2.6)
        if not gesture.get('enabled', True):
            return None
        
        return {
            'action': gesture['action'],
            'params': gesture['params'],
            'cooldown_ms': gesture['cooldown_ms']
        }
    
    def get_all_gestures(self) -> Dict:
        """
        Get all gesture metadata.
        
        Returns:
            Dictionary of all gestures with their metadata
        """
        return self.gestures.copy()
    
    def get_gesture_metadata(self, gesture_name: str) -> Optional[Dict]:
        """
        Get metadata for a specific gesture.
        
        Requirement 2.7: Include metadata (display_name, icon, description, cooldown_ms, enabled)
        
        Args:
            gesture_name: Name of the gesture
        
        Returns:
            Dictionary with gesture metadata, or None if not found
        """
        if gesture_name not in self.gestures:
            return None
        
        gesture = self.gestures[gesture_name]
        return {
            'display_name': gesture.get('display_name'),
            'icon': gesture.get('icon'),
            'description': gesture.get('description'),
            'cooldown_ms': gesture.get('cooldown_ms'),
            'enabled': gesture.get('enabled', True)
        }
    
    def update_gesture(self, gesture_name: str, updates: Dict) -> bool:
        """
        Update gesture configuration.
        
        Requirement 2.4: Persist changes to configuration file
        
        Args:
            gesture_name: Name of the gesture to update
            updates: Dictionary of fields to update
        
        Returns:
            True if successful, False if gesture not found
        """
        if gesture_name not in self.gestures:
            return False
        
        self.gestures[gesture_name].update(updates)
        return self.save_config()
    
    def set_enabled(self, gesture_name: str, enabled: bool) -> bool:
        """
        Enable or disable a gesture.
        
        Requirement 2.6: Support disabling gestures
        
        Args:
            gesture_name: Name of the gesture
            enabled: True to enable, False to disable
        
        Returns:
            True if successful, False if gesture not found
        """
        if gesture_name not in self.gestures:
            return False
        
        self.gestures[gesture_name]['enabled'] = enabled
        return self.save_config()
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all gestures to default configuration.
        
        Returns:
            True if successful, False otherwise
        """
        self.gestures = self.DEFAULT_GESTURES.copy()
        return self.save_config()
    
    def validate_gesture(self, gesture_name: str) -> bool:
        """
        Validate that a gesture exists in the registry.
        
        Args:
            gesture_name: Name of the gesture to validate
        
        Returns:
            True if gesture exists, False otherwise
        """
        return gesture_name in self.gestures
