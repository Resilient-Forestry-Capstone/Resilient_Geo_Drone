import rasterio
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Any
from matplotlib import pyplot as plt

class SurfaceModelParser:
    def __init__(self, config_loader):
        self.config = config_loader.get_geospatial_config()
        
    def read_surface_model(self, file_path: Path) -> Dict[str, Any]:
        """Read and Parse Surface Model File"""
        with rasterio.open(file_path) as src:
            metadata = {
                'crs': src.crs,
                'transform': src.transform,
                'bounds': src.bounds,
                'resolution': src.res
            }
            elevation_data = src.read(1)
            color_scale = self._extract_color_scale(src)
            return {
                'metadata': metadata,
                'elevation': elevation_data,
                'color_scale': color_scale,
                'statistics': self._calculate_statistics(elevation_data)
            }
    
    def _extract_color_scale(self, src) -> Dict[str, float]:
        """Extract Color Scale from Image"""
        if 'colormap' in src.tags():
            return self._parse_colormap(src.tags()['colormap'])
        data = src.read(1)
        return {
            'min_elevation': float(np.min(data)),
            'max_elevation': float(np.max(data))
        }
    
    def _calculate_statistics(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate Surface Model Statistics"""
        return {
            'mean_elevation': float(np.mean(data)),
            'std_elevation': float(np.std(data)),
            'median_elevation': float(np.median(data)),
            'min_elevation': float(np.min(data)),
            'max_elevation': float(np.max(data))
        }

    def validate_against_benchmark(self, model_data: Dict[str, Any], benchmark_path: Path) -> Dict[str, bool]:
        """Validate Surface Model Against Benchmark"""
        with rasterio.open(benchmark_path) as benchmark:
            benchmark_data = benchmark.read(1)
            return {
                'resolution_check': self._check_resolution(model_data, benchmark),
                'coverage_check': self._check_coverage(model_data, benchmark),
                'accuracy_check': self._check_accuracy(model_data['elevation'], benchmark_data)
            }

    def generate_difference_map(self, model_data: np.ndarray, benchmark_data: np.ndarray, output_path: Path) -> None:
        """Generate Difference Map Between Model and Benchmark"""
        difference = model_data - benchmark_data
        plt.figure(figsize=(12, 8))
        plt.imshow(difference, cmap='RdYlBu')
        plt.colorbar(label='Elevation Difference (m)')
        plt.title('Surface Model Difference Map')
        plt.savefig(output_path)
        plt.close()