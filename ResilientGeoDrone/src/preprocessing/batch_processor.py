from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict
from .image_validator import ImageValidator
from ..utils.logger import LoggerSetup

class BatchProcessor:
    """Batch Image Processing Controller"""
    
    def __init__(self, config_loader):
        self.logger = LoggerSetup(__name__).get_logger()
        self.config = config_loader.get_preprocessing_config()
        self.validator = ImageValidator(config_loader)
        
    def process_batch(self, image_paths: List[Path], max_workers: int = 4) -> Dict[str, List[Path]]:
        """Process Multiple Images Concurrently"""
        results = {'valid': [], 'invalid': []}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(self.validator.validate_image, path): path 
                for path in image_paths
            }
            
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
                    
        return results