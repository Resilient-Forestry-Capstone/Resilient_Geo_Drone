import os
import rasterio
import numpy as np
from skimage import measure
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from rasterio.plot import show
import yaml

def load_config():
    """Load configuration parameters from YAML file"""
    try:
        with open(r"C:\Users\bensp\OneDrive\Desktop\Code Box Two\Python\GeoDrone\ResilientRepo\Resilient_Geo_Drone\ResilientGeoDrone\config\config.yaml", 'r') as file:
            config = yaml.safe_load(file)
        
        # Extract canopy analysis parameters
        params = {
            'min_tree_height': config['geospatial']['analysis']['min_tree_height'],
            'canopy_threshold': config['geospatial']['analysis']['canopy_threshold'],
            'slope_threshold': config['geospatial']['analysis']['terrain']['slope_threshold'],
            'roughness_threshold': config['geospatial']['analysis']['terrain']['roughness_threshold']
        }
        
        # Add default parameters if not in config
        if 'min_gap_size_m2' not in params:
            params['min_gap_size_m2'] = 2.0
        if 'max_gap_size_m2' not in params:
            params['max_gap_size_m2'] = 5000.0
        if 'max_tree_height' not in params:
            params['max_tree_height'] = 30.0
            
        return params
    except Exception as e:
        print(f"Error loading config: {e}")
        # Fallback to default parameters
        return {
            'min_tree_height': 2.0,
            'max_tree_height': 30.0,
            'min_gap_size_m2': 2.0,
            'max_gap_size_m2': 5000.0,
            'canopy_threshold': 0.5,
            'slope_threshold': 30.0,
            'roughness_threshold': 0.5
        }

def perform_gap_analysis(chm_path, orthophoto_path=None, output_dir=None):
    """
    Performs canopy gap analysis on a CHM raster file
    
    Args:
        chm_path: Path to the Canopy Height Model GeoTIFF
        orthophoto_path: Optional path to orthophoto for visualization
        output_dir: Directory to save output files (defaults to CHM directory)
    
    Returns:
        GeoDataFrame of canopy gaps with metrics
    """
    # Get config parameters
    params = load_config()
    min_tree_height = params['min_tree_height']
    max_tree_height = params['max_tree_height']
    min_gap_size_m2 = params['min_gap_size_m2']
    max_gap_size_m2 = params['max_gap_size_m2']
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.dirname(chm_path)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing CHM: {chm_path}")
    print(f"Using parameters: min_height={min_tree_height}m, max_height={max_tree_height}m")
    print(f"Gap size range: {min_gap_size_m2}-{max_gap_size_m2} m²")
    
    # Open the CHM file
    with rasterio.open(chm_path) as src:
        chm = src.read(1)
        transform = src.transform
        crs = src.crs
        
        # Calculate pixel resolution for real-world measurements
        pixel_width = abs(transform[0])
        pixel_height = abs(transform[4])
        pixel_area = pixel_width * pixel_height
        
        print(f"CHM dimensions: {chm.shape}")
        print(f"Pixel resolution: {pixel_width:.2f} x {pixel_height:.2f} meters")
    
    # 1. Identify gaps based on height threshold
    canopy_mask = (chm >= min_tree_height) & (chm <= max_tree_height)
    gap_mask = ~canopy_mask & (chm >= 0)  # Identify gaps, exclude no-data areas
    
    # 2. Label and analyze connected components (gaps)
    labeled_gaps, num_gaps = measure.label(gap_mask, connectivity=2, return_num=True)
    print(f"Found {num_gaps} potential gaps")
    
    # 3. Calculate properties for each gap
    props = measure.regionprops(labeled_gaps)
    
    # 4. Filter gaps by size and store metrics
    gap_data = []
    valid_gaps = np.zeros_like(labeled_gaps)
    
    for prop in props:
        # Calculate area in square meters
        area_m2 = prop.area * pixel_area
        
        # Calculate perimeter in meters
        perimeter_m = prop.perimeter * ((pixel_width + pixel_height) / 2)
        
        # Filter by size in real-world units
        if min_gap_size_m2 <= area_m2 <= max_gap_size_m2:
            valid_gaps[labeled_gaps == prop.label] = prop.label
            
            # Shape complexity (circularity/compactness)
            circularity = 4 * np.pi * area_m2 / (perimeter_m ** 2) if perimeter_m > 0 else 0
            
            # Create centroid coordinates in projection units
            y, x = prop.centroid
            centroid_x = transform[0] * x + transform[2]
            centroid_y = transform[3] * y + transform[5]
            

            if len(gap_data) == 10:
                break

            # Store metrics
            gap_data.append({
                'id': int(prop.label),
                'area_m2': area_m2,
                'perimeter_m': perimeter_m,
                'circularity': circularity,
                'centroid_x': centroid_x,
                'centroid_y': centroid_y,
                'width_m': prop.bbox_area**0.5 * pixel_width,  # Approximated width
                'elongation': prop.major_axis_length / prop.minor_axis_length if prop.minor_axis_length > 0 else 0
            })
    
    print(f"After filtering: {len(gap_data)} gaps meet size criteria")
    
   
    # 5. Convert gaps to vector format using multithreading
    from concurrent.futures import ThreadPoolExecutor
    import concurrent.futures
    import multiprocessing
    
    # Determine optimal number of threads (use 75% of available cores)
    max_threads = 2
    gap_ids = np.unique(valid_gaps)[1:-1]  # Skip 0 (background)
    print(f"Processing {len(gap_ids)} gaps using {max_threads} threads")
    
    polygons = []
    
    # Process gaps in parallel
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Create a list of future results
        futures = {
            executor.submit(process_single_gap, gap_id, valid_gaps, transform): gap_id 
            for gap_id in gap_ids
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            gap_id = futures[future]
            try:
                polygon = future.result()
                if polygon:
                    polygons.append(polygon)
                    if len(polygons) % 50 == 0:  # Progress update
                        print(f"Processed {len(polygons)} valid polygons so far...")
            except Exception as e:
                print(f"Error processing gap ID {gap_id}: {e}")
    
    print(f"Created {len(polygons)} valid polygons")
    
    
    # Create GeoDataFrame with gap metrics
    gap_metrics_df = pd.DataFrame(gap_data)
    
    # Handle case where no valid gaps were found
    if len(polygons) == 0:
        print("No valid gaps found matching the criteria.")
        return None
    
    gap_gdf = gpd.GeoDataFrame(
        gap_metrics_df,
        geometry=polygons,
        crs=crs
    )
    
    # Export results to files
    base_filename = os.path.splitext(os.path.basename(chm_path))[0]
    output_base = os.path.join(output_dir, f"gap_analysis_{base_filename}")
    
    # Save GeoPackage
    gpkg_path = f"{output_base}.gpkg"
    gap_gdf.to_file(gpkg_path, driver='GPKG')
    print(f"Saved gap polygons to: {gpkg_path}")
    
    # Export CSV
    csv_path = f"{output_base}.csv"
    export_to_csv(gap_gdf, csv_path)
    print(f"Saved gap metrics to: {csv_path}")
    
    # Create visualization if orthophoto is provided
    if orthophoto_path and os.path.exists(orthophoto_path):
        vis_path = f"{output_base}_map.png"
        try:
            visualize_gaps(chm_path, orthophoto_path, gap_gdf, vis_path)
            print(f"Saved visualization to: {vis_path}")
        except Exception as e:
            print(f"Error creating visualization: {e}")
    else:
        # Create a simple visualization without orthophoto
        simple_vis_path = f"{output_base}_simple_map.png"
        fig, ax = plt.subplots(figsize=(12, 8))
        gap_gdf.plot(column='area_m2', cmap='viridis', legend=True, ax=ax)
        plt.title('Canopy Gaps by Area (m²)')
        plt.savefig(simple_vis_path, dpi=300)
        plt.close()
        print(f"Saved simple visualization to: {simple_vis_path}")
    
    # Generate summary statistics
    print("\nGap Statistics Summary:")
    gap_stats = gap_gdf.describe()
    print(gap_stats)
    
    total_gap_area = gap_gdf['area_m2'].sum()
    mean_gap_size = gap_gdf['area_m2'].mean()
    total_area = chm.shape[0] * chm.shape[1] * pixel_area
    gap_density = len(gap_gdf) / (total_area / 10000)  # Gaps per hectare
    gap_fraction = total_gap_area / total_area * 100  # Percentage of area that is gap
    
    print(f"Total analyzed area: {total_area:.2f} m²")
    print(f"Total gap area: {total_gap_area:.2f} m² ({gap_fraction:.2f}%)")
    print(f"Mean gap size: {mean_gap_size:.2f} m²")
    print(f"Gap density: {gap_density:.2f} gaps/ha")
    
    # Save summary stats to text file
    summary_path = f"{output_base}_summary.txt"
    with open(summary_path, 'w') as f:
        f.write(f"Gap Analysis Summary for {os.path.basename(chm_path)}\n")
        f.write(f"Parameters: min_tree_height={min_tree_height}m, max_tree_height={max_tree_height}m\n")
        f.write(f"Gap size range: {min_gap_size_m2}-{max_gap_size_m2} m²\n\n")
        f.write(f"Number of identified gaps: {len(gap_gdf)}\n")
        f.write(f"Total analyzed area: {total_area:.2f} m²\n")
        f.write(f"Total gap area: {total_gap_area:.2f} m² ({gap_fraction:.2f}%)\n")
        f.write(f"Mean gap size: {mean_gap_size:.2f} m²\n")
        f.write(f"Gap density: {gap_density:.2f} gaps/ha\n")
    
    return gap_gdf


def process_single_gap(gap_id, valid_gaps, transform):
    """Process a single gap and return its polygon"""
    # Extract contours of the gap
    gap_contours = measure.find_contours(valid_gaps == gap_id, 0.5)
    
    print(f"Processing gap ID {gap_id} with {len(gap_contours)} contours")

    if not gap_contours:
        return None
        
    # Convert to real-world coordinates
    coords = []
    for point in gap_contours[0]:
        # Convert raster coordinates to projection coordinates
        y, x = point
        proj_x = transform[0] * x + transform[2]
        proj_y = transform[3] * y + transform[5]
        coords.append((proj_x, proj_y))
    
    # Create and return polygon if valid
    if len(coords) >= 3:  # Need at least 3 points for a valid polygon
        return Polygon(coords)
    return None


def visualize_gaps(chm_path, orthophoto_path, gaps_gdf, output_path):
    """
    Create a visualization of gaps overlaid on the orthophoto
    """
    try:
        import matplotlib as mpl
        mpl.use('Agg')  # Use non-interactive backend for reliable rendering
        
        print(f"Opening orthophoto: {orthophoto_path}")
        
        # Open orthophoto using rasterio
        with rasterio.open(orthophoto_path) as src:
            # Get orthophoto data
            if src.count >= 3:
                # For RGB orthophoto
                rgb = np.zeros((src.height, src.width, 3), dtype=np.uint8)
                for i in range(3):
                    rgb[:,:,i] = src.read(i+1)
                
                # Stretch contrast for better visibility
                for i in range(3):
                    p2, p98 = np.percentile(rgb[:,:,i], (2, 98))
                    rgb[:,:,i] = np.clip((rgb[:,:,i] - p2) * 255 / (p98 - p2), 0, 255).astype(np.uint8)
                
                # Create figure with appropriate dimensions
                aspect_ratio = src.height / src.width
                fig_width = 12
                fig_height = fig_width * aspect_ratio
                fig, ax = plt.subplots(figsize=(fig_width, fig_height))
                
                # Display image
                ax.imshow(rgb)
            else:
                # For single band orthophoto
                data = src.read(1)
                
                # Create figure with appropriate dimensions
                aspect_ratio = src.height / src.width
                fig_width = 12
                fig_height = fig_width * aspect_ratio
                fig, ax = plt.subplots(figsize=(fig_width, fig_height))
                
                # Display image with grayscale
                ax.imshow(data, cmap='gray')
            
            # Convert world coordinates to pixel coordinates manually
            print(f"Converting {len(gaps_gdf)} polygons from world to pixel coordinates...")
            pixel_polygons = []
            
            for idx, row in gaps_gdf.iterrows():
                geom = row['geometry']
                if geom.geom_type == 'Polygon':
                    exterior_coords = []
                    for x, y in geom.exterior.coords:
                        # Convert world to pixel coordinates using src.index()
                        try:
                            # Use src.index() instead of ~transform
                            row, col = src.index(x, y)
                            exterior_coords.append((col, row))
                        except Exception as e:
                            print(f"Point transformation error: {e}")
                    
                    if len(exterior_coords) >= 3:
                        pixel_polygons.append((idx, Polygon(exterior_coords)))
            
            print(f"Successfully converted {len(pixel_polygons)} polygons")
            
            # Plot polygons directly with matplotlib for better control
            for idx, poly in pixel_polygons:
                # Get polygon exterior coordinates
                x, y = poly.exterior.xy
                
                # Plot polygon outline
                ax.plot(x, y, color='yellow', linewidth=1.5)
                
                # Fill polygon with red, semi-transparent
                ax.fill(x, y, color='red', alpha=0.5)
                
                # Add label at centroid
                cx, cy = poly.centroid.x, poly.centroid.y
                gap_id = gaps_gdf.loc[idx, 'id']
                ax.annotate(f"Gap {gap_id}", xy=(cx, cy), ha='center', fontsize=10, 
                           color='white', fontweight='bold',
                           bbox=dict(facecolor='black', alpha=0.7, boxstyle="round,pad=0.3"))
            
            # Add title and clean up
            plt.title("Forest Canopy Gap Analysis", fontsize=18, fontweight='bold')
            ax.set_axis_off()
            plt.tight_layout(pad=0)
            
            # Save high-resolution figure with minimal whitespace
            print(f"Saving visualization to {output_path}")
            plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
            plt.close()
            
            print(f"Visualization complete with {len(pixel_polygons)} gaps")
            return output_path
            
    except Exception as e:
        import traceback
        print(f"Error in visualization: {str(e)}")
        traceback.print_exc()
        
        # Create a simple fallback visualization
        try:
            print("Creating fallback visualization...")
            fig, ax = plt.subplots(figsize=(12, 8))
            gaps_gdf.plot(ax=ax, column='area_m2', cmap='viridis', 
                         legend=True, legend_kwds={'label': "Gap Area (m²)"})
            plt.title("Forest Canopy Gaps (Orthophoto Visualization Failed)")
            plt.savefig(output_path, dpi=300)
            plt.close()
            return output_path
        except:
            print("Fallback visualization also failed")
            return None


def export_to_csv(gaps_gdf, output_path):
    """
    Export gap analysis data to CSV
    
    Args:
        gaps_gdf: GeoDataFrame with gap information
        output_path: Path to save CSV file
    """
    # Create a DataFrame with only the attributes (not geometry)
    csv_df = gaps_gdf.drop(columns='geometry').copy()
    
    # Add centroid coordinates as separate columns
    csv_df['centroid_x'] = gaps_gdf.geometry.centroid.x
    csv_df['centroid_y'] = gaps_gdf.geometry.centroid.y
    
    # Save to CSV
    csv_df.to_csv(output_path, index_label='gap_id')
    
    return output_path


import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
import os
from pathlib import Path

def create_canopy_height_model(dsm_path, dtm_path, output_path=None):
    """
    Create a Canopy Height Model (CHM) by subtracting a Digital Terrain Model (DTM) 
    from a Digital Surface Model (DSM).
    
    Args:
        dsm_path: Path to the Digital Surface Model (DSM) GeoTIFF file
        dtm_path: Path to the Digital Terrain Model (DTM) GeoTIFF file
        output_path: Path where the CHM file will be saved. If None, will generate 
                    a path based on the DSM filename.
    
    Returns:
        Path to the created CHM file
    """
    
    # Generate output path if not provided
    if output_path is None:
        dsm_filename = Path(dsm_path).stem
        output_dir = Path(dsm_path).parent
        output_path = output_dir / f"chm_{dsm_filename}.tif"
    
    print(f"Creating Canopy Height Model...")
    
    try:
        # Open both raster files
        with rasterio.open(dsm_path) as dsm_src, rasterio.open(dtm_path) as dtm_src:
            print(f"Reading Digital Surface Model Data")
            dsm_data = dsm_src.read(1)
            print(f"Reading Digital Terrain Model Data")
            dtm_data = dtm_src.read(1)

            print(f"Checking If DSM And DTM Have Same Shape...")
            
            # Resample DTM to match DSM if they have different shapes
            if dsm_data.shape != dtm_data.shape:
                print(f"DSM Shape {dsm_data.shape} Differs From DTM Shape {dtm_data.shape}")
                print(f"Resampling DTM To Match DSM Shape...")
                
                dtm_resampled = np.zeros_like(dsm_data)
                
                reproject(
                    source=dtm_data,
                    destination=dtm_resampled,
                    src_transform=dtm_src.transform,
                    src_crs=dtm_src.crs,
                    dst_transform=dsm_src.transform,
                    dst_crs=dsm_src.crs,
                    resampling=Resampling.bilinear
                )
                
                print(f"DTM Resampling Complete")
                dtm_data = dtm_resampled
            else:
                print(f"DSM And DTM Have The Same Shape, No Resampling Needed")

            # Get NoData values from both rasters
            dsm_nodata = dsm_src.nodata
            dtm_nodata = dtm_src.nodata
            
            # Handle NoData values
            if dsm_nodata is not None:
                dsm_data = np.where(dsm_data == dsm_nodata, np.nan, dsm_data)
            if dtm_nodata is not None:
                dtm_data = np.where(dtm_data == dtm_nodata, np.nan, dtm_data)
            
            # Create CHM by subtracting DTM from DSM
            print(f"Calculating Vegetation Heights (DSM - DTM)...")
            chm_data = dsm_data - dtm_data
            
            # Replace negative values (where DTM > DSM) with 0
            # This can happen due to data errors or resolution mismatches
            chm_data = np.where(chm_data < 0, 0, chm_data)
            
            # Copy the metadata from DSM
            profile = dsm_src.profile.copy()
            
            # Save CHM to file
            print(f"Saving Canopy Height Model To {output_path}...")
            with rasterio.open(output_path, 'w', **profile) as chm_dst:
                chm_dst.write(chm_data, 1)
            
            print(f"Canopy Height Model Created Successfully")
            
            # Calculate basic statistics
            valid_data = chm_data[~np.isnan(chm_data)]
            if len(valid_data) > 0:
                stats = {
                    "min_height": np.nanmin(chm_data),
                    "max_height": np.nanmax(chm_data),
                    "mean_height": np.nanmean(chm_data),
                    "median_height": np.nanmedian(chm_data)
                }
                print(f"CHM Statistics: Min={stats['min_height']:.2f}m, Max={stats['max_height']:.2f}m, Mean={stats['mean_height']:.2f}m")
            
            return output_path
            
    except Exception as e:
        print(f"Error Creating Canopy Height Model: {str(e)}")
        raise


def createCHM():
  # Example usage
  dsm_file = r"C:\Users\bensp\OneDrive\Desktop\Code Box Two\Python\GeoDrone\ResilientRepo\Resilient_Geo_Drone\data\output\point_cloud\20250410_173750\dsm.tif"
  dtm_file = r"C:\Users\bensp\OneDrive\Desktop\Code Box Two\Python\GeoDrone\ResilientRepo\Resilient_Geo_Drone\data\output\point_cloud\20250410_173750\dtm.tif"
  output_file = r"C:\Users\bensp\OneDrive\Desktop\Code Box Two\Python\GeoDrone\ResilientRepo\Resilient_Geo_Drone\data\output\four_seventy_chm.tif"

  # Create CHM with custom output path
  chm_path = create_canopy_height_model(dsm_file, dtm_file, output_file)



if __name__ == "__main__":
    
    createCHM()

