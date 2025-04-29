import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from .logger import LoggerSetup



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
        self.logger = LoggerSetup().get_logger()
        self.logger.info(f"ConfigLoader ID: {self}  -  Initializing Config Loader...")
        self.config_path = Path(config_path)
        if not self.config_path.is_file() or not self.config_path.suffix == '.yaml':
            self.logger.error(f"ConfigLoader ID: {self}  -  Config Loader Initialization Failed: Failed To Provide A Valid Config File.")
            raise FileNotFoundError(f"Configuration File Not Found: {self.config_path}")
        self.config: Optional[Dict[str, Any]] = None
        self.logger.info(f"ConfigLoader ID: {self}  -  Config Loader Initialized.")
        

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
        try:
          self.logger.info(f"ConfigLoader ID: {self}  -  Loading Configuration File...")
          # If Our File Is Invalid (If It's Been Deleted Or Moved During Runtime)
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
        
        Postconditions:
            1. Validate Configuration Structure For Essential Sections
    
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
        self.logger.info(f"ConfigLoader ID: {self}  -  Getting Preprocessing Configuration...")

        result = self.load()['preprocessing']

        self.logger.info(f"ConfigLoader ID: {self}  -  Preprocessing Configuration Retrieved.")
        return result
    

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
        self.logger.info(f"ConfigLoader ID: {self}  -  Getting Point Cloud Configuration...")

        result = self.load()['point_cloud']

        self.logger.info(f"ConfigLoader ID: {self}  -  Point Cloud Configuration Retrieved.")

        return result
    

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
        self.logger.info(f"ConfigLoader ID: {self}  -  Getting Geospatial Configuration...")

        result =  self.load()['geospatial']

        self.logger.info(f"ConfigLoader ID: {self}  -  Geospatial Configuration Retrieved.")

        return result
    

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


    def get_webodm_params(self, environment: str) -> list:
        """
        Gets all WebODM parameters in the format expected by the WebODM API.
        Returns a list of dictionaries with 'name' and 'value' keys.
        """
        try:
            self.logger.info(f"WebODM ID: {self}  -  Getting WebODM Parameters...")
            
            config = self.load()
            env_params = self.get_environment_params(environment)
            
            # Track parameters we've already added to avoid duplicates
            processed_params = set()
            
            # Start with our standard outputs we always want
            options = []
            
            # Iterate through all parameters in the environment config
            for param_name, param_value in env_params.items():
                # Skip empty or None values
                if param_value is None or (isinstance(param_value, str) and param_value == "") or param_name in ('sm-cluster', 'sm-no-align'):
                    continue
                
                # Skip duplicate parameters (if we've already added a kebab-case version)
                base_name = param_name.replace('_', '-')
                if base_name in processed_params:
                    continue
                
                # Only use kebab-case names (with hyphens)
                kebab_name = param_name.replace('_', '-')
                processed_params.add(kebab_name)
                
                # Convert all values to strings as required by WebODM API
                if isinstance(param_value, bool):
                    # Convert Python booleans to JSON booleans (no quotes)
                    value = "true" if param_value else "false"
                elif isinstance(param_value, (int, float)):
                    value = str(param_value)  # Convert numbers to strings
                elif param_value == "None":
                    value = ""  # Replace "None" string with empty string
                else:
                    # Convert other values to strings
                    value = param_value
                
                # Add the parameter in WebODM API format
                options.append({"name": kebab_name, "value": value})
            
            self.logger.info(f"ConfigLoader ID: {self}  -  WebODM options generated successfully with {len(options)} parameters.")
            
            return options
            
        except Exception as e:
            self.logger.error(f"ConfigLoader ID: {self}  -  Failed to generate WebODM options: {str(e)}.")
            raise