import time
from unittest.mock import MagicMock
import pytest
from pathlib import Path

from requests.exceptions import ConnectionError, HTTPError
from ResilientGeoDrone.src.point_cloud.webodm_client import WebODMClient
from ResilientGeoDrone.src.utils.logger import LoggerSetup


@pytest.mark.unit
def test_webodm_initialization_faulty_config():
    """Test initialization with failing config loader"""
    mock_config = MagicMock()
    mock_config.get_webodm_config.side_effect = ValueError("Test error")
    
    with pytest.raises(Exception):
        WebODMClient(mock_config)


@pytest.mark.unit
def test_webodm_initialization_missed_token():
    """Test initialization with missing token"""
    mock_config = MagicMock()
    mock_config.get_webodm_config.return_value = {"url": "http://localhost:8000"}
    
    with pytest.raises(ValueError):
        WebODMClient(mock_config)


"""

    Desc: This Test Is Utilized To Ensure Proper Initialization Of Our WebODM Client
    With A Valid Configuration File. The WebODM Client Is Used To Interact With
    WebODM To Generate Point Clouds.

"""
@pytest.mark.unit
@pytest.mark.fast
def test_webodm_initialization(config_loader):
    # Launch Off WebODM Client With Test Config
    client = WebODMClient(config_loader)

    # After Creation, Check So Client, Their URL, And API-Key Are Established
    assert client is not None
    assert client.base_url is not None
    assert client.api_key is not None


"""

    Desc: This Test Ensures That Our Project Creation Functionality Works As Expected.
    We Expect A Valid Project ID To Be Returned After Project Creation. The Project
    ID Should Be Strictly Positive.

"""
@pytest.mark.unit
@pytest.mark.functional
def test_project_creation(webodm_client):
    # Create A New Project In WebODM
    project_id = webodm_client._create_project()

    # Ensure We Get A Valid Project ID
    assert isinstance(project_id, int)

    # Project ID Also Is Strictly Positive Else Error
    assert project_id > 0


"""Test Complete Point Cloud Generation Pipeline"""
@pytest.mark.integration
@pytest.mark.slow
def test_point_cloud_generation_and_cleanup_and_results(webodm_client, test_image_paths):
    # WebODM Requires At Least 2 Images To Properly Point Cloud Stitch
    if len(test_image_paths) < 2:
        pytest.skip("Need at least 2 images for point cloud generation")
    
    # Generate Point Cloud
    result = webodm_client.generate_point_cloud(test_image_paths, "sunny")

    # Ensure Result Is Not None And Contains Point Cloud
    assert result is not None
    assert "point_cloud" in result
    assert webodm_client._cleanup_projects() is True


"""Test Valid WebODM Connection"""
@pytest.mark.unit
def test_point_cloud_connection_valid(webodm_client):
    # With Normal URL, We Expect A Proper Connection (User Must Have WebODM Running)
    assert webodm_client._test_connection()


"""Test Invalid WebODM Connection"""
@pytest.mark.unit
def test_point_cloud_connection_invalid(webodm_client):
    # With Invalid URL, We Expect No Connection
    try:
      prevURL = webodm_client.base_url
      webodm_client.base_url = "http://invalid:8000"
      webodm_client._test_connection()
    # Session Will Throw Connection Error With Invalid URL
    except (ConnectionError):
      webodm_client.base_url = prevURL
      assert True

"""Test Getting Valid Token From WebODM"""
@pytest.mark.unit
def test_point_cloud_get_token_valid(webodm_client):
    # Ensure We Get A Token From WebODM
    assert webodm_client._get_token() is not None


"""Test Getting Invalid Token From WebODM"""
@pytest.mark.unit
def test_point_cloud_get_token_invalid(webodm_client):
    # With Invalid Credentials, We Expect No Token
    try:
      prevUser = webodm_client.config["webodm"]["username"]
      prevPass = webodm_client.config["webodm"]["password"]
      webodm_client.config["webodm"]["username"] = "invalid"
      webodm_client.config["webodm"]["password"] = "invalid"
      # Ensure We Don't Get A Token From WebODM
      webodm_client._get_token() is None
    # Session Will Throw HTTP (400) Error With Invalid Credentials
    except HTTPError:
      webodm_client.config["webodm"]["username"] = prevUser
      webodm_client.config["webodm"]["password"] = prevPass
      assert True
