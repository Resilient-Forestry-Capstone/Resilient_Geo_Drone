import os
import pytest
import logging
from pathlib import Path
from unittest.mock import patch, mock_open
from ResilientGeoDrone.src.utils.logger import LoggerSetup


@pytest.mark.unit
@pytest.mark.fast
def test_logger_init():
  # Ensure Logger Is Properly Initialized With Name And Default Level
  logger = LoggerSetup("test")
  assert logger is not None
  assert logger.logger is not None
  assert logger.logger.level == logging.INFO
  assert logger.logger.name == "test" 


@pytest.mark.unit
def test_logger_info():
  with patch("logging.Logger.info") as mock_info:
    logger = LoggerSetup("test")
    logger.logger.info("Test Message")
    mock_info.assert_called_once_with("Test Message")


@pytest.mark.unit
def test_logger_error():
  with patch("logging.Logger.error") as mock_error:
    logger = LoggerSetup("test")
    logger.logger.error("Test Message")
    mock_error.assert_called_once_with("Test Message")


@pytest.mark.unit
def test_logger_warning():
  with patch("logging.Logger.warning") as mock_warning:
    logger = LoggerSetup("test")
    logger.logger.warning("Test Message")
    mock_warning.assert_called_once_with("Test Message")


@pytest.mark.unit
def test_logger_debug():
  with patch("logging.Logger.debug") as mock_debug:
    logger = LoggerSetup("test")
    logger.logger.debug("Test Message")
    mock_debug.assert_called_once_with("Test Message")


@pytest.mark.unit
def test_logger_file_handler():
  log_path = Path(__file__).parent.parent / "logs"

  with patch('pathlib.Path.mkdir'), patch('logging.FileHandler') as mock_file_handler, patch('logging.Logger.addHandler') as mock_add_handler:
    logger = LoggerSetup("test_module", log_dir=log_path)
    mock_file_handler.assert_called_once()
    mock_add_handler.assert_called()


@pytest.mark.unit
def test_logger_exception_handling():
  with pytest.raises(Exception):
    logger = LoggerSetup(name="test_module_2", log_dir="test.log")
  