import requests
from pathlib import Path
from typing import List, Dict, Any
from .environment_params import EnvironmentConfig
from ..utils.logger import LoggerSetup

class WebODMClient:
    """WebODM interface for environment-specific point cloud generation"""
    
    def __init__(self, config_loader):
        self.logger = LoggerSetup(__name__).get_logger()
        self.config = config_loader.get_point_cloud_config()
        self.base_url = f"http://{self.config['webodm']['host']}:{self.config['webodm']['port']}"
        self.session = requests.Session()

    def generate_point_cloud(self, image_paths: List[Path], environment: str) -> Dict[str, Any]:
        """Generate point cloud with environment-specific parameters"""
        try:
            # Get environment configuration
            env_config = EnvironmentConfig.get_environment(environment)
            if not env_config:
                raise ValueError(f"Invalid environment type: {environment}")

            # Create WebODM project and task
            project_id = self._create_project()
            task_id = self._upload_images(project_id, image_paths)
            
            # Configure and process
            self._configure_task(task_id, env_config)
            results = self._process_task(task_id)
            
            return results

        except Exception as e:
            self.logger.error(f"Point cloud generation failed: {str(e)}")
            raise

    def _create_project(self) -> int:
        """Create new WebODM project"""
        response = self.session.post(f"{self.base_url}/api/projects/")
        response.raise_for_status()
        return response.json()['id']

    def _upload_images(self, project_id: int, image_paths: List[Path]) -> int:
        """Upload images to WebODM"""
        files = [('images', open(str(path), 'rb')) for path in image_paths]
        response = self.session.post(
            f"{self.base_url}/api/projects/{project_id}/tasks/",
            files=files
        )
        response.raise_for_status()
        return response.json()['id']

    def _configure_task(self, task_id: int, env_config: EnvironmentConfig) -> None:
        """Configure task with environment-specific parameters"""
        response = self.session.patch(
            f"{self.base_url}/api/tasks/{task_id}/",
            json=env_config.to_webodm_options()
        )
        response.raise_for_status()

    def _process_task(self, task_id: int) -> Dict[str, Any]:
        """Process task and return results"""
        response = self.session.post(f"{self.base_url}/api/tasks/{task_id}/commit/")
        response.raise_for_status()
        return self._wait_for_completion(task_id)

    def _wait_for_completion(self, task_id: int) -> Dict[str, Any]:
        """Wait for task completion and return results"""
        while True:
            response = self.session.get(f"{self.base_url}/api/tasks/{task_id}/")
            status = response.json()['status']
            
            if status == 'completed':
                return self._get_results(task_id)
            elif status in ['failed', 'canceled']:
                raise Exception(f"Task failed with status: {status}")

    def _get_results(self, task_id: int) -> Dict[str, Any]:
        """Get processing results"""
        return {
            'point_cloud': f"{self.base_url}/api/tasks/{task_id}/download/pointcloud",
            'orthophoto': f"{self.base_url}/api/tasks/{task_id}/download/orthophoto",
            'dsm': f"{self.base_url}/api/tasks/{task_id}/download/dsm",
            'dtm': f"{self.base_url}/api/tasks/{task_id}/download/dtm"
        }