import cv2
import numpy as np
from pathlib import Path
from .quality_metrics import QualityMetrics
from ..utils.logger import LoggerSetup

class ImageValidator:
    """Image Validation and Quality Control"""
    
    def __init__(self, config_loader):
        self.logger = LoggerSetup(__name__).get_logger()
        self.config = config_loader.get_preprocessing_config()
        self.metrics = QualityMetrics(self.config)
        
    def validate_image(self, image_path: Path) -> bool:
        """Validate Single Image"""
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                self.logger.warning(f"Failed to load {image_path}")
                return False
                
            checks = [
                self.metrics.check_resolution(img),
                self.metrics.check_blur(img),
                self.metrics.check_brightness(img),
                self.metrics.check_contrast(img)
            ]
            
            return all(checks)
            
        except Exception as e:
            self.logger.error(f"Validation failed for {image_path}: {str(e)}")
            return False