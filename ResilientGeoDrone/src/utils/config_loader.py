import yaml
from pathlib import Path
from typing import Dict, Any, Optional

<<<<<<< HEAD
from .logger import LoggerSetup

=======
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576


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
<<<<<<< HEAD
        self.logger = LoggerSetup().get_logger()
        self.logger.info(f"ConfigLoader ID: {self}  -  Initializing Config Loader...")
        try:
          self.config_path = Path(config_path)
          if not self.config_path.exists():
              raise FileNotFoundError(f"Configuration File Not Found: {self.config_path}")
          self.config: Optional[Dict[str, Any]] = None
          self.logger.info(f"ConfigLoader ID: {self}  -  Config Loader Initialized.")
        except Exception as e:
            self.logger.error(f"ConfigLoader ID: {self}  -  Config Loader Initialization Failed: {str(e)}.")
            raise
=======
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        self.config: Optional[Dict[str, Any]] = None
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
        

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
<<<<<<< HEAD
        try:
          self.logger.info(f"ConfigLoader ID: {self}  -  Loading Configuration File...")
          # If Our File Is Invalid
          if not self.config_path.exists():
              raise FileNotFoundError(f"Configuration File Not Found: {self.config_path}")
              
          # If We Haven't Loaded Our config, Load It In
          if self.config is None:
              with open(self.config_path, 'r') as f:
                  self.config = yaml.safe_load(f)
                  self._validate_config()
          self.logger.info(f"ConfigLoader ID: {self}  -  Configuration Loaded.")
          return self.config
        except Exception as e:
            self.logger.error(f"ConfigLoader ID: {self}  -  Configuration Loading Failed: {str(e)}.")
            raise
    

    """
    
        Desc: This Function Validates The Configuration Structure
        To Ensure That It Contains Preprocessing, Point Cloud, And
        Geospatial Sections. If The Configuration Is Invalid, An
        Error Is Raised.

        Preconditions:
            1. config Is Initialized
=======
        # If Our File Is Invalid
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        # If We Haven't Loaded Our config, Load It In
        if self.config is None:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                self._validate_config()
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
        
        Postconditions:
            1. Validate Configuration Structure For Essential Sections
    
<<<<<<< HEAD
    """
    def _validate_config(self) -> None:
        try:
          self.logger.info(f"ConfigLoader ID: {self}  -  Validating Configuration...")
          # Get For Required Sections
          required_sections = ['preprocessing', 'point_cloud', 'geospatial']

          # Check If Required Sections Are Present
          for section in required_sections:
              if section not in self.config:
                  raise ValueError(f"Missing Required Configuration Section: {section}")
          self.logger.info(f"ConfigLoader ID: {self}  -  Configuration Validated.")
        except Exception as e:
            self.logger.error(f"ConfigLoader ID: {self}  -  Configuration Validation Failed: {str(e)}.")
            raise
=======

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
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
    

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
<<<<<<< HEAD
        self.logger.info(f"ConfigLoader ID: {self}  -  Getting Preprocessing Configuration...")

        result = self.load()['preprocessing']

        self.logger.info(f"ConfigLoader ID: {self}  -  Preprocessing Configuration Retrieved.")
        return result
=======
        return self.load()['preprocessing']
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
    

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
<<<<<<< HEAD
        self.logger.info(f"ConfigLoader ID: {self}  -  Getting Point Cloud Configuration...")

        result = self.load()['point_cloud']

        self.logger.info(f"ConfigLoader ID: {self}  -  Point Cloud Configuration Retrieved.")

        return result
=======
        return self.load()['point_cloud']
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
    

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
<<<<<<< HEAD
        self.logger.info(f"ConfigLoader ID: {self}  -  Getting Geospatial Configuration...")

        result =  self.load()['geospatial']

        self.logger.info(f"ConfigLoader ID: {self}  -  Geospatial Configuration Retrieved.")

        return result
=======
        return self.load()['geospatial']
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
    

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
<<<<<<< HEAD
        try:
          self.logger.info(f"ConfigLoader ID: {self}  -  Getting Environment Parameters...")
          # Get Environment Parameters
          environments = self.load()['point_cloud']['webodm']['environments']

          # Check If Environment Is Valid
          if environment not in environments:
              raise ValueError(f"Invalid Environment: {environment}")
          self.logger.info(f"ConfigLoader ID: {self}  -  Environment Parameters Retrieved.")
          return environments[environment]
        except Exception as e:
            self.logger.error(f"ConfigLoader ID: {self}  -  Environment Parameters Retrieval Failed: {str(e)}.")
            raise
=======
        # Get Environment Parameters
        environments = self.load()['point_cloud']['webodm']['environments']

        # Check If Environment Is Valid
        if environment not in environments:
            raise ValueError(f"Invalid environment: {environment}")
        return environments[environment]
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
