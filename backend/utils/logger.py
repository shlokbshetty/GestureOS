"""
Structured logging system with file rotation.

This module provides a centralized logging configuration with:
- Rotating file handler (10MB max, 5 files kept)
- Structured log format with timestamps, severity levels, and component names
- Console output for development
- Thread-safe logging operations
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


class StructuredLogger:
    """
    Centralized logging system with file rotation and structured format.
    
    Features:
    - Rotating file handler (10MB max, 5 backup files)
    - Structured log format: [TIMESTAMP] [LEVEL] [COMPONENT] message
    - Console output for development
    - Thread-safe operations
    """
    
    # Log format with timestamp, level, component, and message
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # File rotation settings
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5  # Keep 5 rotated files
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure single logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger with file rotation and console output."""
        if StructuredLogger._initialized:
            return
        
        # Create logs directory if it doesn't exist
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize root logger
        self.root_logger = logging.getLogger()
        self.root_logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self.root_logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            self.LOG_FORMAT,
            datefmt=self.DATE_FORMAT
        )
        
        # File handler with rotation
        log_file = self.logs_dir / 'app.log'
        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file),
            maxBytes=self.MAX_BYTES,
            backupCount=self.BACKUP_COUNT
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.root_logger.addHandler(file_handler)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.root_logger.addHandler(console_handler)
        
        StructuredLogger._initialized = True
        
        # Log initialization
        self.root_logger.info('Logging system initialized')
        self.root_logger.info(f'Log file: {log_file}')
        self.root_logger.info(f'Max file size: {self.MAX_BYTES / (1024*1024):.1f}MB')
        self.root_logger.info(f'Backup files kept: {self.BACKUP_COUNT}')
    
    @staticmethod
    def get_logger(component_name: str) -> logging.Logger:
        """
        Get a logger instance for a specific component.
        
        Args:
            component_name: Name of the component (e.g., 'engine', 'controller')
        
        Returns:
            Logger instance with component name
        """
        # Ensure singleton is initialized
        StructuredLogger()
        return logging.getLogger(component_name)
    
    @staticmethod
    def initialize() -> None:
        """
        Initialize the logging system on application startup.
        
        This should be called once at application startup to ensure
        the logging system is properly configured.
        """
        logger = StructuredLogger()
        logger.root_logger.info('=' * 60)
        logger.root_logger.info('Application startup')
        logger.root_logger.info('=' * 60)
    
    @staticmethod
    def shutdown() -> None:
        """
        Shutdown the logging system gracefully.
        
        This should be called during application shutdown to ensure
        all log messages are flushed to disk.
        """
        logger = StructuredLogger()
        logger.root_logger.info('=' * 60)
        logger.root_logger.info('Application shutdown')
        logger.root_logger.info('=' * 60)
        
        # Flush all handlers
        for handler in logger.root_logger.handlers:
            handler.flush()
            handler.close()
        
        logging.shutdown()


def get_logger(component_name: str) -> logging.Logger:
    """
    Convenience function to get a logger for a component.
    
    Args:
        component_name: Name of the component (e.g., 'engine', 'controller')
    
    Returns:
        Logger instance with component name
    
    Example:
        >>> logger = get_logger('gesture_engine')
        >>> logger.info('Gesture detected: app_switch')
    """
    return StructuredLogger.get_logger(component_name)


def initialize_logging() -> None:
    """
    Initialize the logging system on application startup.
    
    This should be called once at application startup.
    
    Example:
        >>> initialize_logging()
    """
    StructuredLogger.initialize()


def shutdown_logging() -> None:
    """
    Shutdown the logging system gracefully.
    
    This should be called during application shutdown.
    
    Example:
        >>> shutdown_logging()
    """
    StructuredLogger.shutdown()
