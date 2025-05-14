from pathlib import Path
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QFormLayout,
                           QSpinBox, QLineEdit, QComboBox, QPushButton,
                           QDoubleSpinBox, QListWidget, QHBoxLayout,
                           QFileDialog, QMessageBox, QGroupBox, QLabel,
                           QCheckBox, QInputDialog, QTextEdit, QListWidgetItem, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
import yaml
from datetime import datetime



"""

    Desc: This Module Provides A Settings Window For The User To Adjust
    The Configuration Parameters Of The Pipeline. The Settings Window
    Will Allow The User To Adjust Preprocessing, Point Cloud, And Geospatial
    Configuration Parameters. The Window Is Formatted As A Tabbed Widget
    With Each Tab Representative Of A Configuration Section. 


"""
class SettingsWindow(QWidget):

    """
    
        Desc: Initializes Our Settings Window With A Configuration Path
        For Loading Of Our Configuration Parameters. The Settings Window
        Will Allow The User To Adjust Preprocessing, Point Cloud, And
        Geospatial Configuration Parameters. The Intializer Also
        Establishes Two Buttons For Saving And Resetting The Settings.
        Our Window Is Layed Out In A Vertical Layout With Tabs For Each
        Configuration Section.

        Preconditions:
            1. config_path: Path To Configuration File
            2. config_path Must Be A Valid Path
        
        Postconditions:
            1. Set Our Configuration Path
            2. Load Our Configuration Parameters
            3. Create A Tabbed Widget For Each Configuration Section
            4. Add Buttons For Saving And Resetting The Settings
            5. Set-Up A Vertical Layout For Our Window
    
    """
    def __init__(self, config_path = Path(__file__).parent.parent.parent / "config/config.yaml"):
        # Initialize QWidget Superclass
        super().__init__()

        # Set-Up Our Config Path
        self.config_path = config_path
        self.logs_dir = Path(__file__).parent.parent.parent / "logs"
        self.env_widgets = {}

        # Set-Up Our Pop-Up Window
        self.setWindowTitle("Settings")
        self.setMinimumSize(800, 600)

        # Load Current Config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Set-Up A Vertical Layout (Make Our Overall Settings In A Stacked Order)
        layout = QVBoxLayout(self)
        
        # Create Our Top Tab Widgets
        tabs = QTabWidget()
        self.add_preprocessing_tab(tabs)
        self.add_point_cloud_tab(tabs)
        self.add_geospatial_tab(tabs)
        self.add_logs_tab(tabs)
        layout.addWidget(tabs)

        # Buttons Formatting
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("Save Settings")
        reset_btn = QPushButton("Reset to Defaults")

        # Connect Them To Their Function
        save_btn.clicked.connect(self.save_settings)
        reset_btn.clicked.connect(self.reset_settings)

        # Add The Buttons To The Layout
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(reset_btn)

        # Add The Buttons Layout To The Main Layout
        layout.addLayout(buttons_layout)


    """
    
        Desc: Function Adds A Tab For Preprocessing Settings. The Tab
        Will Allow The User To Adjust The Supported Image Formats, Minimum
        Resolution, Blur Threshold, Brightness Range, And Maximum Workers
        For Preprocessing Images. The Parts Are All Formatted In A 2-Column
        Layout For Easy User Access. It Also Provides Buttons For The Adding
        And Removing Of Supported Image Formats.

        Preconditions:
            1. tabs: QTabWidget Object
        
        Postconditions:
            1. Add A Tab For Preprocessing Settings To The Tab Widget
            2. Add Supported Image Formats, Minimum Resolution, Blur Threshold, Brightness Range, And Maximum Workers To The Tab
    
    """
    def add_preprocessing_tab(self, tabs):
        # Create A Tab For Preprocessing
        tab = QWidget()

        # Create A Form Layout
        layout = QFormLayout(tab)

        # Supported Formats Of Image
        formats_group = QGroupBox("Supported Formats")
        formats_layout = QVBoxLayout()

        # Create A List Widget
        self.formats_list = QListWidget()
        # Add The Supported Formats To The List
        self.formats_list.addItems(self.config['preprocessing']['supported_formats'])

        # Create Buttons For Adding And Removing Image Formats (.png, .jpg, ...)
        format_buttons = QHBoxLayout()
        add_format_btn = QPushButton("Add")
        remove_format_btn = QPushButton("Remove")
        
        # Connect The Buttons To Their Functions
        add_format_btn.clicked.connect(self.add_format)
        remove_format_btn.clicked.connect(self.remove_format)

        # Add The Buttons To Our Layout
        format_buttons.addWidget(add_format_btn)
        format_buttons.addWidget(remove_format_btn)

        # Add Widgets To The Layout For The Row
        formats_layout.addWidget(self.formats_list)

        # Add The Buttons Layout To The Layout Of The Image Formats
        formats_layout.addLayout(format_buttons)
        formats_group.setLayout(formats_layout)

        # Add The Formats Group To The Main Layout
        layout.addRow(formats_group)

        # Now Set-Up For Our Resolution Row
        res_group = QGroupBox("Minimum Resolution")
        res_layout = QFormLayout()

        # Create Spin Boxes For Width And Height
        self.width = QSpinBox()
        self.height = QSpinBox()

        # Set The Range Of The Spin Boxes
        self.width.setRange(0, 10000)
        self.height.setRange(0, 10000)

        # Set The Default Values
        self.width.setValue(self.config['preprocessing']['min_resolution'][0])
        self.height.setValue(self.config['preprocessing']['min_resolution'][1])

        # Add The Spin Boxes To The Layout
        res_layout.addRow("Width:", self.width)
        res_layout.addRow("Height:", self.height)

        # Add The Row To The Group
        res_group.setLayout(res_layout)
        layout.addRow(res_group)

        # Set-Up Processing Settings Row
        proc_group = QGroupBox("Processing Settings")
        proc_layout = QFormLayout()

        # Create Spin Boxes For Blur, Brightness, And Max Workerss
        self.blur = QSpinBox()
        self.blur.setRange(0, 1000)

        self.blur.setValue(self.config['preprocessing']['blur_threshold'])
        proc_layout.addRow("Blur Threshold:", self.blur)

        self.bright_min = QSpinBox()
        self.bright_max = QSpinBox()
        self.bright_min.setRange(0, 255)
        self.bright_max.setRange(0, 255)

        self.bright_min.setValue(self.config['preprocessing']['brightness_range'][0])
        self.bright_max.setValue(self.config['preprocessing']['brightness_range'][1])

        proc_layout.addRow("Min Brightness:", self.bright_min)
        proc_layout.addRow("Max Brightness:", self.bright_max)

        self.max_workers = QSpinBox()
        self.max_workers.setRange(1, 32)

        self.max_workers.setValue(self.config['preprocessing']['max_workers'])
        proc_layout.addRow("Max Workers:", self.max_workers)

        # Add The Processing Settings Row To The Group
        proc_group.setLayout(proc_layout)
        layout.addRow(proc_group)

        # Finally Implement Our Tab To The Main Tab
        tabs.addTab(tab, "Preprocessing")


    """

        Desc: Function Adds A Tab For Point Cloud Settings. The Tab
        Will Allow The User To Adjust The WebODM Connection Settings
        And Environment Settings For Point Cloud Generation. The Tab
        Will Also Allow The User To Adjust The Quality, Min Features,
        Matcher, And Max Concurrency For Each Environment. The Tab
        Will Also Allow The User To Adjust The Point Cloud Quality,
        Mesh Quality, And Ignore GSD For Foggy Environments.

        Preconditions:
            1. tabs: QTabWidget Object
        
        Postconditions:
            1. Add A Tab For Point Cloud Settings To The Tab Widget
            2. Add WebODM Connection Settings And Environment Settings To The Tab

    """
    def add_point_cloud_tab(self, tabs):
        # Create A Tab For Point Cloud
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Set-Up WebODM Connection Settings Group
        webodm_group = QGroupBox("WebODM Connection")
        webodm_layout = QFormLayout()

        # Create A Entry For Our Port And Host Name For WebODM API 
        self.host = QLineEdit(self.config['point_cloud']['webodm']['host'])
        self.port = QSpinBox()
        self.port.setRange(0, 65535)

        self.port.setValue(self.config['point_cloud']['webodm']['port'])

        # Ask The Authentication Information For Their WebODM Session
        self.username = QLineEdit(self.config['point_cloud']['webodm']['username'])
        self.password = QLineEdit(self.config['point_cloud']['webodm']['password'])

        # Censor The Password
        self.password.setEchoMode(QLineEdit.Password)

        # Ask For The Timeout For The WebODM Session (For API Access Key)
        self.timeout = QSpinBox()
        self.timeout.setRange(0, 86400)
        
        self.timeout.setValue(self.config['point_cloud']['webodm']['timeout'])

        # Add The Widgets To The Layout In A Row Format
        webodm_layout.addRow("Host:", self.host)
        webodm_layout.addRow("Port:", self.port)
        webodm_layout.addRow("Username:", self.username)
        webodm_layout.addRow("Password:", self.password)
        webodm_layout.addRow("Timeout (s):", self.timeout)

        # Add The Layout To The Group
        webodm_group.setLayout(webodm_layout)
        layout.addWidget(webodm_group)

        # Environment Settings Group
        env_group = QGroupBox("Environment Settings")
        env_layout = QVBoxLayout(env_group)

        self.env_tabs = QTabWidget()

        tooltips = {
            '3d-tiles': "Generate OGC 3D Tiles outputs. Useful for web-based 3D visualization.",
            'auto-boundary': "Automatically set a boundary using camera shot locations to limit reconstruction area. Helps remove distant background artifacts like sky or landscapes.",
            'auto-boundary-distance': "Distance (meters) between camera locations and boundary edge when using auto-boundary. Set to 0 to automatically choose a value.",
            'bg-removal': "Use AI to automatically mask and remove image backgrounds. Experimental feature.",
            'boundary': "GeoJSON polygon defining reconstruction area limits. Can be a file path or JSON string.",
            'camera-lens': "Camera projection type. Manually setting helps improve geometric undistortion. Options: auto, perspective, brown, fisheye, fisheye_opencv, spherical, equirectangular, dual.",
            'cameras': "Use camera parameters from another dataset instead of calculating them. Can be a file path or JSON string.",
            'crop': "Automatically crop outputs by creating a buffer around dataset boundaries, shrunk by N meters. Use 0 to disable.",
            'dem-decimation': "Reduce point density before DEM generation. 1 is full quality, 100 decimates ~99% of points. Useful for large datasets.",
            'dem-euclidean-map': "Generate a raster map showing distance from each cell to nearest NODATA value. Helps identify filled areas.",
            'dem-gapfill-steps': "Number of steps for filling gaps. 0 disables gap filling. Uses progressively larger IDW interpolation radii.",
            'dem-resolution': "Resolution of DSM/DTM in cm/pixel. Limited by ground sampling distance (GSD) estimate.",
            'dsm': "Build a Digital Surface Model (ground + objects) using progressive morphological filtering.",
            'dtm': "Build a Digital Terrain Model (ground only) using morphological filtering.",
            'end-with': "Stop processing at specified stage. Options: dataset, split, merge, opensfm, openmvs, odm_filterpoints, odm_meshing, mvs_texturing, odm_georeferencing, odm_dem, odm_orthophoto, odm_report, odm_postprocess.",
            'fast-orthophoto': "Skip dense reconstruction and 3D model generation. Creates orthophoto directly from sparse reconstruction. Faster but less accurate.",
            'feature-quality': "Quality level for feature extraction. Higher quality means better features but more memory and time.",
            'feature-type': "Algorithm for keypoint extraction and descriptor computation. Options: akaze, dspsift, hahog, orb, sift.",
            'force-gps': "Use image GPS data for reconstruction even with GCPs present. Useful with high-precision GPS measurements.",
            'gps-accuracy': "GPS Dilution of Precision in meters. Lower values can help control bowling effects over large areas.",
            'ignore-gsd': "Ignore Ground Sampling Distance limitations. Memory intensive but can improve image quality. Use with caution.",
            'matcher-neighbors': "Match with nearest images based on GPS data. 0 matches by triangulation.",
            'matcher-order': "Match with nearest N images based on filename order. Speeds up sequential image processing. 0 disables.",
            'matcher-type': "Algorithm for matching. FLANN is slower but stable, BOW faster but may miss matches, BRUTEFORCE slow but robust.",
            'max-concurrency': "Maximum processes to use. Each thread requires ~1GB memory per 2MP image resolution.",
            'merge': "What to merge in split datasets. Options: all, pointcloud, orthophoto, dem.",
            'mesh-octree-depth': "Octree depth for mesh reconstruction. Higher values create more vertices. Recommended: 8-12.",
            'mesh-size': "Maximum vertex count in output mesh. Higher values create more detailed models but require more resources.",
            'min-num-features': "Minimum features to extract per image. More features help match images with little overlap but slow processing.",
            'no-gpu': "Disable GPU acceleration even if available.",
            'optimize-disk-space': "Delete intermediate files to save space. Limits restarting from intermediate stages.",
            'orthophoto-cutline': "Generate polygon around cropping area for seamless mosaic stitching.",
            'orthophoto-resolution': "Resolution in cm/pixel. Limited by ground sampling distance (GSD) estimate.",
            'pc-classify': "Classify point cloud outputs. Behavior controlled by --dem-* parameters.",
            'pc-filter': "Remove points deviating more than N standard deviations from local mean. 0 disables filtering.",
            'pc-quality': "Point cloud density and quality. Higher quality means denser clouds but more memory and time.",
            'pc-rectify': "Reclassify ground points and fill gaps in the point cloud. Useful for DTM generation.",
            'pc-sample': "Keep only one point within radius N (meters). Limits resolution and removes duplicates. 0 disables.",
            'pc-skip-geometric': "Disable geometric consistency checks. May be necessary for large datasets but reduces accuracy.",
            'primary-band': "Primary band for multispectral dataset reconstruction. Choose band with sharp details and good focus.",
            'radiometric-calibration': "Calibration for multispectral/thermal images. 'camera' applies vignetting/exposure corrections, 'camera+sun' adds DLS compensation.",
            'rerun-from': "Restart processing from specified stage.",
            'rolling-shutter': "Enable rolling shutter correction for images taken in motion.",
            'rolling-shutter-readout': "Rolling shutter readout time (ms) for your camera sensor. 0 uses database value.",
            'sfm-algorithm': "Structure from Motion algorithm. 'triangulation' better for aerial data with GPS, 'planar' faster for nadir imagery.",
            'sfm-no-partial': "Don't merge partial reconstructions from isolated or non-overlapping images.",
            'skip-3dmodel': "Skip full 3D model generation. Saves time when only 2D outputs are needed.",
            'skip-band-alignment': "Skip multispectral band alignment. Use if images are already aligned.",
            'skip-orthophoto': "Skip orthophoto generation. Saves time when only 3D or DEM outputs are needed.",
            'skip-report': "Skip PDF report generation to save processing time.",
            'sky-removal': "Use AI to automatically mask and remove sky from images. Experimental feature.",
            'sm-cluster': "ClusterODM URL for distributed processing on multiple nodes.",
            'sm-no-align': "Skip submodel alignment in split-merge. Useful with good GPS on large datasets.",
            'smrf-scalar': "Simple Morphological Filter elevation scalar parameter. Controls ground point classification.",
            'smrf-slope': "Simple Morphological Filter slope parameter (rise/run). Controls ground point classification on slopes.",
            'smrf-threshold': "Simple Morphological Filter elevation threshold (meters). Controls ground point classification.",
            'smrf-window': "Simple Morphological Filter window radius (meters). Controls terrain feature detection scale.",
            'split': "Average images per submodel when splitting large datasets. Higher values create fewer, larger submodels.",
            'split-overlap': "Overlap radius between submodels in meters. Ensures neighboring models connect properly.",
            'texturing-keep-unseen-faces': "Keep mesh faces not visible in any camera.",
            'texturing-single-material': "Generate OBJs with single material and texture instead of multiple files.",
            'texturing-skip-global-seam-leveling': "Skip color normalization across images. Useful for radiometric data.",
            'tiles': "Generate static map tiles for web viewers like Leaflet or OpenLayers.",
            'use-3dmesh': "Use full 3D mesh for orthophoto generation instead of 2.5D mesh. Similar results for flat areas.",
            'use-exif': "Use EXIF information for georeferencing instead of GCP file.",
            'use-fixed-camera-params': "Turn off camera parameter optimization during bundle adjustment. Can help with doming/bowling issues.",
            'use-hybrid-bundle-adjustment': "Run local bundle adjustment for each image and global every 100 images. Speeds up large dataset processing.",
            'video-limit': "Maximum frames to extract from video files. 0 for no limit.",
            'video-resolution': "Maximum resolution in pixels for extracted video frames."
        }

        # Boolean Checkbox Options
        bool_options = [
            '3d-tiles', 'auto-boundary', 'bg-removal', 'dem-euclidean-map', 
            'dsm', 'dtm', 'fast-orthophoto', 'force-gps', 'no-gpu',
            'optimize-disk-space', 'orthophoto-cutline', 'pc-classify', 'pc-rectify',
            'pc-skip-geometric', 'rolling-shutter', 'sfm-no-partial', 'skip-3dmodel',
            'skip-band-alignment', 'skip-orthophoto', 'skip-report', 'sky-removal',
            'sm-no-align', 'texturing-keep-unseen-faces', 'texturing-single-material',
            'texturing-skip-global-seam-leveling', 'tiles', 'use-3dmesh', 'use-exif',
            'use-fixed-camera-params', 'use-hybrid-bundle-adjustment'
        ]

        # Numeric Options
        float_options = {
            'auto-boundary-distance': (0, 0, 1000, 0.1),
            'crop': (3, 0, 100, 0.1),
            'dem-resolution': (5, 0.1, 1000, 0.1),
            'gps-accuracy': (3, 0, 100, 0.1),
            'pc-filter': (5, 0, 100, 0.1),
            'pc-sample': (0, 0, 100, 0.1),
            'orthophoto-resolution': (5, 0.1, 100, 0.1),
            'smrf-scalar': (1.25, 0.1, 10, 0.05),
            'smrf-slope': (0.15, 0.01, 1, 0.01),
            'smrf-threshold': (0.5, 0.01, 10, 0.01),
            'smrf-window': (18, 1, 100, 1)
        }

        # Integer options
        int_options = {
            'dem-decimation': (1, 1, 100),
            'dem-gapfill-steps': (3, 0, 100),
            'matcher-neighbors': (0, 0, 100),
            'matcher-order': (0, 0, 100),
            'max-concurrency': (16, 1, 32),
            'mesh-octree-depth': (11, 1, 14),
            'mesh-size': (200000, 1000, 1000000),
            'min-num-features': (10000, 1000, 50000),
            'rolling-shutter-readout': (0, 0, 1000),
            'split': (999999, 1, 9999999),
            'split-overlap': (150, 0, 1000),
            'video-limit': (500, 0, 10000),
            'video-resolution': (4000, 100, 10000)
        }

        dropdown_options = {
            'camera-lens': ['auto', 'perspective', 'brown', 'fisheye', 'fisheye_opencv'],
            'end-with': ['odm_postprocess', 'odm_filterpoints', 'odm_meshing', 'odm_25dmeshing', 
                    'odm_texturing', 'mvs_texturing', 'odm_georeferencing', 'odm_dem', 
                    'odm_orthophoto', 'odm_report'],
            'feature-quality': ['ultra', 'high', 'medium', 'low'],
            'feature-type': ['sift', 'dspsift', 'akaze', 'hahog', 'orb'],
            'matcher-type': ['flann', 'bfmatcher'],
            'merge': ['all', 'pointcloud', 'orthophoto', 'dem'],
            'pc-quality': ['ultra', 'high', 'medium', 'low'],
            'radiometric-calibration': ['none', 'camera', 'camera+sun'],
            'rerun-from': ['dataset', 'opensfm', 'openmvs', 'odm_filterpoints', 'odm_meshing', 
                        'odm_25dmeshing', 'odm_texturing', 'mvs_texturing', 'odm_georeferencing', 
                        'odm_dem', 'odm_orthophoto', 'odm_report'],
            'sfm-algorithm': ['incremental', 'planar', 'triangulation']
        }

        # Create A Tab For Each Environment
        for env in ['sunny', 'rainy', 'foggy', 'night']:

            # Add Dictionary Element
            self.env_widgets[env] = {}

            # Create Our Tab And Its Layout
            env_tab = QWidget()
            main_layout = QVBoxLayout(env_tab)

            # Add Scroll Area For The Tab
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)

            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll.setWidget(scroll_content)

            # Create Settings Sections
            general_group = QGroupBox("General Settings")
            general_layout = QFormLayout(general_group)

            mesh_group = QGroupBox("Mesh Settings")
            mesh_layout = QFormLayout(mesh_group)

            dem_group = QGroupBox("DEM & Orthophoto Settings")
            dem_layout = QFormLayout(dem_group)

            point_cloud_group = QGroupBox("Point Cloud Settings")
            point_cloud_layout = QFormLayout(point_cloud_group)

            SfM_group = QGroupBox("Structure from Motion Settings")
            SfM_layout = QFormLayout(SfM_group)

            # Get Config Ref For Advanced Settings
            adv_config = self.config['point_cloud']['webodm']['environments'][env]

            # Create Settings List
            for option in bool_options:
                checkbox = QCheckBox()
                checkbox.setChecked(adv_config[option])
                checkbox.setToolTip(tooltips.get(option, ""))
                self.env_widgets[env][option] = checkbox

                # Add To Right Group
                if option in ['dsm', 'dtm', 'dem-euclidean-map', 'orthophoto-cutline', 'skip-orthophoto']:
                    dem_layout.addRow(option, checkbox)
                elif option in ['3d-tiles', 'texturing-keep-unseen-faces', 'texturing-single-material', 
                            'texturing-skip-global-seam-leveling', 'use-3dmesh', 'skip-3dmodel']:
                    mesh_layout.addRow(option, checkbox)
                elif option in ['pc-classify', 'pc-rectify', 'pc-skip-geometric']:
                    point_cloud_layout.addRow(option, checkbox)
                elif option in ['sfm-no-partial', 'use-hybrid-bundle-adjustment', 'force-gps']:
                    SfM_layout.addRow(option, checkbox)
                else:
                    general_layout.addRow(option, checkbox)

            # Create Spin Boxes For Float Options
            for option, (default, min_val, max_val, step) in float_options.items():
                spinbox = QDoubleSpinBox()
                spinbox.setRange(min_val, max_val)
                spinbox.setSingleStep(step)
                spinbox.setValue(adv_config.get(option, default))
                spinbox.setToolTip(tooltips.get(option, ""))
                self.env_widgets[env][option] = spinbox
                
                # Add To Appropriate Group
                if option in ['dem-resolution', 'orthophoto-resolution']:
                    dem_layout.addRow(option, spinbox)
                elif option.startswith('smrf-'):
                    point_cloud_layout.addRow(option, spinbox)
                elif option in ['pc-filter', 'pc-sample']:
                    point_cloud_layout.addRow(option, spinbox)
                else:
                    general_layout.addRow(option, spinbox)
            
            # Spin Boxes For Integer Options
            for option, (default, min_val, max_val) in int_options.items():
                spinbox = QSpinBox()
                spinbox.setRange(min_val, max_val)
                spinbox.setValue(adv_config.get(option, default))
                spinbox.setToolTip(tooltips.get(option, ""))
                self.env_widgets[env][option] = spinbox
                
                # Add To Appropriate Group
                if option in ['dem-decimation', 'dem-gapfill-steps']:
                    dem_layout.addRow(option, spinbox)
                elif option in ['mesh-octree-depth', 'mesh-size']:
                    mesh_layout.addRow(option, spinbox)
                elif option in ['min-num-features', 'matcher-neighbors', 'matcher-order']:
                    SfM_layout.addRow(option, spinbox)
                else:
                    general_layout.addRow(option, spinbox)
            
            # Dropdown Options
            for option, values in dropdown_options.items():
                dropdown = QComboBox()
                dropdown.addItems(values)
                current = adv_config.get(option, values[0])
                if current in values:
                    dropdown.setCurrentText(current)

                dropdown.setToolTip(tooltips.get(option, ""))
                self.env_widgets[env][option] = dropdown
                
                # Add To Appropriate Group
                if option in ['feature-quality', 'feature-type', 'sfm-algorithm']:
                    SfM_layout.addRow(option, dropdown)
                elif option in ['pc-quality']:
                    point_cloud_layout.addRow(option, dropdown)
                elif option in ['end-with', 'rerun-from']:
                    general_layout.addRow(option, dropdown)
                else:
                    general_layout.addRow(option, dropdown)

            # String Field Options
            string_options = {
                'primary-band': 'auto',
                'sm-cluster': 'None'
            }
            
            # Create String Fields For String Options
            for option, default in string_options.items():
                text_field = QLineEdit(adv_config.get(option, default))
                self.env_widgets[env][option] = text_field
                text_field.setToolTip(tooltips.get(option, ""))
                general_layout.addRow(option, text_field)
            
            # File Chooser Options
            file_options = ['boundary', 'cameras']

            # Create File Chooser For File Options
            for option in file_options:
                file_layout = QHBoxLayout()
                text_field = QLineEdit(adv_config.get(option, ''))
                browse_btn = QPushButton("Browse...")

                browse_btn.setToolTip(tooltips.get(option, ""))
                
                # Connect Browse Button To File Dialog
                def make_browse_function(field, opt):
                    def browse_file():
                        path, _ = QFileDialog.getOpenFileName(self, f"Select {opt} JSON file", "", "JSON Files (*.json)")
                        if path:
                            field.setText(path)
                    return browse_file
                
                browse_btn.clicked.connect(make_browse_function(text_field, option))
                
                file_layout.addWidget(text_field)
                file_layout.addWidget(browse_btn)
                
                self.env_widgets[env][option] = text_field
                general_layout.addRow(f"{option} (json)", file_layout)

            
            # Set Layouts For All Groups
            general_group.setLayout(general_layout)
            mesh_group.setLayout(mesh_layout)
            dem_group.setLayout(dem_layout)
            point_cloud_group.setLayout(point_cloud_layout)
            SfM_group.setLayout(SfM_layout)
            
            # Add All Groups To The Scroll Layout
            scroll_layout.addWidget(general_group)
            scroll_layout.addWidget(SfM_group)
            scroll_layout.addWidget(point_cloud_group)
            scroll_layout.addWidget(dem_group)
            scroll_layout.addWidget(mesh_group)
            
            # Add Scroll Area To Main Layout
            main_layout.addWidget(scroll)
            
            # Add A Note About These Being Advanced Settings
            note_label = QLabel("Note: These are advanced WebODM processing options. Incorrect settings may cause processing to fail.")
            note_label.setStyleSheet("color: #FFA500;") # Orange Warning Color
            main_layout.addWidget(note_label)

            # Add The Tab To The Environment Tabs
            self.env_tabs.addTab(env_tab, env.capitalize())

        env_layout.addWidget(self.env_tabs)

        # Add The Environment Layout To The Group
        layout.addWidget(env_group)

        # Add The Environment Group To The Main Layout
        tabs.addTab(tab, "Point Cloud")


    """
    
        Desc: Function Adds A Tab For Logs. The Tab Will Allow The User
        To View The Log Files And Their Content. The Tab Will Allow The
        Content To Be Scrolled And Will Allow The User To Delete All Logs.
        The Tab Will Also Allow The User To Refresh The List Of Log Files.

        Preconditions:
            1. tabs Should Be A QTabWidget Object

        Postconditions:
            1. Add A Tab For Logs To The Tab Widget
            2. Add A List Of Log Files And Their Content To The Tab
            3. Add A Button To Delete All Logs
            4. Add A Button To Refresh The List Of Log Files
    
    """
    def add_logs_tab(self, tabs):
        # Create A Tab Widget And Main Layout
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Horizontal Layout For Log And Content
        logs_content = QHBoxLayout()

        # Left Side Will Be Log Files
        logs_group = QGroupBox("Log Files")
        logs_layout = QVBoxLayout()

        # Create A List Widget For Log Files
        self.logs_list = QListWidget()
        self.logs_list.setMinimumWidth(250)
        self.refresh_logs_list()

        # When Selected, Display The Log Content
        self.logs_list.itemSelectionChanged.connect(self.display_log_content)

        # Add Refresh
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_logs_list)

        # Add Widgets To Layout
        logs_layout.addWidget(self.logs_list)
        logs_layout.addWidget(refresh_btn)
        logs_group.setLayout(logs_layout)

        # Now Do The Right Side For Log Content
        content_group = QGroupBox("Log Content")
        content_layout = QVBoxLayout()

        # Create Text Edit For Log Content
        self.log_content = QTextEdit()
        self.log_content.setReadOnly(True)
        self.log_content.setFontPointSize(8)
        self.log_content.setLineWrapMode(QTextEdit.NoWrap)
        self.log_content.setAcceptRichText(True)

        # Add The Text Edit To The Layout
        content_layout.addWidget(self.log_content)
        content_group.setLayout(content_layout)

        # Add The Groups To The Main Layout
        logs_content.addWidget(logs_group)
        logs_content.addWidget(content_group, stretch=1)

        # Add The Layout To The Main Layout
        layout.addLayout(logs_content)

        # Add Button To Delete All Logs
        delete_btn = QPushButton("Delete All Logs")
        delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        delete_btn.clicked.connect(self.delete_all_logs)

        layout.addWidget(delete_btn)

        # Add The Tab To The Tab Widget
        tabs.addTab(tab, "Logs")


    """
    
        Desc: Function Refreshes The List Of Log Files. It Will Clear
        The List And Then Get All Log Files In The Logs Directory. It Will
        Sort The Log Files By Date And Add Each Log File To The List.
        It Will Also Display The Size Of Each Log File In KB And The
        Modification Time Of Each Log File.

        Preconditions:
            1. logs_dir Should Be The Path To The Logs Directory

        Postconditions:
            1. The List Of Log Files Will Be Cleared
            2. The List Of Log Files Will Be Refreshed
            3. The List Of Log Files Will Be Sorted By Date
            4. The Size Of Each Log File Will Be Displayed In KB
            5. The Modification Time Of Each Log File Will Be Displayed
    
    """
    def refresh_logs_list(self):
        # Refresh The List Of Log Files
        self.logs_list.clear()

        # Get Directory
        if not self.logs_dir.exists():
            return
        
        # Get All Log Files
        log_files = self.logs_dir.glob("*.log")

        # Sort By Date
        log_files = sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)

        # Add Each Log File To The List
        for log_file in log_files:
            size_kb = log_file.stat().st_size / 1024
            modificationTime = datetime.fromtimestamp(log_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            item_text = f"Log Report ({size_kb:.2f} KB) - {modificationTime}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, str(log_file))
            self.logs_list.addItem(item)


    """
    
        Desc: Function Displays The Content Of The Selected Log File.
        It Will Read The Log File And Display The Content In The Text Edit.
        It Will Also Scroll To The End Of The Text Edit. If No Log File
        Is Selected, It Will Clear The Text Edit.

        Preconditions:
            1. logs_list Should Be A QListWidget Object
            2. log_content Should Be A QTextEdit Object
        
        Postconditions:
            1. The Content Of The Selected Log File Will Be Displayed
            2. The Text Edit Will Scroll To The End
            3. If No Log File Is Selected, The Text Edit Will Be Cleared
            4. If The Log File Cannot Be Read, An Error Message Will Be Displayed
    
    """
    def display_log_content(self):
        #  Check For Selected Item
        selected = self.logs_list.selectedItems()
        if not selected:
            self.log_content.clear()
            return
        
        # Get The Selected Log File
        log_file = Path(selected[0].data(Qt.UserRole))

        try:
            # Read The Log File
            with open(log_file, 'r') as f:
                content = f.read()

            # Display The Content
            self.log_content.setText(content)

            # Scroll To One ENd
            cursor = self.log_content.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.log_content.setTextCursor(cursor)

        except Exception as e:
            self.log_content.setText(f"Error Reading Log File: {str(e)}")

    """
    
        Desc: Function Deletes All Log Files In The Logs Directory.
        It Will Prompt The User For Confirmation Before Deleting The Files.

        Preconditions:
            1. logs_dir Should Be The Path To The Logs Directory

        Postconditions:
            1. All Log Files In The Logs Directory Will Be Deleted
            2. The List Of Log Files Will Be Refreshed
            3. The Text Edit Will Be Cleared
            4. A Success Message Will Be Displayed
            5. If The Deletion Fails, An Error Message Will Be Displayed
    
    """
    def delete_all_logs(self):
        # Confirm They Want To Delete
        reply = QMessageBox.question(
            self,
            "Delete All Logs",
            "Are You Sure You Want To Delete All Log Files?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Get Path To Logs
                if not self.logs_dir.exists():
                    return
                
                # Delete All Logs
                for log_file in self.logs_dir.glob("*.log"):
                    log_file.unlink()

                # Refresh The List
                self.refresh_logs_list()
                self.log_content.clear()

                QMessageBox.information(self, "Success", "All Log Files Have Been Deleted Successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed To Delete Log Files: {str(e)}")


    """
    
        Desc: Function Adds A Tab For Geospatial Settings. The Tab
        Will Allow The User To Adjust The Output Path, Analysis Settings,
        Terrain Settings, And Output Settings. The Tab Will Allow The
        User To Adjust The Min Tree Height, Canopy Threshold, Slope
        Threshold, Roughness Threshold, Output Formats, And Resolution.

        Preconditions:
            1. tabs: QTabWidget Object

        Postconditions:
            1. Add A Tab For Geospatial Settings To The Tab Widget
            2. Add Output Path, Analysis Settings, Terrain Settings, And Output Settings To The Tab
    
    """
    def add_geospatial_tab(self, tabs):
        # Create A Tab For Geospatial Settings
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Set-Up Output Settings Group
        output_group = QGroupBox("Output Settings")
        output_layout = QHBoxLayout()

        # Create A Line Edit For The Output Path
        self.output_path = QLineEdit(self.config['geospatial']['output_path'])
        browse_btn = QPushButton("Browse...")

        # Connect The Button To The Function
        browse_btn.clicked.connect(self.browse_output)

        # Add The Widgets To The Layout
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(browse_btn)

        # Add The Layout To The Group
        output_group.setLayout(output_layout)

        # Add The Group To The Main Layout
        layout.addWidget(output_group)

        # Set-Up Analysis Settings Group
        analysis_group = QGroupBox("Analysis Settings")
        analysis_layout = QFormLayout()

        # Set-Up Min Tree Height And Canopy Threshold
        self.tree_height = QDoubleSpinBox()
        self.tree_height.setRange(0, 100)

        self.tree_height.setValue(self.config['geospatial']['gap_detection']['min_tree_height'])

        # Create A Double Spin Box For The Canopy Threshold
        analysis_layout.addRow("Min Tree Height (m):", self.tree_height)

        self.canopy = QDoubleSpinBox()
        self.canopy.setRange(0, 1)
        self.canopy.setSingleStep(0.1)

        self.canopy.setValue(self.config['geospatial']['gap_detection']['max_tree_height'])
        analysis_layout.addRow("Canopy Threshold:", self.canopy)

        # Add The Analysis Layout To The Group
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)

        # Set-Up Output Settings Group
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout()

        # Set-Up Output Formats And Resolution
        self.geo_formats_list = QListWidget()
        self.geo_formats_list.addItems(self.config['geospatial']['output']['formats'])

        # Add The Output Formats To The Layout
        output_layout.addRow("Output Formats:", self.geo_formats_list)

        self.resolution = QDoubleSpinBox()
        self.resolution.setRange(0.1, 1.0)
        self.resolution.setSingleStep(0.05)

        self.resolution.setValue(self.config['geospatial']['output']['resolution'])
        output_layout.addRow("Resolution (m/px):", self.resolution)

        # Add The Output Layout To The Group
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Add The Group To The Main Layout
        tabs.addTab(tab, "Geospatial")


    """
    
        Desc: Function Adds A Format To The Supported Image Formats List
        When The User Clicks The Add Button. The Function Will Prompt
        The User For A Format And Add It To The List. 

        Preconditions:
            1. None

        Postconditions:
            1. Add A Format To The Supported Image Formats List
    
    """
    def add_format(self):
        # Add A Format To The Supported Formats
        text, ok = QInputDialog.getText(self, "Add Format", "Enter format (e.g., .jpg):")
        if ok and text:
            self.formats_list.addItem(text)


    """
    
        Desc: Function Removes A Format From The Supported Image Formats
        List When The User Clicks The Remove Button. The Function Will
        Remove The Selected Format From The List.

        Preconditions:
            1. None

        Postconditions:
            1. Remove A Format From The Supported Image Formats
    
    """
    def remove_format(self):
        # Remove A Format From The Supported Formats
        row = self.formats_list.currentRow()
        if row >= 0:
            self.formats_list.takeItem(row)


    """
    
        Desc: Function Allows The User To Browse For The Output Executable
        When The User Clicks The Browse Button. The Function Will Open
        A File Dialog For The User To Select The Output Executable.

        Preconditions:
            1. None

        Postconditions:
            1. Open A File Dialog For The User To Select The Output Executable
    
    """
    def browse_output(self):
        # Browse For The Output Path
        path = QFileDialog.getOpenFileName(self, "Select Output Directory", filter="Output Directorys (*.dir)")
        if path[0]:
            self.output_path.setText(path[0])


    """
    
        Desc: Function Saves The Settings To The Configuration File
        When The User Clicks The Save Settings Button. The Function
        Will Save The Specified Settings To The Configuration File,
        Including Preprocessing, Point Cloud, And Geospatial Settings.
        These Include Supported Formats, Minimum Resolution, Blur
        Threshold, Brightness Range, Maximum Workers, WebODM Connection
        Settings, Environment Settings, Output Path, Analysis Settings,
        Terrain Settings, And Output Settings. 

        Preconditions:
            1. None

        Postconditions:
            1. Save The Settings To The Configuration File
    
    """
    def save_settings(self, silent: bool = True):
        try:
            # Ensure top-level keys exist, matching the structure of your new config
            # This helps if starting from a minimal or partially formed self.config
            if 'preprocessing' not in self.config:
                self.config['preprocessing'] = {}
            if 'point_cloud' not in self.config:
                self.config['point_cloud'] = {}
            if 'webodm' not in self.config['point_cloud']:
                self.config['point_cloud']['webodm'] = {}
            if 'environments' not in self.config['point_cloud']['webodm']:
                self.config['point_cloud']['webodm']['environments'] = {}
            if 'geospatial' not in self.config:
                self.config['geospatial'] = {}
            if 'gap_detection' not in self.config['geospatial']:
                self.config['geospatial']['gap_detection'] = {}
            if 'output' not in self.config['geospatial']:
                self.config['geospatial']['output'] = {}

            # Update Preprocessing Settings
            preprocessing_config = self.config['preprocessing']
            preprocessing_config['supported_formats'] = [
                self.formats_list.item(i).text() 
                for i in range(self.formats_list.count())
            ]
            preprocessing_config['min_resolution'] = [
                self.width.value(),
                self.height.value()
            ]
            preprocessing_config['blur_threshold'] = self.blur.value()
            preprocessing_config['brightness_range'] = [
                self.bright_min.value(),
                self.bright_max.value()
            ]
            preprocessing_config['max_workers'] = self.max_workers.value()

            # Update Point Cloud Settings - WebODM Connection
            webodm_base_config = self.config['point_cloud']['webodm']
            webodm_base_config['host'] = self.host.text()
            webodm_base_config['port'] = self.port.value()
            webodm_base_config['username'] = self.username.text()
            webodm_base_config['password'] = self.password.text()
            webodm_base_config['timeout'] = self.timeout.value()

            # Update Point Cloud Settings - WebODM Environment Settings
            for env_name in ['sunny', 'rainy', 'foggy', 'night']:
                if env_name not in webodm_base_config['environments']: # Ensure environment key exists
                    webodm_base_config['environments'][env_name] = {}
                
                env_specific_config = webodm_base_config['environments'][env_name]
                
                if env_name in self.env_widgets: # Check if UI widgets for this environment were initialized
                    for option_key, widget in self.env_widgets[env_name].items():
                        value = None
                        if isinstance(widget, QCheckBox):
                            value = widget.isChecked()
                        elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                            value = widget.value()
                        elif isinstance(widget, QComboBox):
                            value = widget.currentText()
                        elif isinstance(widget, QLineEdit):
                            value = widget.text()
                        else:
                            continue # Skip unsupported widget types
                        
                        # Save to the primary kebab-case key (which matches the widget key)
                        env_specific_config[option_key] = value
                        
                        # Handle cases where the new YAML has both kebab-case and snake_case
                        # or specific remappings for conceptual duplicates.
                        # Update the snake_case version if it exists in the loaded config for that environment.
                        if option_key == 'feature-quality' and 'feature_quality' in env_specific_config:
                            env_specific_config['feature_quality'] = value
                        elif option_key == 'min-num-features' and 'min_num_features' in env_specific_config:
                            env_specific_config['min_num_features'] = value
                        elif option_key == 'matcher-type' and 'matcher_type' in env_specific_config:
                            env_specific_config['matcher_type'] = value
                        elif option_key == 'max-concurrency' and 'max_concurrency' in env_specific_config:
                            env_specific_config['max_concurrency'] = value
                        elif option_key == 'pc-quality':
                            if 'point-cloud-quality' in env_specific_config: # kebab-case conceptual equivalent
                                env_specific_config['point-cloud-quality'] = value
                            if 'point_cloud_quality' in env_specific_config: # snake_case conceptual equivalent
                                env_specific_config['point_cloud_quality'] = value
                        elif option_key == 'mesh-size': # widget key
                            if 'mesh-quality' in env_specific_config: # kebab-case conceptual equivalent
                                env_specific_config['mesh-quality'] = value
                            if 'mesh_quality' in env_specific_config: # snake_case conceptual equivalent
                                env_specific_config['mesh_quality'] = value
                        # Note: 'ignore-gsd' was in the old logic but is not a standard WebODM param
                        # and not in the provided new YAML structure for environments.
                        # If it were, it would be handled like other boolean options by `env_specific_config[option_key] = value`.

            # Update Geospatial Settings (Moved outside the environment loop)
            geospatial_config = self.config['geospatial']
            
            geospatial_config['output_path'] = self.output_path.text()

            # Gap Detection settings
            gap_detection_config = geospatial_config['gap_detection']
            # Save values from existing UI widgets
            gap_detection_config['min_tree_height'] = self.tree_height.value() # From self.tree_height widget
            gap_detection_config['max_tree_height'] = self.canopy.value()    # From self.canopy widget

            # For other gap_detection parameters present in your new YAML:
            # (min_area, max_area, pixel_size, threshold_type, manual_threshold,
            #  apply_dilation, dilation_size, apply_erosion, erosion_size,
            #  apply_smoothing, smoothing_sigma)
            # Since no UI widgets (e.g., self.min_area_widget, self.pixel_size_widget etc.)
            # are defined for these in the `add_geospatial_tab` method you've shown,
            # this `save_settings` function cannot get new values for them from the UI.
            # Their existing values in `self.config['geospatial']['gap_detection']`
            # (loaded from the YAML file) will be preserved when the config is saved.
            # If you add UI widgets for these parameters later, you would add lines here to save them, e.g.:
            # if hasattr(self, 'min_area_widget'):
            #     gap_detection_config['min_area'] = self.min_area_widget.value()
            # ...and so on for other parameters if their widgets are added.

            # Geospatial Output settings
            geospatial_output_config = geospatial_config['output']
            geospatial_output_config['formats'] = [
                self.geo_formats_list.item(i).text() 
                for i in range(self.geo_formats_list.count())
            ]
            geospatial_output_config['resolution'] = self.resolution.value()

            # Clean up old 'analysis' structure if it exists from a previous config version
            if 'analysis' in geospatial_config:
                del geospatial_config['analysis']
                if 'terrain' in geospatial_config.get('analysis', {}): # defensive
                    del geospatial_config['analysis']['terrain']


            # Save To File
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(self.config, f, default_flow_style=False, sort_keys=False)

            if not silent:
                QMessageBox.information(self, "Success", "Settings saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")


    """
    
        Desc: Function Resets The Settings To The Default Configuration
        When The User Clicks The Reset Settings Button. The Function
        Will Reset The Configuration To The Default Configuration File
        And Reinitialize All Widgets.

        Preconditions:
            1. None

        Postconditions:
            1. Reset The Settings To The Default Configuration
            2. Reset Widgets To Default State
    
    """
    def reset_settings(self):
        try:
            # Load Default Config
            default_config_file = Path(__file__).parent.parent.parent / "config/default_config.yaml"

            # Now Add Changes
            with open(default_config_file, 'r') as f:
                self.config = yaml.safe_load(f)

            # Reinitialize all widgets
            self.__init__(self.config_path)
            QMessageBox.information(self, "Success", "Settings reset to defaults!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset settings: {str(e)}")