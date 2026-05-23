"""
Configuration management system for Gesture Control Desktop Application.

This module provides JSON-based configuration loading, validation, and management.
It handles default configurations, file persistence, and runtime updates.

Requirements: 12.0, 2.0
"""

import json
import os
import copy
from pathlib import Path
from typing import Any, Dict, Optional
import logging


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigManager:
    """
    Manages application configuration with JSON-based persistence.
    
    Responsibilities:
    - Load configuration from config.json file
    - Validate configuration values
    - Provide default configuration if file is missing
    - Persist configuration changes to file
    - Support runtime configuration updates
    
    Attributes:
        config_path: Path to config.json file
        config: Current configuration dictionary
        logger: Logger instance for debug/error logging
    """
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "application": {
            "name": "Gesture Control Desktop App",
            "version": "1.0.0",
            "logging_level": "INFO"
        },
        "camera": {
            "device_id": 0,
            "fps_target": 30,
            "frame_width": 640,
            "frame_height": 480
        },
        "gesture_engine": {
            "confidence_threshold": 0.70,
            "smoothing_frames": 20,
            "inference_latency_ms": 50
        },
        "gestures": {
            "app_switch": {
                "action": "keyboard_shortcut",
                "params": {"keys": ["alt", "tab"]},
                "cooldown_ms": 500,
                "enabled": True,
                "display_name": "App Switch",
                "icon": "app_switch.svg",
                "description": "Switch between open applications"
            },
            "close_window": {
                "action": "keyboard_shortcut",
                "params": {"keys": ["alt", "F4"]},
                "cooldown_ms": 500,
                "enabled": True,
                "display_name": "Close Window",
                "icon": "close_window.svg",
                "description": "Close current window"
            },
            "play_pause": {
                "action": "keyboard_key",
                "params": {"key": "space"},
                "cooldown_ms": 300,
                "enabled": True,
                "display_name": "Play/Pause",
                "icon": "play_pause.svg",
                "description": "Play or pause media"
            },
            "volume_up": {
                "action": "media_key",
                "params": {"key": "volume_up"},
                "cooldown_ms": 200,
                "enabled": True,
                "display_name": "Volume Up",
                "icon": "volume_up.svg",
                "description": "Increase volume"
            },
            "volume_down": {
                "action": "media_key",
                "params": {"key": "volume_down"},
                "cooldown_ms": 200,
                "enabled": True,
                "display_name": "Volume Down",
                "icon": "volume_down.svg",
                "description": "Decrease volume"
            },
            "scroll_up": {
                "action": "mouse_scroll",
                "params": {"units": 200},
                "cooldown_ms": 100,
                "enabled": True,
                "display_name": "Scroll Up",
                "icon": "scroll_up.svg",
                "description": "Scroll up"
            },
            "scroll_down": {
                "action": "mouse_scroll",
                "params": {"units": -200},
                "cooldown_ms": 100,
                "enabled": True,
                "display_name": "Scroll Down",
                "icon": "scroll_down.svg",
                "description": "Scroll down"
            },
            "screenshot": {
                "action": "keyboard_key",
                "params": {"key": "print"},
                "cooldown_ms": 1000,
                "enabled": True,
                "display_name": "Screenshot",
                "icon": "screenshot.svg",
                "description": "Take screenshot"
            },
            "nothing": {
                "action": "none",
                "params": {},
                "cooldown_ms": 0,
                "enabled": True,
                "display_name": "No Gesture",
                "icon": "nothing.svg",
                "description": "No gesture detected"
            }
        },
        "paths": {
            "model_path": "backend/models/cnn_model_keras.h5",
            "logs_path": "logs",
            "config_path": "config.json"
        },
        "thresholds": {
            "confidence_min": 0.50,
            "confidence_max": 0.95,
            "confidence_default": 0.70,
            "cooldown_min_ms": 0,
            "cooldown_max_ms": 5000,
            "cooldown_default_ms": 500
        }
    }
    
    def __init__(self, config_path: str = "config.json", logger: Optional[logging.Logger] = None):
        """
        Initialize ConfigManager.
        
        Args:
            config_path: Path to config.json file (default: config.json in current directory)
            logger: Logger instance for debug/error logging (optional)
        
        Raises:
            ConfigurationError: If configuration validation fails
        """
        self.config_path = Path(config_path)
        self.logger = logger or logging.getLogger(__name__)
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.
        
        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.logger.info(f"Configuration loaded from {self.config_path}")
                    return config
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse config.json: {e}")
                self.logger.warning("Using default configuration")
                return copy.deepcopy(self.DEFAULT_CONFIG)
            except IOError as e:
                self.logger.error(f"Failed to read config.json: {e}")
                self.logger.warning("Using default configuration")
                return copy.deepcopy(self.DEFAULT_CONFIG)
        else:
            self.logger.info(f"Configuration file not found at {self.config_path}")
            self.logger.info("Using default configuration")
            return copy.deepcopy(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _validate_config(self) -> None:
        """
        Validate configuration values.
        
        Raises:
            ConfigurationError: If validation fails
        """
        try:
            # Validate confidence threshold (support both gesture_engine and gesture_recognition keys)
            gesture_engine = self.config.get("gesture_engine", {}) or self.config.get("gesture_recognition", {})
            confidence = gesture_engine.get("confidence_threshold", 0.70)
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                raise ConfigurationError(
                    f"Invalid confidence_threshold: {confidence}. Must be between 0.0 and 1.0"
                )
            
            # Validate smoothing frames
            smoothing = gesture_engine.get("smoothing_frames", 20)
            if not isinstance(smoothing, int) or smoothing < 1:
                raise ConfigurationError(
                    f"Invalid smoothing_frames: {smoothing}. Must be a positive integer"
                )
            
            # Validate camera device ID
            camera = self.config.get("camera", {})
            device_id = camera.get("device_id", 0)
            if not isinstance(device_id, int) or device_id < 0:
                raise ConfigurationError(
                    f"Invalid camera device_id: {device_id}. Must be a non-negative integer"
                )
            
            # Validate FPS target (support both fps_target and fps keys)
            fps = camera.get("fps_target") or camera.get("fps", 30)
            if not isinstance(fps, int) or fps < 1 or fps > 120:
                raise ConfigurationError(
                    f"Invalid fps_target: {fps}. Must be between 1 and 120"
                )
            
            # Validate gesture configurations
            gestures = self.config.get("gestures", {})
            for gesture_name, gesture_config in gestures.items():
                if not isinstance(gesture_config, dict):
                    raise ConfigurationError(
                        f"Invalid gesture configuration for '{gesture_name}': must be a dictionary"
                    )
                
                # Validate required fields
                required_fields = ["action", "params", "cooldown_ms", "enabled"]
                for field in required_fields:
                    if field not in gesture_config:
                        raise ConfigurationError(
                            f"Missing required field '{field}' in gesture '{gesture_name}'"
                        )
                
                # Validate cooldown
                cooldown = gesture_config.get("cooldown_ms", 0)
                if not isinstance(cooldown, int) or cooldown < 0:
                    raise ConfigurationError(
                        f"Invalid cooldown_ms for gesture '{gesture_name}': {cooldown}. Must be non-negative"
                    )
                
                # Validate enabled flag
                if not isinstance(gesture_config.get("enabled"), bool):
                    raise ConfigurationError(
                        f"Invalid 'enabled' flag for gesture '{gesture_name}': must be boolean"
                    )
            
            self.logger.debug("Configuration validation passed")
        
        except ConfigurationError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Examples:
            config.get("gesture_engine.confidence_threshold")
            config.get("gestures.app_switch.cooldown_ms")
            config.get("camera.device_id", 0)
        
        Args:
            key: Configuration key in dot notation
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot-notation key.
        
        Examples:
            config.set("gesture_engine.confidence_threshold", 0.75)
            config.set("gestures.app_switch.enabled", False)
        
        Args:
            key: Configuration key in dot notation
            value: New value to set
        
        Raises:
            ConfigurationError: If key path is invalid
        """
        keys = key.split(".")
        config = self.config
        
        # Navigate to parent of target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            if not isinstance(config, dict):
                raise ConfigurationError(
                    f"Cannot set '{key}': intermediate key '{k}' is not a dictionary"
                )
        
        # Set the value
        config[keys[-1]] = value
        self.logger.debug(f"Configuration updated: {key} = {value}")
    
    def get_gesture_config(self, gesture_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific gesture.
        
        Args:
            gesture_name: Name of the gesture (e.g., 'app_switch')
        
        Returns:
            Gesture configuration dictionary or None if not found
        """
        return self.config.get("gestures", {}).get(gesture_name)
    
    def update_gesture(self, gesture_name: str, updates: Dict[str, Any]) -> None:
        """
        Update gesture configuration.
        
        Args:
            gesture_name: Name of the gesture
            updates: Dictionary of updates to apply
        
        Raises:
            ConfigurationError: If gesture not found
        """
        if gesture_name not in self.config.get("gestures", {}):
            raise ConfigurationError(f"Gesture '{gesture_name}' not found in configuration")
        
        self.config["gestures"][gesture_name].update(updates)
        self.logger.debug(f"Gesture '{gesture_name}' updated: {updates}")
    
    def save(self) -> None:
        """
        Persist current configuration to file.
        
        Raises:
            ConfigurationError: If file write fails
        """
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write configuration with pretty formatting
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
        
        except IOError as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def reload(self) -> None:
        """
        Reload configuration from file.
        
        Raises:
            ConfigurationError: If validation fails
        """
        self.config = self._load_config()
        self._validate_config()
        self.logger.info("Configuration reloaded")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get entire configuration dictionary.
        
        Returns:
            Complete configuration dictionary
        """
        return copy.deepcopy(self.config)
    
    def reset_to_defaults(self) -> None:
        """
        Reset configuration to default values.
        
        Raises:
            ConfigurationError: If validation fails
        """
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        self._validate_config()
        self.logger.info("Configuration reset to defaults")
