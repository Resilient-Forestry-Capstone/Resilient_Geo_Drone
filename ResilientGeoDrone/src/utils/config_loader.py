import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    """Configuration Management System"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self.config: Optional[Dict[str, Any]] = None
        
    def load(self) -> Dict[str, Any]:
        """Load and validate configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        if self.config is None:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                self._validate_config()
        
        return self.config
    
    def _validate_config(self) -> None:
        """Validate configuration structure"""
        required_sections = ['preprocessing', 'point_cloud', 'geospatial']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
    
    def get_preprocessing_config(self) -> Dict[str, Any]:
        """Get preprocessing specific configuration"""
        return self.load()['preprocessing']
    
    def get_point_cloud_config(self) -> Dict[str, Any]:
        """Get point cloud specific configuration"""
        return self.load()['point_cloud']
    
    def get_geospatial_config(self) -> Dict[str, Any]:
        """Get geospatial specific configuration"""
        return self.load()['geospatial']
    
    def get_environment_params(self, environment: str) -> Dict[str, Any]:
        """Get environment specific parameters"""
        environments = self.load()['point_cloud']['webodm']['environments']
        if environment not in environments:
            raise ValueError(f"Invalid environment: {environment}")
        return environments[environment]