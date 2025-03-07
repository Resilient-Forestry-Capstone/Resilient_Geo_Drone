<<<<<<< HEAD
"""ResilientGeoDrone - Drone Image Processing Pipeline

A three-stage pipeline for processing aerial drone imagery into analyzed point clouds.
"""

from . import src
from .src.utils import ConfigLoader, FileHandler, LoggerSetup
from .src.point_cloud import WebODMClient, CloudProcessor
from .src.preprocessing import BatchProcessor
from .src.front_end import PipelineWorker, MainClientWindow, DragDropWidget, ProgressWidget, PipelineWorker




# Package metadata
__version__ = '0.1.0'
__author__ = 'ResilientGeoDrone Team'
__email__ = 'team@resilientgeodrone.com'
__status__ = 'Development'

# Define public interface
__all__ = [
    'ConfigLoader',
    'FileHandler',
    'LoggerSetup',
    'WebODMClient',
    'CloudProcessor',
    'BatchProcessor',
    'PipelineWorker',
    'MainClientWindow',
    'DragDropWidget',
    'ProgressWidget'
]

# Package level constants
DEFAULT_CONFIG_PATH = 'config/config.yaml'
=======
"""ResilientGeoDrone - Drone Image Processing Pipeline

A three-stage pipeline for processing aerial drone imagery into analyzed point clouds.
"""

from . import src
from .src.utils import ConfigLoader, FileHandler, LoggerSetup
from .src.point_cloud import WebODMClient, CloudProcessor
from .src.preprocessing import BatchProcessor


# Package metadata
__version__ = '0.1.0'
__author__ = 'ResilientGeoDrone Team'
__email__ = 'team@resilientgeodrone.com'
__status__ = 'Development'

# Define public interface
__all__ = [
    'ConfigLoader',
    'FileHandler',
    'LoggerSetup',
    'WebODMClient',
    'CloudProcessor',
    'BatchProcessor'
]

# Package level constants
DEFAULT_CONFIG_PATH = 'config/config.yaml'
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
DEFAULT_OUTPUT_DIR = 'data/output'