import os
import tempfile
import pytest
from ResilientGeoDrone.src.utils.config_loader import ConfigLoader
from pathlib import Path
from ResilientGeoDrone.src.utils.logger import LoggerSetup



"""

    Desc: This Test Is utilized To Ensure Proper Loading Of Our Main WebODM Configuration
    Section of Our JSON Configuration File.

"""
@pytest.mark.unit
@pytest.mark.fast
def test_config_loading_success():
    """Test basic config loading"""
    loader = ConfigLoader(str(Path(__file__).parent.parent / "data" / "configs" / "test_config.yaml"))
    config = loader.get_point_cloud_config()
    assert config is not None
    assert "webodm" in config


"""

    Desc: This Test Is Utilized To Ensure Proper Handling Of Invalid File Paths
    When Loading Our Configuration File.

"""
@pytest.mark.unit
@pytest.mark.fast
def test_config_loading_invalid_path():
    """Test handling of non-existent file path"""
    with pytest.raises(FileNotFoundError):
        ConfigLoader("invalid/path.yaml")


"""

    Desc: This Test Is Utilized To Ensure Proper Handling Of Directory Paths
    When Loading Our Configuration File.

"""
@pytest.mark.unit
@pytest.mark.fast
def test_config_loading_directory_path():
    """Test handling when path is a directory"""
    with pytest.raises(FileNotFoundError):
        ConfigLoader("config/")


"""

    Desc: This Test Is Utilized To Ensure Proper Loading Of Our Preprocessing Configuration

"""
@pytest.mark.unit
@pytest.mark.fast
def test_get_preprocessing_config():
    """Test retrieving preprocessing configuration"""
    loader = ConfigLoader(str(Path(__file__).parent.parent.parent / "config" / "default_config.yaml"))
    config = loader.get_preprocessing_config()
    assert config is not None
    # Check for specific preprocessing keys that should exist in your test config
    assert "max_workers" in config  # Adjust based on your config structure


"""

    Desc: This Test Is Utilized To Ensure Proper Loading Of Our Geospatial Configuration

"""
@pytest.mark.unit
@pytest.mark.fast
def test_get_geospatial_config():
    """Test retrieving geospatial configuration"""
    loader = ConfigLoader(str(Path(__file__).parent.parent.parent / "config" / "default_config.yaml"))
    config = loader.get_geospatial_config()
    assert config is not None
    # Check for specific geospatial keys that should exist in your test config
    assert "analysis" in config  # Adjust based on your config structure


"""

    Desc: This Test Is Utilized To Ensure Proper Handling Of Invalid Environments

"""
@pytest.mark.unit
@pytest.mark.fast
def test_invalid_environment():
    """Test handling of invalid environment"""
    loader = ConfigLoader(str(Path(__file__).parent.parent.parent / "config" / "default_config.yaml"))
    with pytest.raises(ValueError, match="Invalid Environment: nonexistent"):
        loader.get_environment_params("nonexistent")


"""

    Desc: This Test Is Utilized To Ensure Proper Handling Of File Deletion Between Init And Load

"""
@pytest.mark.unit
@pytest.mark.fast
def test_file_deleted_during_runtime():
    """Test handling of file deletion between init and load"""
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp:
        temp.write(b"""
preprocessing:
  quality_threshold: 0.8
point_cloud:
  webodm:
    environments:
      sunny: {}
geospatial:
  crs: EPSG:4326
""")
        temp_path = temp.name
    
    try:
        # Initialize ConfigLoader with the temp file
        loader = ConfigLoader(temp_path)
        # Delete the file
        os.remove(temp_path)
        # Attempt to load, should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            loader.load()
    finally:
        # Clean up if test fails
        if os.path.exists(temp_path):
            os.remove(temp_path)


"""

    Desc: This Test Is Utilized To Ensure Proper Validation Of Configuration Structure

"""
@pytest.mark.unit
@pytest.mark.fast
def test_missing_required_section():
    """Test handling of missing required section"""
    # Create a temporary config file with missing sections
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp:
        temp.write(b"""
preprocessing:
  quality_threshold: 0.8
# Missing point_cloud and geospatial sections
""")
        temp_path = temp.name
    
    try:
        # Initialize ConfigLoader
        loader = ConfigLoader(temp_path)
        # Attempt to load, should raise ValueError
        with pytest.raises(ValueError, match="Missing Required Configuration Section"):
            loader.load()
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


"""

    Desc: This Test Is Utilized To Ensure Proper Handling Of Invalid YAML

"""
@pytest.mark.unit
@pytest.mark.fast
def test_invalid_yaml():
    """Test handling of invalid YAML"""
    # Create a temporary file with invalid YAML
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp:
        temp.write(b"""
preprocessing: {
  quality_threshold: 0.8,
  This is invalid YAML
""")
        temp_path = temp.name
    
    try:
        # Initialize ConfigLoader
        loader = ConfigLoader(temp_path)
        # Attempt to load, should raise a YAML parsing error
        with pytest.raises(Exception):
            loader.load()
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

"""

    Desc: This Test Is Utilized To Ensure Valid Environment Parameters Are Retrieved

"""
@pytest.mark.unit
@pytest.mark.fast
def test_get_environment_params():
    """Test retrieving valid environment parameters"""
    loader = ConfigLoader(str(Path(__file__).parent.parent.parent / "config" / "default_config.yaml"))
    # Assuming "sunny" is a valid environment in your test config
    params = loader.get_environment_params("sunny")
    assert params is not None
    # Check for specific environment parameter keys
    assert isinstance(params, dict)


"""

    Desc: This Test Is Utilized To Ensure Proper Loading Of Our Point Cloud Configuration

"""
@pytest.mark.unit
@pytest.mark.fast
def test_get_point_cloud_config():
    loader = ConfigLoader(str(Path(__file__).parent.parent.parent / "config" / "default_config.yaml"))
    config = loader.get_point_cloud_config()
    assert config is not None
    assert "webodm" in config


"""

    Desc: This Test Is Utilized To Ensure Proper Loading Of Our Environments
    Section Of Our WebODM Configuration File.

"""
@pytest.mark.unit
@pytest.mark.smoke
def test_environment_config():
    loader = ConfigLoader(str(Path(__file__).parent.parent.parent / "config" / "default_config.yaml"))
    config = loader.get_point_cloud_config()
    assert "environments" in config["webodm"]


"""

    Desc: This Test Is Utilized To Ensure We Properly Handle Invalid
    Configuration Files

"""
@pytest.mark.unit
@pytest.mark.regression
def test_invalid_config_path():
    """Test handling of invalid config path"""
    with pytest.raises(FileNotFoundError):
        ConfigLoader("invalid/path.yaml")