import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import rasterio.transform
from skimage.filters import gaussian
from shapely.geometry import Polygon
from skimage.measure import label, regionprops
from skimage.morphology import binary_dilation, binary_erosion, disk
from pathlib import Path
from ..utils.config_loader import ConfigLoader
from ..utils.logger import LoggerSetup


"""

  Desc: This Module Provides A Class For Detecting Gaps In Canopy Height Models
  (CHM) Using Raster Data. The Class Utilizes Morphological Operations
  To Identify Gaps In The Canopy And Provides Visualization And Analysis
  Capabilities.

"""
class GapDetector:
    """
    
      Desc: Will Setup The Gap Detector Class With A Configuration Loader
      As Well As A Logger. 

      Preconditions:
        1. config_loader Is The .yaml Configuration File To Be Used For Gap Detection

      Postconditions:
        1. Initialize Gap Detector With Configuration Loader
        2. Load Configuration Parameters
    
    """
    def __init__(self, config_loader : ConfigLoader):
        self.config_loader = config_loader
        self.config = config_loader.load()
        self.gap_config = self.config['geospatial']['gap_detection']
        self.logger = LoggerSetup().get_logger()
        
    def load_and_clean_dsm(self, dsm_file):
        """Load DSM/CHM and clean nodata values"""
        self.logger.info(f"Loading DSM/CHM from {dsm_file}")
        with rasterio.open(dsm_file) as src:
            dsm = src.read(1).astype(float)
            dsm[dsm == -9999.0] = np.nan
            return dsm, src.transform

    def classify_dsm(self, dsm_data):
        """Apply threshold to classify areas as gaps or non-gaps"""
        threshold = None
        if self.gap_config["threshold_type"] == "manual":
            threshold = self.gap_config["manual_threshold"]
        elif self.gap_config["threshold_type"] == "otsu":
            from skimage.filters import threshold_otsu
            threshold = threshold_otsu(dsm_data[~np.isnan(dsm_data)])

        self.logger.info(f"Using Threshold: {threshold}")
        bit_mask = np.where((dsm_data <= threshold) & ~np.isnan(dsm_data), 1, 0)
        return bit_mask

    def identify_gaps(self, binary_dsm):
        """Identify gaps in binary mask using morphological operations"""
        # Apply morphological operations
        if self.gap_config["apply_dilation"]:
            binary_dsm = binary_dilation(binary_dsm, disk(self.gap_config["dilation_size"]))
            
        if self.gap_config["apply_erosion"]:
            binary_dsm = binary_erosion(binary_dsm, disk(self.gap_config["erosion_size"]))
            
        if self.gap_config["apply_smoothing"]:
            binary_dsm = gaussian(binary_dsm, sigma=self.gap_config["smoothing_sigma"], mode='reflect')

        # Label connected components
        labels = label(binary_dsm, None, False, connectivity=1)
        props = regionprops(labels)

        gaps = []
        gap_areas = {}

        # Process each region
        for prop in props:
            area = prop.area * (self.gap_config["pixel_size"] ** 2)
            if self.gap_config["min_area"] <= area <= self.gap_config["max_area"]:
                gap_polygon = Polygon(prop.coords[:, ::-1])
                centroid = np.mean(prop.coords[:, ::-1], axis=0)
                gaps.append(gap_polygon)
                gap_areas[len(gap_areas)+1] = {
                    'polygon': gap_polygon,
                    'area': area,
                    'centroid': centroid,
                    'coords': prop.coords
                }

        self.logger.info(f"Identified {len(gap_areas)} gaps")
        return gap_areas

    def pixel_to_world(self, transform, px, py):
        """Convert pixel coordinates to world coordinates using the affine transform"""
        wx, wy = rasterio.transform.xy(transform, py, px)
        return wx, wy

    def visualize_gaps_on_bitmask(self, bit_mask, gap_areas, transform, output_path=None):
        """Visualize identified gaps on the binary mask"""
        # Get the extent of the plot in real-world coordinates
        height, width = bit_mask.shape
        top_left_x, top_left_y = self.pixel_to_world(transform, 0, 0)
        bottom_right_x, bottom_right_y = self.pixel_to_world(transform, width - 1, height - 1)

        # Create figure and axes
        fig, ax = plt.subplots(figsize=(12, 10))

        # Display binary mask
        ax.imshow(bit_mask, cmap='gray', extent=(top_left_x, bottom_right_x, bottom_right_y, top_left_y))

        # Add polygons for each gap
        for idx, gap_data in gap_areas.items():
            polygon = gap_data['polygon']
            polygon_coords = [(self.pixel_to_world(transform, x, y)) for x, y in polygon.exterior.coords]
            patch = patches.Polygon(polygon_coords, closed=True, edgecolor='green', facecolor='none', linewidth=2)
            ax.add_patch(patch)
            
            # Add gap labels
            centroid = gap_data['centroid']
            cx, cy = self.pixel_to_world(transform, centroid[0], centroid[1])
            ax.annotate(f"{idx} ", (cx, cy), color='blue', fontsize=10, ha='center', backgroundcolor='none')

        # Set axis ticks and labels
        x_ticks = np.linspace(top_left_x, bottom_right_x, num=10)
        y_ticks = np.linspace(bottom_right_y, top_left_y, num=10)
        ax.set_xticks(x_ticks)
        ax.set_xticklabels([f"{x:.2f}" for x in x_ticks], rotation=45)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels([f"{y:.2f}" for y in y_ticks])

        # Set titles and labels
        ax.set_title("Identified Gaps in Canopy")
        ax.set_xlabel("Northing")
        ax.set_ylabel("Easting")

        # Create legend
        legend_patches = [
            patches.Patch(edgecolor='green', facecolor='none', linewidth=2, label='Gap'),
            patches.Patch(edgecolor='black', facecolor='black', label='Tree'),
            patches.Patch(edgecolor='white', facecolor='white', label='Ground')
        ]
        ax.legend(handles=legend_patches, loc='lower right', title="Legend", borderaxespad=0.)
        
        plt.tight_layout()
        
        # Save figure if output path provided
        if output_path:
            plt.savefig(output_path)
            self.logger.info(f"Gap visualization saved to {output_path}")
            
        plt.show()
        plt.pause(0.001)  # Short pause to ensure the plot updates

    def save_gap_info(self, gap_areas, transform, output_file):
        """Save gap information to a text file"""
        with open(output_file, 'w') as f:
            f.write("GAP ANALYSIS RESULTS\n")
            f.write("====================\n\n")
            
            for idx, gap_data in gap_areas.items():
                centroid = gap_data['centroid']
                cx, cy = self.pixel_to_world(transform, centroid[0], centroid[1])
                f.write(f"Gap {idx}\n")
                f.write(f"Area: {gap_data['area']:.2f} square meters\n")
                f.write(f"Center coordinates: ({cx:.2f} N, {cy:.2f} E)\n\n")
                
        self.logger.info(f"Gap information saved to {output_file}")

    def process_gaps(self, chm_path, output_dir=None):
        """
        Process gaps in CHM/DSM
        
        Args:
            chm_path: Optional path to CHM/DSM file. If not provided, uses path from config
            output_dir: Optional output directory. If not provided, uses path from config
            
        Returns:
            Dictionary of identified gaps
        """
        # Set paths based on configuration
        if output_dir is None:
            output_dir = Path(self.config['geospatial'].get('output_path', '.'))
        else:
            output_dir = Path(output_dir)
            
        # Ensure output directory exists
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Get CHM file path
        chm_path = Path(chm_path)
            
        self.logger.info(f"Processing gaps using CHM: {chm_path}")
            
        # Load and process DSM/CHM
        dsm_data, transform = self.load_and_clean_dsm(chm_path)
        bit_mask = self.classify_dsm(dsm_data)
        
        # Show binary mask
        plt.figure(figsize=(8, 6))
        plt.imshow(bit_mask, cmap='gray')
        plt.title("Binary Mask")
        plt.colorbar(label="Class")
        plt.show(block=False)
        plt.pause(0.001)
        
        # Process gaps
        gap_areas = self.identify_gaps(bit_mask)
        
        # Visualize results
        vis_output = output_dir / "gap_visualization.png"
        self.visualize_gaps_on_bitmask(bit_mask, gap_areas, transform, vis_output)
        
        # Save gap information
        gap_info_path = output_dir / 'gap_info.txt'
        self.save_gap_info(gap_areas, transform, gap_info_path)
        
        return gap_areas


# Example usage with YAML configuration
if __name__ == "__main__":
    config_path = Path(__file__).parent.parent.parent / "config/config.yaml"
    config_loader = ConfigLoader(config_path)
    gap_detector = GapDetector(config_loader)
    gap_areas = gap_detector.process_gaps("")