# tests/test_helpers.py
import pytest
# Assuming your main script is in the parent directory and named gap_analysis_oop.py
# If your script is in the same directory or project root, adjust the import:
# from ..gap_analysis_oop import get_area_bin_index
# For simplicity if tests/ is a top-level package or script is in PYTHONPATH:
from gap_detection import get_area_bin_index # Adjust if your script is named differently

def test_get_area_bin_index_basic():
    """Test the area classification helper function with various inputs."""
    bins = [100, 500, 1000] # Upper bounds of bins
    assert get_area_bin_index(50, bins) == 1   # 0-100
    assert get_area_bin_index(100, bins) == 1  # <= 100
    assert get_area_bin_index(100.1, bins) == 2 # >100 and <=500
    assert get_area_bin_index(500, bins) == 2  # <= 500
    assert get_area_bin_index(750, bins) == 3  # >500 and <=1000
    assert get_area_bin_index(1000, bins) == 3 # <= 1000
    assert get_area_bin_index(1500, bins) == 4 # > 1000 (last bin + 1)

def test_get_area_bin_index_no_bins():
    """Test with no bins defined, should return 0."""
    assert get_area_bin_index(250, []) == 0

def test_get_area_bin_index_single_bin():
    """Test with a single bin defined."""
    bins = [100]
    assert get_area_bin_index(50, bins) == 1
    assert get_area_bin_index(100, bins) == 1
    assert get_area_bin_index(150, bins) == 2

def test_get_area_bin_index_zero_area():
    """Test with zero area, should fall into the first bin."""
    bins = [100, 500]
    assert get_area_bin_index(0, bins) == 1
