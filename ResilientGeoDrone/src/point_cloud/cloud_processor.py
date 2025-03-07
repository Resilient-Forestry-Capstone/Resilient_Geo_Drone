from pathlib import Path
from typing import Dict, Any
import numpy as np
import rasterio
from ..utils.logger import LoggerSetup
from ..utils.surface_model_parser import SurfaceModelParser



"""

    Desc: This Module Provides A Quick Point-Cloud Processor For Generating
    Data Analytics From Point-Clouds Including Surface Models, Canopy Height
    Models, And Quality Metrics. The Module Utilizes A Surface Model Parser
    To Read Surface Models And Calculate Metrics.

"""
class CloudProcessor:
    
    """
    
        Desc: Initializes Our Cloud Processor With A Config Loader (config_loader)
        To Load Point-Cloud Configuration Parameters. It Also Initializes Our
        Surface Model Parser (surface_parser). As Well As The Logger We Are Writing
        To.

        Preconditions:
            1. config_loader: ConfigLoader Object
        
        Postconditions:
            1. Set Our logger 
            2. Load Point-Cloud Configuration Parameters
            3. Initialize Surface Model Parser
    
    """
    def __init__(self, config_loader):
        self.logger = LoggerSetup().get_logger()
        try:
          self.logger.info(f"Cloud Processor ID: {self}  -  Initializing Cloud Processor...")
          self.config = config_loader.get_point_cloud_config()
          self.surface_parser = SurfaceModelParser(config_loader)
          self.logger.info(f"CloudProcessor ID: {self}  -  Cloud Processor Initialized.")
        except Exception as e:
            self.logger.error(f"CloudProcessor ID: {self}  -  Cloud Processor Initialization Failed: {str(e)}.")
            raise
        

    """
    
        Desc: This Function Takes In webodm_results And output_dir And
        Processes The WebODM Outputs To Generate Analysis. The Analysis
        Includes Surface Models, Canopy Height Models, And Quality Metrics.
        The Function Returns The Analysis Results As A Dictionary.

        Preconditions:
            1. webodm_results: Dictionary Of WebODM Outputs
            2. output_dir: Path To Output Directory
            3. webodm_results And output_dir Must Be Valid
        
        Postconditions:
            1. Processes WebODM Outputs To Generate Analysis
            2. Returns Analysis Results As A Dictionary
    
    """
    def process_webodm_results(self, webodm_results: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        try:
            self.logger.info(f"Cloud Processor ID: {self}  -  Processing WebODM Results...")
            # Create Our Output Directory If It Does Not Exist
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Process Our Surface Models For Digital Surface Model (dsm_data) And Digital Terrain Model (dtm_data)
            dsm_data = self.surface_parser.read_surface_model(Path(webodm_results['dsm']))
            dtm_data = self.surface_parser.read_surface_model(Path(webodm_results['dtm']))
            
            # Calculate Canopy Height Model (CHM) From dsm_data And dtm_data
            chm = self._calculate_chm(dsm_data['elevation'], dtm_data['elevation'])
            
            result = {
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

            self.logger.info(f"Cloud Processor ID: {self}  -  WebODM Results Processed.")

            # Return Our Analysis Results As A Dictionary
            return result
        # Catch Any Exceptions And Log The Error   
        except Exception as e:
            self.logger.error(f"Cloud Processor ID: {self}  -  Results Processing Failed: {str(e)}.")
            raise


    """
    
        Desc: This Function Takes In dsm And dtm As Numpy Arrays And
        Calculates The Canopy Height Model (chm) By Subtracting The
        Digital Terrain Model (dtm) From The Digital Surface Model (dsm).
        The chm Is Returned As A Numpy Array.

        Preconditions:
            1. dsm: Numpy Array Representing Digital Surface Model
            2. dtm: Numpy Array Representing Digital Terrain Model
            3. dsm And dtm Must Be Valid Surface Models
            4. dsm And dtm Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Calculates Canopy Height Model (chm)
            2. Returns chm As Numpy Array
    
    """      
    def _calculate_chm(self, dsm: np.ndarray, dtm: np.ndarray) -> np.ndarray:
        try:
          self.logger.info(f"Cloud Processor ID: {self}  -  Calculating Canopy Height Model (CHM)...")
          result = np.subtract(dsm, dtm)
          self.logger.info(f"Cloud Processor ID: {self}  -  Canopy Height Model (CHM) Calculated.")
          # Subtract The Digital Terrain Model (DTM) From The Digital Surface Model (DSM) For CHM
          return result
        except Exception as e:
            self.logger.error(f"Cloud Processor ID: {self}  -  Failed To Calculate Canopy Height Model (CHM): {str(e)}.")
            raise
        

    """
    
        Desc: This Function Takes In data And Calculates Basic Statistics
        For Elevation Data. The Statistics Include Mean, Standard Deviation,
        Min, Max, And Median. The Statistics Are Returned As A Dictionary.

        Preconditions:
            1. data: Numpy Array Representing Elevation Data

        Postconditions:
            1. Calculates Basic Statistics For Elevation Data
            2. Returns Statistics As A Dictionary
    
    """
    def _calculate_statistics(self, data: np.ndarray) -> Dict[str, float]:
        
        try:
          self.logger.info(f"Cloud Processor ID: {self}  -  Calculating Statistics...")
          result = {
              'mean': float(np.mean(data)),
              'std': float(np.std(data)),
              'min': float(np.min(data)),
              'max': float(np.max(data)),
              'median': float(np.median(data))
          }

          self.logger.info(f"Cloud Processor ID: {self}  -  Statistics Calculated.")
          return result
        except Exception as e:
            self.logger.error(f"Cloud Processor ID: {self}  -  Failed To Calculate Statistics: {str(e)}.")
            raise
        

    """
    
        Desc: This Function Takes In dsm_data And dtm_data And Calculates
        Quality Metrics For Surface Models. The Quality Metrics Include
        Resolution Check, Coverage Check, And Noise Metrics. The Metrics
        Are Returned As A Dictionary.

        Preconditions:
            1. dsm_data: Dictionary Representing Digital Surface Model Data
            2. dtm_data: Dictionary Representing Digital Terrain Model Data
            3. dsm_data And dtm_data Must Be Valid Surface Models
            4. dsm_data And dtm_data Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Calculates Quality Metrics For Surface Models
            2. Returns Metrics As A Dictionary
    
    """
    def _calculate_quality_metrics(self, dsm_data: Dict[str, Any], 
                                 dtm_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
          self.logger.info(f"Cloud Processor ID: {self}  -  Calculating Quality Metrics...")
          result = self._calculate_metrics(dsm_data, dtm_data)
          self.logger.info(f"Cloud Processor ID: {self}  -  Quality Metrics Calculated.")
          return result
        except Exception as e:
            self.logger.error(f"Cloud Processor ID: {self}  -  Failed To Calculate Quality Metrics: {str(e)}.")
            raise
        

    """
    
        Desc: This Function Takes In dsm_data And dtm_data And Checks
        If The Surface Models Have Matching Resolution. The Function
        Returns True If The Resolution Matches And False Otherwise.

        Preconditions:
            1. dsm_data: Dictionary Representing Digital Surface Model Data
            2. dtm_data: Dictionary Representing Digital Terrain Model Data
            3. dsm_data And dtm_data Must Be Valid Surface Models
            4. dsm_data And dtm_data Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Checks If Surface Models Have Matching Resolution
            2. Returns True If Resolution Matches And False Otherwise
    
    """
    def _check_resolution(self, dsm_data: Dict[str, Any], 
                         dtm_data: Dict[str, Any]) -> bool:
        self.logger.info(f"Cloud Processor ID: {self}  -  Checking Resolution...")
        
        result = dsm_data['metadata']['resolution'] == dtm_data['metadata']['resolution']

        self.logger.info(f"Cloud Processor ID: {self}  -  Resolution Check Complete, Result Is {result}.")

        # Check If The Resolution Of The dsm_data And dtm_data Are The Same
        return result
        

    """
    
        Desc: This Function Takes In dsm_data And dtm_data And Checks
        If The Surface Models Have Matching Coverage. The Function
        Returns True If The Coverage Matches And False Otherwise.
        This Is To Ensure That The DSM And DTM Are Of The Same Area.

        Preconditions:
            1. dsm_data: Dictionary Representing Digital Surface Model Data
            2. dtm_data: Dictionary Representing Digital Terrain Model Data
            3. dsm_data And dtm_data Must Be Valid Surface Models
            4. dsm_data And dtm_data Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Checks If Surface Models Have Matching Coverage
            2. Returns True If Coverage Matches And False Otherwise
    
    """
    def _check_coverage(self, dsm_data: Dict[str, Any], 
                       dtm_data: Dict[str, Any]) -> bool:
        self.logger.info(f"Cloud Processor ID: {self}  -  Checking Coverage...")

        # Check If The Bounds Of The dsm_data And dtm_data Are The Same
        result = dsm_data['metadata']['bounds'] == dtm_data['metadata']['bounds']

        self.logger.info(f"Cloud Processor ID: {self}  -  Coverage Check Complete, Result Is {result}.")
        return result
        

    """
    
        Desc: This Function Takes In data And Calculates Noise Metrics
        For Surface Model. The Noise Metrics Include Roughness And Noise
        Ratio. The Metrics Are Returned As A Dictionary.

        Preconditions:
            1. data: Numpy Array Representing Surface Model Data

        Postconditions:
            1. Calculates Noise Metrics For Surface Model
            2. Returns Metrics As A Dictionary
    
    """
    def _calculate_noise_metrics(self, data: np.ndarray) -> Dict[str, float]:
        try:
          self.logger.info(f"Cloud Processor ID: {self}  -  Calculating Noise Metrics...")
          # Calculate The Gradient Of The Surface Model Data
          gradient = np.gradient(data)

          result = {
              'roughness': float(np.std(gradient)),
              'noise_ratio': float(np.sum(np.abs(gradient)) / data.size)
          } 

          self.logger.info(f"Cloud Processor ID: {self}  -  Noise Metrics Calculated.")

          return result
        except Exception as e:
            self.logger.error(f"Cloud Processor ID: {self}  -  Failed To Calculate Noise Metrics: {str(e)}.")
            raise