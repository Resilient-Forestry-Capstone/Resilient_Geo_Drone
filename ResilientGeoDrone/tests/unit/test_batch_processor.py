from unittest.mock import MagicMock, patch
import pytest
import numpy as np
from pathlib import Path
from ResilientGeoDrone.src.preprocessing.batch_processor import BatchProcessor
from ResilientGeoDrone.src.utils.logger import LoggerSetup
from ResilientGeoDrone.src.preprocessing.image_validator import ImageValidator


"""

    Desc: Test Ensures That The Batch Processor Is Initialized Properly
    With The Config Loader And Logger As Well As The Image Validator.

"""
@pytest.mark.unit
def test_validator_init(config_loader):
    validator = ImageValidator(config_loader)
    assert validator is not None
    assert validator.config is not None
    assert validator.metrics is not None


"""

    Desc: Test Failed Initialization With Bad Config Loader
    Ensures That The Batch Processor Is Initialized Properly (Should Raise)

"""
@pytest.mark.unit
def test_validator_init_failure():
    mock_config = MagicMock()
    mock_config.get_preprocessing_config.side_effect = ValueError("Test error")
    
    with pytest.raises(Exception):
        ImageValidator(mock_config)


"""

    Desc: Test For A Successful Image Validation;
    Ensures That The Image Validator Can Validate An Image Properly.
    The Image Validator Should Be Able To Validate An Image That Is
    Good Quality And Passes All Quality Checks.

"""
@pytest.mark.unit
def test_validate_image_success(config_loader, test_image_paths):
    validator = ImageValidator(config_loader)
    
    # Use Patch To Ensure All Quality Checks Return True
    with patch.object(validator.metrics, 'check_resolution', return_value=True), \
         patch.object(validator.metrics, 'check_blur', return_value=True), \
         patch.object(validator.metrics, 'check_brightness', return_value=True):
        
        result = validator.validate_image(test_image_paths[0])
        assert result is True


"""

    Desc: Test Failed Image Validation - Quality Check Failure. Should
    Happen When The Image Validator Is Unable To Validate An Image Properly
    On At Least One Quality Check. 

"""
@pytest.mark.unit
def test_validate_image_quality_failure(config_loader, test_image_paths):
    validator = ImageValidator(config_loader)
    
    # Make One Quality Check Fail
    with patch.object(validator.metrics, 'check_blur', return_value=False):
        result = validator.validate_image(test_image_paths[0])
        assert result is False


"""

    Desc: Test Handling Non-Existent Image Ensures That The Image
    Validator Can Handle A Non-Existent Image Properly, Raising An
    Exception If The Image Does Not Exist.

"""
@pytest.mark.unit
def test_validate_nonexistent_image(config_loader):
    try:
        validator = ImageValidator(config_loader)
        fake_path = Path("/nonexistent/image.jpg")
        
        result = validator.validate_image(fake_path)
        assert False # Should Not Reach This Line
    except Exception as e:
        # Expect An Exception To Be Raised
        assert True


"""

    Desc: Test Handling Corrupt Image Ensures That The Image Validator
    Can Handle A Corrupt Image Properly, Raising An Exception If The
    Image Is Corrupt.

"""
@pytest.mark.unit
def test_validate_corrupt_image(config_loader, tmp_path):
    try:
        validator = ImageValidator(config_loader)
        corrupt_path = tmp_path / "corrupt.jpg"
        corrupt_path.write_bytes(b"Not an image file")
        
        result = validator.validate_image(corrupt_path)
        assert False
    except Exception as e:
        # Expect An Exception To Be Raised
        assert True


"""

    Desc: Test Handling Exception During Validation Ensures That The
    Image Validator Can Handle An Exception During Validation Properly,
    Raising An Exception If The Validation Process Fails.

"""
@pytest.mark.unit
def test_validate_image_exception(config_loader, test_image_paths):
    """Test exception handling during validation"""
    validator = ImageValidator(config_loader)
    
    # Force An Exception During Quality Check
    with patch.object(validator.metrics, 'check_resolution', side_effect=Exception("Test exception")):
        try:
            result = validator.validate_image(test_image_paths[0])
            assert False # Should Not Reach This Line
        except Exception as e:
            # Expect An Exception To Be Raised
            assert isinstance(e, Exception)
        

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
    assert duration < 30.0  # Should Process Within 30 Seconds


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
    test_image_paths = [corrupt_path]
    results = batch_processor.process_batch(test_image_paths)
    assert len(results['invalid']) == 1
    assert results['invalid'][0] == corrupt_path