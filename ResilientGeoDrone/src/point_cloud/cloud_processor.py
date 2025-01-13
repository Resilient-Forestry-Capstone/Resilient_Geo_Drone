from pathlib import Path
from typing import Dict, Any
import numpy as np
import rasterio
from ..utils.logger import LoggerSetup
from ..utils.surface_model_parser import SurfaceModelParser

class CloudProcessor:
    """Process WebODM outputs and generate analysis"""
    
    def __init__(self, config_loader):
        self.logger = LoggerSetup(__name__).get_logger()
        self.config = config_loader.get_point_cloud_config()
        self.surface_parser = SurfaceModelParser(config_loader)
        
    def process_webodm_results(self, webodm_results: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """Process WebODM outputs and generate analysis"""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Process surface models
            dsm_data = self.surface_parser.read_surface_model(Path(webodm_results['dsm']))
            dtm_data = self.surface_parser.read_surface_model(Path(webodm_results['dtm']))
            
            # Calculate Canopy Height Model (CHM)
            chm = self._calculate_chm(dsm_data['elevation'], dtm_data['elevation'])
            
            # Generate analysis results
            return {
                'surface_models': {
                    'dsm': dsm_data,
                    'dtm': dtm_data,
                    'chm': {
                        'elevation': chm,
                        'statistics': self._calculate_statistics(chm)
                    }
                },
                'quality_metrics': self._calculate_quality_metrics(dsm_data, dtm_data),
                'metadata': {
                    'resolution': dsm_data['metadata']['resolution'],
                    'crs': dsm_data['metadata']['crs'],
                    'bounds': dsm_data['metadata']['bounds']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Results processing failed: {str(e)}")
            raise
            
    def _calculate_chm(self, dsm: np.ndarray, dtm: np.ndarray) -> np.ndarray:
        """Calculate Canopy Height Model"""
        return np.subtract(dsm, dtm)
        
    def _calculate_statistics(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate basic statistics for elevation data"""
        return {
            'mean': float(np.mean(data)),
            'std': float(np.std(data)),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'median': float(np.median(data))
        }
        
    def _calculate_quality_metrics(self, dsm_data: Dict[str, Any], 
                                 dtm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality metrics for surface models"""
        return {
            'resolution_check': self._check_resolution(dsm_data, dtm_data),
            'coverage_check': self._check_coverage(dsm_data, dtm_data),
            'noise_metrics': self._calculate_noise_metrics(dsm_data['elevation'])
        }
        
    def _check_resolution(self, dsm_data: Dict[str, Any], 
                         dtm_data: Dict[str, Any]) -> bool:
        """Check if surface models have matching resolution"""
        return dsm_data['metadata']['resolution'] == dtm_data['metadata']['resolution']
        
    def _check_coverage(self, dsm_data: Dict[str, Any], 
                       dtm_data: Dict[str, Any]) -> bool:
        """Check if surface models have matching coverage"""
        return dsm_data['metadata']['bounds'] == dtm_data['metadata']['bounds']
        
    def _calculate_noise_metrics(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate noise metrics for surface model"""
        gradient = np.gradient(data)
        return {
            'roughness': float(np.std(gradient)),
            'noise_ratio': float(np.sum(np.abs(gradient)) / data.size)
        }