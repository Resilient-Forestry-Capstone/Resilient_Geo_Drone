from pathlib import Path
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QLabel, QSplitter, QComboBox, QGroupBox, 
                             QStackedWidget, QScrollArea, QFileDialog, QMessageBox, QFrame, QSlider,
                             QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QEvent
from PyQt5.QtGui import QPixmap, QImage
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
import cv2


class ResultsViewerWidget(QWidget):
   
    """
    
        Desc: Initialize Initial Variables For Viewing Of Folders And Files.
        Sets Up The Output Base Directory To Retrieve The Task Folders, As Well As
        The Current Task Path, File Path, And Colormap For .tif Visualization.
        The Class Will Also Set Up The UI For The Results Viewer, Including The Layout,
        Task Folders, File List, File Viewer, And Navigation Buttons.

        Preconditions:
            1. None

        Postconditions:
            1. Set Up The Results Viewer UI Components
            2. Set Up The Task Folders List
            3. Set Up The File List
            4. Set Up The File Viewer
            5. Set Up The Navigation Buttons
            6. Set Up The Colormap Selector
    
    """ 
    def __init__(self):
        super().__init__()
        self.setObjectName("resultsViewer")
        self.setWindowTitle("Results Viewer")
        self.setMinimumSize(900, 600)
        
        self.output_base_dir = Path("data/output/point_cloud")
        self.current_task_path = None
        self.current_file_path = None
        self.scale_factor_override = 1.0  # Default = full resolution
        self.auto_scaling = True 
        self.contour_line_count = 5
        self.current_colormap = 'viridis'
        self._setup_ui()


    def _update_contour_value(self, value):
        """Update the contour value label based on the slider value"""
        self.contour_value.setText(str(value))


    def _apply_contour_changes(self):
        self.contour_line_count = self.contour_slider.value()

        if self.current_file_path and self.current_file_path.suffix.lower() in ('.tiff', '.tif'):
            self._load_tif_file(self.current_file_path)
        
        
    """
    
        Desc: Function Will Setup The UI Layout For The Results Viewer
        Including The Task Folders Panel, File List Panel, As Well As 
        File Contents Panel. The Function Will Also Setup The Navigation Buttons
        For The User To Navigate Back To The Pipeline Page As Well As Open
        The Selected File In Through Their Web Browser And Also Export The File.

        Preconditions:
            1. None

        Postconditions:
            1. Set Up The UI Layout For The Results Viewer
            2. Set Up The Task Folders Panel
            3. Set Up The File List Panel
            4. Set Up The File Contents Panel
            5. Set Up The Navigation Buttons
            6. Set Up The Colormap Selector
    
    """
    def _setup_ui(self):
        """Set up the results viewer UI components"""
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header Of Our Pane
        header = QLabel("Pipeline Results Viewer")
        header.setObjectName("sectionHeader")
        main_layout.addWidget(header)
        
        # Description Of Users Capabilities
        description = QLabel("Select a task folder to view its output files (DSM, DTM, orthophotos, and reports)")
        description.setWordWrap(True)
        description.setObjectName("sectionDescription")
        main_layout.addWidget(description)
        
        # Horizontal Split For Folder And File Selection
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)
        
        # Left Side: Task Folder And File Selection
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Task Folders Will Be Top Group
        folders_group = QGroupBox("Task Folders")
        folders_group.setObjectName("taskFoldersGroup")
        folders_layout = QVBoxLayout()
        
        # Task Folders Container
        self.task_folders_list = QListWidget()
        self.task_folders_list.setMinimumWidth(200)
        # When We Select A Folder, What Do We Do
        self.task_folders_list.itemSelectionChanged.connect(self._on_task_selected)
        folders_layout.addWidget(self.task_folders_list)
        
        # Refresh The Task Folders
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_task_folders)
        folders_layout.addWidget(refresh_btn)
        
        # Add Together The Layout With Our Group
        folders_group.setLayout(folders_layout)
        left_layout.addWidget(folders_group)
        
        # Files Will Be Below Folders
        files_group = QGroupBox("Available Files")
        files_group.setObjectName("availableFilesGroup")
        files_layout = QVBoxLayout()
        
        # Files List
        self.files_list = QListWidget()
        self.files_list.setMinimumWidth(200)
        # When A File Is Selected, What Do We Do
        self.files_list.itemSelectionChanged.connect(self._on_file_selected)
        files_layout.addWidget(self.files_list)
        
        # Open File In External Viewer Button (For PDFs Open In Their Default Web Browser)
        open_external_btn = QPushButton("Open in External Viewer")
        open_external_btn.clicked.connect(self._open_external)
        files_layout.addWidget(open_external_btn)
        
        # Add Together The Layout With Our Group
        files_group.setLayout(files_layout)
        left_layout.addWidget(files_group)
        
        # Add Left Panel To Splitter
        splitter.addWidget(left_panel)
        
        # Right Side: File Content Viewer
        viewer_panel = QWidget()
        viewer_layout = QVBoxLayout(viewer_panel)
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        
        # File Information Header Description
        self.file_info = QLabel("No file selected")
        self.file_info.setObjectName("fileInfoHeader")
        viewer_layout.addWidget(self.file_info)
        
        # Specified Options For .tif Files
        options_layout = QHBoxLayout()
        
        # Colormap Selector (Only For TIFs)
        self.colormap_label = QLabel("Colormap:")
        self.colormap_selector = QComboBox()
        self.colormap_selector.addItems(['viridis', 'plasma', 'inferno', 'magma', 'terrain', 'rainbow'])
        self.colormap_selector.currentTextChanged.connect(self._on_colormap_changed)
        
        # Add Colormap Selector To Layout
        options_layout.addWidget(self.colormap_label)
        options_layout.addWidget(self.colormap_selector)

        # Add Box Frame
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        options_layout.addWidget(line)

        # Countour Lines
        self.contour_label = QLabel("Contour Line Count:")
        options_layout.addWidget(self.contour_label)

        self.contour_slider = QSlider(Qt.Horizontal)
        self.contour_slider.setRange(1, 1000)
        self.contour_slider.setValue(self.contour_line_count)  # Default value
        self.contour_slider.setFixedWidth(120)
        options_layout.addWidget(self.contour_slider)

        self.contour_value = QLabel("5")
        options_layout.addWidget(self.contour_value)

        # Connect Slider Value Changed Signal
        self.contour_slider.valueChanged.connect(self._update_contour_value)

        # After your contour slider section, add:
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        options_layout.addWidget(line)

        # Scale Factor controls
        self.auto_scale_checkbox = QCheckBox("Auto")
        self.auto_scale_checkbox.setChecked(True)
        self.auto_scale_checkbox.stateChanged.connect(self._toggle_scale_slider)
        options_layout.addWidget(self.auto_scale_checkbox)

        self.scale_label = QLabel("Resolution:")
        options_layout.addWidget(self.scale_label)

        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 100)  # 10% to 100%
        self.scale_slider.setValue(100)      # Default 100%
        self.scale_slider.setFixedWidth(120)
        self.scale_slider.setEnabled(False)  # Initially disabled when auto is on
        options_layout.addWidget(self.scale_slider)

        self.scale_value = QLabel("100%")
        options_layout.addWidget(self.scale_value)

        # Connect slider value changed signal
        self.scale_slider.valueChanged.connect(self._update_scale_value)

        # Apply Button
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_contour_changes)
        options_layout.addWidget(self.apply_btn)


        options_layout.addStretch(1)

        
        
        # Export File Button
        self.export_btn = QPushButton("Export File")
        self.export_btn.clicked.connect(self._export_file)
        options_layout.addWidget(self.export_btn)
        viewer_layout.addLayout(options_layout)
        
        # Stacked Widget To Cycle File Type Viewers
        self.file_viewers = QStackedWidget()
        
        # .tif File Viewer (Page 0)
        self.tif_viewer = QScrollArea()
        self.tif_viewer.setWidgetResizable(True)
        self.tif_viewer.setAlignment(Qt.AlignCenter)
        self.tif_image = QLabel("No image selected")
        self.tif_image.setAlignment(Qt.AlignCenter)
        self.tif_image.mousePressEvent = self._on_image_clicked

        # Set Our Defaut Image To Nothing Currently
        self.tif_viewer.setWidget(self.tif_image)
        self.file_viewers.addWidget(self.tif_viewer)
        
        # Empty State (page 1)
        self.empty_state = QLabel("Select a file from the list to view its contents")
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.file_viewers.addWidget(self.empty_state)
        
        # Set To Our Default State Initally
        self.file_viewers.setCurrentIndex(1)
        viewer_layout.addWidget(self.file_viewers)
        
        # Add Viewer To Splitter
        splitter.addWidget(viewer_panel)
        
        # Set Initial Splitter Sizes (30% Left, 70% Right)
        splitter.setSizes([300, 700])
        
        # Add The Splitter To The Main Layout
        main_layout.addWidget(splitter)
        
        # Navigation Buttons
        nav_layout = QHBoxLayout()
        
        # Redirect Button Back To Pipeline
        back_btn = QPushButton("Back to Pipeline")
        back_btn.clicked.connect(self._go_back_to_pipeline)
        nav_layout.addWidget(back_btn)
        nav_layout.addStretch(1)
        
        # Now Add Layout To Main Layout
        main_layout.addLayout(nav_layout)

        self.setObjectName("resultsViewer")
        self.tif_image.setObjectName("tifImage") 
        

        self._update_file_config(False)  # Hide Colormap and Export Button
        
        # Initial Refresh Of Task Folders
        self.refresh_task_folders()


    def _toggle_scale_slider(self, state):
        """Enable/disable scale slider based on auto checkbox"""
        self.auto_scaling = bool(state)
        self.scale_slider.setEnabled(not self.auto_scaling)
        
        # If we just turned auto back on, reload the current file
        if self.auto_scaling and self.current_file_path and self.current_file_path.suffix.lower() in ('.tiff', '.tif'):
            self._load_tif_file(self.current_file_path)

    def _update_scale_value(self, value):
        """Update the scale value label based on slider value"""
        self.scale_value.setText(f"{value}%")
        self.scale_factor_override = value / 100.0
        
        # Don't automatically reload - wait for Apply button


    """
    
        Desc: Function Will Handle When The User Clicks On The Image In The TIF Viewer.
        It Will Check If The Image Is Valid And If So, It Will Show The Image In Full Screen.
        Else If It's Empty No Action Will Be Taken.

        Precondition:
            1. The Image Should Be A Valid Image Loaded In The TIF Viewer
            2. The Function Should Be Called When The User Clicks On The Image
            3. The Image Should Be A Valid QPixmap Object

        Postcondition:
            1. If The Image Is Valid, It Will Be Shown In Full Screen
            2. If The Image Is Empty, No Action Will Be Taken
    
    """
    def _on_image_clicked(self, event):
        if event.button() == Qt.LeftButton:
            # Only Expand If We Have A Image Setup
            if not self.tif_image.pixmap() or self.tif_image.pixmap().isNull():
                return
            
            # Get Our Current Pixmap
            pixmap = self.tif_image.pixmap()
            if pixmap:
                # If We Have A Pixmap, Show It In Full Screen
                self._show_full_screen_image(pixmap)

    
    def _show_full_screen_image(self, pixmap):
        # Setup Our Full-Screen Overlay Widget
        overlay = QWidget(self.window())
        overlay.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        overlay.setStyleSheet("background-color: black;")

        # Create Our Layout
        layout = QVBoxLayout(overlay)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create An Image Label 
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(False) # Disable Scaling

        # Create Scroll Area For Image
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignCenter)
        scroll_area.setWidget(image_label)
        scroll_area.setStyleSheet("background-color: black; border: none;")

        layout.addWidget(scroll_area)

        # Instruction Label
        instructions = QLabel("ESC: Exit | Mouse Wheel: Zoom | Left Click + Drag: Pan")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: white; padding: 5px; background-color: rgba(0, 0, 0, 150);")
        layout.addWidget(instructions)

        # Setup Zoom Handling
        self.current_scale_factor = 1.0

        # Store Original Pixmap Size For Scaling
        self.original_pixmap_size = pixmap.size()

        # Install Event Filter For Key Press Events
        overlay.installEventFilter(self)

        # Install Event Filter On Scroll Area
        scroll_area.viewport().installEventFilter(self)

        # Store Preferences For Overlay
        self.fullscreen_overlay = overlay
        self.fullscreen_image = image_label
        self.fullscreen_scroll_area = scroll_area

        # Show The Overlay
        overlay.showFullScreen()


    def eventFilter(self, obj, event):
        # Handles ESC Key To Exit Full-Screen
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            # Close The Full-Screen Overlay
            self.fullscreen_overlay.close()
            return True
        
        # Handle Mouse Wheel Events For Zooming
        if event.type() == QEvent.Wheel and self.fullscreen_image:
            # Calculate Zoom Factor
            zoom_in_factor = 1.15
            zoom_out_factor = 1 / zoom_in_factor

            if event.angleDelta().y() > 0:
                # Zoom In
                self.current_scale_factor *= zoom_in_factor
            else:
                # Zoom Out
                self.current_scale_factor *= zoom_out_factor

            # Limit Zoom
            self.current_scale_factor = max(0.1, min(self.current_scale_factor, 10.0))

            # Apply Our Zoom
            self._update_fullscreen_zoom()
            return True
        
        if self.fullscreen_scroll_area and obj == self.fullscreen_scroll_area.viewport():
            # Handle Mouse Move Events For Panning
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.is_dragging = True
                self.drag_start_pos = event.pos()
                self.fullscreen_scroll_area.viewport().setCursor(Qt.ClosedHandCursor)
                self.drag_start_h_scroll = self.fullscreen_scroll_area.horizontalScrollBar().value()
                self.drag_start_v_scroll = self.fullscreen_scroll_area.verticalScrollBar().value()
                return True
            elif event.type() == QEvent.MouseMove and self.is_dragging:
                # Get Our Offset
                delta = event.pos() - self.drag_start_pos
                self.fullscreen_scroll_area.horizontalScrollBar().setValue(self.drag_start_h_scroll - delta.x())
                self.fullscreen_scroll_area.verticalScrollBar().setValue(self.drag_start_v_scroll - delta.y())
                return True
            
            elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                self.is_dragging = False
                self.fullscreen_scroll_area.viewport().setCursor(Qt.ArrowCursor)
                return True
        
        # If Failed, Call The Parent Event Filter
        return super().eventFilter(obj, event)
    

    def _update_fullscreen_zoom(self):
        if not self.fullscreen_image or not self.original_pixmap_size:
            return
        
        # Get Original Pixmap
        pixmap = self.tif_image.pixmap()

        if not pixmap:
            return
        
        # Calulate New Size
        new_size = self.original_pixmap_size * self.current_scale_factor

        # Scale The Pixmap
        scaled_pixmap = pixmap.scaled(new_size.width(), new_size.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Update The Image In UI
        self.fullscreen_image.setPixmap(scaled_pixmap)


    


    """
    
        Desc: Will Refresh The Task Folders List In The UI By Scanning
        The Provided self.output_base_dir For Subdirectories. It Will Populate The
        Task Folders List With The Names Of The Subdirectories, Along With The Number
        Of Files In Each Directory.

        Preconditions:
            1. self.output_base_dir Should Be Declared And Point To A Valid Directory
            2. The Directory Is Expected To Contain Subdirectories Containing The Results
               Of The WebODM Staging.
            3. The Subdirectories Should Be Named With A Timestamp Format (YYYYMMDD_HHMMSS)
            4. Subdirectories Are Expected To Contain .tif, .pdf, .ply, and .laz Files
            5. The Function Should Be Called When The User Clicks The "Refresh List" Button

        Postconditions:
            1. The Task Folders List Will Be Cleared And Re-populated With The Names Of The
               Subdirectories Found In self.output_base_dir.
            2. Each Item In The List Will Contain The Name Of The Subdirectory And The Number
               Of Files It Contains.
            3. If No Subdirectories Are Found, A Message Will Be Displayed Indicating So.
            4. If An Error Occurs While Scanning The Directory, An Error Message Will Be Displayed.
            5. The File Viewer Will Be Reset To An Empty State.
            6. The Colormap Selector Will Be Hidden And The Export Button Disabled.
    
    """
    def refresh_task_folders(self):
        
        # Clear List And Viewer Content
        self.task_folders_list.clear()
        self.files_list.clear()

        # Reset File Viewer To Empty State
        self.file_viewers.setCurrentIndex(1)
        self.file_info.setText("No file selected")

        # Hide Colormap Selector And Disable Export Button
        self.colormap_label.setVisible(False)
        self.colormap_selector.setVisible(False)
        self.export_btn.setEnabled(False)
        
        # Check If Directory Exists
        if not self.output_base_dir.exists():
            self.task_folders_list.addItem("No output directory found")
            return
        
        # Find All Task Directories
        task_dirs = []
        try:
            # Get All Subdirectories In The Output Base Directory
            task_dirs = [d for d in self.output_base_dir.iterdir() if d.is_dir()]
            
            # Sort By Modification Time (Newest First)
            task_dirs = sorted(task_dirs, key=lambda d: d.stat().st_mtime, reverse=True)
        except Exception as e:
            # Handle Errors While Scanning Directory
            self.task_folders_list.addItem(f"Error scanning directory: {str(e)}")
            return
        
        # No Task Folders Were Found
        if not task_dirs:
            self.task_folders_list.addItem("No task folders found")
            return
        
        # Add All Task Folders To The List
        for task_dir in task_dirs:
            # Try To Format The Name As A Date/Time String
            name = task_dir.name
            if len(name) >= 15 and name[8] == '_':  # Assuming Format Like YYYYMMDD_HHMMSS
                try:
                    display_name = f"Task {name[0:4]}-{name[4:6]}-{name[6:8]} {name[9:11]}:{name[11:13]}:{name[13:15]}"
                except:
                    display_name = name
            else:
                display_name = name
            
            # Count Files In The Directory
            file_count = sum(1 for f in task_dir.glob("*") if f.is_file())
            if file_count == 0:
                display_name += " (empty)"
            else:
                display_name += f" ({file_count} files)"
                
            # Add To UI List Widget
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, str(task_dir))
            self.task_folders_list.addItem(item)
        

    """
    
        Desc: Function Will Handle The Selection Of A Task Folder From The List.
        It Will Clear The Files List And Viewer, Then Populate The Files List
        With The Files Found In The Selected Task Folder. It Will Also Update
        The File Viewer To Display The Selected Folder's Files. The Function Will
        Handle The Selection Of A Task Folder By The User And Update The UI
        Accordingly. It Will Also Handle The Case Where No Files Are Found In The
        Selected Folder.

        Preconditions:
            1. The Task Folders List Should Be Populated With Task Folders
            2. The Function Should Be Called When The User Selects A Task Folder
            3. The Task Folder Expects File Types Of .tif, .pdf, .ply, and .laz
            4. The Function Should Be Called When The User Selects A Task Folder
    
        Postconditions:
            1. The Files List Will Be Cleared And Re-populated With The Files Found
               In The Selected Task Folder.
            2. Each Item In The Files List Will Contain The Name Of The File And Its
               Size.
            3. If No Files Are Found, A Message Will Be Displayed Indicating So.
            4. The File Viewer Will Be Reset To An Empty State.
            5. The Colormap Selector Will Be Hidden And The Export Button Disabled.

    """
    def _on_task_selected(self):
        # Clear Files And Viewer Content
        self.files_list.clear()
        self.file_viewers.setCurrentIndex(2)
        self.file_info.setText("No file selected")
        self.colormap_label.setVisible(False)
        self.colormap_selector.setVisible(False)
        self.export_btn.setEnabled(False)
        
        # Check For The Selected Task Folder
        selected_items = self.task_folders_list.selectedItems()
        if not selected_items:
            return
        
        # Get Our Selected Task File Path
        task_path = Path(selected_items[0].data(Qt.UserRole))
        self.current_task_path = task_path
        
        # List All Extracted File Types
        file_types = {
            "*.tif": "Digital Surface Model",
            "*.pdf": "Report Document",
            "*.ply": "Point Cloud (PLY)",
            "*.laz": "Point Cloud (LAZ)"
        }
        
        files_found = False
        
        # Add Each Of Our Files To THe List With Their Size
        for pattern, description in file_types.items():

            # Find Files Matching The Pattern
            for file_path in sorted(task_path.glob(pattern)):
                files_found = True
                # Format File's Size In Megabytes Or Kilobytes
                size_mb = file_path.stat().st_size / (1024 * 1024)
                size_str = f"{size_mb:.1f} MB" if size_mb >= 1 else f"{file_path.stat().st_size / 1024:.1f} KB"
                
                # Create List Item With Description, File Name, And Size
                item = QListWidgetItem(f"{description} - {file_path.name} ({size_str})")
                item.setData(Qt.UserRole, str(file_path))
                self.files_list.addItem(item)
        
        # Prompt User When Theres No Files Retreived
        if not files_found:
            self.files_list.addItem("No output files found in this folder")
    

    """

        Desc: Function Will Handle The Selection Of A File From The Provided
        Viewer List. When A File Is Selected, It Will Check The File Type
        And Load The Appropriate Viewer For That Type. It Will Also
        Update The File Information Label With The Selected File's Name
        And Size.

        Preconditions:
            1. File List Contains Files To Select From.
            2. The Function Is Called In Conjunction With The Selection Of A File.
            3. The File List Should Contain Files Of Type .tif, .pdf, .ply, and .laz
        
        Postconditions:
            1. The File Viewer Will Be Updated To Display The Selected File.
            2. The File Information Label Will Be Updated With The Selected File's Name And Size
            3. The Colormap Selector Will Be Enabled For .tif Files To Change Filter Used.
            4. The Colormap Selected Will Be Hidden If Not A .tif File.
            5. The Export Button Will Be Enabled For All File Types.
            6. The File Viewer Will Be Set To An Empty State If No File Is Selected Or Selected Unsupported Format.

    """
    def _on_file_selected(self):
        # Get Selected Item From The List
        selected_items = self.files_list.selectedItems()

        # Clear Viewer Content If No File Is Selected
        if not selected_items:
            self.file_viewers.setCurrentIndex(2)  # Empty state
            self.file_info.setText("No file selected")
            self.colormap_label.setVisible(False)
            self.colormap_selector.setVisible(False)
            self.export_btn.setEnabled(False)
            return
        
        # Get Our File Path
        file_path = Path(selected_items[0].data(Qt.UserRole))
        self.current_file_path = file_path
        
        # Enable Our Export Button In The UI
        self.export_btn.setEnabled(True)
        
        # Update The File Size And Name In The UI
        size_mb = file_path.stat().st_size / (1024 * 1024)
        size_str = f"{size_mb:.1f} MB" if size_mb >= 1 else f"{file_path.stat().st_size / 1024:.1f} KB"
        self.file_info.setText(f"Selected: {file_path.name} ({size_str})")
        
        # Determine The Suffix Of Our File For Appropriate Viewer
        extension = file_path.suffix.lower()
        
        # If A .tif File (View As Image)
        if extension == '.tif' or extension == '.tiff':
            self._load_tif_file(file_path)
            # Show Colormap Only For .tif Files
            self._update_file_config(True)
        else:
            # For Other Files, Request Client To Open In External Viewer
            self.file_viewers.setCurrentIndex(1)  # Empty State
            self.empty_state.setText(f"File type {extension} cannot be previewed.\nUse 'Open in External Viewer' to view this file.")
            self._update_file_config(False)  # Hide Colormap and Export Button
    

    def _update_file_config(self, state : bool):
        self.colormap_label.setVisible(state)
        self.colormap_selector.setVisible(state)
        self.contour_label.setVisible(state)
        self.contour_slider.setVisible(state)
        self.contour_value.setVisible(state)
        self.apply_btn.setVisible(state)
        


    """
    
        Desc: Function Will Load A .tif File And Display It In The Viewer.
        It Will Apply Enhanced Terrain Visualization Techniques To The
        Image, Including Hillshading And Colormap Application. The Function
        Will Also Handle The Case Where The File Cannot Be Loaded Or Displayed,
        And Will Provide An Error Message To The User. It Will Also Grab
        Metadata Information From The File And Display It In The UI For Height
        Maps.

        Preconditions:
            1. The File Path Provided Should Be A .tif File
            2. The File Should Be A Valid Raster File That Can Be Opened With Rasterio
            3. The File Should Have Metadata Information For Height Map Key
        
        Postconditions:
            1. The .tif File Will Be Displayed To The User Through The UI
            2. The .tif File Metadata Information As Well As Name Will Be Displayed
            3. The File Viewer Will Be Set To The TIF Page
            4. If We Have A Single Band File, The Colormap Will Be Applied
            5. If We Have A Multi-Band File, The RGB Bands Will Be Displayed Without Colormap
            6. If The File Cannot Be Loaded, An Error Message Will Be Displayed.
    
    """
    def _load_tif_file(self, file_path):
        try:
            with rasterio.Env(GDAL_CACHEMAX=512):
                with rasterio.open(str(file_path)) as src:
                    # Single Band Photo (e.g. DSM, DTM) Or Multi-Band (e.g. RGB)
                    if src.count == 1:
                        # If Single-Band, Read The Data
                        data = src.read(1)
                        # For Given NoData Value, Set To NaN For Visualization
                        if src.nodata is not None:
                            data = np.where(data == src.nodata, np.nan, data)
                        
                        # Create Our Figure...
                        dpi = 15                                  # DPI Is Utilized For Content Scaling
                        height, width = data.shape                 # Get The Height And Width Of The Image
                        
                        if height * width > 4000000:  # 4 megapixels threshold
                            if self.auto_scaling:
                                # Use automatic scaling based on image size 
                                scale_factor = np.sqrt(5000000 / (height * width))
                            else:
                                # Use user-defined scaling from slider
                                scale_factor = self.scale_factor_override
                                
                            # Don't scale up if scale factor > 1
                            if scale_factor < 1.0:
                                new_height = int(height * scale_factor)
                                new_width = int(width * scale_factor)
                                
                                # Use high-quality Lanczos resampling
                                data = cv2.resize(data, (new_width, new_height), 
                                                interpolation=cv2.INTER_LANCZOS4)
                                
                                # Apply subtle sharpening to preserve perceived detail
                                kernel = np.array([[-0.1, -0.1, -0.1],
                                                [-0.1,  1.8, -0.1],
                                                [-0.1, -0.1, -0.1]])
                                data = cv2.filter2D(data, -1, kernel)
                                
                                # Update dimensions
                                height, width = data.shape
                                dpi = int(dpi / scale_factor)  # Adjust DPI based on scaling
                            

                        figsize = (width/dpi, height/dpi)          # Figure Size Will Depend On Our DPI And Image Size
                        fig = Figure(figsize=figsize, dpi=dpi)     # Setup Our Figures Size With Its Overall DPI

                        # Create Our Key Axes For The Figure
                        ax = fig.add_subplot(111)
                        
                        # Calculate Our Hillshade Filter For The Image
                        from matplotlib.colors import LightSource
                        ls = LightSource(azdeg=315, altdeg=35)
                        
                        # Compute Our Minimum And Maximum Values For The Data This Is Used For The Hillshade And Color Mapping
                        vmin, vmax = np.nanpercentile(data, [2, 98])

                        amin, amax = np.nanmin(data), np.nanmax(data)
                        # Apply Our Colormap And Hillshade To The Provided .tif Data
                        cmap = plt.get_cmap(self.current_colormap)
                        rgb = ls.shade(data, cmap=cmap, blend_mode='soft', 
                                    vmin=vmin, vmax=vmax, vert_exag=3)
                        
                        # Add Contour Lines On .tif Image To Help With Texturing (Optional To Avoid Cluttering In Small Images)
                        levels = np.linspace(amin, amax, self.contour_line_count)
                        contour = ax.contour(data, levels=levels, colors='black', 
                                        alpha=0.25, linewidths=0.4, linestyles='solid')

                        # Display Our RGB Formatted Image To User
                        ax.imshow(rgb)

                        # Get The Normalization Of The Data For The Colorbar
                        norm = Normalize(vmin=amin, vmax=amax)
                        sm = ScalarMappable(cmap=cmap, norm=norm)
                        sm.set_array([])

                        # Add Colorbar To The Figure
                        cbar = fig.colorbar(sm, ax=ax, shrink=0.9)
                        cbar.set_label(f'Elevation ({amin:.2f}m - {amax:.2f}m)', 
                                fontsize=45, fontweight='bold', labelpad=12)
                        cbar.ax.tick_params(labelsize=40, width=3, length=15)       

                        # Hide Axes For Layout Currently
                        ax.axis('off')

                        # Set The Figures Layout To Pad 0 So We Don't Overlap But Aren't Far Away
                        fig.tight_layout(pad=0)
                        
                        # Render Our Figure And Convert To QImage For Display
                        canvas = FigureCanvasAgg(fig)
                        canvas.draw()
                        buf = canvas.buffer_rgba()

                        # Convert To A QImage For UI Displayment
                        qimg = QImage(buf, width, height, QImage.Format_RGBA8888)

                        pixmap = QPixmap.fromImage(qimg)
                        
                    else:
                        # Multi-Bande Image (RGB) Will Simply Just Be Displayed Without Filter
                        rgb = np.zeros((src.height, src.width, 3), dtype=np.uint8)
                        
                        # Read All 3 Bands
                        for i in range(min(3, src.count)):
                            band = src.read(i+1)
                            
                            # Normalize Our Bands Contents
                            if np.any(band):
                                min_val = np.percentile(band[band > 0], 2)
                                max_val = np.percentile(band[band > 0], 98)
                                if min_val == max_val:
                                    # Increment Through Our Buffer And Set Our Values For Each Entry
                                    rgb[:,:,i] = 0
                                else:
                                    # Increment Through Our Buffer And Set Our Values For Each Entry
                                    rgb[:,:,i] = np.clip((band - min_val) * 255 / (max_val - min_val), 0, 255).astype(np.uint8)
                        
                        # Create A QImage With RGB Data And Then Pass It Into Pixmap For Display
                        qimg = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.shape[1] * 3, QImage.Format_RGB888)
                        pixmap = QPixmap.fromImage(qimg)
                    
                    # Update The Image Label With The Pixmap
                    self.tif_image.setPixmap(pixmap)
                    self.tif_image.setMinimumSize(QSize(1, 1))  # Allow Our Images Scaling
                    
                    # Set Our Current View To The .tif Viewer
                    self.file_viewers.setCurrentIndex(0)
                    
                    # Add Metadata Information To The File Info Label If We Are A Single-Band Image
                    if src.count == 1:
                        stats = {
                            "Min elevation": f"{np.nanmin(data):.2f}m",
                            "Max elevation": f"{np.nanmax(data):.2f}m",
                            "Mean elevation": f"{np.nanmean(data):.2f}m",
                            "Resolution": f"{src.res[0]:.2f}m/pixel"
                        }
                        # Format With Key: Value Pairs
                        stats_str = " | ".join([f"{k}: {v}" for k, v in stats.items()])
                        self.file_info.setText(f"{file_path.name} - {stats_str}")
                    
         # Else If We Fail, Set To Empty State And Return To User A Traceback Error
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.file_viewers.setCurrentIndex(2)  # Empty state
            self.empty_state.setText(f"Error loading TIF file: {str(e)}")
    

    """
    
        Desc: Function Will Handle The Changing Of The Colormap Filter For .tif Files.
        It Will Change The Colormap Based On Our Selection Presented And Reload The .tif Image
        With This New Colormap.

        Preconditions:
            1. Called When The User Changes The Active Colormap Through The UI
            2. The Colormap Selected, Should Be Within The List Of Available Colormaps
            3. The File Path Is A Valid .tif File

        Postconditions:
            1. The Colormap Used Is Changed To The Selected Colormap
            2. The .tif File Is Reloaded With The New Colormap Filter Through self._load_Tif_file(...)
            3. The File Viewer Is Updated To Display The New Colormap
            4. The File Information Label Will Be Adjusted With The New Colormap
    
    """
    def _on_colormap_changed(self, colormap_name):
        # Set The Current Colormap To The Selected One
        self.current_colormap = colormap_name
        
        # Reload The .tif File With The New Colormap
        if self.current_file_path and self.current_file_path.suffix.lower() in ('.tif', '.tiff'):
            self._load_tif_file(self.current_file_path)
    

    """
    
        Desc: Function Will Open A Selected File Based On User's Platform And The User's
        Preferred Software To View The File. This Is Utilized To Launch Open Unsupported File Types
        On The User's System Without Need For Special Handling. This Is Mainly Utilized To Launch
        Open User's Web Browser For Filetypes Like .pdf, .ply, and .laz. It Will Also Handle The Case 
        Where The File Cannot Be Opened, And Provide An Error Message.

        Preconditions:
            1. The File Path Should Be A Valid File Path
            2. The Function Should Be Called When The User Clicks On The Open In External Viewer Button
            3. The File Path Has Read Access
            4. The File Is A Valid File Type That Can Be Opened By The User's System

        Postconditions:
            1. The File Selected Will Be Opened In The User's Default Software Of Choice.
            2. If The File Cannot Be Opened, Provide An Error Message To User
    
    """
    def _open_external(self):
        # If We Have No File Selected, Return
        if not self.current_file_path:
            return
        
        # Attempt To Open The Users File In Their Default Software
        try:
            import os
            import subprocess
            import platform
            
            # If Windows OS
            if platform.system() == 'Windows':
                os.startfile(str(self.current_file_path))
            # If MacOS OS
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', str(self.current_file_path)))
            # If Linux OS
            else:  # Linux
                subprocess.call(('xdg-open', str(self.current_file_path)))
        # Else If We Fail To Open A Provided File Prompt User With An Error Message
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file: {str(e)}")
    

    """
    
        Desc: Function Will Allow User To Export A Selected File To A User-Specified Location
        On Their System. When A User Wants To Export A File, It Will Prompt The User For A Destination Directory
        And Copy The File To That Location. It Will Also Handle The Case Where The File Cannot Be Exported,
        And Provide An Error Message.

        Preconditions:
            1. The File Path Should Be A Valid File Path
            2. This Function Is Called When The User Clicks On The Export Button Through The UI
            3. The File Path Has Read Access
            4. The Destination Directory Should Have Write Access
        
        Postconditions:
            1. The File Selected Will Be Copied To The User-Specified Directory
            2. If The File Cannot Be Exported, Provide A Error Message To User
            3. If The File Is Exported Successfully, Provide A Success Message To User
    
    """
    def _export_file(self):
        # If We Selected No File, Return
        if not self.current_file_path:
            return
        
        # Get The Destination Path For Our File To Be Copied To
        dest_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export File", 
            str(self.current_file_path.name),
            f"*{self.current_file_path.suffix}"
        )
        
        # IF Not A Valid Destination Path, Return
        if not dest_path:
            return

        # Attempt To Copy Our File Into Our Destination Path
        try:
            import shutil
            shutil.copy2(self.current_file_path, dest_path)
            QMessageBox.information(self, "Success", f"File exported to {dest_path}")
        # If We Fail Copying Our File's Contents, Return Error Message
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not export file: {str(e)}")
    

    """
    
        Desc: Function Will Close Up The Results Viewer When The User Selects Our Return
        To Pipeline BUtton. It Uses Our Parent Windows QStackedWidget To Change The Pane

        Preconditions:
            1. The Parent Window Should Be A QStackedWidget
            2. The Function Should Be Called When The User Clicks On The Return To Pipeline Button

        Postconditions:
            1. The Results Viewer Will Be Closed Up And The User Will Be Returned To The Pipeline Page
            2. The Stacked Widget Will Be Set To The Pipeline Page Index (0)
    
    """
    def _go_back_to_pipeline(self):
        # Close UI Window We're Associated With
        self.close()
        del self


















from pathlib import Path    
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QVBoxLayout, 
                           QLabel, QFrame, QStackedWidget, QMessageBox)
from PyQt5.QtCore import Qt, QMimeData, pyqtSlot, QThread
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication
from .settings_window import SettingsWindow
from .drag_drop_widget import DragDropWidget
from .styles import STYLE_SHEET
from .progress_bar import ProgressWidget
from .pipeline_worker import PipelineWorker
from PyQt5.QtCore import pyqtSignal
from .result_dialog import ResultDialog
from ..utils.config_loader import ConfigLoader

"""

    Desc: Class Is Utilized To Create Our Main Client Window Which Will
    Be The Base For Our Application. The Main Client Window Will Contain
    A Drag & Drop Area For Image Uploads, A Settings Button, And A Status
    Bar For User Feedback. The Window Will Utilize A Dark Green And Brown
    Theme. The Window Also Gives The User Settings To Alter The Pipeline
    By Adjusting Our YAML Config.

"""
class MainClientWindow(QMainWindow):

    """
    
        Desc: Initializes Our Main Client Window With A Title And Minimum
        Size. The Window Will Contain A Drag & Drop Area, Settings Button,
        And Status Bar. The Window Will Utilize A Dark Green And Brown Theme
        For Styling. The Window Will Also Allow The User To Open A Settings
        Window To Adjust The Pipeline Configuration. It Is Formatted As A
        Vertical Layout.

        Preconditions:
            1. None

        Postconditions:
            1. Set Our Window Title
            2. Set Our Window Minimum Size
            3. Set Our Window Style
            4. Create Our Central Widget
            5. Create A Vertical Layout For Our Central Widget
            6. Add Our Title To The Layout
            7. Add Our Drag & Drop Area To The Layout
            8. Add Our Settings Button To The Layout
            9. Add Our Status Bar To The Window
    
    """
    def __init__(self, config_path = Path(__file__).parent.parent.parent / "config/config.yaml"):
        super().__init__()
        self.setWindowTitle("Resilient Geo Drone")

        self.config_path = config_path
        self.config = ConfigLoader(self.config_path)

        # Set The Minimum Size Of The Window
        self.setMinimumSize(800, 600)
       
        
        # Set Our Style Guideline As Forest Theme (Dark Green & Brown)
        self.setStyleSheet(STYLE_SHEET)
        
        # Create Our Central Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create A Vertical Layout For Our Central Widget
        layout = QVBoxLayout(main_widget)

        # Set Spacing And Margins For Our Layout
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header Title
        title = QLabel("Resilient Geo Drone")
        title.setObjectName("title")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # Stacked Widget
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Drag & Drop Area (Page 1)
        self.drag_drop = DragDropWidget(self.config)
        self.stacked_widget.addWidget(self.drag_drop)

        # Progress Widget (Page 2)
        self.progress_widget = ProgressWidget()
        self.progress_widget.cancel_request.connect(self.cancel_pipeline)
        self.stacked_widget.addWidget(self.progress_widget)

        # Tasks Pane (Page 3)
        self.tasks_pane = QWidget()
        self.tasks_pane.setObjectName("tasksPane")
        self.stacked_widget.addWidget(self.tasks_pane)

        tasks_layout = QVBoxLayout(self.tasks_pane)
        tasks_layout.setContentsMargins(0, 0, 0, 0)
        tasks_layout.setSpacing(0)
        
        
        # Start On Drag & Drop Page
        self.stacked_widget.setCurrentIndex(0)

        # Settings Button
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.setObjectName("settingsButton")

        # Connect Settings Button To Open Settings Window
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn, alignment=Qt.AlignRight)


        # Status Bar
        self.statusBar().showMessage("Ready")

        self.view_results_button = QPushButton("📁 View Results")
        self.view_results_button.setObjectName("viewResultsButton")
        self.view_results_button.clicked.connect(self.open_tasks_pane)
        layout.addWidget(self.view_results_button, alignment=Qt.AlignRight)


        self.launch_button = QPushButton("Launch Pipeline")
        self.launch_button.setObjectName("launchButton")

        # Connect Settings Button To Open Settings Window
        self.launch_button.clicked.connect(self.launch_pipeline)
        layout.addWidget(self.launch_button, alignment=Qt.AlignRight)
        

    def open_tasks_pane(self):
        """Open the tasks pane and refresh the results list"""
        results_viewer = ResultsViewerWidget()
        results_viewer.setStyleSheet(STYLE_SHEET)
        results_viewer.show()


    def launch_pipeline(self):
        if not self.drag_drop.image_paths:
            self.statusBar().showMessage("No Images To Process")
            return
        
        # Update UI
        self.statusBar().showMessage("Launching Pipeline...")
        self.stacked_widget.setCurrentIndex(1)
        self.launch_button.setEnabled(False)


        # Create Our Pipeline Worker
        self.pipeline_worker = PipelineWorker(self.config_path, self.drag_drop.image_paths)

        self.pipeline_worker.progress_updated_status.connect(self.update_progress)
        self.pipeline_worker.progress_completion_status.connect(self.pipeline_complete)
        self.pipeline_worker.start()
      
    def update_progress(self, progress, status, detail):
        self.progress_widget.update_progress(progress, status, detail)
        self.statusBar().showMessage(f"Processing: {status} ({progress}%)")

    def pipeline_complete(self, success, status, detail):
        self.stacked_widget.setCurrentIndex(0)
        self.launch_button.setEnabled(True)

        # Show Resulting Dialog
        dialog = ResultDialog("Pipeline Results", status, detail, success, self)
        dialog.exec_()

        # Update Status Bar
        if success:
            self.statusBar().showMessage("Pipeline Completed Successfully")
        else:
            self.statusBar().showMessage("Pipeline Failed")


    def cancel_pipeline(self):
        reply = QMessageBox.question(self, 'Cancel Pipeline',
            "Are you sure you want to cancel the pipeline?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.pipeline_worker.cancel()
            self.statusBar().showMessage("Pipeline Cancelled")
            self.stacked_widget.setCurrentIndex(0)
            self.launch_button.setEnabled(True)
            self.pipeline_worker.wait()


    """
    
        Desc: Function Will Launch Off Our Settings Window And Display
        The Settings Pop-Up Window To The User. The Settings Window Will
        Allow The User To Adjust The Pipeline Configuration By Altering
        The YAML Configuration File.

        Preconditions:
            1. None

        Postconditions:
            1. Launch Off Settings Pop-Up Window
    
    """
    def open_settings(self):
        # Launch Off Our Settings Pop-Up Window
        self.settings_window = SettingsWindow()
        self.settings_window.show()




# If Running As Main, Initialize The Application
if __name__ == '__main__':

    # Initialize The Application
    app = QApplication(sys.argv)

    # Create Our Main Client Window
    window = MainClientWindow()
    window.show()

    # Execute The Application And Wait For Exit
    sys.exit(app.exec_())