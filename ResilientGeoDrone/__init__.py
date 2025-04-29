"""ResilientGeoDrone - Drone Image Processing Pipeline

A three-stage pipeline for processing aerial drone imagery into analyzed point clouds.
"""

from . import src
from .src.utils import ConfigLoader, FileHandler, LoggerSetup
from .src.point_cloud import WebODMClient
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
DEFAULT_OUTPUT_DIR = 'data/output'