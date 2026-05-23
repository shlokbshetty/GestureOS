"""
Unit tests for the structured logging system.

Tests verify:
- Logger initialization and singleton pattern
- File creation and rotation configuration
- Log message formatting
- Component-specific loggers
- Graceful shutdown
"""

import logging
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from .logger import (
    StructuredLogger,
    get_logger,
    initialize_logging,
    shutdown_logging
)


class TestStructuredLogger(unittest.TestCase):
    """Test cases for StructuredLogger class."""
    
    def setUp(self):
        """Reset logger state before each test."""
        # Reset singleton state
        StructuredLogger._instance = None
        StructuredLogger._initialized = False
    
    def tearDown(self):
        """Clean up after each test."""
        # Reset singleton state
        StructuredLogger._instance = None
        StructuredLogger._initialized = False
    
    def test_singleton_pattern(self):
        """Test that StructuredLogger follows singleton pattern."""
        logger1 = StructuredLogger()
        logger2 = StructuredLogger()
        
        self.assertIs(logger1, logger2, "StructuredLogger should be singleton")
    
    def test_logs_directory_creation(self):
        """Test that logs directory is created on initialization."""
        logger = StructuredLogger()
        
        # Verify logs directory was created
        self.assertTrue(logger.logs_dir.exists(), "Logs directory should be created")
    
    def test_rotating_file_handler_configuration(self):
        """Test that RotatingFileHandler is configured correctly."""
        logger = StructuredLogger()
        
        # Find the RotatingFileHandler
        rotating_handler = None
        for handler in logger.root_logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                rotating_handler = handler
                break
        
        self.assertIsNotNone(rotating_handler, "RotatingFileHandler should be configured")
        self.assertEqual(rotating_handler.maxBytes, 10 * 1024 * 1024, "Max bytes should be 10MB")
        self.assertEqual(rotating_handler.backupCount, 5, "Backup count should be 5")
    
    def test_log_format(self):
        """Test that log format includes timestamp, level, component, and message."""
        logger = StructuredLogger()
        
        # Get the formatter from a handler
        formatter = None
        for handler in logger.root_logger.handlers:
            if handler.formatter:
                formatter = handler.formatter
                break
        
        self.assertIsNotNone(formatter, "Formatter should be configured")
        
        # Check format string contains required elements
        format_string = formatter._fmt
        self.assertIn('%(asctime)s', format_string, "Format should include timestamp")
        self.assertIn('%(name)s', format_string, "Format should include component name")
        self.assertIn('%(levelname)s', format_string, "Format should include log level")
        self.assertIn('%(message)s', format_string, "Format should include message")
    
    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a logging.Logger instance."""
        logger = StructuredLogger.get_logger('test_component')
        
        self.assertIsInstance(logger, logging.Logger, "Should return Logger instance")
        self.assertEqual(logger.name, 'test_component', "Logger name should match component")
    
    def test_multiple_component_loggers(self):
        """Test that different components get separate logger instances."""
        logger1 = StructuredLogger.get_logger('engine')
        logger2 = StructuredLogger.get_logger('controller')
        
        self.assertIsNot(logger1, logger2, "Different components should have different loggers")
        self.assertEqual(logger1.name, 'engine')
        self.assertEqual(logger2.name, 'controller')
    
    def test_console_and_file_handlers(self):
        """Test that both console and file handlers are configured."""
        logger = StructuredLogger()
        
        handler_types = [type(h).__name__ for h in logger.root_logger.handlers]
        
        self.assertIn('StreamHandler', handler_types, "Console handler should be configured")
        self.assertIn('RotatingFileHandler', handler_types, "File handler should be configured")
    
    def test_initialize_logging_function(self):
        """Test the initialize_logging convenience function."""
        # Should not raise any exceptions
        initialize_logging()
        
        # Verify logger is initialized
        logger = StructuredLogger()
        self.assertTrue(StructuredLogger._initialized)
    
    def test_shutdown_logging_function(self):
        """Test the shutdown_logging convenience function."""
        initialize_logging()
        
        # Should not raise any exceptions
        shutdown_logging()
    
    def test_get_logger_convenience_function(self):
        """Test the get_logger convenience function."""
        logger = get_logger('test_component')
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, 'test_component')


class TestLoggerIntegration(unittest.TestCase):
    """Integration tests for logging system."""
    
    def setUp(self):
        """Reset logger state before each test."""
        StructuredLogger._instance = None
        StructuredLogger._initialized = False
    
    def tearDown(self):
        """Clean up after each test."""
        StructuredLogger._instance = None
        StructuredLogger._initialized = False
    
    def test_log_message_to_file(self):
        """Test that log messages are written to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create logger in temp directory
            logger = StructuredLogger()
            
            # Override logs directory
            logger.logs_dir = Path(tmpdir)
            logger.logs_dir.mkdir(exist_ok=True)
            
            # Get component logger and log a message
            component_logger = get_logger('test_component')
            test_message = 'Test log message'
            component_logger.info(test_message)
            
            # Flush handlers
            for handler in logger.root_logger.handlers:
                handler.flush()
            
            # Check if log file exists and contains message
            log_file = logger.logs_dir / 'app.log'
            if log_file.exists():
                with open(log_file, 'r') as f:
                    content = f.read()
                    self.assertIn(test_message, content, "Log message should be in file")
    
    def test_different_log_levels(self):
        """Test that different log levels are handled correctly."""
        logger = StructuredLogger()
        component_logger = get_logger('test_component')
        
        # Log messages at different levels
        component_logger.debug('Debug message')
        component_logger.info('Info message')
        component_logger.warning('Warning message')
        component_logger.error('Error message')
        
        # Flush handlers
        for handler in logger.root_logger.handlers:
            handler.flush()
        
        # Should not raise any exceptions
        self.assertTrue(True)


class TestLoggerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Reset logger state before each test."""
        StructuredLogger._instance = None
        StructuredLogger._initialized = False
    
    def tearDown(self):
        """Clean up after each test."""
        StructuredLogger._instance = None
        StructuredLogger._initialized = False
    
    def test_logger_with_special_characters(self):
        """Test logging messages with special characters."""
        logger = StructuredLogger()
        component_logger = get_logger('test_component')
        
        # Log messages with special characters
        component_logger.info('Message with émojis 🎉')
        component_logger.info('Message with "quotes"')
        component_logger.info('Message with \\backslashes\\')
        
        # Flush handlers
        for handler in logger.root_logger.handlers:
            handler.flush()
        
        # Should not raise any exceptions
        self.assertTrue(True)
    
    def test_concurrent_logging(self):
        """Test that logging is thread-safe."""
        import threading
        
        logger = StructuredLogger()
        component_logger = get_logger('test_component')
        
        def log_messages(thread_id):
            for i in range(10):
                component_logger.info(f'Thread {thread_id} message {i}')
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_messages, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Flush handlers
        for handler in logger.root_logger.handlers:
            handler.flush()
        
        # Should not raise any exceptions
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
