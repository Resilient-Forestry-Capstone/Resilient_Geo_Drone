"""Utility Package for ResilientGeoDrone Pipeline

This package provides core functionality for:
- Configuration management
- File system operations
- Logging services
- Error handling

Classes:
    ConfigLoader: YAML configuration management
    FileHandler: File system operations
    LoggerSetup: Custom logging configuration
"""


from .config_loader import ConfigLoader
from .file_handler import FileHandler
from .logger import LoggerSetup


# Package metadata
__version__ = '0.1.0'
__author__ = 'ResilientGeoDrone Team'
__email__ = 'team@resilientgeodrone.com'
__status__ = 'Development'

# Define public interface
__all__ = [
    'ConfigLoader',
    'FileHandler',
    'LoggerSetup'
]

# Package level constants
DEFAULT_CONFIG_PATH = 'config/config.yaml'
DEFAULT_LOG_DIR = 'logs'