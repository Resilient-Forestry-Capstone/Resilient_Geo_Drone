# === Required Libraries ===
# pip install rasterio numpy matplotlib scikit-image matplotlib-scalebar geopandas shapely
import yaml
import sys
import argparse
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as mticker
import matplotlib.patheffects as path_effects

import os
import csv
from datetime import datetime
from skimage.filters import gaussian, threshold_otsu
from skimage.measure import label, regionprops, find_contours
from skimage.morphology import binary_dilation, binary_erosion, disk
from matplotlib_scalebar.scalebar import ScaleBar
# Import for multi-page PDF
from matplotlib.backends.backend_pdf import PdfPages
# Import for GeoPackage/Vector Output
try:
    import geopandas as gpd
    from shapely.geometry import Polygon
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    print("Warning: 'geopandas' or 'shapely' not found. Vector file output disabled.")
    print("Install using: pip install geopandas shapely (or using conda)")


# === Helper Function for Area Classification ===
def get_area_bin_index(area_sqm, bins_sqm):
    """Assigns a 1-based bin index based on sorted area bins."""
    sorted_bins = sorted(bins_sqm) if bins_sqm else []
    if not sorted_bins: return 0 # Return 0 if no bins
    for i, upper_bound in enumerate(sorted_bins):
        if area_sqm <= upper_bound: return i + 1
    return len(sorted_bins) + 1 # Larger than last bin

# === Class Definitions ===

class RasterData:
    """Handles loading, cleaning, and accessing raster data and metadata."""
    # (Code identical to the previous version - robust CRS/unit handling)
    def __init__(self, filepath):
        self.filepath = filepath; self.data = None; self.transform = None; self.crs = None
        self.units_name = "unknown"; self.to_meters_factor = 1.0; self.pixel_size_x_crs = None
        self.pixel_size_y_crs = None; self.pixel_size_crs = None # Keep X dim for linear scale
        self._load_data()
    def _load_data(self):
        print(f"Loading raster data from: {self.filepath}")
        try:
            with rasterio.open(self.filepath) as src:
                self.data = src.read(1).astype(float)
                self.transform = src.transform; self.crs = src.crs # CRS object from rasterio
                if self.crs and self.crs.is_projected: self._determine_projected_units()
                elif self.crs: self.units_name = "degree"; print("Warn: Geographic CRS. Scale bar/area may be inaccurate.")
                else: self.units_name = 'meter'; print("Warn: CRS missing. Assuming meters.")
                print(f"CRS: {self.crs.to_string() if self.crs else 'None'}")
                print(f"Units: {self.units_name}, Factor to Meters: {self.to_meters_factor:.8f}")
                self.pixel_size_x_crs = abs(self.transform.a); self.pixel_size_y_crs = abs(self.transform.e)
                self.pixel_size_crs = self.pixel_size_x_crs
                if not np.isclose(self.pixel_size_x_crs, self.pixel_size_y_crs):
                    print(f"Warn: Non-square pixels ({self.pixel_size_x_crs:.4f}x{self.pixel_size_y_crs:.4f} {self.units_name}). Area calc uses both dims.")
                nodata = src.nodata
                if nodata is not None: print(f"Replacing NoData {nodata} with NaN."); self.data[np.isclose(self.data, nodata)] = np.nan
                else: print("No NoData value found.")
                print(f"Data loaded: {self.data.shape}, PixelSizeX: {self.pixel_size_crs:.4f} {self.units_name}")
        except FileNotFoundError: print(f"Error: File not found '{self.filepath}'."); raise
        except rasterio.RasterioIOError as e: print(f"Error reading file '{self.filepath}': {e}"); raise
        except Exception as e: print(f"Unexpected error loading raster: {e}"); raise
    def _determine_projected_units(self):
        if not self.crs: print("Warn: _determine... called but self.crs is None."); self.units_name = 'meter'; self.to_meters_factor = 1.0; return
        try:
            if hasattr(self.crs, 'linear_units') and self.crs.linear_units: self.units_name = self.crs.linear_units
            else:
                crs_info_str = str(self.crs).lower()
                if 'metre' in crs_info_str or 'meter' in crs_info_str: self.units_name = 'meter'
                elif 'us survey foot' in crs_info_str: self.units_name = 'US survey foot'
                elif 'foot' in crs_info_str: self.units_name = 'foot'
                else: self.units_name = 'meter'; print("Warn: Couldn't parse unit. Assume 'meter'.")
        except Exception as e: self.units_name = 'meter'; print(f"Error parsing CRS unit: {e}. Assume 'meter'.")
        unit_lower = self.units_name.lower()
        if unit_lower in ['metre', 'meter']: self.to_meters_factor = 1.0
        elif unit_lower == 'us survey foot': self.to_meters_factor = 0.304800609601219
        elif unit_lower == 'foot': self.to_meters_factor = 0.3048
        else: print(f"Warn: Unhandled unit '{self.units_name}'. Using factor 1.0.")
    def get_pixel_area_m2(self):
        if self.pixel_size_x_crs is None or self.pixel_size_y_crs is None or self.to_meters_factor is None: print("Error: Cannot calc pixel area."); return 0
        pixel_area_crs_units = self.pixel_size_x_crs * self.pixel_size_y_crs
        return pixel_area_crs_units * (self.to_meters_factor ** 2)
    def pixel_to_world(self, px, py):
        if self.transform is None: print("Error: Transform not available."); return None, None
        return self.transform * (px, py)

class GapAnalyzer:
    """Performs classification, morphology, and gap identification."""
    # (Code identical to the previous version - assigns area_bin_index)
    def __init__(self, config):
        self.config = config; self.binary_mask = None; self.labeled_image = None
        self.processed_mask = None; self.gaps = {}; self.actual_threshold = None
    def classify(self, raster_data):
        chm_data = raster_data.data; threshold_type = self.config.get("threshold_type", "manual")
        manual_fallback = self.config.get("manual_threshold", 2.0)
        if threshold_type == "manual": self.actual_threshold = self.config.get("manual_threshold", manual_fallback); print(f"Manual Thresh: {self.actual_threshold}")
        elif threshold_type == "otsu":
            valid_data = chm_data[~np.isnan(chm_data)]
            if valid_data.size > 0:
                try: self.actual_threshold = threshold_otsu(valid_data); print(f"Otsu Thresh: {self.actual_threshold:.4f}")
                except Exception as e: print(f"Otsu Error: {e}. Fallback: {manual_fallback}"); self.actual_threshold = manual_fallback
            else: print(f"No valid data for Otsu. Fallback: {manual_fallback}"); self.actual_threshold = manual_fallback
        else: print(f"Unknown thresh type. Fallback: {manual_fallback}"); self.actual_threshold = manual_fallback
        mask = np.zeros_like(chm_data, dtype=int); valid_mask = ~np.isnan(chm_data)
        mask[valid_mask] = np.where(chm_data[valid_mask] <= self.actual_threshold, 1, 0)
        self.binary_mask = mask; print(f"Bit mask created. Gap pixels: {np.sum(self.binary_mask)}")
        return self.binary_mask, self.actual_threshold
    def _apply_morphology(self, input_mask):
        processed = input_mask.copy()
        if self.config.get("apply_erosion", False): disk_r=self.config.get("erosion_size",1); print(f"Erosion: disk={disk_r}"); processed=binary_erosion(processed,disk(disk_r))
        if self.config.get("apply_dilation", False): disk_r=self.config.get("dilation_size",1); print(f"Dilation: disk={disk_r}"); processed=binary_dilation(processed,disk(disk_r))
        if self.config.get("apply_smoothing", False): sigma=self.config.get("smoothing_sigma",1.0); print(f"Smoothing: sigma={sigma}"); processed=gaussian(processed.astype(float),sigma=sigma,mode='reflect'); processed=(processed>0.5).astype(int)
        return processed
    def identify_regions(self, raster_data):
        """Labels regions, calculates properties, filters gaps, assigns area bin index, and returns processed mask."""
        if self.binary_mask is None: print("Error: Classify first."); return {}, None, None
        self.processed_mask = self._apply_morphology(self.binary_mask)
        self.labeled_image = label(self.processed_mask, background=0, connectivity=2)
        pixel_area_m2 = raster_data.get_pixel_area_m2()
        if np.isclose(pixel_area_m2, 0): print("Error: Pixel area zero."); return {}, self.labeled_image, self.processed_mask
        props = regionprops(self.labeled_image); print(f"Found {len(props)} initial regions.")
        self.gaps = {}; min_a = self.config.get("min_area", 0); max_a = self.config.get("max_area", float('inf'))
        area_bins = self.config.get("area_classification_bins_sqm", [])
        for prop in props:
            area_m2 = prop.area * pixel_area_m2
            if not (min_a <= area_m2 <= max_a): continue
            centroid_yx = prop.centroid; centroid_xy = centroid_yx[::-1]
            minr, minc, maxr, maxc = prop.bbox; bbox_xy = (minc, minr, maxc, maxr)
            area_bin_idx = get_area_bin_index(area_m2, area_bins)
            idx = len(self.gaps) + 1
            self.gaps[idx] = {
                'label': prop.label, 'bbox_pixels': bbox_xy, 'area_pixels': prop.area,
                'area_sq_meters': area_m2, 'centroid_pixel': centroid_xy,
                'area_bin_index': area_bin_idx
            }
        print(f"Identified {len(self.gaps)} gaps meeting criteria (Min:{min_a:.2f}m², Max:{max_a:.2f}m²).")
        return self.gaps, self.labeled_image, self.processed_mask

class ReportGenerator:
    """Generates the CSV data report with area classification index."""
    # (Code identical to the previous version - uses area_bin_index)
    def __init__(self, config):
        self.config = config
    def generate_csv(self, output_filename, raster_data, analyzer_results):
        print(f"Generating CSV data report: {output_filename}")
        gap_areas = analyzer_results.get('gaps', {}); actual_threshold = analyzer_results.get('threshold', None)
        transform = raster_data.transform
        if not gap_areas: print("No gaps found to write to CSV."); return
        headers = ["InputFile", "ProcessingTimestamp", "CRS_WKT", "LinearUnits", "PixelSizeX_CRS", "PixelSizeY_CRS",
                   "CRS_Unit_To_Meters", "ThresholdType", "ThresholdValue", "MinAreaFilter_m2", "MaxAreaFilter_m2",
                   "ErosionSize", "DilationSize", "SmoothingSigma", "OriginalGapID", "Area_m2", "Area_Pixels",
                   "AreaBinIndex", "CentroidX_CRS", "CentroidY_CRS", "BBoxMinX_px", "BBoxMinY_px", "BBoxMaxX_px", "BBoxMaxY_px"]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S'); input_file = self.config.get('chm_file', raster_data.filepath)
        crs_wkt = raster_data.crs.to_wkt() if raster_data.crs else 'None'; thresh_type = self.config.get('threshold_type','N/A')
        min_area_conf = self.config.get('min_area',0); max_area_conf = self.config.get('max_area',float('inf'))
        erosion_size_str = str(self.config.get("erosion_size", 'N/A')) if self.config.get("apply_erosion") else "N/A"
        dilation_size_str = str(self.config.get("dilation_size", 'N/A')) if self.config.get("apply_dilation") else "N/A"
        smoothing_sigma_str = str(self.config.get("smoothing_sigma", 'N/A')) if self.config.get("apply_smoothing") else "N/A"
        try:
            with open(output_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Summary Statistic", "Value"])
                num_gaps = len(gap_areas)
                writer.writerow(["Total Gaps Found Meeting Criteria", num_gaps])
                if num_gaps > 0:
                    all_areas_m2 = [data['area_sq_meters'] for data in gap_areas.values()]
                    total_gap_area_m2 = sum(all_areas_m2); avg_gap_area_m2 = total_gap_area_m2 / num_gaps
                    min_gap_area_m2 = min(all_areas_m2); max_gap_area_m2 = max(all_areas_m2)
                    writer.writerow(["Total Gap Area (m^2)", f"{total_gap_area_m2:.2f}"])
                    writer.writerow(["Average Gap Area (m^2)", f"{avg_gap_area_m2:.2f}"])
                    writer.writerow(["Smallest Gap Area (m^2)", f"{min_gap_area_m2:.2f}"])
                    writer.writerow(["Largest Gap Area (m^2)", f"{max_gap_area_m2:.2f}"])
                else: writer.writerow(["Total Gap Area (m^2)", "0.00"]); writer.writerow(["Average Gap Area (m^2)", "N/A"])
                writer.writerow([]); writer.writerow(["--- Detailed Gap Data ---"]); writer.writerow(headers)
                for original_id, gap_data in gap_areas.items():
                    centroid_px, centroid_py = gap_data['centroid_pixel']; cx_world, cy_world = raster_data.pixel_to_world(centroid_px, centroid_py)
                    minX_px, minY_px, maxX_px, maxY_px = gap_data['bbox_pixels']; area_bin_idx = gap_data.get('area_bin_index', 0)
                    row_data = [
                        input_file, timestamp, crs_wkt, raster_data.units_name,
                        f"{raster_data.pixel_size_x_crs:.6f}", f"{raster_data.pixel_size_y_crs:.6f}",
                        f"{raster_data.to_meters_factor:.8f}", thresh_type, f"{actual_threshold:.4f}",
                        f"{min_area_conf:.2f}", f"{max_area_conf:.2f}", erosion_size_str, dilation_size_str, smoothing_sigma_str,
                        original_id, f"{gap_data['area_sq_meters']:.4f}", gap_data['area_pixels'], area_bin_idx,
                        f"{cx_world:.4f}", f"{cy_world:.4f}", minX_px, minY_px, maxX_px, maxY_px
                    ]
                    writer.writerow(row_data)
            print(f"CSV data report successfully generated: {output_filename}")
        except IOError as e: print(f"Error writing CSV file {output_filename}: {e}")
        except Exception as e: print(f"Unexpected error during CSV generation: {e}")



class PlotGenerator:
    """Generates and saves the multi-page PDF plot visualization with area bin coloring."""
    def __init__(self, config):
        self.config = config
        try: self.colormap = plt.get_cmap('viridis')
        except ValueError: print("Warn: Colormap 'viridis' not found, defaulting to 'gray'."); self.colormap = plt.get_cmap('gray')

    def _plot_common_elements(self, ax, raster_data, im):
        """Adds common elements like axes labels, scale bar (in METERS) to an axes object."""
        # (Code identical to the previous version - scale bar uses METERS)
        axis_unit_label = raster_data.units_name
        if 'foot' in raster_data.units_name.lower(): axis_unit_label = 'ft'
        elif 'meter' in raster_data.units_name.lower(): axis_unit_label = 'm'
        elif 'degree' in raster_data.units_name.lower(): axis_unit_label = 'deg'
        ax.set_xlabel(f"Easting ({axis_unit_label})"); ax.set_ylabel(f"Northing ({axis_unit_label})")
        ax.tick_params(axis='x', labelsize=9, rotation=45); ax.tick_params(axis='y', labelsize=9)
        ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f')); ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'));
        ax.set_aspect('equal', adjustable='box')
        pixel_size_meters = raster_data.pixel_size_crs * raster_data.to_meters_factor
        if pixel_size_meters is not None and pixel_size_meters > 1e-9:
            print(f"Adding ScaleBar with pixel size: {pixel_size_meters:.4f} m/pixel, Unit Label: m")
            scalebar=ScaleBar(pixel_size_meters, 'm', location='lower right', frameon=True, color='black', box_color='white', box_alpha=0.8, font_properties={'size':'medium'})
            #ax.add_artist(scalebar)
        else: print("Skipping scale bar due to invalid pixel size in meters.")
        legend_elements = [patches.Patch(color=im.cmap(0), label='Canopy/Non-Gap'), patches.Patch(color=im.cmap(255), label='Potential Gap Area')]
        return legend_elements

    # --- NEW: Helper method for binary mask plot ---
    def _create_bit_mask_plot(self, raster_data, analyzer_results):
        """Creates the plot figure showing the binary mask after morphology."""
        print("Generating plot page 1 (Binary Mask - Post Morphology)...")
        fig, ax = plt.subplots(figsize=(12, 10))
        # Use processed_mask for background visualization
        processed_mask = analyzer_results.get('processed_mask')
        transform = raster_data.transform
        if processed_mask is None:
             print("Error: Missing processed mask for plot 1.")
             plt.close(fig) # Close empty figure
             return None

        height, width = processed_mask.shape # Use shape of displayed mask
        extent_list=[transform.c, transform.c+width*transform.a, transform.f+height*transform.e, transform.f]
        # Display the PROCESSED mask
        im = ax.imshow(processed_mask, cmap='gray', extent=tuple(extent_list), origin='upper', interpolation='nearest')

        # Add common elements (axes, scale bar, base legend)
        legend_elements = self._plot_common_elements(ax, raster_data, im)
        ax.legend(handles=legend_elements, loc='lower left', title="Legend", fontsize='small', framealpha=0.8)
        ax.set_title("Binary Mask (Post Morphology)")
        try: fig.tight_layout()
        except ValueError: print("Warn: tight_layout failed for plot 1.")
        return fig
    # --- END OF NEW METHOD ---

    def _create_original_style_plot(self, raster_data, analyzer_results):
        """Creates the plot figure with original gap styling on processed mask."""
        print("Generating plot page 2 (Original style Gaps)...") # Updated print
        fig, ax = plt.subplots(figsize=(12, 10))
        processed_mask = analyzer_results.get('processed_mask') # Use processed mask
        labels_img = analyzer_results.get('labeled_image')
        gap_areas = analyzer_results.get('gaps', {})
        transform = raster_data.transform
        if processed_mask is None or labels_img is None: print("Error: Missing data for plot 2."); plt.close(fig); return None

        outline_only = self.config.get("outline_gaps_only", True)
        face_color_standard = 'none' if outline_only else (0.2, 0.8, 0.2, 0.4)
        edge_color_standard = 'lime'
        height, width = processed_mask.shape
        extent_list=[transform.c, transform.c+width*transform.a, transform.f+height*transform.e, transform.f]
        im = ax.imshow(processed_mask, cmap='gray', extent=tuple(extent_list), origin='upper', interpolation='nearest') # Show processed mask

        for idx, gap_data in gap_areas.items():
            gap_label=gap_data['label']; gap_mask=(labels_img == gap_label)
            padded_mask = np.pad(gap_mask, pad_width=1, mode='constant', constant_values=0)
            contours = find_contours(padded_mask.astype(float), level=0.5)
            for contour in contours:
                adj_cont=contour-1;
                if len(adj_cont)<4: continue
                world_coords = [raster_data.pixel_to_world(c[1], c[0]) for c in adj_cont]
                if len(world_coords)>=3: patch = patches.Polygon(world_coords, closed=True, edgecolor=edge_color_standard, facecolor=face_color_standard, linewidth=1.5); ax.add_patch(patch)
            centroid_px, centroid_py = gap_data['centroid_pixel']; cx_world, cy_world = raster_data.pixel_to_world(centroid_px, centroid_py)
            ax.annotate(f"{idx}", (cx_world,cy_world), color='cyan', fontsize=9, ha='center', va='center', weight='bold', path_effects=[path_effects.withStroke(linewidth=1.5, foreground='black')])

        legend_elements = self._plot_common_elements(ax, raster_data, im)
        legend_elements.append(patches.Patch(edgecolor=edge_color_standard, facecolor=face_color_standard, linewidth=1.5, label='Identified Gap'))
        #ax.legend(handles=legend_elements, loc='lower left', title="Legend", fontsize='small', framealpha=0.8)
        ax.set_title("Identified Canopy Gaps (Original Style - Post Morphology)")
        try: fig.tight_layout()
        except ValueError: print("Warn: tight_layout failed for plot 2.")
        return fig

    def _create_classified_style_plot(self, raster_data, analyzer_results):
        """Creates the plot figure with gaps colored by area bin on processed mask."""
        print("Generating plot page 3 (Classified by Area Bin)...") # Updated print
        fig, ax = plt.subplots(figsize=(12, 10))
        processed_mask = analyzer_results.get('processed_mask') # Use processed mask
        labels_img = analyzer_results.get('labeled_image')
        gap_areas = analyzer_results.get('gaps', {})
        transform = raster_data.transform
        if processed_mask is None or labels_img is None: print("Error: Missing data for plot 3."); plt.close(fig); return None

        outline_only = self.config.get("outline_gaps_only", True)
        area_bins = self.config.get("area_classification_bins_sqm", [])
        bin_labels = {}
        if area_bins:
            num_bins_plus_one = len(area_bins) + 1
            sorted_bins = sorted(area_bins)
            for i, upper_bound in enumerate(sorted_bins): bin_labels[i+1] = f"{int(0 if i==0 else sorted_bins[i-1])}-{int(upper_bound)} m²"
            bin_labels[num_bins_plus_one] = f">{int(sorted_bins[-1])} m²"
        bin_labels[0] = "N/A (No Bins)"
        num_classes = len(area_bins) + 1
        color_map = {idx: self.colormap((idx-1) / max(1, num_classes-1)) for idx in range(1, num_classes + 1)}
        color_map[0] = (0.5, 0.5, 0.5, 1.0) # Grey RGBA for N/A

        height, width = processed_mask.shape
        extent_list=[transform.c, transform.c+width*transform.a, transform.f+height*transform.e, transform.f]
        im = ax.imshow(processed_mask, cmap='gray', extent=tuple(extent_list), origin='upper', interpolation='nearest') # Show processed mask

        present_bin_indices = set()
        for idx, gap_data in gap_areas.items():
            bin_index = gap_data.get('area_bin_index', 0); present_bin_indices.add(bin_index)
            plot_color = color_map.get(bin_index, color_map[0]); edge_color_classified = plot_color
            face_color_classified = 'none' if outline_only else (*plot_color[:3], 0.4)
            gap_label=gap_data['label']; gap_mask=(labels_img == gap_label); padded_mask = np.pad(gap_mask, pad_width=1, mode='constant', constant_values=0)
            contours = find_contours(padded_mask.astype(float), level=0.5)
            for contour in contours:
                adj_cont=contour-1;
                if len(adj_cont)<4: continue
                world_coords = [raster_data.pixel_to_world(c[1], c[0]) for c in adj_cont]
                if len(world_coords)>=3: patch = patches.Polygon(world_coords, closed=True, edgecolor=edge_color_classified, facecolor=face_color_classified, linewidth=1.5); ax.add_patch(patch)

        legend_elements = self._plot_common_elements(ax, raster_data, im)
        sorted_present_indices = sorted([idx for idx in present_bin_indices if idx != 0]);
        if 0 in present_bin_indices: sorted_present_indices.append(0)
        for bin_idx in sorted_present_indices:
            color = color_map[bin_idx]; label_text = bin_labels.get(bin_idx, f"Bin {bin_idx}")
            face_color_leg = 'none' if outline_only else (*color[:3], 0.4)
            legend_elements.append(patches.Patch(edgecolor=color, facecolor=face_color_leg, linewidth=1.5, label=f'Gap: {label_text}'))
        ax.legend(handles=legend_elements, loc='lower left', title="Legend (Area Class)", fontsize='small', framealpha=0.8); ax.set_title("Identified Canopy Gaps (Classified by Area - Post Morphology)")
        try: fig.tight_layout()
        except ValueError: print("Warn: tight_layout failed for plot 3.")
        return fig

    # --- MODIFIED: Generate 3 pages ---
    def generate_pdf_plot(self, output_filename, raster_data, analyzer_results):
        """Generates a multi-page PDF with mask, original, and classified plots."""
        print(f"Generating multi-page PDF plot: {output_filename}")
        fig0, fig1, fig2 = None, None, None # Initialize figures
        gap_areas = analyzer_results.get('gaps', {})
        area_bins = self.config.get("area_classification_bins_sqm", [])

        # No need to plot if no gaps were found AFTER filtering
        # But we might still want to see the binary mask? Let's plot page 1 regardless.
        # if not gap_areas: print("No gaps found, skipping plot generation."); return

        try:
            with PdfPages(output_filename) as pdf:
                # Create and save plot 0: Binary Mask
                fig0 = self._create_bit_mask_plot(raster_data, analyzer_results)
                if fig0:
                    try: pdf.savefig(fig0); print("   Page 1 (Binary Mask) saved to PDF.")
                    except Exception as e_save0: print(f"   ERROR saving page 1 to PDF: {e_save0}")
                    plt.close(fig0)

                # Only proceed if gaps exist
                if gap_areas:
                    # Create and save plot 1: Original Style
                    fig1 = self._create_original_style_plot(raster_data, analyzer_results)
                    if fig1:
                        try: pdf.savefig(fig1); print("   Page 2 (Original Style) saved to PDF.")
                        except Exception as e_save1: print(f"   ERROR saving page 2 to PDF: {e_save1}")
                        plt.close(fig1)

                    # Create and save plot 2: Classified Style (only if bins defined)
                    if area_bins:
                        fig2 = self._create_classified_style_plot(raster_data, analyzer_results)
                        if fig2:
                            try: pdf.savefig(fig2); print("   Page 3 (Classified Style) saved to PDF.")
                            except Exception as e_save2: print(f"   ERROR saving page 3 to PDF: {e_save2}")
                            plt.close(fig2)
                    else: print("Skipping classified plot page - 'area_classification_bins_sqm' empty.")
                else:
                    print("No gaps found meeting criteria, skipping gap plots (Pages 2 & 3).")


            print(f"Multi-page PDF plot generation attempt complete: {output_filename}")

        except Exception as e:
            print(f"Error during PDF plot generation process: {e}"); import traceback; traceback.print_exc()
        finally:
            # Ensure figures are closed if error occurred before explicit close
            if fig0 and plt.fignum_exists(fig0.number): plt.close(fig0)
            if fig1 and plt.fignum_exists(fig1.number): plt.close(fig1)
            if fig2 and plt.fignum_exists(fig2.number): plt.close(fig2)
    # --- END OF MODIFICATION ---


class VectorGenerator:
    """Generates a vector file (GeoPackage) from the identified gaps."""
    def __init__(self, config):
        self.config = config
    def generate_vector_file(self, output_filename, raster_data, analyzer_results):
        if not HAS_GEOPANDAS: print("Error: Cannot generate vector file - 'geopandas'/'shapely' not installed."); return
        print(f"Generating vector file: {output_filename}")
        gap_areas = analyzer_results.get('gaps', {}); labels_img = analyzer_results.get('labeled_image')
        crs = raster_data.crs
        if not gap_areas or labels_img is None: print("No gap data or labeled image available for vector generation."); return
        features = []
        for gap_id, gap_data in gap_areas.items():
            gap_label = gap_data['label']; gap_mask = (labels_img == gap_label)
            padded_mask = np.pad(gap_mask, pad_width=1, mode='constant', constant_values=0)
            contours = find_contours(padded_mask.astype(float), level=0.5)
            polygons = []
            for contour in contours:
                adjusted_contour = contour - 1
                if len(adjusted_contour) < 4: continue
                world_coords = [raster_data.pixel_to_world(c[1], c[0]) for c in adjusted_contour]
                try:
                    polygon = Polygon(world_coords)
                    if polygon.is_valid: polygons.append(polygon)
                    else: print(f"Warn: Invalid polygon geometry generated for gap {gap_id}, contour part. Skipping.")
                    
                except Exception as poly_e: print(f"Warn: Could not create polygon for gap {gap_id}, contour part. Error: {poly_e}")
            if not polygons: print(f"Warn: No valid polygon geometry found for gap {gap_id}. Skipping."); continue
            final_geom = max(polygons, key=lambda p: p.area)
            attributes = {'GapID': gap_id, 'Area_m2': gap_data.get('area_sq_meters'), 'Area_px': gap_data.get('area_pixels'),
                          'AreaBinIdx': gap_data.get('area_bin_index'), 'CentroidX': final_geom.centroid.x, 'CentroidY': final_geom.centroid.y}
            features.append({'geometry': final_geom, **attributes})
        if not features: print("No valid features created for vector file."); return
        try:
            gdf = gpd.GeoDataFrame(features, crs=crs)
            driver = "None"
            if output_filename.lower().endswith(".gpkg"): driver = "GPKG"
            elif output_filename.lower().endswith(".shp"): driver = "ESRI Shapefile"
            elif output_filename.lower().endswith(".geojson"): driver = "GeoJSON"
            gdf.to_file(output_filename, driver=driver) # Removed schema argument
            print(f"Vector file successfully generated: {output_filename} (Driver: {driver or 'Auto'})")
        except Exception as e: print(f"Error generating vector file {output_filename}: {e}"); import traceback; traceback.print_exc()


class GapAnalysisPipeline:
    """Orchestrates the gap analysis workflow."""
    def __init__(self, config_file):
        self.config_file = config_file; self.config = self._load_config()
        self.raster_data = None; self.analyzer = None; self.reporter = None
        self.plotter = None; self.vector_generator = None; self.results = {}

    def _load_config(self):
        print(f"Loading config: {self.config_file}")
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) # <--- MODIFIED HERE
        except FileNotFoundError:
            print(f"Error: Config file '{self.config_file}' not found.")
            raise
        except yaml.YAMLError as e: # <--- MODIFIED HERE for specific YAML errors
            print(f"Error parsing YAML config file '{self.config_file}': {e}")
            raise
        except Exception as e:
            print(f"Unexpected error loading config '{self.config_file}': {e}")
            raise

    # --- MODIFIED: Capture and pass processed_mask ---
    def run_analysis(self):
        """Executes the full analysis pipeline."""
        print("\n--- Starting Gap Identification Pipeline ---")
        if not self.config: return None
        chm_file = self.config.get("chm_file")
        if not chm_file: print("Error: 'chm_file' missing."); return None
        plot_filename = self.config.get("plot_filename", "gap_visualization.pdf"); data_filename = self.config.get("data_filename", "gap_data.csv")
        vector_filename = self.config.get("vector_filename", "gaps.gpkg")
        if not plot_filename.lower().endswith(".pdf"): print(f"Warn: plot_filename needs .pdf"); plot_filename+=".pdf"
        if not data_filename.lower().endswith(".csv"): print(f"Warn: data_filename needs .csv"); data_filename+=".csv"
        if not vector_filename.lower().endswith((".gpkg", ".shp", ".geojson")): print(f"Warn: vector_filename missing extension. Assuming .gpkg."); vector_filename+=".gpkg"
        try:
            # 1. Load Data
            self.raster_data = RasterData(chm_file)
            if self.raster_data.data is None or np.all(np.isnan(self.raster_data.data)): print("Error: Raster data empty/NaN."); return None

            # 2. Analyze Gaps
            self.analyzer = GapAnalyzer(self.config)
            binary_mask, threshold = self.analyzer.classify(self.raster_data)
            # Capture processed_mask here
            gaps, labels_img, processed_mask = self.analyzer.identify_regions(self.raster_data)

            # Store results including processed_mask
            self.results = {
                'binary_mask': binary_mask, # Original binary mask (before morphology)
                'processed_mask': processed_mask, # Mask after morphology (used for plotting background)
                'threshold': threshold,
                'gaps': gaps,
                'labeled_image': labels_img # Labels correspond to processed_mask
            }

            # 3. Generate CSV Report
            self.reporter = ReportGenerator(self.config)
            self.reporter.generate_csv(output_filename=data_filename, raster_data=self.raster_data, analyzer_results=self.results)

            # 4. Generate Vector File
            if gaps and HAS_GEOPANDAS:
                self.vector_generator = VectorGenerator(self.config)
                # Pass labels_img needed for contour finding inside vector generator
                self.vector_generator.generate_vector_file(output_filename=vector_filename, raster_data=self.raster_data, analyzer_results=self.results)
            elif not HAS_GEOPANDAS: print("Skipping vector file generation - geopandas not installed.")

            # 5. Generate Multi-Page PDF Plot
            # Always attempt to plot page 1 (binary mask) even if no gaps found after filtering
            self.plotter = PlotGenerator(self.config)
            # Pass the full results dict which includes the processed_mask
            self.plotter.generate_pdf_plot(output_filename=plot_filename, raster_data=self.raster_data, analyzer_results=self.results)
            # if gaps: # Plotting is now handled inside generate_pdf_plot
            # else: print("No gaps found, skipping plot generation.") # Message now inside generate_pdf_plot

            print("--- Gap Identification Pipeline Complete ---")
            return self.results.get('gaps')
        except Exception as e:
            print(f"\n--- Pipeline Error ---"); print(f"An critical error occurred: {e}")
            import traceback; traceback.print_exc(); return None
    # --- END OF MODIFICATION ---

# === Main Execution Block ===
# (Identical to previous version)
# === Main Execution Block ===
if __name__ == "__main__":
    default_config_file = 'config/gap_config.yaml' 
    parser = argparse.ArgumentParser(description="Identify canopy gaps from CHM GeoTIFF (OOP Version).")
    parser.add_argument('-c', '--config', default=default_config_file,
                        help=f"Config YAML path (default: {default_config_file})") # <--- MODIFIED HERE
    args = parser.parse_args()
    try:
        pipeline = GapAnalysisPipeline(args.config)
        gap_data_result = pipeline.run_analysis()
        if gap_data_result is not None:
            try:
                # Re-read config for filenames in summary (ensure this also uses YAML)
                with open(args.config, 'r') as f:
                    config = yaml.safe_load(f) # <--- MODIFIED HERE
                plot_filename = config.get("plot_filename", "gap_visualization.pdf")
                data_filename = config.get("data_filename", "gap_data.csv")
                vector_filename = config.get("vector_filename", "gaps.gpkg")
                # ... (rest of the filename handling logic remains the same)
            except Exception as e_cfg_read: # More specific exception handling for config re-read
                print(f"Warning: Could not re-read config for final summary: {e_cfg_read}")
                plot_filename = "[Config Error]"
                data_filename = "[Config Error]"
                vector_filename = "[Config Error]"

            num_gaps = len(gap_data_result)
            print(f"\n--- Final Summary ---")
            print(f"Processing completed using config: {args.config}")
            print(f"Generated PDF plot: '{plot_filename}'")
            print(f"Generated CSV data: '{data_filename}'")
            if HAS_GEOPANDAS: print(f"Generated Vector file: '{vector_filename}'")
            if num_gaps > 0:
                print(f"Found {num_gaps} gaps meeting criteria.")
            else:
                print("No gaps found meeting criteria.")
        else:
            print("\nProcessing did not complete successfully.")
    except Exception as main_e:
        print(f"\n--- Fatal Error ---")
        print(f"Failed to initialize or run pipeline: {main_e}")
        import traceback
        traceback.print_exc()