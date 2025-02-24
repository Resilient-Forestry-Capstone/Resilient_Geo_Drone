from pathlib import Path
from typing import List, Union, Dict, Any
import shutil
import yaml
from datetime import datetime



"""

    Desc: This Module Provides A Interface For File System Operations
    Including Directory Creation, File Copying, And Results Saving. The
    Module Utilizes A Configuration Loader To Load Configuration Parameters
    And Supported Formats. The File Handler Is Used To Manage File System
    Operations In The ResilientGeoDrone Pipeline.

"""
class FileHandler:
    
    """
    
        Desc: Initializes Our File Handler With A Config Loader (config_loader)
        To Load Configuration Parameters. The Supported Formats Are Used To
        Filter Valid Image Files.

        Preconditions:
            1. config_loader: ConfigLoader Object

        Postconditions:
            1. Load Configuration Parameters
            2. Initialize Supported Formats
    
    """
    def __init__(self, config_loader):
        self.config = config_loader.load()
        self.supported_formats = self.config['preprocessing']['supported_formats']
    

    """
    
        Desc: This Function Takes In path And Creates A Directory If
        It Does Not Exist. The Function Returns The Path As A Path Object.

        Preconditions:
            1. path: Path To Directory
            2. path Must Be A Valid Path

        Postconditions:
            1. Creates Directory If It Does Not Exist
            2. Returns Path As Path Object
    
    """
    def create_directory(self, path: Union[str, Path]) -> Path:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    

    """
    
        Desc: This Function Takes In directory And Gets All Valid Image
        Files From The Directory. The Function Returns A List Of Image
        Files As Path Objects. The Image Files Are Filtered By Supported
        Formats.

        Preconditions:
            1. directory: Path To Directory
            2. directory Must Be A Valid Directory

        Postconditions:
            1. Get All Valid Image Files From Directory
            2. Returns List Of Image Files As Path Objects
    
    """
    def get_image_files(self, directory: Union[str, Path]) -> List[Path]:
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
            
        # Filter For Files That Are In Our Specified Supported Formats
        return [
            f for f in directory.glob("**/*")
            if f.is_file() and f.suffix.lower() in self.supported_formats
        ]
    

    """
    
        Desc: This Function Takes In base_dir And Creates Timestamped
        Processing Directories. The Function Returns A Dictionary Of
        Processing Directories. The Directories Include Processed,
        Point Cloud, And Analysis Directories.

        Preconditions:
            1. base_dir: Path To Base Directory
            2. base_dir Must Be A Valid Directory

        Postconditions:
            1. Create Timestamped Processing Directories
            2. Returns Dictionary Of Processing Directories
    
    """
    def create_processing_directories(self, base_dir: Union[str, Path]) -> Dict[str, Path]:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_path = Path(base_dir)
        
        # Create Processing Directories For Given TimeStamp
        directories = {
            'processed': base_path / 'processed' / timestamp,
            'point_cloud': base_path / 'point_cloud' / timestamp,
            'analysis': base_path / 'analysis' / timestamp
        }
        
        # Create Directories If They Do Not Exist
        for dir_path in directories.values():
            self.create_directory(dir_path)
            
        return directories
    

    """
    
        Desc: This Function Takes In results And output_path And Saves
        Processing Results. The Results Are Saved As YAML In The Output
        Path. The Function Returns None.

        Preconditions:
            1. results: Dictionary Of Processing Results
            2. output_path: Path To Output File
            3. results And output_path Must Be Valid
        
        Postconditions:
            1. Save Processing Results As YAML In Output Path
            2. Returns None
    
    """
    def save_results(self, results: Dict[str, Any], output_path: Union[str, Path]) -> None:
        output_path = Path(output_path)
        self.create_directory(output_path.parent)
        
        # Save Results As YAML
        with open(output_path, 'w') as f:
            yaml.dump(results, f, default_flow_style=False)
    

    """
    
        Desc: This Function Takes In files And Destination And Copies
        Files To The Destination. The Function Returns None.
    
    """
    def copy_files(self, files: List[Path], destination: Union[str, Path]) -> None:
        destination = Path(destination)
        self.create_directory(destination)
        
        # Copy Files To Destination
        for file in files:
            shutil.copy2(file, destination / file.name)