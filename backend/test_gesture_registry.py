"""
Unit tests for GestureRegistry class

Tests the gesture registry data structure, configuration loading/saving,
and gesture metadata management.

Requirements: 2.1, 2.2, 2.7
"""

import json
import os
import tempfile
import pytest
from gesture_registry import GestureRegistry


class TestGestureRegistry:
    """Test suite for GestureRegistry class"""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    @pytest.fixture
    def registry(self, temp_config_file):
        """Create a GestureRegistry instance with temp config"""
        return GestureRegistry(config_path=temp_config_file)
    
    def test_default_gestures_exist(self):
        """Test that DEFAULT_GESTURES contains all 9 required gestures"""
        # Requirement 2.2: Support 9 gestures
        expected_gestures = {
            'app_switch', 'close_window', 'play_pause', 'screenshot',
            'scroll_down', 'scroll_up', 'volume_down', 'volume_up', 'nothing'
        }
        assert set(GestureRegistry.DEFAULT_GESTURES.keys()) == expected_gestures
    
    def test_gesture_metadata_structure(self):
        """Test that each gesture has required metadata"""
        # Requirement 2.7: Include metadata
        required_fields = {'display_name', 'icon', 'description', 'cooldown_ms', 'enabled'}
        
        for gesture_name, gesture_data in GestureRegistry.DEFAULT_GESTURES.items():
            # Check required metadata fields
            assert 'display_name' in gesture_data
            assert 'icon' in gesture_data
            assert 'description' in gesture_data
            assert 'cooldown_ms' in gesture_data
            assert 'enabled' in gesture_data
            
            # Check action and params
            assert 'action' in gesture_data
            assert 'params' in gesture_data
    
    def test_gesture_action_mapping(self):
        """Test that gestures have correct action mappings"""
        # Requirement 2.1: Maintain mapping of gesture names to system actions
        registry = GestureRegistry.DEFAULT_GESTURES
        
        assert registry['app_switch']['action'] == 'keyboard_shortcut'
        assert registry['close_window']['action'] == 'keyboard_shortcut'
        assert registry['play_pause']['action'] == 'keyboard_key'
        assert registry['volume_up']['action'] == 'media_key'
        assert registry['volume_down']['action'] == 'media_key'
        assert registry['scroll_up']['action'] == 'mouse_scroll'
        assert registry['scroll_down']['action'] == 'mouse_scroll'
        assert registry['screenshot']['action'] == 'keyboard_key'
        assert registry['nothing']['action'] == 'none'
    
    def test_load_config_default_when_file_missing(self, temp_config_file):
        """Test that DEFAULT_GESTURES are used when config file doesn't exist"""
        # Requirement 2.3: Load from file, fallback to defaults
        registry = GestureRegistry(config_path=temp_config_file)
        
        # Should have all default gestures
        assert len(registry.gestures) == 9
        assert 'app_switch' in registry.gestures
        assert 'nothing' in registry.gestures
    
    def test_save_and_load_config(self, temp_config_file):
        """Test saving and loading configuration"""
        # Requirement 2.4: Persist changes to configuration file
        registry = GestureRegistry(config_path=temp_config_file)
        
        # Modify a gesture
        registry.update_gesture('app_switch', {'cooldown_ms': 1000})
        
        # Create new registry instance and verify changes persisted
        registry2 = GestureRegistry(config_path=temp_config_file)
        assert registry2.gestures['app_switch']['cooldown_ms'] == 1000
    
    def test_get_action_returns_correct_structure(self, registry):
        """Test that get_action returns action, params, and cooldown"""
        # Requirement 2.5: Return action type, parameters, and cooldown period
        action = registry.get_action('app_switch')
        
        assert action is not None
        assert 'action' in action
        assert 'params' in action
        assert 'cooldown_ms' in action
        assert action['action'] == 'keyboard_shortcut'
        assert action['cooldown_ms'] == 500
    
    def test_get_action_returns_none_for_unknown_gesture(self, registry):
        """Test that get_action returns None for unknown gesture"""
        action = registry.get_action('unknown_gesture')
        assert action is None
    
    def test_get_action_respects_enabled_status(self, registry):
        """Test that disabled gestures return None"""
        # Requirement 2.6: Ignore disabled gestures
        registry.set_enabled('app_switch', False)
        action = registry.get_action('app_switch')
        assert action is None
        
        # Re-enable and verify it works
        registry.set_enabled('app_switch', True)
        action = registry.get_action('app_switch')
        assert action is not None
    
    def test_get_gesture_metadata(self, registry):
        """Test retrieving gesture metadata"""
        # Requirement 2.7: Include metadata
        metadata = registry.get_gesture_metadata('app_switch')
        
        assert metadata is not None
        assert metadata['display_name'] == 'App Switch'
        assert metadata['icon'] == 'app_switch.svg'
        assert metadata['description'] == 'Switch between open applications'
        assert metadata['cooldown_ms'] == 500
        assert metadata['enabled'] is True
    
    def test_get_all_gestures(self, registry):
        """Test retrieving all gestures"""
        all_gestures = registry.get_all_gestures()
        
        assert len(all_gestures) == 9
        assert 'app_switch' in all_gestures
        assert 'nothing' in all_gestures
    
    def test_update_gesture(self, registry):
        """Test updating gesture configuration"""
        # Requirement 2.4: Persist changes
        success = registry.update_gesture('app_switch', {'cooldown_ms': 750})
        
        assert success is True
        assert registry.gestures['app_switch']['cooldown_ms'] == 750
    
    def test_update_gesture_nonexistent(self, registry):
        """Test updating nonexistent gesture returns False"""
        success = registry.update_gesture('nonexistent', {'cooldown_ms': 100})
        assert success is False
    
    def test_set_enabled(self, registry):
        """Test enabling/disabling gestures"""
        # Requirement 2.6: Support disabling gestures
        success = registry.set_enabled('app_switch', False)
        assert success is True
        assert registry.gestures['app_switch']['enabled'] is False
        
        success = registry.set_enabled('app_switch', True)
        assert success is True
        assert registry.gestures['app_switch']['enabled'] is True
    
    def test_set_enabled_nonexistent(self, registry):
        """Test enabling nonexistent gesture returns False"""
        success = registry.set_enabled('nonexistent', True)
        assert success is False
    
    def test_validate_gesture(self, registry):
        """Test gesture validation"""
        assert registry.validate_gesture('app_switch') is True
        assert registry.validate_gesture('nothing') is True
        assert registry.validate_gesture('unknown') is False
    
    def test_reset_to_defaults(self, registry):
        """Test resetting to default configuration"""
        # Modify some gestures
        registry.update_gesture('app_switch', {'cooldown_ms': 1000})
        registry.set_enabled('play_pause', False)
        
        # Reset to defaults
        success = registry.reset_to_defaults()
        assert success is True
        
        # Verify defaults are restored
        assert registry.gestures['app_switch']['cooldown_ms'] == 500
        assert registry.gestures['play_pause']['enabled'] is True
    
    def test_config_file_format(self, temp_config_file):
        """Test that config file is saved in correct JSON format"""
        registry = GestureRegistry(config_path=temp_config_file)
        registry.save_config()
        
        # Read and verify JSON structure
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        assert 'gestures' in config
        assert 'app_switch' in config['gestures']
    
    def test_cooldown_values_are_reasonable(self, registry):
        """Test that cooldown values are within reasonable ranges"""
        for gesture_name, gesture_data in registry.gestures.items():
            cooldown = gesture_data['cooldown_ms']
            # Cooldown should be between 0 and 5000ms
            assert 0 <= cooldown <= 5000
    
    def test_nothing_gesture_has_zero_cooldown(self, registry):
        """Test that 'nothing' gesture has zero cooldown"""
        nothing_action = registry.get_action('nothing')
        assert nothing_action is not None
        assert nothing_action['cooldown_ms'] == 0
    
    def test_all_gestures_have_unique_icons(self):
        """Test that each gesture has a unique icon"""
        icons = [g['icon'] for g in GestureRegistry.DEFAULT_GESTURES.values()]
        assert len(icons) == len(set(icons))
    
    def test_gesture_params_structure(self):
        """Test that gesture params have correct structure"""
        registry = GestureRegistry.DEFAULT_GESTURES
        
        # Keyboard shortcuts should have 'keys' param
        assert 'keys' in registry['app_switch']['params']
        assert 'keys' in registry['close_window']['params']
        
        # Keyboard keys should have 'key' param
        assert 'key' in registry['play_pause']['params']
        assert 'key' in registry['screenshot']['params']
        
        # Media keys should have 'key' param
        assert 'key' in registry['volume_up']['params']
        assert 'key' in registry['volume_down']['params']
        
        # Mouse scroll should have 'units' param
        assert 'units' in registry['scroll_up']['params']
        assert 'units' in registry['scroll_down']['params']


class TestGestureRegistryIntegration:
    """Integration tests for GestureRegistry"""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    def test_multiple_registries_share_config(self, temp_config_file):
        """Test that multiple registry instances share the same config file"""
        registry1 = GestureRegistry(config_path=temp_config_file)
        registry1.update_gesture('app_switch', {'cooldown_ms': 1500})
        
        registry2 = GestureRegistry(config_path=temp_config_file)
        assert registry2.gestures['app_switch']['cooldown_ms'] == 1500
    
    def test_config_persistence_across_instances(self, temp_config_file):
        """Test that configuration persists across registry instances"""
        # Create and modify
        registry1 = GestureRegistry(config_path=temp_config_file)
        registry1.set_enabled('volume_up', False)
        registry1.update_gesture('scroll_up', {'cooldown_ms': 250})
        
        # Create new instance and verify
        registry2 = GestureRegistry(config_path=temp_config_file)
        assert registry2.gestures['volume_up']['enabled'] is False
        assert registry2.gestures['scroll_up']['cooldown_ms'] == 250
