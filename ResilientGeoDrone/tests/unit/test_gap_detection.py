# tests/test_gap_detection.py
import pytest
import os
import numpy as np
from pathlib import Path
# Assuming your main script is in the parent directory and named gap_detection.py
# If pytest is run from the project root and the root is in PYTHONPATH:
from gap_detection_pipeline import GapAnalyzer, RasterData # Adjust if your script is named differently

# --- Mock RasterData for GapAnalyzer tests ---
class MockRasterData:
    def __init__(self, data_array, pixel_size_x_crs=1.0, pixel_size_y_crs=1.0, to_meters_factor=1.0, units_name="meter", transform=None, crs=None):
        self.data = np.array(data_array, dtype=float)
        self.pixel_size_x_crs = pixel_size_x_crs
        self.pixel_size_y_crs = pixel_size_y_crs
        self.pixel_size_crs = pixel_size_x_crs # Used for linear scale bar
        self.to_meters_factor = to_meters_factor
        self.units_name = units_name
        self.transform = transform
        self.crs = crs

    def get_pixel_area_m2(self):
        return (self.pixel_size_x_crs * self.pixel_size_y_crs) * (self.to_meters_factor ** 2)

    def pixel_to_world(self, px, py): # Dummy implementation
        if self.transform:
            return self.transform * (px, py)
        return px, py # Fallback if no transform

@pytest.fixture
def simple_raster_data():
    """Provides a simple RasterData mock for testing."""
    data = [[10, 10,  2, 10],
            [10,  2,  2, 10],
            [ 2,  2, 10, 10],
            [10, 10, 10, 10]]
    return MockRasterData(data, pixel_size_x_crs=1.0, pixel_size_y_crs=1.0, to_meters_factor=1.0)

@pytest.fixture
def raster_data_for_morphology():
    """
    Test data for morphological operations.
    Two 3x3 gap areas, separated by a 1-pixel non-gap bridge,
    and one isolated noise pixel.
    Threshold of 5.0 will make '2's into gaps (1) and '10's into non-gaps (0).
    """
    data = [[10, 10, 10, 10, 10, 10, 10, 10, 10],
            [10,  2,  2,  2, 10, 10, 10, 10, 10], # Gap 1 (3x3)
            [10,  2,  2,  2, 10, 10, 10, 10, 10],
            [10,  2,  2,  2, 10, 10,  2, 10, 10], # Gap 1, noise pixel at (3,6)
            [10, 10, 10, 10, 10, 10, 10, 10, 10], # Separator
            [10, 10, 10, 10,  2,  2,  2, 10, 10], # Gap 2 (3x3)
            [10, 10, 10, 10,  2,  2,  2, 10, 10],
            [10, 10, 10, 10,  2,  2,  2, 10, 10],
            [10, 10, 10, 10, 10, 10, 10, 10, 10]]
    return MockRasterData(data, pixel_size_x_crs=1.0, pixel_size_y_crs=1.0, to_meters_factor=1.0)


def test_classify_manual(simple_raster_data):
    config = {"threshold_type": "manual", "manual_threshold": 5.0}
    analyzer = GapAnalyzer(config)
    mask, threshold = analyzer.classify(simple_raster_data)
    expected_mask = np.array([[0, 0, 1, 0],
                              [0, 1, 1, 0],
                              [1, 1, 0, 0],
                              [0, 0, 0, 0]])
    assert threshold == 5.0
    np.testing.assert_array_equal(mask, expected_mask)

def test_classify_otsu_simple(simple_raster_data):
    config = {"threshold_type": "otsu"}
    analyzer = GapAnalyzer(config)
    mask, threshold = analyzer.classify(simple_raster_data)
    assert 2.0 <= threshold <= 10.0 # Otsu should pick something reasonable
    assert mask.shape == simple_raster_data.data.shape
    assert np.sum(mask) > 0
    assert np.sum(mask) < mask.size

def test_identify_regions_no_morphology(simple_raster_data):
    config = {
        "threshold_type": "manual", "manual_threshold": 5.0,
        "min_area": 1.0, "max_area": 100.0,
        "area_classification_bins_sqm": [2, 5]
    }
    analyzer = GapAnalyzer(config)
    analyzer.classify(simple_raster_data)
    gaps, labels_img, processed_mask = analyzer.identify_regions(simple_raster_data)
    assert processed_mask is not None
    assert len(gaps) == 1
    gap1 = list(gaps.values())[0]
    assert gap1['area_pixels'] == 5
    assert np.isclose(gap1['area_sq_meters'], 5.0)
    assert gap1['area_bin_index'] == 2

def test_identify_regions_with_erosion_breaks_bridge(raster_data_for_morphology):
    config = {
        "threshold_type": "manual", "manual_threshold": 5.0,
        "apply_erosion": True, "erosion_size": 1,
        "apply_dilation": False,
        "min_area": 0.5, "max_area": 100.0, # m^2
        "area_classification_bins_sqm": []
    }
    analyzer = GapAnalyzer(config)
    analyzer.classify(raster_data_for_morphology) # Creates binary_mask
    # Expected binary_mask from raster_data_for_morphology and threshold 5:
    # [[0,0,0,0,0,0,0,0,0],
    #  [0,1,1,1,0,0,0,0,0],
    #  [0,1,1,1,0,0,0,0,0],
    #  [0,1,1,1,0,0,1,0,0], # Noise at (3,6)
    #  [0,0,0,0,0,0,0,0,0],
    #  [0,0,0,0,1,1,1,0,0],
    #  [0,0,0,0,1,1,1,0,0],
    #  [0,0,0,0,1,1,1,0,0],
    #  [0,0,0,0,0,0,0,0,0]]
    # Erosion(1) on a 3x3 block leaves a 1x1 center pixel. Noise is removed.
    gaps, _, processed_mask_after_erosion = analyzer.identify_regions(raster_data_for_morphology)

    # After erosion(1), each 3x3 block becomes a 1x1 pixel. The noise pixel is removed.
    # So we expect two gaps, each of 1 pixel.
    assert len(gaps) == 2, f"Expected 2 gaps after erosion, found {len(gaps)}"
    for gap_data in gaps.values():
        assert gap_data['area_pixels'] == 1

def test_identify_regions_with_opening_removes_noise(raster_data_for_morphology):
    config = {
        "threshold_type": "manual", "manual_threshold": 5.0,
        "apply_erosion": True, "erosion_size": 1,
        "apply_dilation": True, "dilation_size": 1, # Morphological opening
        "min_area": 2.0, "max_area": 100.0, # Filter out single pixel gaps if they survive opening
        "area_classification_bins_sqm": []
    }
    analyzer = GapAnalyzer(config)
    analyzer.classify(raster_data_for_morphology)
    gaps, _, processed_mask_after_opening = analyzer.identify_regions(raster_data_for_morphology)
    # Initial binary mask has two 3x3 blocks and one noise pixel.
    # Erosion(1) turns 3x3 blocks into 1x1 pixels and removes noise.
    # Dilation(1) on a 1x1 pixel (with disk(1)) creates a 5-pixel cross.
    # So we expect two gaps, each of 5 pixels.
    # Since min_area is 2.0, these 5-pixel gaps should survive.
    assert len(gaps) == 2, f"Expected 2 gaps after opening, found {len(gaps)}"
    for gap_data in gaps.values():
        assert gap_data['area_pixels'] == 5

def test_identify_regions_no_gaps_found(simple_raster_data):
    config = {
        "threshold_type": "manual", "manual_threshold": 1.0, # Threshold too low
        "min_area": 0.1, "max_area": 100.0,
        "area_classification_bins_sqm": []
    }
    analyzer = GapAnalyzer(config)
    analyzer.classify(simple_raster_data)
    gaps, _, _ = analyzer.identify_regions(simple_raster_data)
    assert len(gaps) == 0

def test_identify_regions_area_filtering(simple_raster_data):
    config = {
        "threshold_type": "manual", "manual_threshold": 5.0,
        "min_area": 6.0, "max_area": 100.0, # Min area too high for the 5-pixel gap
        "area_classification_bins_sqm": []
    }
    analyzer = GapAnalyzer(config)
    analyzer.classify(simple_raster_data)
    gaps, _, _ = analyzer.identify_regions(simple_raster_data)
    assert len(gaps) == 0

    config["min_area"] = 1.0
    config["max_area"] = 4.0 # Max area too low for the 5-pixel gap
    analyzer2 = GapAnalyzer(config)
    analyzer2.classify(simple_raster_data)
    gaps2, _, _ = analyzer2.identify_regions(simple_raster_data)
    assert len(gaps2) == 0

def test_identify_regions_different_binning(simple_raster_data):
    config = {
        "threshold_type": "manual", "manual_threshold": 5.0,
        "min_area": 1.0, "max_area": 100.0,
        "area_classification_bins_sqm": [1, 3, 6] # Gap area is 5 m^2
    }
    analyzer = GapAnalyzer(config)
    analyzer.classify(simple_raster_data)
    gaps, _, _ = analyzer.identify_regions(simple_raster_data)
    assert len(gaps) == 1
    gap1 = list(gaps.values())[0]
    # Bins: (0-1], (1-3], (3-6], (>6]
    # Indices: 1,    2,     3,      4
    # Area 5.0 falls into bin 3 ( >3 and <=6 )
    assert gap1['area_bin_index'] == 3