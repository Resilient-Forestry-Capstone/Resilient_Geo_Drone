from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict
from .image_validator import ImageValidator
from ..utils.logger import LoggerSetup



"""

    Desc: This Module Provides A Batch Image Processor For Processing
    Multiple Images Concurrently. The Batch Processor Utilizes An Image
    Validator To Validate Images And Process Them To Ensure We Process
    Images That Are Poorer Quality So We Don't Overprocess Images.

"""
class BatchProcessor:
    
    """
    
        Desc: Initializes Our Batch Processor With A Config Loader (config_loader)
        To Load Preprocessing Configuration Parameters. It Also Initializes Our
        Image Validator (validator). As Well As The Logger We Are Writing
        To.

        Preconditions:
            1. config_loader: ConfigLoader Object
        
        Postconditions:
            1. Set Our logger 
            2. Load Preprocessing Configuration Parameters
            3. Initialize Image Validator
            4. Initialize Image Processor
    
    """
    def __init__(self, config_loader):
        self.logger = LoggerSetup(__name__).get_logger()
        self.config = config_loader.get_preprocessing_config()
        self.validator = ImageValidator(config_loader)
        

    """
    
        Desc: This Function Takes In image_paths And Processes The Images
        Concurrently Using A ThreadPoolExecutor. The Function Returns A
        Dictionary Of Valid And Invalid Images. The Valid Images Are Saved
        In The 'valid' Key And The Invalid Images Are Saved In The 'invalid'
        Key.

        Preconditions:
            1. image_paths: List Of Paths To Images
            2. image_paths Must Be Valid Paths
            3. max_workers: Maximum Number Of Workers For ThreadPoolExecutor
        
        Postconditions:
            1. Processes Images Concurrently
            2. Returns Dictionary Of Valid And Invalid Images
    
    """
    def process_batch(self, image_paths: List[Path], max_workers: int = 4) -> Dict[str, List[Path]]:
        # Results Dictionary
        results = {'valid': [], 'invalid': []}
        
        # Send Out Multiple Workers To Process Images Concurrently
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit Image Validation Tasks
            future_to_path = {
                executor.submit(self.validator.validate_image, path): path 
                for path in image_paths
            }
            
            # Process Results As They Come In
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    if future.result():
                        results['valid'].append(path)
                    else:
                        results['invalid'].append(path)
                except Exception as e:
                    self.logger.error(f"Error processing {path}: {str(e)}")
                    results['invalid'].append(path)

        # Return Results Of Valid Or Invalidated Images       
        return results