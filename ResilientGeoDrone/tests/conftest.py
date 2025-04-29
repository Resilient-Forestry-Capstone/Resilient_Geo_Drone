from pathlib import Path
import pytest
import sys

from ResilientGeoDrone.src.utils.logger import LoggerSetup
from ResilientGeoDrone.src.utils.config_loader import ConfigLoader
from ResilientGeoDrone.src.point_cloud.webodm_client import WebODMClient
from ResilientGeoDrone.src.preprocessing.batch_processor import BatchProcessor

@pytest.fixture
def config_loader():
    """Fixture for config loader with test configuration"""
    return ConfigLoader(str(Path(__file__).parent / "data" / "configs" / "test_config.yaml"))

@pytest.fixture
def test_image_paths():
    """Fixture for test image paths"""
    test_dir = (Path(__file__).parent / "data" / "images")
    return list(test_dir.glob("*.jpg"))

@pytest.fixture
def webodm_client(config_loader):
    """Fixture for WebODM client"""
    return WebODMClient(config_loader)

@pytest.fixture
def batch_processor(config_loader):
    """Fixture for batch processor"""
    return BatchProcessor(config_loader)

