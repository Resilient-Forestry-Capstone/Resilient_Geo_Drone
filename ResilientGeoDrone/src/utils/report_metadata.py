from pathlib import Path
import json
from typing import Dict, Any

from .logger import LoggerSetup



"""

    Desc: This Module Provides A Report Metadata Class For Extracting
    Benchmark Information From Reports. The Class Utilizes Metadata To
    Extract Benchmark Information And Validate Quality Metrics.

"""
class ReportMetadata:

    """
    
        Desc: Initializes Our Report Metadata With A Report Path (report_path)
        To Load And Extract Metadata From. The Report Path Is Expected To Be
        A Valid Path To A Report File. The Report Must Be A JSON File Of A
        WebODM Report.
    
        Preconditions:
            1. report_path: Path To WebODM Report File
            2. report_path Must Be A Valid Path

        Postconditions:
            1. Set Our Report Path
            2. Load Report Metadata

    """
    def __init__(self, report_path: Path):
        self.logger = LoggerSetup().get_logger()
        self.logger.info(f"Report Metadata ID: {self}  -  Initializing Report Metadata...")
        try:
          self.report_path = report_path
          self.metadata = self._load_metadata()
          self.logger.info(f"Report Metadata ID: {self}  -  Report Metadata Initialized.")
        except Exception as e:
            self.logger.error(f"Report Metadata ID: {self}  -  Report Metadata Initialization Failed: {str(e)}.")
            raise
    

    """
    
        Desc: This Function Loads Report Metadata From A JSON File. The
        Function Returns The Metadata As A Dictionary. The Metadata Is
        Expected To Be In JSON Format.

        Preconditions:
            1. report_path Is Intiialized
        
        Postconditions:
            1. Loads Report Metadata From JSON File
            2. Returns Metadata As A Dictionary
    
    """
    def _load_metadata(self) -> Dict[str, Any]:
        self.logger.info(f"Report Metadata ID: {self}  -  Loading Report Metadata (Parse Or JSON)...")
        # If This Is A JSON File, Load It
        if self.report_path.suffix == '.json':
            with open(self.report_path) as f:
                
                result = json.load(f)
                self.logger.info(f"Report Metadata ID: {self}  -  JSON Report Metadata Loaded.")
                return result
        # Otherwise, Parse Metadata From Report
        else:
            self.logger.info(f"Report Metadata ID: {self}  -  Parsing Report Metadata...")

            result = self._parse_metadata_from_report()

            self.logger.info(f"Report Metadata ID: {self}  -  Report Metadata Parsed.")

            return result
    

    """
    
        Desc: This Function Parses Metadata From A WebODM Report. The
        Function Extracts Benchmark Information Including Ground Sampling
        Distance, Coordinate System, Accuracy Metrics, And Quality Scores.
        The Metadata Is Returned As A Dictionary. The Metadata Is Extracted
        From A WebODM Report.

        Preconditions:
            1. metadata Is Intiialized With Values From Parsing Report

        Postconditions:
            1. Parses Metadata From WebODM Report
            2. Returns Metadata As A Dictionary,
    
    """
    def get_benchmark_data(self) -> Dict[str, Any]:
        self.logger.info(f"Report Metadata ID: {self}  -  Extracting Benchmark Data...")
        try:
          result = {
              'ground_sampling_distance': self.metadata.get('gsd', None),
              'coordinate_system': self.metadata.get('crs', None),
              'accuracy_metrics': self.metadata.get('accuracy', {}),
              'quality_scores': self.metadata.get('quality', {})
          }
          self.logger.info(f"Report Metadata ID: {self}  -  Benchmark Data Extracted.")
          return result
        except Exception as e:
            self.logger.error(f"Report Metadata ID: {self}  -  Failed To Extract Benchmark Data: {str(e)}.")
            return {}


    """
    
        Desc: This Function Goes Through Our Quality Metadata
        And Ensures They Meet Our Quality Requirements. The Requirements
        Include Minimum Ground Sampling Distance, Minimum Coverage, And
        Maximum Root Mean Square Error. The Function Returns A Boolean Dictionary
        With Checks For Each Requirement.

    
    """
    def validate_quality_metrics(self) -> Dict[str, bool]:
        self.logger.info(f"Report Metadata ID: {self}  -  Validating Quality Metrics...")
        try:
          # Get Quality Metrics From Metadata
          quality = self.metadata.get('quality', {})

          # Quality Requirements
          requirements = {
              'min_gsd': 0.05,
              'min_coverage': 0.95,
              'max_rmse': 0.10
          }

          result = {
              'gsd_check': quality.get('gsd', float('inf')) <= requirements['min_gsd'],
              'coverage_check': quality.get('coverage', 0) >= requirements['min_coverage'],
              'accuracy_check': quality.get('rmse', float('inf')) <= requirements['max_rmse']
          }
          self.logger.info(f"Report Metadata ID: {self}  -  Quality Metrics Valid.")
          # Check Quality Metrics Against Requirements And Return Boolean Dictionary
          return result
        except Exception as e:
            self.logger.error(f"Report Metadata ID: {self}  -  Quality Metrics Validation Failed: {str(e)}.")
            return {}