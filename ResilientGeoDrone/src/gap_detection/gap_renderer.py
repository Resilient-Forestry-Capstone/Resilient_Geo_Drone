import cv2
import geojson
import rasterio
import numpy as np
from rasterio.features import geometry_mask
from pathlib import Path
import sys
import cv2
import numpy as np
import rasterio
import geojson
from pathlib import Path
import torch
from PIL import Image
from transformers import pipeline
import matplotlib.pyplot as plt



"""

    Desc: This Function Takes In ortho_path, geojson_path, output_path,
    And opacity And Creates An Overlay Image With Gap Visualization. The
    Overlay Image Is Saved As A PNG Image In output_path. 

    Preconditions:
        1. ortho_path: Path To Orthophoto Image
        2. geojson_path: Path To GeoJSON File Representing Gaps And Trees
        3. output_path: Path To Save Overlay Image
        4. opacity: Opacity Of Overlay Image
        5. ortho_path And geojson_path Must Be Of The Same Orthophoto Image

    Postconditions:
        1. Creates Overlay Image With Gap Visualization
        2. Saves Overlay Image As PNG Image In output_path
        3. Overlay Image Has Opacity Of opacity

"""
def create_gap_overlay(ortho_path: Path, geojson_path: Path, output_path: Path, opacity=0.4):
    
    # Open Orthophoto Through rasterio
    with rasterio.open(ortho_path) as src:
        """
            Read and convert to OpenCV-compatible format
            (rasterio Reads as bands x height x width, OpenCV expects height x width x bands)
            Transpose To Convert To Height x Width x Bands
        """
        ortho = src.read([1,2,3]).transpose(1,2,0)

        # Normalize to 0-255 and convert to BGR
        ortho = cv2.normalize(ortho, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Convert to BGR for OpenCV
        ortho = cv2.cvtColor(ortho, cv2.COLOR_RGB2BGR)

        # Get Transform For Geo-Referencing
        transform = src.transform

    # Create A Blank Overlay Image On Our Orthophoto
    overlay = np.zeros_like(ortho, dtype=np.uint8)
    
    # Define Colors (BGR Format)
    gap_color = (0, 255, 0)  # Red
    tree_color = (255, 0, 255)  # Blue

    # Open GeoJSON File And Extract Features
    with open(geojson_path) as f:
        features = geojson.load(f)['features']

    # Iterate Over Features And Draw On Overlay
    for feature in features:
        # Extract Geometry And Properties
        geom = feature['geometry']
        prop = feature['properties']
        
        # Draw Based On Geometry Type
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
        # Draw Points As Circles 
        elif geom['type'] == 'Point':
            lon, lat = geom['coordinates']
            x, y = ~transform * (lon, lat)
            cv2.circle(overlay, (int(x), int(y)), 5, tree_color, -1)

    # Create Overlay With Proper Blending
    overlayed = cv2.addWeighted(overlay, opacity, ortho, 1 - opacity, 0)
    
    # Convert Back To RGB For Saving
    overlayed = cv2.cvtColor(overlayed, cv2.COLOR_BGR2RGB)
    
    # Save Overlay Image As PNG Image
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
    geojson_path=Path(r"C:\Users\bensp\OneDrive\Desktop\Code Box Two\Python\GeoDrone\ResilientRepo\Resilient_Geo_Drone\ResilientGeoDrone\gap_detection\gap_analysis.geojson"),
    output_path=Path(r"C:\Users\bensp\OneDrive\Desktop\Code Box Two\Python\GeoDrone\ResilientRepo\Resilient_Geo_Drone\ResilientGeoDrone\gap_detection\demo\gap_map.png"),
    opacity=0.5
)