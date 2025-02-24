import yaml
from pathlib import Path
from typing import Dict, Any, Optional



"""

    Desc: This Module Provides A Configuration Loader For Loading And
    Validating Configuration Files. The Configuration File Is Expected
    To Be In YAML Format And Contains Preprocessing, Point Cloud, And
    Geospatial Configuration Parameters. 

"""
class ConfigLoader:
    
    """
    
        Desc: Initializes Our Config Loader With A Configuration Path
        To Load Configuration Parameters. The Configuration Path Is
        Expected To Be In YAML Format.

        Preconditions:
            1. config_path: Path To Configuration File
            2. config_path Must Be A Valid Path
        
        Postconditions:
            1. Set Our Configuration Path
    
    """
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        self.config: Optional[Dict[str, Any]] = None
        

    """
    
        Desc: This Function Loads And Validates The Configuration File.
        The Function Returns The Configuration As A Dictionary. The
        Configuration Is Expected To Have Preprocessing, Point Cloud,
        And Geospatial Sections.

        Preconditions:
            1. config_path Is Intiialized

        Postconditions:
            1. Loads And Validates Configuration File
            2. Returns Configuration As A Dictionary
    
    """
    def load(self) -> Dict[str, Any]:
        # If Our File Is Invalid
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        # If We Haven't Loaded Our config, Load It In
        if self.config is None:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                self._validate_config()
        
        return self.config
    

    """
    
        Desc: This Function Validates The Configuration Structure
        To Ensure That It Contains Preprocessing, Point Cloud, And
        Geospatial Sections. If The Configuration Is Invalid, An
        Error Is Raised.

        Preconditions:
            1. config Is Initialized
        
        Postconditions:
            1. Validate Configuration Structure For Essential Sections
    
    """
    def _validate_config(self) -> None:
        # Get For Required Sections
        required_sections = ['preprocessing', 'point_cloud', 'geospatial']

        # Check If Required Sections Are Present
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
    

    """
    
        Desc: This Function Gets Preprocessing Specific Configuration
        Parameters From The Configuration File. The Parameters Include
        Image Quality Thresholds, Brightness Thresholds, And Contrast
        Thresholds. The Parameters Are Returned As A Dictionary.

        Preconditions:
            1. config Is Initialized

        Postconditions:
            1. Get Preprocessing Specific Configuration Parameters
            2. Return Parameters As A Dictionary
    
    """
    def get_preprocessing_config(self) -> Dict[str, Any]:
        return self.load()['preprocessing']
    

    """
    
        Desc: This Function Gets Point Cloud Specific Configuration
        Parameters From The Configuration File. The Parameters Include
        WebODM Environment Configuration And Point Cloud Generation
        Options. The Parameters Are Returned As A Dictionary.

        Preconditions:
            1. config Is Initialized

        Postconditions:
            1. Get Point Cloud Specific Configuration Parameters
            2. Return Parameters As A Dictionary
    
    """
    def get_point_cloud_config(self) -> Dict[str, Any]:
        return self.load()['point_cloud']
    

    """
    
        Desc: This Function Gets Geospatial Specific Configuration
        Parameters From The Configuration File. The Parameters Include
        Environment Configuration And Geospatial Options. The Parameters
        Are Returned As A Dictionary.

        Preconditions:
            1. config Is Initialized

        Postconditions:
            1. Get Geospatial Specific Configuration Parameters
            2. Return Parameters As A Dictionary
    
    """
    def get_geospatial_config(self) -> Dict[str, Any]:
        return self.load()['geospatial']
    

    """
    
        Desc: This Function Gets Environment Specific Parameters
        From The Configuration File. The Parameters Include Feature
        Quality, Matcher Type, Minimum Number Of Features, Point Cloud
        Quality, Mesh Quality, Use 3D Mesh, Mesh Octree Depth, Point
        Cloud Filter, Point Cloud Geometric, Maximum Concurrency, Auto
        Boundary, And Ignore GSD. The Parameters Are Returned As A Dictionary.

        Preconditions:
            1. config Is Initialized

        Postconditions:
            1. Get Environment Specific Parameters
            2. Return Parameters As A Dictionary
    
    """
    def get_environment_params(self, environment: str) -> Dict[str, Any]:
        # Get Environment Parameters
        environments = self.load()['point_cloud']['webodm']['environments']

        # Check If Environment Is Valid
        if environment not in environments:
            raise ValueError(f"Invalid environment: {environment}")
        return environments[environment]