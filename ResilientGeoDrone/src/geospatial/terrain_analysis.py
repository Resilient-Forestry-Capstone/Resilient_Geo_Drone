import numpy as np
import rasterio
from pathlib import Path
from ..utils.logger import LoggerSetup

class TerrainAnalyzer:
    """Digital Terrain Model Analysis"""
    
    def __init__(self, config_loader):
        self.logger = LoggerSetup(__name__).get_logger()
        self.config = config_loader.get_geospatial_config()
        
    def generate_dtm(self, point_cloud_path: Path) -> np.ndarray:
        """Generate Digital Terrain Model"""
        try:
            with rasterio.open(point_cloud_path) as src:
                return self._process_terrain(src)
        except Exception as e:
            self.logger.error(f"DTM generation failed: {str(e)}")
            raise
            
    def calculate_metrics(self, dtm: np.ndarray) -> dict:
        """Calculate Terrain Metrics"""
        return {
            'mean_elevation': np.mean(dtm),
            'slope': self._calculate_slope(dtm),
            'aspect': self._calculate_aspect(dtm),
            'roughness': self._calculate_roughness(dtm)
        }
        
    def _process_terrain(self, src) -> np.ndarray:
        """Process Terrain Data"""
        data = src.read(1)
        return data
        
    def _calculate_slope(self, dtm: np.ndarray) -> float:
        """Calculate Slope"""
        dy, dx = np.gradient(dtm)
        slope = np.arctan(np.sqrt(dx*dx + dy*dy))
        return float(np.mean(slope))
        
    def _calculate_aspect(self, dtm: np.ndarray) -> float:
        """Calculate Aspect"""
        dy, dx = np.gradient(dtm)
        aspect = np.arctan2(dy, dx)
        return float(np.mean(aspect))
        
    def _calculate_roughness(self, dtm: np.ndarray) -> float:
        """Calculate Surface Roughness"""
        return float(np.std(dtm))