import qgis.core as qgis
from pathlib import Path
from .canopy_analysis import CanopyAnalyzer
from .terrain_analysis import TerrainAnalyzer
from ..utils.logger import LoggerSetup

class QGISAnalyzer:
    """QGIS Integration and Analysis Controller"""
    
    def __init__(self, config_loader):
        self.logger = LoggerSetup(__name__).get_logger()
        self.config = config_loader.get_geospatial_config()
        self.canopy_analyzer = CanopyAnalyzer(config_loader)
        self.terrain_analyzer = TerrainAnalyzer(config_loader)
        
        # Initialize QGIS
        qgis.QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.40.1", True)
        self.qgs = qgis.QgsApplication([], False)
        self.qgs.initQgis()
        
    def analyze(self, point_cloud_path: Path, output_dir: Path) -> dict:
        """Execute Full Geospatial Analysis"""
        try:
            # Generate canopy height model
            chm = self.canopy_analyzer.generate_chm(point_cloud_path)
            
            # Generate terrain model
            dtm = self.terrain_analyzer.generate_dtm(point_cloud_path)
            
            # Analyze results
            results = {
                'canopy_metrics': self.canopy_analyzer.calculate_metrics(chm),
                'terrain_metrics': self.terrain_analyzer.calculate_metrics(dtm)
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise
            
        finally:
             self.qgs.exitQgis()