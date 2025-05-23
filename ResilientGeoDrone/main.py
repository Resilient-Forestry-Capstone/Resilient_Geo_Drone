from datetime import datetime
from pathlib import Path
import argparse
import sys

# Core
from src.utils.config_loader import ConfigLoader
from src.utils.logger import LoggerSetup
from src.utils.file_handler import FileHandler

# Processing
from src.preprocessing.batch_processor import BatchProcessor
from src.point_cloud.webodm_client import WebODMClient
from src.geospatial.gap_detection import GapDetector

# GUI
from PyQt5.QtWidgets import QApplication
from src.front_end.client_window import MainClientWindow


def run_preprocessing(config_path, input_dir, output_dir):
    logger = LoggerSetup().get_logger()
    logger.info("Running preprocessing stage")
    
    config_loader = ConfigLoader(config_path)
    file_handler = FileHandler(config_loader)
    batch_processor = BatchProcessor(config_loader)
    
    # Create output directory
    dirs = file_handler.create_processing_directories(output_dir)
    
    # Get and process images
    image_paths = file_handler.get_image_files(input_dir)
    result = batch_processor.process_batch(image_paths)
    
    logger.info(f"Preprocessing complete. Valid images: {len(result['valid'])}/{len(image_paths)}")
    return result


def run_webodm(config_path, input_dir, output_dir, environment='sunny'):
    logger = LoggerSetup().get_logger()
    logger.info("Running WebODM point cloud generation")
    
    # First get valid images through preprocessing
    preprocess_result = run_preprocessing(config_path, input_dir, output_dir)
    valid_images = preprocess_result['valid']
    
    if not valid_images:
        logger.error("No valid images to process")
        return None
    
    # Run WebODM processing
    config_loader = ConfigLoader(config_path)
    webodm_client = WebODMClient(config_loader)
    result = webodm_client.generate_point_cloud(valid_images, environment)
    
    logger.info(f"WebODM processing complete. Output in {webodm_client.output_dir}")
    return result


def create_chm(config_path, dsm_path, dtm_path, output_path=None):
    logger = LoggerSetup().get_logger()
    logger.info(f"Creating Canopy Height Model from {dsm_path} and {dtm_path}")
    
    config_loader = ConfigLoader(config_path)
    webodm_client = WebODMClient(config_loader)
    
    # If output_path is None, create a default timestamped path
    if not output_path:
        output_dir = Path(config_loader.load()['geospatial']['output_path']) / "output" / "point_cloud" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_dir.mkdir(parents=True, exist_ok=True)
        webodm_client.output_dir = output_dir
    else:
        webodm_client.output_dir = Path(output_path)
    
    # Generate CHM
    chm_path = webodm_client.create_chm(Path(dsm_path), Path(dtm_path))
    
    logger.info(f"CHM created successfully at {chm_path}")
    return str(chm_path)


def run_gap_detection(config_path, chm_path, output_dir=None):
    logger = LoggerSetup().get_logger()
    logger.info("Running gap detection analysis")
    
    config_loader = ConfigLoader(config_path)
    gap_detector = GapDetector(config_loader)
    
    # If no output dir specified, create one based on current time
    if not output_dir:
        output_dir = "./"
    
    # Run gap detection
    result = gap_detector.process_gaps(chm_path, output_dir)
    
    logger.info(f"Gap detection complete. Found {len(result)} gaps.")
    return result


def run_full_pipeline(config_path, input_dir, output_dir, environment='sunny'):
    logger = LoggerSetup().get_logger()
    logger.info("Running full pipeline")
    
    # Run WebODM (which includes preprocessing)
    webodm_result = run_webodm(config_path, input_dir, output_dir, environment)
    
    if not webodm_result:
        logger.error("WebODM processing failed")
        return None
    
    # Run gap detection on the generated CHM
    webodm_output_dir = Path(webodm_result['output_dir'])
    chm_path = webodm_output_dir / "chm.tif"
    
    if not chm_path.exists():
        logger.error(f"CHM file not found at {chm_path}")
        return None
    
    gap_results = run_gap_detection(config_path, chm_path, 
                                    Path(output_dir) / "analysis")
    
    logger.info("Full pipeline completed successfully")
    return {
        'webodm_results': webodm_result,
        'gap_results': gap_results
    }


def run_gui_mode():
    app = QApplication(sys.argv)
    window = MainClientWindow()
    window.show()
    return app.exec_()


def main():
    parser = argparse.ArgumentParser(
        description='ResilientGeoDrone - UAV Image Processing Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
              # Run with GUI
              python main.py --gui
              
              # Run full pipeline in CLI mode
              python main.py --input ./data/raw/images --output ./data/output --env sunny
              
              # Run individual stages
              python main.py --preprocess --input ./data/raw/images --output ./data/processed
              python main.py --webodm --input ./data/processed --output ./data/point_cloud
              python main.py --gap-detection --chm-path ./data/point_cloud/chm.tif --output ./data/analysis
              
              # Create a CHM from DSM and DTM files
              python main.py --create-chm --dsm-path ./data/dsm.tif --dtm-path ./data/dtm.tif --output ./data/chm.tif
                    """
    )
    
    # Mode Selection
    mode_group = parser.add_argument_group('Mode Selection')
    mode_group.add_argument('--gui', action='store_true', help='Run in GUI mode (default if no other mode specified)')
    
    # CLI 
    stage_group = parser.add_argument_group('Pipeline Stage Selection')
    stage_group.add_argument('--preprocess', action='store_true', help='Run image preprocessing only')
    stage_group.add_argument('--webodm', action='store_true', help='Run WebODM point cloud generation (includes preprocessing)')
    stage_group.add_argument('--gap-detection', action='store_true', help='Run gap detection analysis only')
    stage_group.add_argument('--create-chm', action='store_true', help='Create Canopy Height Model from DSM and DTM')
    stage_group.add_argument('--full-pipeline', action='store_true', help='Run full pipeline (default CLI mode)')
    
    # Common Params.
    param_group = parser.add_argument_group('Parameters')
    param_group.add_argument('--config', '-c', default=(Path(__file__).parent / "config/config.yaml"), help='Configuration file path')
    param_group.add_argument('--input', '-i', help='Input directory with images')
    param_group.add_argument('--output', '-o', help='Output directory for results')
    param_group.add_argument('--env', '-e', default='sunny', choices=['sunny', 'rainy', 'foggy', 'night'], 
                       help='Environmental conditions for WebODM processing')
    param_group.add_argument('--chm-path', help='Path to CHM file for gap detection')
    param_group.add_argument('--dsm-path', help='Path to DSM file for CHM creation')
    param_group.add_argument('--dtm-path', help='Path to DTM file for CHM creation')
    
    args = parser.parse_args()
    
    use_gui = args.gui or not any([args.preprocess, args.webodm, args.gap_detection, 
                                  args.full_pipeline, args.create_chm])
    
    if use_gui:
        return run_gui_mode()

    try:
        if args.preprocess:
            if not args.input or not args.output:
                parser.error("--preprocess requires --input and --output")
            run_preprocessing(args.config, args.input, args.output)
            
        elif args.webodm:
            if not args.input or not args.output:
                parser.error("--webodm requires --input and --output")
            run_webodm(args.config, args.input, args.output, args.env)
            
        elif args.gap_detection:
            if not args.chm_path:
                parser.error("--gap-detection requires --chm-path")
            run_gap_detection(args.config, args.chm_path, args.output)
            
        elif args.create_chm:
            if not args.dsm_path or not args.dtm_path:
                parser.error("--create-chm requires --dsm-path and --dtm-path")
            chm_path = create_chm(args.config, args.dsm_path, args.dtm_path, args.output)
            print(f"CHM created successfully at: {chm_path}")
            
        else: 
            if not args.input or not args.output:
                parser.error("Full pipeline requires --input and --output")
            run_full_pipeline(args.config, args.input, args.output, args.env)
            
        print("Operation completed successfully")
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
