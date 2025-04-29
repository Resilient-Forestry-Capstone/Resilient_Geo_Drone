"""Point Cloud Generation Package

Components:
- WebODM interface for environment-specific processing
- Point cloud analysis and metrics
- Surface model processing (DSM/DTM)
- Environment configuration management

Classes:
    WebODMClient: Interface to WebODM API
    CloudProcessor: Process and analyze WebODM outputs
    EnvironmentConfig: Environment-specific parameters
"""

from .webodm_client import WebODMClient


# Package metadata
__version__ = '0.1.0'
__author__ = 'ResilientGeoDrone Team'
__email__ = 'team@resilientgeodrone.com'
__status__ = 'Development'

# Define public interface
__all__ = [
    'WebODMClient'
]

# Package level constants
DEFAULT_CONFIG_PATH = 'config/config.yaml'
DEFAULT_OUTPUT_DIR = 'data/output'

# Environment types
SUPPORTED_ENVIRONMENTS = ['sunny', 'rainy', 'foggy']