import pytest
import os
from unittest.mock import MagicMock, patch
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QSignalSpy

from ResilientGeoDrone.src.front_end.pipeline_worker import PipelineWorker


"""
    Desc: Setup Test Fixtures For Pipeline Worker Tests
    These Fixtures Will Be Used To Create A Pipeline Worker Instance
"""
@pytest.fixture
def config_path():
    """Fixture for config path as string"""
    return str(Path(__file__).parent.parent / "data" / "configs" / "test_config.yaml")


@pytest.fixture
def test_image_paths():
    """Fixture for real test image paths from the test data directory"""
    test_dir = Path(__file__).parent.parent / "data" / "images"
    return [p for p in test_dir.glob("*.jpg") if p.is_file()]


@pytest.fixture
def test_output_dir():
    """Fixture for real test output directory"""
    output_dir = Path(__file__).parent.parent / "data" / "output"
    # Ensure directory exists
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def pipeline_worker(config_path, test_image_paths):
    """Fixture for creating a basic pipeline worker instance"""
    return PipelineWorker(config_path, test_image_paths)


"""
    Desc: Test Pipeline Worker Initialization
    This Test Verifies That The Pipeline Worker Is Initialized Correctly
"""
@pytest.mark.unit
def test_pipeline_worker_initialization(pipeline_worker, config_path, test_image_paths):
    """Test PipelineWorker initialization"""
    assert pipeline_worker.config_path == config_path
    assert pipeline_worker.image_paths == test_image_paths
    assert pipeline_worker.is_canceled is False


"""
    Desc: Test That Progress Signals Are Emitted During Initialization Phase
"""
@pytest.mark.unit
def test_pipeline_initialization_signals(qtbot, config_path, test_image_paths):
    """Test that signals are emitted during initialization"""
    # Create worker and spy on signals
    worker = PipelineWorker(config_path, test_image_paths)
    updated_spy = QSignalSpy(worker.progress_updated_status)
    
    worker.run()
    
    # Wait for signals
    qtbot.wait(500)
    
    # Verify initialization signals were emitted Check That We've Progressed Past Initialization
    init_signals = [s for s in updated_spy if s[1].startswith("Preprocessing")]
    assert len(init_signals) > 0


"""
    Desc: Test Pipeline Worker Cancel Method
    This Test Verifies That The Pipeline Worker Can Be Canceled
"""
@pytest.mark.unit
def test_pipeline_worker_cancel(qtbot, pipeline_worker):
    """Test PipelineWorker cancel method"""
    # Setup signal spy
    updated_spy = QSignalSpy(pipeline_worker.progress_updated_status)
    
    # Set logger (normally created in run())
    pipeline_worker.logger = MagicMock()
    
    # Call cancel method
    pipeline_worker.cancel()
    
    # Verify is_canceled flag is set
    assert pipeline_worker.is_canceled is True
    
    # Verify signal was emitted
    assert len(updated_spy) == 1
    assert updated_spy[0][0] == 100.0
    assert "Pipeline Canceled" in updated_spy[0][1]


"""
    Desc: Test Pipeline Worker With No Valid Images
    This Test Verifies That The Pipeline Worker Handles Invalid Images
"""
@pytest.mark.unit
def test_pipeline_run_no_valid_images(qtbot, config_path):
    """Test PipelineWorker run method when no valid images are found"""
    # Create worker with invalid image paths
    invalid_image_paths = [Path("nonexistent_image.jpg")]
    worker = PipelineWorker(config_path, invalid_image_paths)
    
    # Setup signal spies
    updated_spy = QSignalSpy(worker.progress_updated_status)
    completion_spy = QSignalSpy(worker.progress_completion_status)
    
    # Run the worker - this should detect invalid images
    worker.run()
    
    # Wait for signals
    qtbot.waitUntil(lambda: len(completion_spy) > 0, timeout=2000)
    
    # Verify failure signal was emitted
    failure_signals = [s for s in completion_spy if s[0] is False]
    assert len(failure_signals) > 0
    
    # Verify appropriate error message
    error_signals = [s for s in updated_spy if "Failed" in str(s[2]) and "Images" in str(s[2])]
    assert len(error_signals) > 0


"""
    Desc: Test Directory Creation Failure
    This Test Verifies Error Handling When Creating Directories
"""
@pytest.mark.unit
def test_pipeline_run_failed_directory_creation(qtbot, pipeline_worker):
    """Test PipelineWorker run method with directory creation failure"""
    # Spy on signals
    updated_spy = QSignalSpy(pipeline_worker.progress_updated_status)
    
    # Patch FileHandler to simulate directory creation failure
    with patch('ResilientGeoDrone.src.utils.file_handler.FileHandler.create_processing_directories',
              side_effect=Exception("Permission denied")):
        
        # Run the pipeline worker
        pipeline_worker.run()
        
        # Wait for signals
        qtbot.waitUntil(lambda: any("Failed Creating Directories" in str(s[2]) for s in updated_spy), timeout=2000)
    
    # Verify error signal was emitted
    error_signals = [s for s in updated_spy if "Failed" in str(s[2]) and "Directories" in str(s[2])]
    assert len(error_signals) > 0


"""
    Desc: Test WebODM Point Cloud Generation Failure
    This Test Verifies Error Handling In Point Cloud Generation
"""
@pytest.mark.unit
def test_pipeline_run_failed_point_cloud_generation(qtbot, pipeline_worker):
    """Test PipelineWorker run method with point cloud generation failure"""
    # Spy on signals
    updated_spy = QSignalSpy(pipeline_worker.progress_updated_status)
    
    # We need to patch directory creation to succeed but WebODM to fail
    with patch('ResilientGeoDrone.src.utils.file_handler.FileHandler.create_processing_directories',
              return_value={'input': Path('./test_dir'), 'processed': Path('./test_dir'),
                           'point_clouds': Path('./test_dir'), 'analysis': Path('./test_dir')}), \
         patch('ResilientGeoDrone.src.preprocessing.batch_processor.BatchProcessor.process_batch',
              return_value={'valid': [Path("test_image.jpg")]}), \
         patch('ResilientGeoDrone.src.point_cloud.webodm_client.WebODMClient.generate_point_cloud_signal',
              side_effect=Exception("WebODM connection error")):
        
        # Run the pipeline worker
        pipeline_worker.run()
        
        # Wait for signals
        qtbot.waitUntil(lambda: any("Failed Generating Point Clouds" in str(s[2]) for s in updated_spy), timeout=2000)
    
    # Verify error signal was emitted
    error_signals = [s for s in updated_spy if "Failed" in str(s[2]) and "Point Clouds" in str(s[2])]
    assert len(error_signals) > 0

"""
    Desc: Test Gap Detection Failure
    This Test Verifies Error Handling In Gap Detection
"""
@pytest.mark.unit
def test_pipeline_run_failed_gap_detection(qtbot, pipeline_worker, tmp_path):
    """Test PipelineWorker run method with gap detection failure"""
    # Spy on signals
    updated_spy = QSignalSpy(pipeline_worker.progress_updated_status)
    completion_spy = QSignalSpy(pipeline_worker.progress_completion_status)
    
    # Create test directory structure
    test_output_dir = tmp_path / "point_clouds"
    test_output_dir.mkdir(exist_ok=True)

    # Create a CHM file that the gap detector will try to access
    chm_path = test_output_dir / "chm.tif"
    with open(chm_path, 'w') as f:
        f.write("Mock GeoTIFF data")
    
    # Set up the pipeline worker with mocked components
    # 1. Create logger
    pipeline_worker.logger = MagicMock()
    
    # 2. Create config loader
    pipeline_worker.config_loader = MagicMock()
    
    # Use patching to address the is_canceled attribute issue
    with patch.object(pipeline_worker, 'is_canceled', False), \
         patch('PyQt5.QtCore.QThread.currentThread', return_value=pipeline_worker):
        
        # 3. Mock file handler
        pipeline_worker.file_handler = MagicMock()
        pipeline_worker.file_handler.create_processing_directories.return_value = {
            'input': tmp_path / "input",
            'processed': tmp_path / "processed",
            'point_clouds': test_output_dir,
            'analysis': tmp_path / "analysis"
        }
        
        # 4. Mock batch processor
        pipeline_worker.batch_processor = MagicMock()
        pipeline_worker.batch_processor.process_batch.return_value = {
            'valid': [Path("test_image.jpg")]
        }
        
        # 5. Patch WebODM Client before creating an instance
        with patch('ResilientGeoDrone.src.point_cloud.webodm_client.WebODMClient._wait_for_completion_signal') as mock_wait_method:
            # Configure the mocked _wait_for_completion_signal to return immediately
            mock_wait_method.return_value = {
                'dsm': str(test_output_dir / "dsm.tif"),
                'dtm': str(test_output_dir / "dtm.tif"),
                'chm': str(chm_path),
                'orthophoto': str(test_output_dir / "orthophoto.tif")
            }
            
            # Create WebODM client normally since we've patched the problematic method
            # The instance will be created in pipeline_worker.run()
            
            # 6. Mock gap detector to fail
            pipeline_worker.gap_detector = MagicMock()
            pipeline_worker.gap_detector.process_gaps.side_effect = Exception("Gap detection failed")
            
            # Create test files that the pipeline will try to access
            for path_name in ["dsm.tif", "dtm.tif", "orthophoto.tif"]:
                file_path = test_output_dir / path_name
                with open(file_path, 'w') as f:
                    f.write("Mock GeoTIFF data")
            
            # Run the pipeline worker with the actual run method
            pipeline_worker.run()
            
            # Wait for signals
            qtbot.waitUntil(
                lambda: any(s[2].startswith("Failed Gap Detection") for s in updated_spy),
                timeout=2000
            )

        
"""
    Desc: Test Member Variable Creation In Run Method
    This Test Checks If All Required Member Variables Are Created
"""
@pytest.mark.unit
def test_member_variable_creation(qtbot, pipeline_worker):
    """Test that member variables are created during run"""
    # We need to patch various methods to avoid actual execution
    with patch('ResilientGeoDrone.src.utils.file_handler.FileHandler.create_processing_directories',
              return_value={'input': Path('./test_dir'), 'processed': Path('./test_dir'),
                           'point_clouds': Path('./test_dir'), 'analysis': Path('./test_dir')}), \
         patch('ResilientGeoDrone.src.preprocessing.batch_processor.BatchProcessor.process_batch',
              return_value={'valid': []}):
        
        # Run the worker
        pipeline_worker.run()
        
        # Wait for initialization to complete
        qtbot.wait(200)
    
    # Now check if member variables were created
    assert hasattr(pipeline_worker, 'logger')
    assert hasattr(pipeline_worker, 'config_loader')
    assert hasattr(pipeline_worker, 'file_handler')
    assert hasattr(pipeline_worker, 'batch_processor')
    assert hasattr(pipeline_worker, 'webodm_client')
    assert hasattr(pipeline_worker, 'gap_detector')


"""
    Desc: Test Successful Execution Flow With Completion Signal
    This Test Verifies The Pipeline Worker Can Complete Successfully
"""
@pytest.mark.unit
def test_pipeline_successful_completion_signal(qtbot, pipeline_worker, tmp_path):
    """Test that successful completion emits the proper signal"""
    # Setup spy on completion signal
    completion_spy = QSignalSpy(pipeline_worker.progress_completion_status)
    updated_spy = QSignalSpy(pipeline_worker.progress_updated_status)
    
    # Create test directory structure
    test_output_dir = tmp_path / "point_clouds"
    test_output_dir.mkdir(exist_ok=True)

    # Create a CHM file that the gap detector will try to access
    chm_path = test_output_dir / "chm.tif"
    with open(chm_path, 'w') as f:
        f.write("Mock GeoTIFF data")
    
    # Set up the pipeline worker with mocked components
    pipeline_worker.logger = MagicMock()
    pipeline_worker.config_loader = MagicMock()
    
    # Important: Mock the gap detector BEFORE configuring file paths
    # This ensures our mock is in place before any path validation happens
    pipeline_worker.gap_detector = MagicMock()
    
    # Mock more deeply to intercept any file path validation
    # We need to mock not just the process_gaps function, but any file access
    # that might happen before it's called
    with patch('os.path.exists', return_value=True), \
         patch('os.path.isfile', return_value=True), \
         patch.object(pipeline_worker, 'is_canceled', False), \
         patch('PyQt5.QtCore.QThread.currentThread', return_value=pipeline_worker):
        
        # Configure file paths
        pipeline_worker.file_handler = MagicMock()
        pipeline_worker.file_handler.create_processing_directories.return_value = {
            'input': tmp_path / "input",
            'processed': tmp_path / "processed",
            'point_clouds': test_output_dir,
            'analysis': tmp_path / "analysis"
        }
        
        pipeline_worker.batch_processor = MagicMock()
        pipeline_worker.batch_processor.process_batch.return_value = {
            'valid': [Path("test_image.jpg")]
        }
        
        # Configure WebODM to return paths to our test files
        with patch('ResilientGeoDrone.src.point_cloud.webodm_client.WebODMClient._wait_for_completion_signal') as mock_wait_method:
            mock_wait_method.return_value = {
                'dsm': str(test_output_dir / "dsm.tif"),
                'dtm': str(test_output_dir / "dtm.tif"),
                'chm': str(chm_path),  # Make sure this is the correct path
                'orthophoto': str(test_output_dir / "orthophoto.tif")
            }
            
            # Create all necessary files
            for path_name in ["dsm.tif", "dtm.tif", "orthophoto.tif"]:
                file_path = test_output_dir / path_name
                with open(file_path, 'w') as f:
                    f.write("Mock GeoTIFF data")
            
            # CRITICAL: Ensure the gap detector doesn't actually try to access files
            pipeline_worker.gap_detector.process_gaps = MagicMock(return_value=True)
            
            # Also patch the method that might be validating the paths
            with patch('ResilientGeoDrone.src.geospatial.gap_detection.GapDetector.process_gaps', 
                      return_value=True):
                
                # Run the pipeline worker
                pipeline_worker.run()
                
                # Wait for completion signal with more specific condition
                qtbot.waitUntil(
                    lambda: len([s for s in completion_spy if s[0] is True and s[1] == 'Pipeline Completed']) > 0,
                    timeout=5000  # Increased timeout for reliability
                )
            
            # Verify successful completion signal
            assert len(completion_spy) > 0
            assert completion_spy[0][0] is True
            assert completion_spy[0][1] == 'Pipeline Completed'