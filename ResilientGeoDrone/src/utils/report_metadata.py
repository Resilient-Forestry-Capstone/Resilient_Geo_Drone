from pathlib import Path
import json
from typing import Dict, Any

class ReportMetadata:
    def __init__(self, report_path: Path):
        self.report_path = report_path
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load Report Metadata"""
        if self.report_path.suffix == '.json':
            with open(self.report_path) as f:
                return json.load(f)
        else:
            return self._parse_metadata_from_report()
    
    def get_benchmark_data(self) -> Dict[str, Any]:
        """Extract Benchmark Information"""
        return {
            'ground_sampling_distance': self.metadata.get('gsd', None),
            'coordinate_system': self.metadata.get('crs', None),
            'accuracy_metrics': self.metadata.get('accuracy', {}),
            'quality_scores': self.metadata.get('quality', {})
        }

    def validate_quality_metrics(self) -> Dict[str, bool]:
        """Validate Quality Metrics Against Requirements"""
        quality = self.metadata.get('quality', {})
        requirements = {
            'min_gsd': 0.05,
            'min_coverage': 0.95,
            'max_rmse': 0.10
        }
        return {
            'gsd_check': quality.get('gsd', float('inf')) <= requirements['min_gsd'],
            'coverage_check': quality.get('coverage', 0) >= requirements['min_coverage'],
            'accuracy_check': quality.get('rmse', float('inf')) <= requirements['max_rmse']
        }