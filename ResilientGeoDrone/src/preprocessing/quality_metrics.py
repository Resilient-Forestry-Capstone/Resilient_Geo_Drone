import cv2
import numpy as np
from typing import Tuple

class QualityMetrics:
    """Image Quality Metrics Calculator"""
    
    def __init__(self, config):
        self.min_resolution = tuple(config['min_resolution'])
        self.blur_threshold = config['blur_threshold']
        self.brightness_range = tuple(config['brightness_range'])
        
    def check_resolution(self, img: np.ndarray) -> bool:
        """Check Image Resolution"""
        height, width = img.shape[:2]
        return width >= self.min_resolution[0] and height >= self.min_resolution[1]
        
    def check_blur(self, img: np.ndarray) -> bool:
        """Check Image Blur Level"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        return blur_score > self.blur_threshold
        
    def check_brightness(self, img: np.ndarray) -> bool:
        """Check Image Brightness"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        return self.brightness_range[0] <= brightness <= self.brightness_range[1]
        
    def check_contrast(self, img: np.ndarray) -> bool:
        """Check Image Contrast"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contrast = np.std(gray)
        return contrast > 20  # Minimum contrast threshold