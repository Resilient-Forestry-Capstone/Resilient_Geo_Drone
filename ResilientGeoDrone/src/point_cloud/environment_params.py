from dataclasses import dataclass
from typing import Dict, Any, List, Optional



"""

    Desc: A Data Structure To Store Environment-Specific WebODM Parameters
    For Point Cloud Generation. The Parameters Include Feature Quality,
    Minimum Number Of Features, Matcher Type, Point Cloud Quality, Mesh
    Quality, Maximum Concurrency, Auto Boundary, Use 3D Mesh, And Ignore GSD.

    Attributes:
        feature_quality: Quality Of Features Detected In Images
        min_num_features: Minimum Number Of Features Required
        matcher_type: Type Of Matcher To Use
        point_cloud_quality: Quality Of Point Cloud Generated
        mesh_quality: Quality Of Mesh Generated
        max_concurrency: Maximum Number Of Concurrent Tasks
        auto_boundary: Automatically Detect Boundary
        use_3dmesh: Use 3D Mesh
        ignore_gsd: Ignore GSD   

"""
@dataclass
class EnvironmentConfig:

    feature_quality: str
    min_num_features: int
    matcher_type: str
    point_cloud_quality: str
    mesh_quality: str
    max_concurrency: Optional[int] = None
    auto_boundary: bool = True
    use_3dmesh: bool = True
    ignore_gsd: bool = False


    """
    
        Desc: Get Environment Configuration By Type From A Predefined Set
        Of Environment Configurations. The Types Include Sunny, Rainy, And
        Foggy. The Configurations Are Stored In A Dictionary. If The Type
        Is Not Found, An Error Is Raised.

        Preconditions:
            1. env_type: Type Of Environment Configuration
            2. env_type Must Be One Of Sunny, Rainy, Or Foggy

        Postconditions:
            1. Get Environment Configuration By Type
            2. Return Environment Configuration
    
    """
    @classmethod
    def get_environment(cls, env_type: str) -> 'EnvironmentConfig':
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

        # Check If Environment Type Is Valid
        if env_type not in configs:
            raise ValueError(f"Invalid environment type: {env_type}. Supported types: {list(configs.keys())}")
        return configs[env_type]


    """
    
        Desc: Convert Environment Configuration To WebODM API Options
        For Point Cloud Generation. The Options Include Feature Quality,
        Matcher Type, Minimum Number Of Features, Point Cloud Quality,
        Mesh Quality, Use 3D Mesh, Mesh Octree Depth, Point Cloud Filter,
        Point Cloud Geometric, Maximum Concurrency, Auto Boundary, And
        Ignore GSD. The Options Are Returned As A Dictionary.

        Preconditions:
            1. All Members Are Initialized With Valid Values

        Postconditions:
            1. Convert To WebODM API Options
            2. Return Options As A Dictionary
    
    """
    def to_webodm_options(self):
        """Convert environment config to WebODM options format"""
        options = [
            {"name": "feature-quality", "value": self.feature_quality},
            {"name": "matcher-type", "value": self.matcher_type},
            {"name": "min-num-features", "value": self.min_num_features},
            {"name": "pc-quality", "value": self.point_cloud_quality},
            {"name": "mesh-size", "value": self.mesh_quality},
            {"name": "use-3dmesh", "value": self.use_3dmesh},
            {"name": "dsm", "value": True},  # Explicitly enable DSM
            {"name": "dtm", "value": True},  # Explicitly enable DTM
            {"name": "auto-boundary", "value": self.auto_boundary},
            {"name": "ignore-gsd", "value": self.ignore_gsd},
        ]
        
        # Add Maximum Concurrency If Specified
        if self.max_concurrency:
            options.append({"name": "max-concurrency", "value": self.max_concurrency})
            
        return options


    """
    
        Desc: Validate Environment Configuration To Ensure All Members
        Are Initialized With Valid Values. The Valid Values Include Quality
        Levels, Matcher Types, And Minimum Number Of Features. The Function
        Returns True If The Configuration Is Valid And False Otherwise.

        Preconditions:
            1. All Members Are Initialized

        Postconditions:
            1. Validate Environment Configuration
            2. Return True If Configuration Is Valid And False Otherwise

    """
    def validate(self) -> bool:
        # Valid Quality Levels And Matcher Types
        valid_qualities = ['ultra', 'high', 'medium', 'low']
        valid_matchers = ['bfmatcher', 'flann']
        
        # Check If All Members Are Valid
        return (
            self.feature_quality in valid_qualities and
            self.point_cloud_quality in valid_qualities and
            self.mesh_quality in valid_qualities and
            self.matcher_type in valid_matchers and
            self.min_num_features > 0
        )


    """
    
        Desc: String Representation Of Environment Configuration.

        Preconditions:
            1. All Members Are Initialized

        Postconditions:
            1. Return String Representation Of Environment Configuration

    """
    def __str__(self) -> str:
        return (f"Environment Config: {{\n"
                f"  Feature Quality: {self.feature_quality}\n"
                f"  Point Cloud Quality: {self.point_cloud_quality}\n"
                f"  Mesh Quality: {self.mesh_quality}\n"
                f"  Matcher Type: {self.matcher_type}\n"
                f"  Min Features: {self.min_num_features}\n}}")