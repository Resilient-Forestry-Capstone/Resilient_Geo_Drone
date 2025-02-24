import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from ResilientGeoDrone.src.point_cloud import cloud_processor  
from ResilientGeoDrone.src.point_cloud import webodm_client
from ResilientGeoDrone.src.point_cloud import environment_params
from ResilientGeoDrone.src.utils.config_loader import ConfigLoader



class PointCloudProcessor:

    def __init__(self, config_loader):
        self.cloud_processor = cloud_processor.CloudProcessor(config_loader)
        self.webodm_client = webodm_client.WebODMClient(config_loader)
        self.environment_params = environment_params.EnvironmentConfig


    def process_images(self, image_path: str, environment: str):
        """Process a single set of images"""
        return self.webodm_client.generate_point_cloud(image_path, environment)


    def test_connection(self):
        """Test WebODM connection"""
        return self.processor._test_connection()


def debug_point_cloud(image_path: str, environment: str = 'sunny'):
    """Test point cloud generation"""
    config_loader = ConfigLoader(r"C:\Users\bensp\OneDrive\Desktop\Code Box Two\Python\GeoDrone\ResilientRepo\Resilient_Geo_Drone\ResilientGeoDrone\config\config.yaml")
    processor = PointCloudProcessor(config_loader)
    return processor.process_images(image_path, environment)


def debug_connection():
    """Test WebODM connection"""
    config_loader = ConfigLoader()
    processor = PointCloudProcessor(config_loader)
    return processor.test_connection()


def main():
    # Example usage
    imageSet_Path = r"C:\Users\bensp\Downloads\101MEDIA"

    imagesBundle = []
    for each in Path(imageSet_Path).iterdir():
        imagesBundle.append(Path(each))
    
    # Can run individual functions:
    # connection_status = debug_connection()
    # print(f"Connection status: {connection_status}")
    
    # Or process images:
    results = debug_point_cloud(imagesBundle)
    print(f"Processing results: {results}")



if __name__ == "__main__":
    main()