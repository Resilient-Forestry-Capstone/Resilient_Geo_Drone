<<<<<<< HEAD
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



# Class Which Creates A Gap Detector Using Depth-Map Estimation AI Model 
# As Well As Detects Gaps And Trees From A Orthophoto Image
class QuickGapDetector:

    def __init__(self, device='cuda'):
        # Create Our Depth-Map AI Model; Attempting To Utilize Cuda
        self.depth_pipe = pipeline(
            "depth-estimation", 
            model="depth-anything/Depth-Anything-V2-base-hf",
            device=device,
            use_fast=True
        )
        
    """
    
        Desc: This Function Takes In Our ortho_path And output_dir,
        Creating A Output Path From output_dir And Opening A Given Orthophoto 
        Image Provided In ortho_path. It Creates A Depth-Map From A Loaded AI
        Model And Then Looks For Gaps And Trees In The Depth-Map Through 
        Thresholding And Local Maxima Detection. It Converts The Pixel
        Coordinates Into Geographic Coordinates And Saves The Results As
        GeoJSON In output_dir. It Also Saves Debug Images In output_dir.

        Preconditions:
            1. ortho_path: Path To Orthophoto Image
            2. output_dir: Path To Output Directory
            3. Both ortho_path And output_dir Must Be Valid Paths

        Postconditions:
            1. Runs Our Gap Detection Pipeline
            2. Saves Results As GeoJSON In output_dir
            3. Saves Debug Images In output_dir
            4. Creates output_dir If It Does Not Exist
    
    """
    def run(self, ortho_path: Path, output_dir: Path = Path("gap_results")):
        # Create Our Output Directory If It Does Not Exist
        output_dir.mkdir(exist_ok=True)
        
        # Open Our Orthophoto Image Using Rasterio For Interfacing
        with rasterio.open(ortho_path) as src:
            ortho_img = src.read([1,2,3]).transpose(1,2,0)  # RGB
            transform = src.transform
            crs = src.crs
        
        # Generate Depth Map From Orthophoto Image Using PIL
        depth_map = self._generate_depth_map(ortho_img)
        
        # Look In Our Depth Map For Gaps And Trees
        gap_mask = self._find_gaps(depth_map)
        trees = self._find_sparse_trees(depth_map, gap_mask)
        
        # Convert Pixel Coordinates Into Geographic Coordinates
        gap_polygons = self._mask_to_polygons(gap_mask, transform)
        tree_points = self._pixels_to_coords(trees, transform)
        
        # Save Our Results As GeoJSON
        results_path = output_dir / "gap_analysis.geojson"
        self._save_geojson(gap_polygons, tree_points, crs, results_path)
        
        # Visual debug
        self._save_debug_images(ortho_img, depth_map, gap_mask, output_dir)
        
        print(f"Analysis complete. Results saved to {output_dir}")


    """
    
        Desc: This Function Takes In rgb_image And Creates A Depth Map
        From The NumPy Array Image Using Our Depth-Map Estimation AI Model. It Returns
        The Depth Map As A Numpy Array.

        Preconditions:
            1. rgb_img: NumPy Array Representing RGB Image

        Postconditions:
            1. Creates A Depth Map From RGB Image
            2. Returns Depth Map As Numpy Array
    
    """
    def _generate_depth_map(self, rgb_img: np.ndarray) -> np.ndarray:
        # Convert RGB Image To PIL Image And Run Depth-Map Estimation
        pil_img = Image.fromarray(rgb_img)
        return np.array(self.depth_pipe(pil_img)["depth"])


    """
    
        Desc: This Function Takes In Our depth_map As A NumPy Array And
        Thresholds The Depth Map To Identify Gaps. It Returns The Thresholded
        Depth Map As A NumPy Array. The Thresholding Is Done By Blurring The
        Depth Map And Then Applying Otsu's Thresholding Algorithm. The Result
        Is A Binary Mask Of Gaps.

        Preconditions:
            1. depth_map: NumPy Array Representing Depth Map
        
        Postconditions:
            1. Thresholds Depth Map To Identify Gaps
            2. Returns Thresholded Depth Map As Numpy Array
            3. Returns A Binary Mask Of Gaps
    
    """
    def _find_gaps(self, depth_map: np.ndarray) -> np.ndarray:
        # Apply Gaussian Blur To Depth Map
        blurred = cv2.GaussianBlur(depth_map, (15,15), 0)

        # Apply Otsu's Thresholding Algorithm To Find Gaps
        _, thresh = cv2.threshold(blurred, 0, 255, 
                                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Provide Binary Mask Of Gaps
        return thresh.astype(bool)


    """
    
        Desc: This Function Takes In Our depth_map And gap_mask As NumPy
        Arrays And Locates Potential Trees In Gaps Using Local Maxima Detection.
        It Returns The Pixel Coordinates Of The Trees As A Numpy Array. The
        Local Maxima Detection Is Done By Dilating The Depth Map And Then Finding
        The Local Maxima. Dilating Causes The Local Maxima To Be The Peaks In
        The Depth Map.

        Preconditions:
            1. depth_map: NumPy Array Representing Depth Map
            2. gap_mask: NumPy Array Representing Binary Mask Of Gaps
            3. gap_mask And depth_map Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Locates Potential Trees In Gaps Using Local Maxima Detection
            2. Returns Pixel Coordinates Of Trees As Numpy Array
    
    """
    def _find_sparse_trees(self, depth_map: np.ndarray, 
                         gap_mask: np.ndarray) -> np.ndarray:
        # Create Kernel For Dilation With 15x15 Window
        kernel = np.ones((15,15), np.uint8)

        # Dilate Depth Map To Find Local Maxima
        dilated = cv2.dilate(depth_map, kernel)

        # Find Local Maxima In Dilated Depth Map
        peaks = (depth_map == dilated) & gap_mask
        return np.argwhere(peaks)


    """
    
        Desc: This Function Takes In mask And transform And Converts The
        Binary Mask To Simplified Polygons. The Conversion Is Done 
        By Finding The Contours Of The Mask
        And Then Simplifying The Contours To Polygons. 

        Preconditions:
            1. mask: NumPy Array Representing Binary Mask
            2. transform: Rasterio Transform Object
            3. mask And transform Must Be Of The Same Orthophoto Image
        
        Postconditions:
            1. Converts Binary Mask To Simplified Polygons
            2. Returns A List Of Simplified Polygons
    
    """
    def _mask_to_polygons(self, mask: np.ndarray, transform) -> list:
        # Find Contours Of Mask
        contours, _ = cv2.findContours(mask.astype(np.uint8),
                                     cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)
        
        # Simplify Contours To Polygons
        return [self._contour_to_coords(c, transform) for c in contours]


    """
    
        Desc: This Function Takes In contour And transform And Converts
        The Pixel Contour To Geographic Coordinates. It Returns The
        Geographic Coordinates As A List Of Tuples In The Form (x,y).

        Preconditions:
            1. contour: NumPy Array Representing Contour
            2. transform: Rasterio Transform Object
            3. contour And transform Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Converts Pixel Contour To Geographic Coordinates
            2. Returns A List Of Geographic Coordinates
    
    """
    def _contour_to_coords(self, contour: np.ndarray, transform) -> list:
        # Convert Contour To Geographic Coordinates
        return [transform * (point[0][0], point[0][1]) for point in contour]
       

    """
    
        Desc: This Function Takes In pixels And transform And Converts
        The Pixel Coordinates To Geographic Points. It Returns The
        Geographic Points As A List Of Tuples In The Form (x,y).

        Preconditions:
            1. pixels: NumPy Array Representing Pixel Coordinates
            2. transform: Rasterio Transform Object
            3. pixels And transform Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Converts Pixel Coordinates To Geographic Points
            2. Returns A List Of Geographic Points
    
    """
    def _pixels_to_coords(self, pixels: np.ndarray, transform) -> list:
        # Convert Pixel Coordinates To Geographic Points
        return [transform * (x,y) for y,x in pixels]


    """
    
        Desc: This Function Takes In polygons, points, crs, And path
        From A Provided Orthophoto Image And 
        Saves The Results As GeoJSON With CRS Information. The
        Polygons Are Saved As Gaps And The Points Are Saved As Sparse Trees.
        The CRS Information Is Also Saved In The GeoJSON File. 

        Preconditions:
            1. polygons: List Of Simplified Polygons Representing Gaps
            2. points: List Of Geographic Points Representing Sparse Trees
            3. crs: Rasterio CRS Object
            4. path: Path To Save GeoJSON File
            5. polygons, points, crs, And path All Represent The Same Orthophoto Image

        Postconditions:
            1. Saves Results As GeoJSON With CRS Information
            2. Polygons Are Saved As Gaps And Points Are Saved As Sparse Trees

    
    """
    def _save_geojson(self, polygons, points, crs, path: Path):
        # Collection Of All Features We Will Save
        features = []
        
        # Add Polygons And Polygons To Features 
        for poly in polygons:
            features.append(geojson.Feature(
                geometry=geojson.Polygon([[(x,y) for x,y in poly]]),
                properties={"type": "gap"}
            ))
            
        # Add Points To Features
        for x,y in points:
            features.append(geojson.Feature(
                geometry=geojson.Point((x,y)),
                properties={"type": "sparse_tree"}
            ))
            
        # Create Our Feature Collection With CRS Information
        collection = geojson.FeatureCollection(features, crs={
            "type": "name",
            "properties": {"name": crs.to_string()}
        })
        
        # Save Our GeoJSON File
        with open(path, 'w') as f:
            geojson.dump(collection, f)


    """
    
        Desc: This Function Takes In ortho, depth, mask, And output_dir
        And Saves Visualization Of Processing Steps. The Visualization
        Includes The Orthophoto, Depth Map, And Gap Mask. The Visualization
        Is Saved As A PNG Image In output_dir.

        Preconditions:
            1. ortho: NumPy Array Representing Orthophoto Image
            2. depth: NumPy Array Representing Depth Map
            3. mask: NumPy Array Representing Gap Mask
            4. output_dir: Path To Save Debug Visualization
            5. ortho, depth, mask, And output_dir Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Saves Visualization Of Processing Steps As PNG Image
    
    """
    def _save_debug_images(self, ortho, depth, mask, output_dir):
        # Create A Figure Plot With The Size Of 18x6 Inches
        plt.figure(figsize=(18,6))
        
        # Create Subplot On Figure For Orthophoto
        plt.subplot(131)
        plt.imshow(ortho)
        plt.title('Orthophoto')
        
        # Create Subplot On Figure For Depth Map
        plt.subplot(132)
        plt.imshow(depth, cmap='viridis')
        plt.title('Depth Map')
        
        # Create Subplot On Figure For Gap Mask
        plt.subplot(133)
        plt.imshow(mask, cmap='gray')
        plt.title('Gap Mask')
        
        # Save Our Debug Visualization With Tight Bounds
        plt.savefig(output_dir/'debug_visualization.png', bbox_inches='tight')
        plt.close()




if __name__ == "__main__":
    # Check For Correct Usage
    if len(sys.argv) < 2:
        print("Usage: python gap_detection_standalone.py <orthophoto_path> [output_dir]")
        sys.exit(1)
        
    # Get Our Orthophoto Path And Output Directory
    ortho_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()/"gap_results"
    
    # Run Our Gap Detection Pipeline
    detector = QuickGapDetector(device='cuda' if torch.cuda.is_available() else 'cpu')
=======
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



# Class Which Creates A Gap Detector Using Depth-Map Estimation AI Model 
# As Well As Detects Gaps And Trees From A Orthophoto Image
class QuickGapDetector:

    def __init__(self, device='cuda'):
        # Create Our Depth-Map AI Model; Attempting To Utilize Cuda
        self.depth_pipe = pipeline(
            "depth-estimation", 
            model="depth-anything/Depth-Anything-V2-base-hf",
            device=device,
            use_fast=True
        )
        
    """
    
        Desc: This Function Takes In Our ortho_path And output_dir,
        Creating A Output Path From output_dir And Opening A Given Orthophoto 
        Image Provided In ortho_path. It Creates A Depth-Map From A Loaded AI
        Model And Then Looks For Gaps And Trees In The Depth-Map Through 
        Thresholding And Local Maxima Detection. It Converts The Pixel
        Coordinates Into Geographic Coordinates And Saves The Results As
        GeoJSON In output_dir. It Also Saves Debug Images In output_dir.

        Preconditions:
            1. ortho_path: Path To Orthophoto Image
            2. output_dir: Path To Output Directory
            3. Both ortho_path And output_dir Must Be Valid Paths

        Postconditions:
            1. Runs Our Gap Detection Pipeline
            2. Saves Results As GeoJSON In output_dir
            3. Saves Debug Images In output_dir
            4. Creates output_dir If It Does Not Exist
    
    """
    def run(self, ortho_path: Path, output_dir: Path = Path("gap_results")):
        # Create Our Output Directory If It Does Not Exist
        output_dir.mkdir(exist_ok=True)
        
        # Open Our Orthophoto Image Using Rasterio For Interfacing
        with rasterio.open(ortho_path) as src:
            ortho_img = src.read([1,2,3]).transpose(1,2,0)  # RGB
            transform = src.transform
            crs = src.crs
        
        # Generate Depth Map From Orthophoto Image Using PIL
        depth_map = self._generate_depth_map(ortho_img)
        
        # Look In Our Depth Map For Gaps And Trees
        gap_mask = self._find_gaps(depth_map)
        trees = self._find_sparse_trees(depth_map, gap_mask)
        
        # Convert Pixel Coordinates Into Geographic Coordinates
        gap_polygons = self._mask_to_polygons(gap_mask, transform)
        tree_points = self._pixels_to_coords(trees, transform)
        
        # Save Our Results As GeoJSON
        results_path = output_dir / "gap_analysis.geojson"
        self._save_geojson(gap_polygons, tree_points, crs, results_path)
        
        # Visual debug
        self._save_debug_images(ortho_img, depth_map, gap_mask, output_dir)
        
        print(f"Analysis complete. Results saved to {output_dir}")


    """
    
        Desc: This Function Takes In rgb_image And Creates A Depth Map
        From The NumPy Array Image Using Our Depth-Map Estimation AI Model. It Returns
        The Depth Map As A Numpy Array.

        Preconditions:
            1. rgb_img: NumPy Array Representing RGB Image

        Postconditions:
            1. Creates A Depth Map From RGB Image
            2. Returns Depth Map As Numpy Array
    
    """
    def _generate_depth_map(self, rgb_img: np.ndarray) -> np.ndarray:
        # Convert RGB Image To PIL Image And Run Depth-Map Estimation
        pil_img = Image.fromarray(rgb_img)
        return np.array(self.depth_pipe(pil_img)["depth"])


    """
    
        Desc: This Function Takes In Our depth_map As A NumPy Array And
        Thresholds The Depth Map To Identify Gaps. It Returns The Thresholded
        Depth Map As A NumPy Array. The Thresholding Is Done By Blurring The
        Depth Map And Then Applying Otsu's Thresholding Algorithm. The Result
        Is A Binary Mask Of Gaps.

        Preconditions:
            1. depth_map: NumPy Array Representing Depth Map
        
        Postconditions:
            1. Thresholds Depth Map To Identify Gaps
            2. Returns Thresholded Depth Map As Numpy Array
            3. Returns A Binary Mask Of Gaps
    
    """
    def _find_gaps(self, depth_map: np.ndarray) -> np.ndarray:
        # Apply Gaussian Blur To Depth Map
        blurred = cv2.GaussianBlur(depth_map, (15,15), 0)

        # Apply Otsu's Thresholding Algorithm To Find Gaps
        _, thresh = cv2.threshold(blurred, 0, 255, 
                                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Provide Binary Mask Of Gaps
        return thresh.astype(bool)


    """
    
        Desc: This Function Takes In Our depth_map And gap_mask As NumPy
        Arrays And Locates Potential Trees In Gaps Using Local Maxima Detection.
        It Returns The Pixel Coordinates Of The Trees As A Numpy Array. The
        Local Maxima Detection Is Done By Dilating The Depth Map And Then Finding
        The Local Maxima. Dilating Causes The Local Maxima To Be The Peaks In
        The Depth Map.

        Preconditions:
            1. depth_map: NumPy Array Representing Depth Map
            2. gap_mask: NumPy Array Representing Binary Mask Of Gaps
            3. gap_mask And depth_map Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Locates Potential Trees In Gaps Using Local Maxima Detection
            2. Returns Pixel Coordinates Of Trees As Numpy Array
    
    """
    def _find_sparse_trees(self, depth_map: np.ndarray, 
                         gap_mask: np.ndarray) -> np.ndarray:
        # Create Kernel For Dilation With 15x15 Window
        kernel = np.ones((15,15), np.uint8)

        # Dilate Depth Map To Find Local Maxima
        dilated = cv2.dilate(depth_map, kernel)

        # Find Local Maxima In Dilated Depth Map
        peaks = (depth_map == dilated) & gap_mask
        return np.argwhere(peaks)


    """
    
        Desc: This Function Takes In mask And transform And Converts The
        Binary Mask To Simplified Polygons. The Conversion Is Done 
        By Finding The Contours Of The Mask
        And Then Simplifying The Contours To Polygons. 

        Preconditions:
            1. mask: NumPy Array Representing Binary Mask
            2. transform: Rasterio Transform Object
            3. mask And transform Must Be Of The Same Orthophoto Image
        
        Postconditions:
            1. Converts Binary Mask To Simplified Polygons
            2. Returns A List Of Simplified Polygons
    
    """
    def _mask_to_polygons(self, mask: np.ndarray, transform) -> list:
        # Find Contours Of Mask
        contours, _ = cv2.findContours(mask.astype(np.uint8),
                                     cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)
        
        # Simplify Contours To Polygons
        return [self._contour_to_coords(c, transform) for c in contours]


    """
    
        Desc: This Function Takes In contour And transform And Converts
        The Pixel Contour To Geographic Coordinates. It Returns The
        Geographic Coordinates As A List Of Tuples In The Form (x,y).

        Preconditions:
            1. contour: NumPy Array Representing Contour
            2. transform: Rasterio Transform Object
            3. contour And transform Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Converts Pixel Contour To Geographic Coordinates
            2. Returns A List Of Geographic Coordinates
    
    """
    def _contour_to_coords(self, contour: np.ndarray, transform) -> list:
        # Convert Contour To Geographic Coordinates
        return [transform * (point[0][0], point[0][1]) for point in contour]
       

    """
    
        Desc: This Function Takes In pixels And transform And Converts
        The Pixel Coordinates To Geographic Points. It Returns The
        Geographic Points As A List Of Tuples In The Form (x,y).

        Preconditions:
            1. pixels: NumPy Array Representing Pixel Coordinates
            2. transform: Rasterio Transform Object
            3. pixels And transform Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Converts Pixel Coordinates To Geographic Points
            2. Returns A List Of Geographic Points
    
    """
    def _pixels_to_coords(self, pixels: np.ndarray, transform) -> list:
        # Convert Pixel Coordinates To Geographic Points
        return [transform * (x,y) for y,x in pixels]


    """
    
        Desc: This Function Takes In polygons, points, crs, And path
        From A Provided Orthophoto Image And 
        Saves The Results As GeoJSON With CRS Information. The
        Polygons Are Saved As Gaps And The Points Are Saved As Sparse Trees.
        The CRS Information Is Also Saved In The GeoJSON File. 

        Preconditions:
            1. polygons: List Of Simplified Polygons Representing Gaps
            2. points: List Of Geographic Points Representing Sparse Trees
            3. crs: Rasterio CRS Object
            4. path: Path To Save GeoJSON File
            5. polygons, points, crs, And path All Represent The Same Orthophoto Image

        Postconditions:
            1. Saves Results As GeoJSON With CRS Information
            2. Polygons Are Saved As Gaps And Points Are Saved As Sparse Trees

    
    """
    def _save_geojson(self, polygons, points, crs, path: Path):
        # Collection Of All Features We Will Save
        features = []
        
        # Add Polygons And Polygons To Features 
        for poly in polygons:
            features.append(geojson.Feature(
                geometry=geojson.Polygon([[(x,y) for x,y in poly]]),
                properties={"type": "gap"}
            ))
            
        # Add Points To Features
        for x,y in points:
            features.append(geojson.Feature(
                geometry=geojson.Point((x,y)),
                properties={"type": "sparse_tree"}
            ))
            
        # Create Our Feature Collection With CRS Information
        collection = geojson.FeatureCollection(features, crs={
            "type": "name",
            "properties": {"name": crs.to_string()}
        })
        
        # Save Our GeoJSON File
        with open(path, 'w') as f:
            geojson.dump(collection, f)


    """
    
        Desc: This Function Takes In ortho, depth, mask, And output_dir
        And Saves Visualization Of Processing Steps. The Visualization
        Includes The Orthophoto, Depth Map, And Gap Mask. The Visualization
        Is Saved As A PNG Image In output_dir.

        Preconditions:
            1. ortho: NumPy Array Representing Orthophoto Image
            2. depth: NumPy Array Representing Depth Map
            3. mask: NumPy Array Representing Gap Mask
            4. output_dir: Path To Save Debug Visualization
            5. ortho, depth, mask, And output_dir Must Be Of The Same Orthophoto Image

        Postconditions:
            1. Saves Visualization Of Processing Steps As PNG Image
    
    """
    def _save_debug_images(self, ortho, depth, mask, output_dir):
        # Create A Figure Plot With The Size Of 18x6 Inches
        plt.figure(figsize=(18,6))
        
        # Create Subplot On Figure For Orthophoto
        plt.subplot(131)
        plt.imshow(ortho)
        plt.title('Orthophoto')
        
        # Create Subplot On Figure For Depth Map
        plt.subplot(132)
        plt.imshow(depth, cmap='viridis')
        plt.title('Depth Map')
        
        # Create Subplot On Figure For Gap Mask
        plt.subplot(133)
        plt.imshow(mask, cmap='gray')
        plt.title('Gap Mask')
        
        # Save Our Debug Visualization With Tight Bounds
        plt.savefig(output_dir/'debug_visualization.png', bbox_inches='tight')
        plt.close()




if __name__ == "__main__":
    # Check For Correct Usage
    if len(sys.argv) < 2:
        print("Usage: python gap_detection_standalone.py <orthophoto_path> [output_dir]")
        sys.exit(1)
        
    # Get Our Orthophoto Path And Output Directory
    ortho_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()/"gap_results"
    
    # Run Our Gap Detection Pipeline
    detector = QuickGapDetector(device='cuda' if torch.cuda.is_available() else 'cpu')
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
    detector.run(ortho_path, output_dir)