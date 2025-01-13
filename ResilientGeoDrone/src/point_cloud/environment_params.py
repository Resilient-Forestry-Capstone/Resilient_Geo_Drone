from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class EnvironmentConfig:
    """Environment-specific WebODM parameters"""
    feature_quality: str
    min_num_features: int
    matcher_type: str
    point_cloud_quality: str
    mesh_quality: str
    max_concurrency: Optional[int] = None
    auto_boundary: bool = True
    use_3dmesh: bool = True
    ignore_gsd: bool = False

    @classmethod
    def get_environment(cls, env_type: str) -> 'EnvironmentConfig':
        """Get environment configuration by type"""
        configs = {
            'sunny': cls(
                feature_quality='ultra',
                min_num_features=8000,
                matcher_type='bfmatcher',
                point_cloud_quality='high',
                mesh_quality='high',
                max_concurrency=4
            ),
            'rainy': cls(
                feature_quality='high',
                min_num_features=6000,
                matcher_type='flann',
                point_cloud_quality='medium',
                mesh_quality='medium',
                max_concurrency=2
            ),
            'foggy': cls(
                feature_quality='medium',
                min_num_features=4000,
                matcher_type='flann',
                point_cloud_quality='low',
                mesh_quality='low',
                max_concurrency=1,
                ignore_gsd=True
            )
        }
        if env_type not in configs:
            raise ValueError(f"Invalid environment type: {env_type}. Supported types: {list(configs.keys())}")
        return configs[env_type]

    def to_webodm_options(self) -> Dict[str, Any]:
        """Convert to WebODM API options"""
        options = {
            'feature-quality': self.feature_quality,
            'matcher-type': self.matcher_type,
            'min-num-features': self.min_num_features,
            'pc-quality': self.point_cloud_quality,
            'mesh-size': self.mesh_quality,
            'use-3dmesh': self.use_3dmesh,
            'mesh-octree-depth': 10,
            'pc-filter': 2,
            'pc-geometric': True,
            'auto-boundary': self.auto_boundary,
            'ignore-gsd': self.ignore_gsd
        }
        
        if self.max_concurrency:
            options['max-concurrency'] = self.max_concurrency
            
        return options

    def validate(self) -> bool:
        """Validate environment configuration"""
        valid_qualities = ['ultra', 'high', 'medium', 'low']
        valid_matchers = ['bfmatcher', 'flann']
        
        return (
            self.feature_quality in valid_qualities and
            self.point_cloud_quality in valid_qualities and
            self.mesh_quality in valid_qualities and
            self.matcher_type in valid_matchers and
            self.min_num_features > 0
        )

    def __str__(self) -> str:
        """String representation of environment configuration"""
        return (f"Environment Config: {{\n"
                f"  Feature Quality: {self.feature_quality}\n"
                f"  Point Cloud Quality: {self.point_cloud_quality}\n"
                f"  Mesh Quality: {self.mesh_quality}\n"
                f"  Matcher Type: {self.matcher_type}\n"
                f"  Min Features: {self.min_num_features}\n}}")