"""
Unit tests for configuration management system.

Tests cover:
- Configuration loading from file
- Default configuration fallback
- Configuration validation
- Dot-notation get/set operations
- Gesture configuration management
- Configuration persistence
- Error handling
"""

import json
import pytest
import tempfile
import logging
import copy
from pathlib import Path
from unittest.mock import patch, mock_open

from config import ConfigManager, ConfigurationError


class TestConfigManagerInitialization:
    """Test ConfigManager initialization and file loading."""
    
    def test_load_valid_config_file(self):
        """Test loading a valid configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = {
                "application": {"name": "Test App"},
                "camera": {"device_id": 0, "fps_target": 30},
                "gesture_engine": {"confidence_threshold": 0.75, "smoothing_frames": 20},
                "gestures": copy.deepcopy(ConfigManager.DEFAULT_CONFIG["gestures"]),
                "paths": copy.deepcopy(ConfigManager.DEFAULT_CONFIG["paths"]),
                "thresholds": copy.deepcopy(ConfigManager.DEFAULT_CONFIG["thresholds"])
            }
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            assert config.get("application.name") == "Test App"
            assert config.get("camera.device_id") == 0
            assert config.get("gesture_engine.confidence_threshold") == 0.75
    
    def test_use_default_config_when_file_missing(self):
        """Test that default configuration is used when file doesn't exist."""
        config = ConfigManager(config_path="/nonexistent/path/config.json")
        assert config.get("gesture_engine.confidence_threshold") == 0.70
        assert config.get("camera.fps_target") == 30
        assert "app_switch" in config.get("gestures")
    
    def test_use_default_config_on_json_parse_error(self):
        """Test that default configuration is used on JSON parse error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            with open(config_path, 'w') as f:
                f.write("{ invalid json }")
            
            config = ConfigManager(config_path=str(config_path))
            assert config.get("gesture_engine.confidence_threshold") == 0.70
    
    def test_logger_initialization(self):
        """Test that logger is properly initialized."""
        logger = logging.getLogger("test_logger")
        config = ConfigManager(logger=logger)
        assert config.logger == logger


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_validate_confidence_threshold_valid(self):
        """Test validation of valid confidence threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            config_data["gesture_engine"]["confidence_threshold"] = 0.85
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            assert config.get("gesture_engine.confidence_threshold") == 0.85
    
    def test_validate_confidence_threshold_invalid_range(self):
        """Test validation fails for confidence threshold outside 0-1 range."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            config_data["gesture_engine"]["confidence_threshold"] = 1.5
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            with pytest.raises(ConfigurationError):
                ConfigManager(config_path=str(config_path))
    
    def test_validate_smoothing_frames_positive(self):
        """Test validation of smoothing frames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            config_data["gesture_engine"]["smoothing_frames"] = 0
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            with pytest.raises(ConfigurationError):
                ConfigManager(config_path=str(config_path))
    
    def test_validate_camera_device_id(self):
        """Test validation of camera device ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            config_data["camera"]["device_id"] = -1
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            with pytest.raises(ConfigurationError):
                ConfigManager(config_path=str(config_path))
    
    def test_validate_fps_target_range(self):
        """Test validation of FPS target."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            config_data["camera"]["fps_target"] = 200
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            with pytest.raises(ConfigurationError):
                ConfigManager(config_path=str(config_path))
    
    def test_validate_gesture_missing_required_field(self):
        """Test validation fails when gesture is missing required field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            config_data["gestures"]["app_switch"].pop("action")
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            with pytest.raises(ConfigurationError):
                ConfigManager(config_path=str(config_path))
    
    def test_validate_gesture_invalid_cooldown(self):
        """Test validation of gesture cooldown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            config_data["gestures"]["app_switch"]["cooldown_ms"] = -100
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            with pytest.raises(ConfigurationError):
                ConfigManager(config_path=str(config_path))
    
    def test_validate_gesture_invalid_enabled_flag(self):
        """Test validation of gesture enabled flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            config_data["gestures"]["app_switch"]["enabled"] = "yes"
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            with pytest.raises(ConfigurationError):
                ConfigManager(config_path=str(config_path))


class TestConfigGetSet:
    """Test dot-notation get/set operations."""
    
    def test_get_nested_value(self):
        """Test getting nested configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            assert config.get("gesture_engine.confidence_threshold") == 0.70
            assert config.get("camera.device_id") == 0
            assert config.get("gestures.app_switch.cooldown_ms") == 500
    
    def test_get_with_default(self):
        """Test get with default value for missing key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            assert config.get("nonexistent.key", "default") == "default"
            assert config.get("nonexistent.key", 42) == 42
    
    def test_get_returns_none_for_missing_key(self):
        """Test get returns None for missing key without default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            assert config.get("nonexistent.key") is None
    
    def test_set_nested_value(self):
        """Test setting nested configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            config.set("gesture_engine.confidence_threshold", 0.85)
            assert config.get("gesture_engine.confidence_threshold") == 0.85
    
    def test_set_creates_intermediate_dicts(self):
        """Test that set creates intermediate dictionaries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            config.set("new_section.new_key", "new_value")
            assert config.get("new_section.new_key") == "new_value"
    
    def test_set_invalid_path_raises_error(self):
        """Test that set raises error for invalid path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            # Try to set a key on a non-dict value
            with pytest.raises(ConfigurationError):
                config.set("camera.device_id.invalid", "value")


class TestGestureConfiguration:
    """Test gesture-specific configuration operations."""
    
    def test_get_gesture_config(self):
        """Test getting configuration for a specific gesture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            gesture_config = config.get_gesture_config("app_switch")
            assert gesture_config is not None
            assert gesture_config["action"] == "keyboard_shortcut"
            assert gesture_config["cooldown_ms"] == 500
    
    def test_get_gesture_config_not_found(self):
        """Test getting configuration for non-existent gesture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            gesture_config = config.get_gesture_config("nonexistent_gesture")
            assert gesture_config is None
    
    def test_update_gesture(self):
        """Test updating gesture configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            config.update_gesture("app_switch", {"cooldown_ms": 1000, "enabled": False})
            assert config.get("gestures.app_switch.cooldown_ms") == 1000
            assert config.get("gestures.app_switch.enabled") is False
    
    def test_update_gesture_not_found(self):
        """Test updating non-existent gesture raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            with pytest.raises(ConfigurationError):
                config.update_gesture("nonexistent_gesture", {"cooldown_ms": 1000})
    
    def test_all_default_gestures_present(self):
        """Test that all default gestures are present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            expected_gestures = [
                "app_switch", "close_window", "play_pause", "volume_up", "volume_down",
                "scroll_up", "scroll_down", "screenshot", "nothing"
            ]
            for gesture in expected_gestures:
                assert config.get_gesture_config(gesture) is not None


class TestConfigPersistence:
    """Test configuration file persistence."""
    
    def test_save_configuration(self):
        """Test saving configuration to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config = ConfigManager(config_path=str(config_path))
            config.set("gesture_engine.confidence_threshold", 0.85)
            config.save()
            
            # Verify file was created and contains the updated value
            assert config_path.exists()
            with open(config_path, 'r') as f:
                saved_config = json.load(f)
            assert saved_config["gesture_engine"]["confidence_threshold"] == 0.85
    
    def test_save_creates_parent_directories(self):
        """Test that save creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "subdir" / "config.json"
            config = ConfigManager(config_path=str(config_path))
            config.save()
            
            assert config_path.exists()
            assert config_path.parent.exists()
    
    def test_reload_configuration(self):
        """Test reloading configuration from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            config_data["gesture_engine"]["confidence_threshold"] = 0.75
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            assert config.get("gesture_engine.confidence_threshold") == 0.75
            
            # Modify file externally
            config_data["gesture_engine"]["confidence_threshold"] = 0.90
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            # Reload and verify
            config.reload()
            assert config.get("gesture_engine.confidence_threshold") == 0.90
    
    def test_save_invalid_path_raises_error(self):
        """Test that save raises error for invalid path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config = ConfigManager(config_path=str(config_path))
            config.save()
            
            # Verify file was created
            assert config_path.exists()


class TestConfigReset:
    """Test configuration reset functionality."""
    
    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            config.set("gesture_engine.confidence_threshold", 0.50)
            config.set("camera.device_id", 5)
            
            config.reset_to_defaults()
            
            assert config.get("gesture_engine.confidence_threshold") == 0.70
            assert config.get("camera.device_id") == 0
    
    def test_reset_validates_after_reset(self):
        """Test that reset validates configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            config.reset_to_defaults()
            # Should not raise any errors
            assert config.get("gesture_engine.confidence_threshold") == 0.70


class TestConfigGetAll:
    """Test getting entire configuration."""
    
    def test_get_all_returns_copy(self):
        """Test that get_all returns a copy, not reference."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            all_config = config.get_all()
            all_config["gesture_engine"]["confidence_threshold"] = 0.50
            
            # Original should not be modified
            assert config.get("gesture_engine.confidence_threshold") == 0.70
    
    def test_get_all_contains_all_sections(self):
        """Test that get_all contains all configuration sections."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            all_config = config.get_all()
            
            assert "application" in all_config
            assert "camera" in all_config
            assert "gesture_engine" in all_config
            assert "gestures" in all_config
            assert "paths" in all_config
            assert "thresholds" in all_config


class TestConfigIntegration:
    """Integration tests for configuration system."""
    
    def test_full_workflow(self):
        """Test complete configuration workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            
            # Create and modify config
            config = ConfigManager(config_path=str(config_path))
            config.set("gesture_engine.confidence_threshold", 0.80)
            config.update_gesture("app_switch", {"cooldown_ms": 1000})
            config.save()
            
            # Load in new instance and verify
            config2 = ConfigManager(config_path=str(config_path))
            assert config2.get("gesture_engine.confidence_threshold") == 0.80
            assert config2.get("gestures.app_switch.cooldown_ms") == 1000
    
    def test_multiple_gesture_updates(self):
        """Test updating multiple gestures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_data = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            config = ConfigManager(config_path=str(config_path))
            
            config.update_gesture("app_switch", {"enabled": False})
            config.update_gesture("close_window", {"cooldown_ms": 2000})
            config.update_gesture("play_pause", {"enabled": False})
            
            assert config.get("gestures.app_switch.enabled") is False
            assert config.get("gestures.close_window.cooldown_ms") == 2000
            assert config.get("gestures.play_pause.enabled") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
