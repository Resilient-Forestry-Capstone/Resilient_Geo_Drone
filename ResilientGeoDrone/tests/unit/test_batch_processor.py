from unittest.mock import MagicMock, patch
import pytest
import numpy as np
from pathlib import Path
from ResilientGeoDrone.src.preprocessing.batch_processor import BatchProcessor
from ResilientGeoDrone.src.utils.logger import LoggerSetup
from ResilientGeoDrone.src.preprocessing.image_validator import ImageValidator


"""
    Desc: Test Successful Initialization Of ImageValidator
"""
@pytest.mark.unit
def test_validator_init(config_loader):
    """Test basic initialization succeeds"""
    validator = ImageValidator(config_loader)
    assert validator is not None
    assert validator.config is not None
    assert validator.metrics is not None

"""
    Desc: Test Failed Initialization With Bad Config
"""
@pytest.mark.unit
def test_validator_init_failure():
    """Test initialization with failing config loader"""
    mock_config = MagicMock()
    mock_config.get_preprocessing_config.side_effect = ValueError("Test error")
    
    with pytest.raises(Exception):
        ImageValidator(mock_config)

"""
    Desc: Test Successful Image Validation
"""
@pytest.mark.unit
def test_validate_image_success(config_loader, test_image_paths):
    """Test Validating A Good Image"""
    validator = ImageValidator(config_loader)
    
    # Use patch to ensure all quality checks return True
    with patch.object(validator.metrics, 'check_resolution', return_value=True), \
         patch.object(validator.metrics, 'check_blur', return_value=True), \
         patch.object(validator.metrics, 'check_brightness', return_value=True), \
         patch.object(validator.metrics, 'check_contrast', return_value=True):
        
        result = validator.validate_image(test_image_paths[0])
        assert result is True

"""
    Desc: Test Failed Image Validation - Quality Check Failure
"""
@pytest.mark.unit
def test_validate_image_quality_failure(config_loader, test_image_paths):
    """Test Vaidating An Image That Fails Quality Checks"""
    validator = ImageValidator(config_loader)
    
    # Make One Quality Check Fail
    with patch.object(validator.metrics, 'check_blur', return_value=False):
        result = validator.validate_image(test_image_paths[0])
        assert result is False

"""
    Desc: Test Failed Image Loading
"""
@pytest.mark.unit
def test_validate_nonexistent_image(config_loader):
    """Test validating a non-existent image"""
    validator = ImageValidator(config_loader)
    fake_path = Path("/nonexistent/image.jpg")
    
    result = validator.validate_image(fake_path)
    assert result is False

"""
    Desc: Test Handling Corrupt Image
"""
@pytest.mark.unit
def test_validate_corrupt_image(config_loader, tmp_path):
    """Test validating a corrupt image file"""
    validator = ImageValidator(config_loader)
    corrupt_path = tmp_path / "corrupt.jpg"
    corrupt_path.write_bytes(b"Not an image file")
    
    result = validator.validate_image(corrupt_path)
    assert result is False

"""
    Desc: Test Exception During Validation
"""
@pytest.mark.unit
def test_validate_image_exception(config_loader, test_image_paths):
    """Test exception handling during validation"""
    validator = ImageValidator(config_loader)
    
    # Force An Exception During Quality Check
    with patch.object(validator.metrics, 'check_brightness', side_effect=Exception("Test error")):
        result = validator.validate_image(test_image_paths[0])
        assert result is False


"""

    Desc: This Test Is Utilized To Test The Batch Processors Processing Speed,
    Ensuring That The Batch Processor Can Process A Batch Of Images Within A
    Reasonable Timeframe.

"""
@pytest.mark.unit
@pytest.mark.performance
def test_batch_processing_speed(batch_processor, test_image_paths):
    import time
    start_time = time.time()
    batch_processor.process_batch(test_image_paths)
    duration = time.time() - start_time
    assert duration < 30.0  # Should process within 30 seconds


"""

    Desc: This Test Is Utilized To Test The Batch Processors Image Validation
    Functionality, Ensuring That The Batch Processor Can Validate Images
    Valid Properly.

"""
@pytest.mark.unit
@pytest.mark.functional
def test_image_validation(batch_processor, test_image_paths):
    results = batch_processor.process_batch(test_image_paths)
    assert all(result for result in results['valid'])


"""

    Desc: This Test Is Utilized To Test The Batch Processors Image Validation
    Functionality, Ensuring That The Batch Processor Can Validate Images
    That Are Corrupt Properly.

"""
@pytest.mark.unit
@pytest.mark.regression
def test_corrupt_image_handling(batch_processor, tmp_path):
    corrupt_path = tmp_path / "corrupt.jpg"
    corrupt_path.write_bytes(b"Not an image")
    with pytest.raises(Exception):
        batch_processor.validate_images([corrupt_path])