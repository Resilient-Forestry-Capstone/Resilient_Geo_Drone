from typing import List
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from ..utils.config_loader import ConfigLoader
from ..point_cloud.webodm_client import WebODMClient
from ..preprocessing.batch_processor import BatchProcessor
from ..utils.file_handler import FileHandler
from ..utils.logger import LoggerSetup
from ..geospatial.gap_detection import GapDetector
from pathlib import Path



"""

  Desc: This Class Is Utilized To Run The Pipeline Processing In A
  Separate Thread To Keep The UI Responsive. The Worker Will Emit
  Signals To Update The UI With Progress Information. It Handles
  The Processing Of Images, Point Cloud Generation, Gap Detection,
  And Result Processing.


"""
class PipelineWorker(QThread):

  # Define A Signal Status For Communicating With Our Main Thread
  progress_updated_status = pyqtSignal(float, str, str)
  progress_completion_status = pyqtSignal(bool, str, str)


  """
  
    Desc: Initializes Our Pipeline Worker With A Given Configuration Path
    And A List Of Image Paths. The Worker Will Be Used To Process Images,
    Generate Point Clouds, Detect Gaps, And Process Results. The Worker
    Will Emit Signals To Update The UI With Progress Information.

    Preconditions:
      1. Configuration Path Must Be A Valid To A .yaml File
      2. Image Paths Must Be A List Of Valid Image Paths
    
    Postconditions:
      1. Initialize Our Worker Thread
      2. Set Configuration Path
      3. Set Image Paths
      4. Set Is Canceled Flag To False
  
  """
  def __init__(self, config_path : str, image_paths: List[Path]):
    super().__init__()
    self.config_path = config_path
    self.image_paths = image_paths
    self.is_canceled = False


  """
  
    Desc: Run Method Delegated To Our Worker Thread. This Method
    Handles The Processing Of Images, Point Cloud Generation, Gap
    Detection, And Result Processing. It Will Emit Signals To
    Update The UI With Progress Information.

    Preconditions:
      1. Image Paths Must Be Valid
      2. Config Loader Must Be Initialized

    Postconditions:
      1. Process Images
      2. Generate Point Clouds
      3. Detect Gaps
      4. Process Results
  
  """
  @pyqtSlot()
  def run(self):
    try:
      # Initiate Our Pipeline And Tell User
      self.progress_updated_status.emit(0.00, 'Initializing Pipeline', 'Loading Configuration...')

      self.logger = LoggerSetup().get_logger()
      self.progress_updated_status.emit(14.285714, 'Initializing Pipeline', 'Loading Configuration...')

      self.config_loader = ConfigLoader(self.config_path)
      self.progress_updated_status.emit(28.571429, 'Initializing Pipeline', 'Loading Configuration...')

      self.file_handler = FileHandler(self.config_loader)
      self.progress_updated_status.emit(42.857142, 'Initializing Pipeline', 'Loading Configuration...')
      
      # Initialize pipeline components
      self.batch_processor = BatchProcessor(self.config_loader)
      self.progress_updated_status.emit(57.142856, 'Initializing Pipeline', 'Loading Configuration...')

      self.webodm_client = WebODMClient(self.config_loader)
      self.progress_updated_status.emit(71.42857, 'Initializing Pipeline', 'Loading Configuration...')

      self.gap_detector = GapDetector(self.config_loader)
      self.progress_updated_status.emit(100.00, 'Initializing Pipeline', 'Loading Configuration...')

      # Firstly Create Directories
      self.progress_updated_status.emit(0.00, 'Creating Directories', 'Creating Directories...')

      try:
        self.logger.info("Creating Directories")
        dirs = self.file_handler.create_processing_directories('./data/output')
      except Exception as e:
        self.logger.error(f"Creating Directories Failed: {str(e)}")
        self.progress_updated_status.emit(100.00, 'Creating Directories', f"Failed Creating Directories ({str(e)}).")
        return
      
      self.progress_updated_status.emit(100.00, 'Creating Directories', 'Directories Created.')

      # Secondly Preprocess Images
      self.progress_updated_status.emit(0.00, 'Preprocessing Images', 'Processing Images...')
      
      try:
        self.logger.info("Stage 1: Image Preprocessing")
        valid_images = self.batch_processor.process_batch(self.image_paths)['valid']
      except Exception as e:
        self.logger.error(f"Stage 1: Image Preprocessing Failed: {str(e)}")
        self.progress_updated_status.emit(100.00, 'Preprocessing Images', f"Failed Processing Images ({str(e)}).")

        return

      if not valid_images:
          self.progress_updated_status.emit(100.00, 'Preprocessing Images', 'Failed Processing Images (Invalid Images)...')
          self.progress_completion_status.emit(False, 'Pipeline Failed', 'Pipeline Failed Successfully.')
          return
      
      # Generate Point Clouds
      self.progress_updated_status.emit(0.00, 'Generating Point Clouds', 'Generating Point Clouds...')

      try:
        self.logger.info("Stage 2: Point Cloud Generation")
        webodm_results = self.webodm_client.generate_point_cloud_signal(valid_images, 'sunny', self.progress_updated_status)
      except Exception as e:
        self.logger.error(f"Stage 2: Point Cloud Generation Failed: {str(e)}")
        self.progress_updated_status.emit(100.00, 'Generating Point Clouds', f"Failed Generating Point Clouds ({str(e)}).")
        return

      # Process WebODM results
      self.progress_updated_status.emit(0.0, 'Processing Point Clouds', 'Processing Point Clouds...')

      try:
        self.logger.info("Stage 3: Point Cloud Processing")
        
      except Exception as e:
        self.logger.error(f"Stage 3: Point Cloud Processing Failed: {str(e)}")
        self.progress_updated_status.emit(100.00, 'Processing Point Clouds', f"Failed Processing Point Clouds ({str(e)}).")
        return
      
      self.progress_updated_status.emit(100.00, 'Processing Point Clouds', 'Point Clouds Processed.')

      # Analyze Point Clouds
      self.progress_updated_status.emit(0.00, 'Analyzing Point Clouds', 'Starting Gap Detection...')

      try:
        self.logger.info("Stage 4: Point Cloud Analysis")
        self.gap_detector.process_gaps(self.webodm_client.output_dir / "chm.tif", dirs['analysis'])
        self.logger.info("Stage 4: Point Cloud Analysis Completed")
      except Exception as e:
        self.logger.error(f"Stage 4: Point Cloud Analysis Failed: {str(e)}")
        self.progress_updated_status.emit(100.00, 'Analyzing Point Clouds', f"Failed Gap Detection ({str(e)}).")
        return
      
      self.progress_updated_status.emit(100.00, 'Analyzing Point Clouds', 'Point Clouds Analyzed.')

      self.progress_completion_status.emit(True, 'Pipeline Completed', 'Pipeline Completed Successfully.')
    except Exception as e:
      self.logger.error(f"Pipeline failed: {str(e)}")
      self.progress_updated_status.emit(100.00, 'Pipeline Failed', f"Pipeline Failed ({str(e)}).")
      self.progress_completion_status.emit(False, 'Pipeline Failed', 'Pipeline Failed Successfully.')


  """
  
    Desc: This Method Is Used To Cancel The Pipeline Processing.
    It Sets The Is Canceled Flag To True And Emits A Signal
    Indicating That The Pipeline Has Been Canceled.

    Preconditions:
      1. None

    Postconditions:
      1. Set Is Canceled Flag To True
      2. Emit Signal Indicating Pipeline Canceled
  
  """
  def cancel(self):
    self.logger.info("Pipeline Canceled")
    self.is_canceled = True
    self.progress_updated_status.emit(100.00, 'Pipeline Canceled', 'Pipeline Canceled.')