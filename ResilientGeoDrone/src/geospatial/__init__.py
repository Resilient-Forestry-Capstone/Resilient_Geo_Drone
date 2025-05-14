"""Geospatial Analysis Package for ResilientGeoDrone Pipeline

This package provides geospatial analysis tools for:
- QGIS integration
- Canopy height modeling
- Terrain analysis
- Forest statistics
"""

from .gap_detection import GapDetector

__version__ = '0.1.0'
__author__ = 'ResilientGeoDrone Team'

__all__ = [
    'GapDetector'
]