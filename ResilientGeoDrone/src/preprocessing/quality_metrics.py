import cv2
import numpy as np
from typing import Tuple



"""

    Desc: This Module Provides Us Quality Metrics For Image Validation
    And Quality Control. The Module Utilizes Image Metrics To Check Image
    Resolution, Blur, Brightness, And Contrast. The Metrics Are Used To
    Validate Images And Ensure Quality Control.

"""
class QualityMetrics:
    
    """
    
        Desc: Initializes Our Quality Metrics With A Configuration Dictionary
        To Load Quality Metrics Configuration Parameters. The Configuration
        Dictionary Includes Minimum Resolution, Blur Threshold, And Brightness
        Range. The Configuration Is Used To Initialize Our Quality Metric's 
        Minimas And Maximas.

        Preconditions:
            1. config: Dictionary Representing Quality Metrics Configuration

        Postconditions:
            1. Load Quality Metrics Configuration Parameters
            2. Initialize Quality Metrics Minimas And Maximas
    
    """
    def __init__(self, config):
        self.min_resolution = tuple(config['min_resolution'])
        self.blur_threshold = config['blur_threshold']
        self.brightness_range = tuple(config['brightness_range'])
        

    """
    
        Desc: This Function Takes In img And Checks The Image Resolution
        Against The Minimum Resolution. The Function Returns True If The
        Image Resolution Is Greater Than Or Equal To The Minimum Resolution
        And False Otherwise.

        Preconditions:
            1. img: NumPy Array Representing Image

        Postconditions:
            1. Check Image Resolution
            2. Returns True If Image Resolution Is Greater Than Or Equal To Minimum Resolution
            3. Returns False Otherwise
    
    """
    def check_resolution(self, img: np.ndarray) -> bool:
        # Get Image Dimensions And Check Resolution
        height, width = img.shape[:2]
        return width >= self.min_resolution[0] and height >= self.min_resolution[1]
        

    """
    
        Desc: This Function Takes In img And Checks The Image Blur Level
        Against The Blur Threshold. The Function Returns True If The
        Image Blur Level Is Greater Than The Blur Threshold And False Otherwise.

        Preconditions:
            1. img: NumPy Array Representing Image
        
        Postconditions:
            1. Check Image Blur Level
            2. Returns True If Image Blur Level Is Greater Than Blur Threshold
            3. Returns False Otherwise
    
    """
    def check_blur(self, img: np.ndarray) -> bool:
        # Convert Image To Grayscale And Check Blur Level
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Calculate Laplacian Variance As Blur Score
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        return blur_score > self.blur_threshold
        

    """
    
        Desc: This Function Takes In img And Checks The Image Brightness
        Against The Brightness Range. The Function Returns True If The
        Image Brightness Is Within The Brightness Range And False Otherwise.

        Preconditions:
            1. img: NumPy Array Representing Image

        Postconditions:
            1. Check Image Brightness
            2. Returns True If Image Brightness Is Within Brightness Range
            3. Returns False Otherwise
    
    """
    def check_brightness(self, img: np.ndarray) -> bool:
        # Convert Image To Grayscale And Check Brightness
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Calculate Mean Brightness
        brightness = np.mean(gray)
        return self.brightness_range[0] <= brightness <= self.brightness_range[1]