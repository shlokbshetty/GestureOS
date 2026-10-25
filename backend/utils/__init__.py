"""
Utility modules for the gesture control backend.

Includes:
- logger: Structured logging with file rotation
- config: Configuration management
- debounce: Cooldown and debounce system
- smoothing: Temporal smoothing algorithm
"""

from backend.utils.logger import (
    StructuredLogger,
    get_logger,
    initialize_logging,
    shutdown_logging,
)
from backend.utils.config import ConfigManager, ConfigurationError
from backend.utils.debounce import Debouncer, CooldownTracker
from backend.utils.smoothing import TemporalSmoother

__all__ = [
    'StructuredLogger',
    'get_logger',
    'initialize_logging',
    'shutdown_logging',
    'ConfigManager',
    'ConfigurationError',
    'Debouncer',
    'CooldownTracker',
    'TemporalSmoother'
]
