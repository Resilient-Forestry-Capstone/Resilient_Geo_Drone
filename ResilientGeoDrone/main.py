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

class Pipeline:
    """Main Pipeline Controller"""
    
    def __init__(self, config_path: str):
        self.logger = LoggerSetup().get_logger()
        self.config_loader = ConfigLoader(config_path)
        self.file_handler = FileHandler(self.config_loader)
        
        # Initialize pipeline components
        self.batch_processor = BatchProcessor(self.config_loader)
        self.webodm_client = WebODMClient(self.config_loader)
        
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