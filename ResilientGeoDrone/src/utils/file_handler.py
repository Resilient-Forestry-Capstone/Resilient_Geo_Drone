from pathlib import Path
from typing import List, Union, Dict, Any
import shutil
import yaml
from datetime import datetime

class FileHandler:
    """File System Operations Handler"""
    
    def __init__(self, config_loader):
        self.config = config_loader.load()
        self.supported_formats = self.config['preprocessing']['supported_formats']
    
    def create_directory(self, path: Union[str, Path]) -> Path:
        """Create directory if not exists"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_image_files(self, directory: Union[str, Path]) -> List[Path]:
        """Get all valid image files from directory"""
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
            
        return [
            f for f in directory.glob("**/*")
            if f.is_file() and f.suffix.lower() in self.supported_formats
        ]
    
    def create_processing_directories(self, base_dir: Union[str, Path]) -> Dict[str, Path]:
        """Create timestamped processing directories"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_path = Path(base_dir)
        
        directories = {
            'processed': base_path / 'processed' / timestamp,
            'point_cloud': base_path / 'point_cloud' / timestamp,
            'analysis': base_path / 'analysis' / timestamp
        }
        
        for dir_path in directories.values():
            self.create_directory(dir_path)
            
        return directories
    
    def save_results(self, results: Dict[str, Any], output_path: Union[str, Path]) -> None:
        """Save processing results"""
        output_path = Path(output_path)
        self.create_directory(output_path.parent)
        
        with open(output_path, 'w') as f:
            yaml.dump(results, f, default_flow_style=False)
    
    def copy_files(self, files: List[Path], destination: Union[str, Path]) -> None:
        """Copy files to destination"""
        destination = Path(destination)
        self.create_directory(destination)
        
        for file in files:
            shutil.copy2(file, destination / file.name)