from datetime import datetime
from pathlib import Path
import argparse
import sys
from src.preprocessing.batch_processor import BatchProcessor
from src.point_cloud.webodm_client import WebODMClient
from src.utils.config_loader import ConfigLoader
from src.utils.logger import LoggerSetup
from src.utils.file_handler import FileHandler
from src.front_end.pipeline_worker import PipelineWorker
from src.front_end.client_window import MainClientWindow
from src.front_end.drag_drop_widget import DragDropWidget
from PyQt5.QtWidgets import QApplication
from src.geospatial.gap_detection import GapDetector

from datetime import datetime
from pathlib import Path
import argparse
import sys
from src.preprocessing.batch_processor import BatchProcessor
from src.point_cloud.webodm_client import WebODMClient
from src.utils.config_loader import ConfigLoader
from src.utils.logger import LoggerSetup
from src.utils.file_handler import FileHandler
from src.front_end.pipeline_worker import PipelineWorker
from src.front_end.client_window import MainClientWindow
from src.front_end.drag_drop_widget import DragDropWidget
from PyQt5.QtWidgets import QApplication
from src.geospatial.gap_detection import GapDetector

class Pipeline:
    """Main Pipeline Controller"""
    
    def __init__(self, config_path: str):
        self.logger = LoggerSetup().get_logger()
        self.config_loader = ConfigLoader(config_path)
        self.file_handler = FileHandler(self.config_loader)
        
        # Initialize pipeline components
        self.batch_processor = BatchProcessor(self.config_loader)
        self.webodm_client = WebODMClient(self.config_loader)
        self.gap_delineator = GapDetector(self.config_loader)


    def runPartial(self, input_dir: str, output_dir: str, environment: str, stage: int) -> dict:
        try:
            # Create Output Directories
            dirs = self.file_handler.create_processing_directories(output_dir)

            match stage:
                case 0:
                    # Run Full Pipeline
                    self.logger.info("Running Full Pipeline")
                    self.run(input_dir, output_dir, environment)
                    self.logger.info("Pipeline Completed Successfully")
                case 1:
                    # Start From WebODM
                    self.logger.info("Starting From WebODM")

                    image_paths = self.file_handler.get_image_files(input_dir)
                    
                    agentODM = self.webodm_client.generate_point_cloud(image_paths, environment)
                    if not agentODM:
                        raise ValueError("No valid images found for processing")
                    
                    # Stage 3: Geospatial Analysis
                    self.logger.info("Stage 3: Geospatial Analysis")

                    # Use the WebODM output dir
                    output_dir = self.webodm_client.output_dir
                    gap_areas = self.gap_delineator.process_gaps(output_dir / 'chm.tif')

                    self.logger.info(f"Analysis Result: {gap_areas}")

                case 2:
                    # Stage 3: Geospatial Analysis
                    self.logger.info("Stage 3: Geospatial Analysis")

                    # Always set output_dir using the consistent pattern
                    output_dir = Path(self.config_loader.load()['geospatial']['output_path']) / "output" / "point_cloud" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    gap_areas = self.gap_delineator.process_gaps(output_dir / 'chm.tif') 

                    self.logger.info(f"Analysis Result: {gap_areas} Saved To {output_dir}")
                case _:
                    raise ValueError("Invalid stage specified. Must be 0, 1, or 2.")
                    

        except Exception as e:
            self.logger.error(f"Pipeline Failed: {str(e)}")
            raise


    def runStage(self, input_dir: str, output_dir: str, environment: str, stage: int) -> dict:
        try:
            # Create Output Directories
            dirs = self.file_handler.create_processing_directories(output_dir)

            match stage:
                case 0:
                    # Stage 1: Preprocessing
                    self.logger.info("Stage 1: Image Preprocessing")
                    image_paths = self.file_handler.get_image_files(input_dir)

                    valid_images = self.batch_processor.process_batch(image_paths)['valid']

                    if not valid_images:
                        raise ValueError("No valid images found for processing")
                    self.logger.info(f"Valid Images Found: {len(valid_images)}")
                case 1:
                    # Stage 2: Point Cloud Generation
                    self.logger.info("Stage 2: Point Cloud Generation")

                    image_paths = self.file_handler.get_image_files(input_dir)
                    
                    agentODM = self.webodm_client.generate_point_cloud(image_paths, environment)
                    
                    self.logger.info(f"Point Cloud Generated: {agentODM}")
                case 2:
                    # Stage 3: Geospatial Analysis
                    self.logger.info("Stage 3: Geospatial Analysis")

                    # Always set output_dir using the consistent pattern
                    output_dir = Path(self.config_loader.load()['geospatial']['output_path']) / "output" / "point_cloud" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    gap_areas = self.gap_delineator.process_gaps(output_dir / 'chm.tif')

                    self.logger.info(f"Gap Areas: {gap_areas}")

                    self.logger.info(f"Analysis Result: {gap_areas}")
                case _:
                    raise ValueError("Invalid stage specified. Must be 0, 1, or 2.")

        except Exception as e:
            self.logger.error(f"Pipeline Failed: {str(e)}")
            raise

    def run(self, input_dir: str, output_dir: str, environment: str) -> dict:
        """Execute full pipeline"""
        try:
            # Create output directories
            dirs = self.file_handler.create_processing_directories(output_dir)
            
            # Stage 1: Preprocessing
            self.logger.info("Stage 1: Image Preprocessing")
            image_paths = self.file_handler.get_image_files(input_dir)
            valid_images = self.batch_processor.process_batch(image_paths)['valid']
            
            if not valid_images:
                raise ValueError("No valid images found for processing")
            
            # Stage 2: Point Cloud Generation
            self.logger.info("Stage 2: Point Cloud Generation")
            webodm_results = self.webodm_client.generate_point_cloud(valid_images, environment)
            
            # Process WebODM results
            cloud_results = self.cloud_processor.process_webodm_results(
                webodm_results,
                dirs['point_cloud']
            )
            
            # Stage 3: Geospatial Analysis
            self.logger.info("Stage 3: Geospatial Analysis")
            analysis_result = self.qgis_analyzer.analyze(
                Path(webodm_results['point_cloud']),  # Use direct WebODM output
                dirs['analysis']
            )
            
            # Save results
            final_results = {
                'preprocessing': {
                    'valid_images': len(valid_images),
                    'total_images': len(image_paths)
                },
                'point_cloud': {
                    'webodm_results': webodm_results,
                    'processing_results': cloud_results
                },
                'analysis': analysis_result,
                'environment': environment
            }
            
            self.file_handler.save_results(
                final_results,
                dirs['analysis'] / 'final_results.yaml'
            )
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise

def main():
    
    if True:
        # Initialize The Application
        app = QApplication(sys.argv)

        # Create Our Main Client Window
        window = MainClientWindow()
        window.show()

        # Execute The Application And Wait For Exit
        sys.exit(app.exec_())
    """
    parser = argparse.ArgumentParser(description='Drone Image Processing Pipeline')
    parser.add_argument('--input', '-i', required=True, help='Input directory')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    parser.add_argument('--config', '-c', default='config/config.yaml',
                       help='Configuration file path')
    parser.add_argument('--env', '-e', default='sunny',
                       choices=['sunny', 'rainy', 'foggy'],
                       help='Environmental conditions')
    parser.add_argument('--stage', '-s', default=0, type=int,
                       help='Stage to run (0: Preprocessing, 1: Point Cloud Generation, 2: Geospatial Analysis)')
    parser.add_argument('--partial', '-p', default=False, type=bool,
                       help='Run partial (one part onward) pipeline (default: False)')

    args = parser.parse_args()
    
    try:
        pipeline = Pipeline(args.config)
        results = pipeline.run(args.input, args.output, args.env)
        print(f"Pipeline completed successfully. Results saved to: {args.output}")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
    """
if __name__ == "__main__":
    main()