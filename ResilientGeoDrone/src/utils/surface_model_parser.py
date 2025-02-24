import rasterio
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Any
from matplotlib import pyplot as plt



"""

    Desc: This Module Provides A Surface Model Parser Class For Reading
    And Parsing Surface Models. The Class Utilizes Rasterio To Read And
    Parse Surface Models. The Class Also Validates Surface Models Against
    Benchmarks And Generates Difference Maps. The Class Returns Surface
    Model Data As A Dictionary As Well As A Plot Of The Difference Map.

"""
class SurfaceModelParser:

    """
    
        Desc: Initializes Our Surface Model Parser With A Config Loader (config_loader)
        To Load Geospatial Configuration Parameters.

        Preconditions:
            1. config_loader: ConfigLoader Object

        Postconditions:
            1. Load Geospatial Configuration Parameters
    
    """
    def __init__(self, config_loader):
        self.config = config_loader.get_geospatial_config()
        

    """
    
        Desc: This Function Takes In file_path And Reads The Surface Model
        File At The Given Path. The Function Parses The Surface Model File
        Using Rasterio And Extracts Metadata, Elevation Data, Color Scale,
        And Statistics. The Parsed Data Is Returned As A Dictionary.

        Preconditions:
            1. file_path: Path To Surface Model File
            2. file_path Must Be A Valid Path

        Postconditions:
            1. Read And Parse Surface Model File
            2. Returns Surface Model Data As A Dictionary
    
    """
    def read_surface_model(self, file_path: Path) -> Dict[str, Any]:
        # Open Surface Model File Using Rasterio
        with rasterio.open(file_path) as src:
            metadata = {
                'crs': src.crs,
                'transform': src.transform,
                'bounds': src.bounds,
                'resolution': src.res
            }

            # Read Elevation Data
            elevation_data = src.read(1)

            # Extract Color Scale From Image
            color_scale = self._extract_color_scale(src)

            # Calculate Statistics
            return {
                'metadata': metadata,
                'elevation': elevation_data,
                'color_scale': color_scale,
                'statistics': self._calculate_statistics(elevation_data)
            }
    

    """
    
        Desc: This Function Takes In src And Extracts The Color Scale
        From The Image. The Function Checks If The Image Has A Colormap
        And Parses The Colormap To Extract The Color Scale. If The Image
        Does Not Have A Colormap, The Function Calculates The Min And Max
        Elevation Values. The Color Scale Is Returned As A Dictionary.

        Preconditions:
            1. src: Rasterio Dataset Object

        Postconditions:
            1. Extract Color Scale From Image
            2. Returns Color Scale As A Dictionary
    
    """
    def _extract_color_scale(self, src) -> Dict[str, float]:
        # If We Have A Colormap, Parse It
        if 'colormap' in src.tags():
            return self._parse_colormap(src.tags()['colormap'])
        
        # Otherwise, Calculate Min And Max Elevation Values
        data = src.read(1)
        return {
            'min_elevation': float(np.min(data)),
            'max_elevation': float(np.max(data))
        }
    

    """
    
        Desc: This Function Takes In A Surface Model And Parses
        For The Mean Elevation, Standard Deviation, Median, Min,
        And Max Elevation. The Statistics Are Returned As A Dictionary.

        Preconditions:
            1. data: Numpy Array Representing Surface Model Data

        Postconditions:
            1. Calculate Surface Model Statistics
            2. Returns Statistics As A Dictionary
    
    """
    def _calculate_statistics(self, data: np.ndarray) -> Dict[str, float]:
        return {
            'mean_elevation': float(np.mean(data)),
            'std_elevation': float(np.std(data)),
            'median_elevation': float(np.median(data)),
            'min_elevation': float(np.min(data)),
            'max_elevation': float(np.max(data))
        }


    """
    
        Desc: This Function Takes In A model_data As Well As benchmark_path
        And Validates The Surface Model Against A Benchmark. The Function
        Checks The Resolution, Coverage, And Accuracy Of The Surface Model
        Against The Benchmark. The Results Are Returned As A Dictionary.

        Preconditions:
            1. model_data: Dictionary Representing Surface Model Data
            2. benchmark_path: Path To Benchmark File
            3. model_data And benchmark_path Must Be Valid
            4. model_data And benchmark_path Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Validate Surface Model Against Benchmark
            2. Returns Results As A Dictionary
    
    """
    def validate_against_benchmark(self, model_data: Dict[str, Any], benchmark_path: Path) -> Dict[str, bool]:
        with rasterio.open(benchmark_path) as benchmark:
            benchmark_data = benchmark.read(1)
            return {
                'resolution_check': self._check_resolution(model_data, benchmark),
                'coverage_check': self._check_coverage(model_data, benchmark),
                'accuracy_check': self._check_accuracy(model_data['elevation'], benchmark_data)
            }


    """
    
        Desc: This Function Takes In model_data And benchmark_data As Well As
        A output_path And Generates A Difference Map Between The Model And
        Benchmark. The Difference Map Is Saved As A PNG Image In output_path.
    
    """
    def generate_difference_map(self, model_data: np.ndarray, benchmark_data: np.ndarray, output_path: Path) -> None:
        """Generate Difference Map Between Model and Benchmark"""
        difference = model_data - benchmark_data
        plt.figure(figsize=(12, 8))
        plt.imshow(difference, cmap='RdYlBu')
        plt.colorbar(label='Elevation Difference (m)')
        plt.title('Surface Model Difference Map')
        plt.savefig(output_path)
        plt.close()