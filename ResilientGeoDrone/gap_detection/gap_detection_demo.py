#!/usr/bin/env python3
"""
Standalone Gap Detector - Debug Version
Usage: python gap_detection_standalone.py <orthophoto_path> [output_dir]
"""

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

class QuickGapDetector:
    def __init__(self, device='cuda'):
        self.depth_pipe = pipeline(
            "depth-estimation", 
            model="depth-anything/Depth-Anything-V2-base-hf",
            device=device
        )
        
    def run(self, ortho_path: Path, output_dir: Path = Path("gap_results")):
        """Main execution flow"""
        output_dir.mkdir(exist_ok=True)
        
        # Load georeferenced orthophoto
        with rasterio.open(ortho_path) as src:
            ortho_img = src.read([1,2,3]).transpose(1,2,0)  # RGB
            transform = src.transform
            crs = src.crs
        
        # Generate depth map
        depth_map = self._generate_depth_map(ortho_img)
        
        # Detect gaps and trees
        gap_mask = self._find_gaps(depth_map)
        trees = self._find_sparse_trees(depth_map, gap_mask)
        
        # Convert to geographic coordinates
        gap_polygons = self._mask_to_polygons(gap_mask, transform)
        tree_points = self._pixels_to_coords(trees, transform)
        
        # Save results
        results_path = output_dir / "gap_analysis.geojson"
        self._save_geojson(gap_polygons, tree_points, crs, results_path)
        
        # Visual debug
        self._save_debug_images(ortho_img, depth_map, gap_mask, output_dir)
        
        print(f"Analysis complete. Results saved to {output_dir}")

    def _generate_depth_map(self, rgb_img: np.ndarray) -> np.ndarray:
        """Generate depth map from RGB array"""
        pil_img = Image.fromarray(rgb_img)
        return np.array(self.depth_pipe(pil_img)["depth"])

    def _find_gaps(self, depth_map: np.ndarray) -> np.ndarray:
        """Threshold depth map to identify gaps"""
        blurred = cv2.GaussianBlur(depth_map, (15,15), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, 
                                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return thresh.astype(bool)

    def _find_sparse_trees(self, depth_map: np.ndarray, 
                         gap_mask: np.ndarray) -> np.ndarray:
        """Find potential trees in gaps using local maxima"""
        kernel = np.ones((20,20), np.uint8)
        dilated = cv2.dilate(depth_map, kernel)
        peaks = (depth_map == dilated) & gap_mask
        return np.argwhere(peaks)

    def _mask_to_polygons(self, mask: np.ndarray, transform) -> list:
        """Convert binary mask to simplified polygons"""
        contours, _ = cv2.findContours(mask.astype(np.uint8),
                                     cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)
        return [self._contour_to_coords(c, transform) for c in contours]

    def _contour_to_coords(self, contour, transform) -> list:
        """Convert pixel contour to geographic coordinates"""
        return [transform * (point[0][0], point[0][1]) for point in contour]
       
    def _pixels_to_coords(self, pixels: np.ndarray, transform) -> list:
        """Convert pixel coordinates to geographic points"""
        return [transform * (x,y) for y,x in pixels]

    def _save_geojson(self, polygons, points, crs, path: Path):
        """Save results as GeoJSON with CRS information"""
        features = []
        
        for poly in polygons:
            features.append(geojson.Feature(
                geometry=geojson.Polygon([[(x,y) for x,y in poly]]),
                properties={"type": "gap"}
            ))
            
        for x,y in points:
            features.append(geojson.Feature(
                geometry=geojson.Point((x,y)),
                properties={"type": "sparse_tree"}
            ))
            
        collection = geojson.FeatureCollection(features, crs={
            "type": "name",
            "properties": {"name": crs.to_string()}
        })
        
        with open(path, 'w') as f:
            geojson.dump(collection, f)

    def _save_debug_images(self, ortho, depth, mask, output_dir):
        """Save visualization of processing steps"""
        plt.figure(figsize=(18,6))
        
        plt.subplot(131)
        plt.imshow(ortho)
        plt.title('Orthophoto')
        
        plt.subplot(132)
        plt.imshow(depth, cmap='viridis')
        plt.title('Depth Map')
        
        plt.subplot(133)
        plt.imshow(mask, cmap='gray')
        plt.title('Gap Mask')
        
        plt.savefig(output_dir/'debug_visualization.png', bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gap_detection_standalone.py <orthophoto_path> [output_dir]")
        sys.exit(1)
        
    ortho_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()/"gap_results"
    
    detector = QuickGapDetector(device='cuda' if torch.cuda.is_available() else 'cpu')
    detector.run(ortho_path, output_dir)