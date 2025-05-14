import cv2
import numpy as np
from pathlib import Path
from .quality_metrics import QualityMetrics
from ..utils.logger import LoggerSetup



"""

    Desc: This Module Provides A Quality Metrics Class For Image Validation
    And Quality Control. The Class Utilizes Image Metrics To Check Image
    Resolution, Blur, Brightness, And Contrast. The Metrics Are Used To
    Validate Images And Ensure Quality Control. The Class Returns True
    If The Image Passes All Quality Checks And False Otherwise.

"""
class ImageValidator:
    
    """
    
        Desc: Initializes Our Image Validator With A Config Loader (config_loader)
        To Load Preprocessing Configuration Parameters. It Also Initializes Our
        Quality Metrics (metrics). As Well As The Logger We Are Writing
        To.
    
        Preconditions:
            1. config_loader: ConfigLoader Object

        Postconditions:
            1. Set Our logger
            2. Load Preprocessing Configuration Parameters
            3. Initialize Quality Metrics

    """
    def __init__(self, config_loader):
        self.logger = LoggerSetup(__name__).get_logger()
        self.config = config_loader.get_preprocessing_config()
        self.metrics = QualityMetrics(self.config)


    """
    
        Desc: This Function Takes In image_path And Validates The Image
        Using Quality Metrics. The Function Returns True If The Image
        Passes All Quality Checks And False Otherwise.

        Preconditions:
            1. image_path: Path To Image
            2. image_path Must Be A Valid Image

        Postconditions:
            1. Validates Single Image
            2. Returns True If Image Passes Quality Checks And False Otherwise
    
    """  
    def validate_image(self, image_path: Path) -> bool:
        # Attempt To Load Image And Check Quality Metrics
        try:
            # Load Image
            img = cv2.imread(str(image_path))
            if img is None:
                self.logger.warning(f"Failed to load {image_path}")
                return False
                
            # Check Image Quality Metrics
            checks = [
                self.metrics.check_resolution(img),
                self.metrics.check_blur(img),
                self.metrics.check_brightness(img)
            ]
            
            # Return True If All Checks Pass
            return all(checks)
            
        # Log Errors And Return False If Validation Fails
        except Exception as e:
            self.logger.error(f"Validation failed for {image_path}: {str(e)}")
            raise e