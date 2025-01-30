import cv2
import geojson
import rasterio
import numpy as np
from rasterio.features import geometry_mask
from pathlib import Path


def create_gap_overlay(ortho_path: Path, geojson_path: Path, output_path: Path, opacity=0.4):
    """Create overlay image with gap visualization"""
    
    with rasterio.open(ortho_path) as src:
        # Read image as uint8 and convert to BGR format for OpenCV
        ortho = src.read([1,2,3]).transpose(1,2,0)
        ortho = cv2.normalize(ortho, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        ortho = cv2.cvtColor(ortho, cv2.COLOR_RGB2BGR)
        transform = src.transform

    # Create overlay with proper OpenCV-compatible format
    overlay = np.zeros_like(ortho, dtype=np.uint8)
    
    # Define colors (BGR format)
    gap_color = (0, 255, 0)  # Red
    tree_color = (255, 0, 255)  # Blue

    with open(geojson_path) as f:
        features = geojson.load(f)['features']

    for feature in features:
        geom = feature['geometry']
        prop = feature['properties']
        
        if geom['type'] == 'Polygon':
            coords = []
            for lon, lat in geom['coordinates'][0]:
                x, y = ~transform * (lon, lat)
                coords.append((int(x), int(y)))
            
            # Convert to contiguous array
            pts = np.array(coords, dtype=np.int32).reshape((-1, 1, 2))
            
            # Use cv2.polylines first to validate coordinates
            cv2.polylines(overlay, [pts], isClosed=True, color=gap_color, thickness=2)
            cv2.fillPoly(overlay, [pts], gap_color)
            
        elif geom['type'] == 'Point':
            lon, lat = geom['coordinates']
            x, y = ~transform * (lon, lat)
            cv2.circle(overlay, (int(x), int(y)), 5, tree_color, -1)

    # Create overlay with proper blending
    overlayed = cv2.addWeighted(overlay, opacity, ortho, 1 - opacity, 0)
    
    # Convert back to RGB for saving
    overlayed = cv2.cvtColor(overlayed, cv2.COLOR_BGR2RGB)
    
    # Save with rasterio to maintain georeferencing
    with rasterio.open(
        output_path, 'w',
        driver='GTiff',
        height=overlayed.shape[0],
        width=overlayed.shape[1],
        count=3,
        dtype=np.uint8,
        crs=src.crs,
        transform=transform,
    ) as dst:
        dst.write(overlayed.transpose(2, 0, 1))


# Usage example
create_gap_overlay(
    ortho_path=Path(r"C:\Users\bensp\Downloads\Southeast-247th-Street-1-24-2025-orthophoto.tif"),
    geojson_path=Path(r"C:\Users\bensp\OneDrive\Desktop\Code Box Two\Python\GeoDrone\ResilientGeoDrone - Copy\Resilient_Geo_Drone\ResilientGeoDrone\src\gap_detection\gap_analysis.geojson"),
    output_path=Path(r"C:\Users\bensp\OneDrive\Desktop\Code Box Two\Python\GeoDrone\ResilientGeoDrone - Copy\Resilient_Geo_Drone\ResilientGeoDrone\src\gap_detection\demo\gap_overlay.png"),
    opacity=0.5
)