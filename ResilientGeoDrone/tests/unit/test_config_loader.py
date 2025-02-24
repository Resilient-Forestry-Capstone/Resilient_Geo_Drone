import pytest
from ResilientGeoDrone.src.utils.config_loader import ConfigLoader
from pathlib import Path



"""

    Desc: This Test Is utilized To Ensure Proper Loading Of Our Main WebODM Configuration
    Section of Our JSON Configuration File.

"""
@pytest.mark.unit
@pytest.mark.fast
def test_config_loading():
    """Test basic config loading"""
    loader = ConfigLoader(str(Path(__file__).parent.parent / "data" / "configs" / "test_config.yaml"))
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
    loader = ConfigLoader(str(Path(__file__).parent.parent / "data" / "configs" / "test_config.yaml"))
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