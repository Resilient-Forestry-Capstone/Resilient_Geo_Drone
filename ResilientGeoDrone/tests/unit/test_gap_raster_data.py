# tests/test_raster_data.py
import pytest
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_origin
import numpy as np
from gap_detection import RasterData # Adjust if needed

# --- Mocking Rasterio's open for some tests ---
# More advanced mocking might be needed for full coverage without actual files
# For now, we'll focus on testing methods with controlled inputs or small actual files

# It's better to use small, actual test files for loading tests
# Create a dummy test raster file for loading tests if not using a fixture
# For example, in a conftest.py or setup function

@pytest.fixture
def mock_raster_data_meters(tmp_path):
    """Creates a temporary dummy raster file with meter units for testing."""
    filepath = tmp_path / "test_meters.tif"
    transform = from_origin(0, 5, 1, 1) # 1m pixel size
    data = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    with rasterio.open(
        filepath, 'w', driver='GTiff',
        height=data.shape[0], width=data.shape[1],
        count=1, dtype=data.dtype,
        crs=CRS.from_epsg(32610), # UTM Zone 10N (meters)
        transform=transform
    ) as dst:
        dst.write(data, 1)
    return str(filepath)

@pytest.fixture
def mock_raster_data_feet(tmp_path):
    """Creates a temporary dummy raster file with feet units for testing."""
    filepath = tmp_path / "test_feet.tif"
    # Example for US Survey Foot, EPSG:2272 (Texas South Central)
    # Pixel size approx 1 ft
    transform = from_origin(1000000, 10000000, 0.3048006096, 0.3048006096)
    data = np.array([[10.0, 20.0], [30.0, 40.0]], dtype=np.float32)
    with rasterio.open(
        filepath, 'w', driver='GTiff',
        height=data.shape[0], width=data.shape[1],
        count=1, dtype=data.dtype,
        crs=CRS.from_epsg(2272), # Example CRS in US survey feet
        transform=transform
    ) as dst:
        dst.write(data, 1)
    return str(filepath)


def test_raster_data_load_meters(mock_raster_data_meters):
    """Test loading a raster with meter units."""
    rd = RasterData(mock_raster_data_meters)
    assert rd.data is not None
    assert rd.units_name.lower() == "metre" # rasterio might return 'metre'
    assert np.isclose(rd.to_meters_factor, 1.0)
    assert np.isclose(rd.pixel_size_crs, 1.0)
    assert rd.crs.is_projected

def test_raster_data_load_feet(mock_raster_data_feet):
    """Test loading a raster with feet units."""
    rd = RasterData(mock_raster_data_feet)
    assert rd.data is not None
    assert "foot" in rd.units_name.lower() # Could be 'US survey foot' or 'foot'
    assert np.isclose(rd.to_meters_factor, 0.304800609601219) or np.isclose(rd.to_meters_factor, 0.3048)
    assert np.isclose(rd.pixel_size_x_crs, 0.3048006096) # Based on transform
    assert rd.crs.is_projected

def test_get_pixel_area_m2_meters(mock_raster_data_meters):
    """Test pixel area calculation for a meter-based raster."""
    rd = RasterData(mock_raster_data_meters)
    # Pixel size is 1m x 1m, factor is 1.0
    expected_area = (1.0 * 1.0) * (1.0**2)
    assert np.isclose(rd.get_pixel_area_m2(), expected_area)

def test_get_pixel_area_m2_feet(mock_raster_data_feet):
    """Test pixel area calculation for a feet-based raster."""
    rd = RasterData(mock_raster_data_feet)
    # Pixel size is ~1ft x ~1ft, factor is ~0.3048
    # pixel_size_x_crs and pixel_size_y_crs are ~0.3048006096 from the transform
    # so native area is approx (0.3048006096)^2
    # to_meters_factor is also ~0.3048006096 for US survey foot
    # So, area in m2 = (native_x * native_y) * (to_meters_factor^2)
    # If pixel size was exactly 1ft x 1ft, area would be 1 ft^2.
    # Then 1 ft^2 * (0.3048006096 m/ft)^2 = 0.09290341 m^2
    # Here, pixel_size_x_crs * pixel_size_y_crs is already in native_units^2
    # The transform defines pixel size in CRS units. Here, it's ~1ft.
    # So pixel_size_x_crs * pixel_size_y_crs is roughly 1 ft^2.
    # We need to convert this to m^2.
    # The self.to_meters_factor is for linear units. For area, it's (self.to_meters_factor)^2.
    # So, if pixel_size_x_crs = 1 ft, pixel_size_y_crs = 1 ft
    # area_native_units = 1 ft * 1 ft = 1 ft^2
    # area_m2 = area_native_units * (to_meters_factor^2)
    # area_m2 = (rd.pixel_size_x_crs * rd.pixel_size_y_crs) * (rd.to_meters_factor ** 2)
    expected_area_m2 = (rd.pixel_size_x_crs * rd.pixel_size_y_crs) * (rd.to_meters_factor ** 2)
    assert np.isclose(rd.get_pixel_area_m2(), expected_area_m2)


def test_pixel_to_world(mock_raster_data_meters):
    """Test pixel_to_world conversion."""
    rd = RasterData(mock_raster_data_meters)
    # For transform = from_origin(0, 5, 1, 1)
    # Top-left (0,0) pixel center is (0.5, 4.5)
    # Top-left (0,0) pixel outer corner is (0,5)
    # transform * (px, py) maps pixel center to world coords
    world_x, world_y = rd.pixel_to_world(0.5, 0.5) # Center of first pixel (0,0)
    assert np.isclose(world_x, 0.5)
    assert np.isclose(world_y, 4.5)

    world_x_corner, world_y_corner = rd.pixel_to_world(0,0) # Top-left corner of top-left pixel
    assert np.isclose(world_x_corner, 0.0)
    assert np.isclose(world_y_corner, 5.0)
