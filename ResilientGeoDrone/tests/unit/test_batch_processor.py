import pytest
import numpy as np
from pathlib import Path
from ResilientGeoDrone.src.preprocessing.batch_processor import BatchProcessor


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