from pathlib import Path
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QLabel, QSplitter, QComboBox, QGroupBox, 
                             QStackedWidget, QScrollArea, QFileDialog, QMessageBox, QFrame, QSlider,
                             QCheckBox, QTextEdit)
from PyQt5.QtCore import Qt, QSize, QEvent
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

from src.utils.config_loader import ConfigLoader
from src.utils.logger import LoggerSetup


"""

  Desc: This Module Provides A Results Viewer For Viewing The Output Files
  This Will Mainly Allow Users To View .tif, .png, .pdf, . and .txt Files

"""
class ResultsViewerWidget(QWidget):
  
  """

    Desc: Initialize Initial Variables For Viewing Of Folders And Files.
    Sets Up The Output Base Directory To Retrieve The Task Folders, As Well As
    The Current Task Path, File Path, And Colormap For .tif Visualization.
    The Class Will Also Set Up The UI For The Results Viewer, Including The Layout,
    Task Folders, File List, File Viewer, And Navigation Buttons.
    Now supports PNG image viewing and TXT file viewing.

    Preconditions:
      1. None

    Postconditions:
      1. Set Up The Results Viewer UI Components
      2. Set Up The Task Folders List
      3. Set Up The File List
      4. Set Up The File Viewer (TIF, PNG, TXT viewers)
      5. Set Up The Navigation Buttons
      6. Set Up The Colormap Selector

  """ 
  def __init__(self):
    try:
      super().__init__()

      # Setup Our Logger
      self.logger = LoggerSetup().get_logger()

      self.logger.info("Results Viewer ID: {self}  -  Initializing Results Viewer...")

      # Setup Window's Title And Size
      self.setObjectName("resultsViewer")
      self.setWindowTitle("Results Viewer")
      self.setMinimumSize(900, 600)
      
      # Setup The Base Directory For The Output Files
      self.output_base_dir = Path(ConfigLoader().load()['geospatial']['output_path'] + '/point_cloud')

      # Setup The Current Task Path And File Path (Remember For Accession Throughout The Class)
      self.current_task_path = None
      self.current_file_path = None

      # Set-Up Base Resolution Of Viewed Images (Mainly .tifs)
      self.scale_factor_override = 1.0  # Default = Full Resolution

      # Normally, We Want To Auto Scale The Image
      self.auto_scaling = True 
      self.contour_line_count = 5
      self.current_colormap = 'viridis'

      # Initialize drag state for fullscreen viewer
      self.is_dragging = False
      self.drag_start_pos = None
      self.drag_start_h_scroll = 0
      self.drag_start_v_scroll = 0
      self.current_scale_factor = 1.0
      self.original_pixmap_size = None
      self.fullscreen_overlay = None
      self.fullscreen_image = None
      self.fullscreen_scroll_area = None

      self.logger.info("Results Viewer ID: {self}  -  Results Viewer Initialized.")

      # Setup The UI Layout
      self.logger.info("Results Viewer ID: {self}  -  Setting Up Results Viewer UI...")
      self._setup_ui()
      self.logger.info("Results Viewer ID: {self}  -  Results Viewer UI Set Up Successfully.")
    except Exception as e:
      self.logger.error(f"Results Viewer ID: {self}  -  Failed To Initialize Results Viewer: {str(e)}")
      QMessageBox.critical(self, "Initialization Error", f"Failed to initialize Results Viewer: {str(e)}")
      raise e


  """

    Desc: Will Update The UI Feedback For The Current Countour Line
    Count Value. This Should Be Called When The Slider Value Changes.

    Preconditions:
      1. value Is [0, 1000]

    Postconditions:
      1. The Contour Value Label Will Be Updated To Reflect The Current Slider Value

  """
  def _update_contour_value(self, value : int):
    self.contour_value.setText(str(value))


  """

    Desc: Function Will Increase The Contour Line Count Based On The Slider Value.
    This Should Be Called When The User Presses The Update Button To Apply The Changes
    (Should Be Called In Conjunction With The Resolution Slider). 

    Preconditons:
      1. The Slider Should Be A Valid QSlider Object
      2. The Slider Should Be Connected To The _update_contour_value Function

    Postconditions:
      1. The Contour Line Count Will Be Updated Based On The Slider Value
      2. The Function Will Check If The Current File Path Is A Valid TIF File
      3. If So, It Will Reload The TIF File With The New Contour Line Count

  """
  def _apply_contour_changes(self):
    self.logger.info(f"Results Viewer ID: {self}  -  Applying Contour Line Count: {self.contour_slider.value()}")
    self.contour_line_count = self.contour_slider.value()

    # Reload Our TIF File With The New Contour Line Count
    if self.current_file_path and self.current_file_path.suffix.lower() in ('.tiff', '.tif'):
      self.logger.info(f"Results Viewer ID: {self}  -  Reloading TIF File: {self.current_file_path} with Contour Line Count: {self.contour_line_count}")
      self._load_tif_file(self.current_file_path)


  """

    Desc: Function Will Setup The UI Layout For The Results Viewer
    Including The Task Folders Panel, File List Panel, As Well As 
    File Contents Panel. The Function Will Also Setup The Navigation Buttons
    For The User To Navigate Back To The Pipeline Page As Well As Open
    The Selected File In Through Their Web Browser And Also Export The File.
    Now includes support for PNG image viewing and TXT file viewing.

    Preconditions:
      1. None

    Postconditions:
      1. Set Up The UI Layout For The Results Viewer
      2. Set Up The Task Folders Panel
      3. Set Up The File List Panel
      4. Set Up The File Contents Panel (TIF, PNG, TXT viewers)
      5. Set Up The Navigation Buttons
      6. Set Up The Colormap Selector

  """
  def _setup_ui(self):
    # Main Layout
    main_layout = QVBoxLayout(self)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(15)
    
    # Header Of Our Pane
    header = QLabel("Pipeline Results Viewer", objectName="sectionHeader")
    main_layout.addWidget(header)
    
    # Description Of Users Capabilities
    description = QLabel("Select a task folder to view its output files (DSM, DTM, orthophotos, images, text files, and reports)", objectName="sectionDescription", wordWrap=True)
    main_layout.addWidget(description)
    
    # Horizontal Split For Folder And File Selection
    splitter = QSplitter(Qt.Horizontal)
    splitter.setHandleWidth(8)
    
    # Left Side: Task Folder And File Selection
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 0, 0)
    
    # Task Folders Will Be Top Group
    folders_group = QGroupBox("Task Folders", objectName="taskFoldersGroup")
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
    files_group = QGroupBox("Available Files", objectName="availableFilesGroup")
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

    # Open Directory Button (For Opening The Task Folder In File Explorer)
    open_dur_btn = QPushButton("Open Task Directory")
    open_dur_btn.clicked.connect(self._open_output_directory)
    files_layout.addWidget(open_dur_btn)
    
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
    self.file_info = QLabel("No file selected", objectName="fileInfoHeader")
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
    line = QFrame(frameShape=QFrame.VLine, frameShadow=QFrame.Sunken)
    options_layout.addWidget(line)

    # Countour Lines
    self.contour_label = QLabel("Contour Line Count:")
    options_layout.addWidget(self.contour_label)

    self.contour_slider = QSlider(Qt.Horizontal)
    self.contour_slider.setRange(1, 1000)

    self.contour_slider.setValue(self.contour_line_count)  # Default Value
    self.contour_slider.setFixedWidth(120)
    
    options_layout.addWidget(self.contour_slider)

    self.contour_value = QLabel("5")
    options_layout.addWidget(self.contour_value)

    # Connect Slider Value Changed Signal
    self.contour_slider.valueChanged.connect(self._update_contour_value)

    # After Contour slider Section, Add:
    line = QFrame(frameShape=QFrame.VLine, frameShadow=QFrame.Sunken)
    options_layout.addWidget(line)

    # Scale Factor Controls
    self.auto_scale_checkbox = QCheckBox("Auto")
    self.auto_scale_checkbox.setChecked(True)
    self.auto_scale_checkbox.stateChanged.connect(self._toggle_scale_slider)
    options_layout.addWidget(self.auto_scale_checkbox)

    self.scale_label = QLabel("Resolution:")
    options_layout.addWidget(self.scale_label)

    self.scale_slider = QSlider(Qt.Horizontal)
    self.scale_slider.setRange(10, 100)  # 10% To 100%
    self.scale_slider.setValue(100)      # Default 100%
    self.scale_slider.setFixedWidth(120)
    self.scale_slider.setEnabled(False)  # Initially Disabled When Auto Is On
    options_layout.addWidget(self.scale_slider)

    self.scale_value = QLabel("100%")
    options_layout.addWidget(self.scale_value)

    # Connect Slider Value Changed Signal
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
    self.tif_image = QLabel("No image selected", objectName="tifImage")
    self.tif_image.setAlignment(Qt.AlignCenter)
    self.tif_image.mousePressEvent = self._on_image_clicked

    # Set Our Defaut Image To Nothing Currently
    self.tif_viewer.setWidget(self.tif_image)
    self.file_viewers.addWidget(self.tif_viewer)
    
    # Empty State (page 1)
    self.empty_state = QLabel("Select a file from the list to view its contents")
    self.empty_state.setAlignment(Qt.AlignCenter)
    self.file_viewers.addWidget(self.empty_state)
    
    # PNG Image Viewer (Page 2)
    self.png_viewer = QScrollArea()
    self.png_viewer.setWidgetResizable(True)
    self.png_viewer.setAlignment(Qt.AlignCenter)
    self.png_image = QLabel("No PNG selected", objectName="pngImage")
    self.png_image.setAlignment(Qt.AlignCenter)
    self.png_image.mousePressEvent = self._on_png_clicked
    self.png_viewer.setWidget(self.png_image)
    self.file_viewers.addWidget(self.png_viewer)
    
    # Text File Viewer (Page 3)
    self.text_viewer = QTextEdit()
    self.text_viewer.setReadOnly(True)
    self.text_viewer.setObjectName("textViewer")
    self.file_viewers.addWidget(self.text_viewer)
    
    # Set To Our Default State Initially
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

    self._update_file_config(False)  # Hide Colormap And Export Button
    
    # Initial Refresh Of Task Folders
    self.refresh_task_folders()


  """
  
    Desc: Function Will Open The The Output Directory Containing The Result Files
    In Windows File Explorer. If A Specific Task Folder Is Currently Selected, It Will
    Open That Task's Directory, But If Not It Will Open The Base Output Directory.

    Preconditions:
      1. The Output Base Directory Should Exist As A Valid Path
      2. The Function Should Be Called When The User Clicks The "Open Task Directory" Button

    Postconditions:
      1. Windows File Explorer Will Open The Output Base Directory
      2. If The Directory Cannot Be Opened (Mainly If Not On Windows Or Invalid Path), Error Message Will Show
  
  """
  def _open_output_directory(self):
    try:
      self.logger.info(f"Results Viewer ID: {self}  -  Attempting to open output directory...")
      import os
      import subprocess
      import platform

      # Determine The Correct Directory
      if self.current_task_path and self.current_task_path.exists():
        # Open The Current Task Directory
        directory_to_open = self.current_task_path
      else:
        # Open The Base Output Directory
        directory_to_open = self.output_base_dir
      
      # Check If The Directory Exists
      if not directory_to_open.exists():
        QMessageBox.warning(self, "Directory Not Found", f"The directory {directory_to_open} does not exist.")
        return
      
      # Open The Directory In File Explorer
      if platform.system() == "Windows":
        os.startfile(str(directory_to_open))
      elif platform.system() == "Darwin":  # macOS
        subprocess.run(("open", str(directory_to_open)))
      else:  # Linux and Other Systems
        subprocess.run(("xdg-open", str(directory_to_open)))
      self.logger.info(f"Results Viewer ID: {self}  -  Successfully opened directory: {directory_to_open}")

    except Exception as e:
      self.logger.error(f"Results Viewer ID: {self}  -  Failed to open directory: {str(e)}")
      # Show Error Message If We Cannot Open The Directory
      QMessageBox.critical(self, "Error Opening Directory", f"Could not open the directory: {str(e)}")



  """

    Desc: Will Handle The Enabling And Disabiling Of The Scale Slider
    Based On The State Of The Auto Checkbox. If The Auto Checkbox Is Checked,
    The Scale Slider Will Be Disabled. If The Auto Checkbox Is Unchecked,
    The Scale Slider Will Be Enabled. Also If Autoscaling Is Turned
    Back On It Will Reload The Current File.

    Preconditions:
      1. state Is A Boolean Value Indicating The State Of The Auto Checkbox

    Postconditions:
      1. The Scale Slider Will Be Enabled Or Disabled Based On The State Of The Auto Checkbox
      2. If Autoscaling Is Turned On, The Current File Will Be Reloaded

  """
  def _toggle_scale_slider(self, state : bool):
    self.logger.info(f"Results Viewer ID: {self}  -  Toggling Auto Scaling: {'Enabled' if state else 'Disabled'}")
    self.auto_scaling = state
    self.scale_slider.setEnabled(not self.auto_scaling)
    
    # If We Just Turned Autoscaling Back On, Reload The Current File
    if self.auto_scaling and self.current_file_path and self.current_file_path.suffix.lower() in ('.tiff', '.tif'):
      self.logger.info(f"Results Viewer ID: {self}  -  Reloading TIF File: {self.current_file_path} with Auto Scaling Enabled")
      self._load_tif_file(self.current_file_path)


  """

    Desc: Will Handle The Updating Of The Scale Value Based On The Slider Value.
    The Function Will Update The Scale Value Label To Reflect The Current Slider Value
    And Set The Scale Factor Override To The Current Slider Value Divided By 100 
    (To Normalize For Scalar Multiplication Of .tif's).

    Preconditions:
      1. value Is An Integer Value Between (0, 100]

    Postconditions:
      1. The Scale Value Label Will Be Updated To Reflect The Current Slider Value
      2. The Scale Factor Override Will Be Set To The Current Slider Value To A Normalized Value

  """
  def _update_scale_value(self, value : int):
    self.scale_value.setText(f"{value}%")
    self.scale_factor_override = value / 100.0


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
      # Log The Click Event
      self.logger.info(f"Results Viewer ID: {self}  -  Image clicked in TIF Viewer.")

      # Only Expand If We Have A Image Setup
      if not self.tif_image.pixmap() or self.tif_image.pixmap().isNull():
        self.logger.warning(f"Results Viewer ID: {self}  -  No valid image to display in full screen.")
        return
      
      # Get Our Current Pixmap
      pixmap = self.tif_image.pixmap()
      if pixmap:
        self.logger.info(f"Results Viewer ID: {self}  -  Showing image in full screen.")
        # If We Have A Pixmap, Show It In Full Screen
        self._show_full_screen_image(pixmap)
      else:
        self.logger.warning(f"Results Viewer ID: {self}  -  No valid pixmap to display in full screen.")

  """
  
    Desc: Function Will Handle When The User Clicks On The PNG Image In The PNG Viewer.
    It Will Check If The Image Is Valid And If So, It Will Show The Image In Full Screen.
    Else If It's Empty No Action Will Be Taken.

    Preconditions:
      1. The Image Should Be A Valid Image Loaded In The PNG Viewer
      2. The Function Should Be Called When The User Clicks On The Image
      3. The Image Should Be A Valid QPixmap Object

    Postconditions:
      1. If The Image Is Valid, It Will Be Shown In Full Screen
      2. If The Image Is Empty, No Action Will Be Taken
  
  """
  def _on_png_clicked(self, event):
    if event.button() == Qt.LeftButton:
      # Log The Click Event
      self.logger.info(f"Results Viewer ID: {self}  -  PNG image clicked in PNG Viewer.")

      # Only Expand If We Have An Image Setup
      if not self.png_image.pixmap() or self.png_image.pixmap().isNull():
        self.logger.warning(f"Results Viewer ID: {self}  -  No valid PNG image to display in full screen.")
        return
      
      # Get Our Current Pixmap
      pixmap = self.png_image.pixmap()

      if pixmap:
        self.logger.info(f"Results Viewer ID: {self}  -  Showing PNG image in full screen.")
        # If We Have A Pixmap, Show It In Full Screen
        self._show_full_screen_image(pixmap)
      else:
        self.logger.warning(f"Results Viewer ID: {self}  -  No valid PNG pixmap to display in full screen.")


  """

    Desc: Will Handle The Opening Of The Full Screen Image Viewer.
    It Will Create A Full-Screen Overlay Widget With The Image Displayed
    In The Center. The Overlay Will Have A Scroll Area For Panning
    And Zooming. The User Can Exit The Full-Screen Mode By Pressing ESC.
    The User Can Also Zoom In And Out Using The Mouse Wheel And Pan
    By Clicking And Dragging The Image.

    Preconditions:
      1. pixmap Is A Valid QPixmap Object
      2. The Function Should Be Called When The User Clicks On The Image

    Postconditions:
      1. A Full-Screen Overlay Widget Will Be Created With The Image Displayed
      2. The User Can Zoom In And Out Using The Mouse Wheel
      3. The User Can Pan The Image By Clicking And Dragging
      4. The User Can Exit Full-Screen Mode By Pressing ESC

  """
  def _show_full_screen_image(self, pixmap):

    # Log The Full-Screen Image Display
    self.logger.info(f"Results Viewer ID: {self}  -  Showing image in full screen overlay.")

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

    self.logger.info(f"Results Viewer ID: {self}  -  Full screen overlay displayed successfully.")


  """

    Desc: Will Handle The Event Filter For The Full-Screen Overlay.
    It Will Handle Key Press Events For Exiting Full-Screen Mode,
    Mouse Wheel Events For Zooming, And Mouse Move Events For Panning.
    
    Preconditions:
      1. obj Is The Object That Received The Event
      2. event Is The Event That Was Received

    Postconditions:
      1. If The Event Is A Key Press Event For ESC, Close The Full-Screen Overlay
      2. If The Event Is A Mouse Wheel Event, Zoom In Or Out Based On The Scroll Direction
      3. If The Event Is A Mouse Move Event, Pan The Image Based On The Mouse Movement
      4. If The Event Is A Mouse Button Release Event, Stop Panning

  """
  def eventFilter(self, obj, event):

    # Handles ESC Key To Exit Full-Screen
    if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:

      self.logger.info(f"Results Viewer ID: {self}  -  Exiting full screen overlay.")

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
    
    # Handle Panning With Mouse Move Events
    if self.fullscreen_scroll_area and obj == self.fullscreen_scroll_area.viewport():
      # Inital Click
      if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
        self.is_dragging = True
        self.drag_start_pos = event.pos()
        self.fullscreen_scroll_area.viewport().setCursor(Qt.ClosedHandCursor)
        self.drag_start_h_scroll = self.fullscreen_scroll_area.horizontalScrollBar().value()
        self.drag_start_v_scroll = self.fullscreen_scroll_area.verticalScrollBar().value()
        return True
      # During Drag
      elif event.type() == QEvent.MouseMove and self.is_dragging:
        # Get Our Offset
        delta = event.pos() - self.drag_start_pos
        self.fullscreen_scroll_area.horizontalScrollBar().setValue(self.drag_start_h_scroll - delta.x())
        self.fullscreen_scroll_area.verticalScrollBar().setValue(self.drag_start_v_scroll - delta.y())
        return True
      # When Click Release
      elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
        self.is_dragging = False
        self.fullscreen_scroll_area.viewport().setCursor(Qt.ArrowCursor)
        return True
    
    # If Failed, Call The Parent Event Filter
    return super().eventFilter(obj, event)


  """
  
    Desc: Will Update The Full-Screen Zoom Based On The Current Scale Factor.
    It Will Scale The Original Pixmap Size Based On The Current Scale Factor
    And Update The Image In The UI. This Should Be Called When The User Zooms
    In Or Out Of The Image In Full-Screen Mode.

    Preconditions:
      1. self.fullscreen_image Is A Valid QLabel Object
      2. self.original_pixmap_size Is A Valid QSize Object
      3. self.current_scale_factor Is A Valid Float Value

    Postconditions:
      1. The Full-Screen Image Will Be Updated Based On The Current Scale Factor
      2. The Image Will Be Scaled To The New Size
      3. The Image In The UI Will Be Updated With The Scaled Pixmap

  """
  def _update_fullscreen_zoom(self):
    # If We Don't Have A Fullscreen Image Or Original Pixmap Size, Do Nothing
    if not self.fullscreen_image or not self.original_pixmap_size:
      return
    
    # Get Original Pixmap
    pixmap = self.tif_image.pixmap() if self.file_viewers.currentIndex() == 0 else self.png_image.pixmap()

    # If We Are Zooming On A Non-Existent Pixmap, Do Nothing
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
    
    # Log The Refresh Action
    self.logger.info(f"Results Viewer ID: {self}  -  Refreshing task folders list from {self.output_base_dir}")

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
      # If The Directory Does Not Exist, Show An Error Message And Log
      self.logger.error(f"Results Viewer ID: {self}  -  Output base directory does not exist: {self.output_base_dir}")
      self.task_folders_list.setEnabled(False)
      self.task_folders_list.addItem("No output directory found")
      return
    
    # Find All Task Directories
    self.logger.info(f"Results Viewer ID: {self}  -  Scanning for task directories in {self.output_base_dir}")
    task_dirs = []
    try:
      # Get All Subdirectories In The Output Base Directory
      task_dirs = [d for d in self.output_base_dir.iterdir() if d.is_dir()]
      
      # Sort By Modification Time (Newest First)
      task_dirs = sorted(task_dirs, key=lambda d: d.stat().st_mtime, reverse=True)
      self.logger.info(f"Results Viewer ID: {self}  -  Found {len(task_dirs)} task directories")
    except Exception as e:
      # Log The Error And Show It In The UI
      self.logger.error(f"Results Viewer ID: {self}  -  Error scanning directory: {str(e)}")

      # Handle Errors While Scanning Directory
      self.task_folders_list.addItem(f"Error scanning directory: {str(e)}")
      return
    
    # No Task Folders Were Found
    if not task_dirs:
      self.logger.info(f"Results Viewer ID: {self}  -  No task folders found in {self.output_base_dir}")
      # Make It So You Cannot Select A Task Folder
      self.task_folders_list.setEnabled(False)
      self.task_folders_list.addItem("No task folders found")
      return
    
    # Log The Number Of Task Folders Found
    self.logger.info(f"Results Viewer ID: {self}  -  Found {len(task_dirs)} task folders in {self.output_base_dir}")
    
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

    # Enable The Task Folders List (If It Was Disabled [e.g., No Folders Found, Then Refreshed After Running Pipeline With Same Instance Of Viewer])
    self.task_folders_list.setEnabled(True)

    self.logger.info(f"Results Viewer ID: {self}  -  Task folders list refreshed successfully.")


  """

    Desc: Function Will Handle The Selection Of A Task Folder From The List.
    It Will Clear The Files List And Viewer, Then Populate The Files List
    With The Files Found In The Selected Task Folder. It Will Also Update
    The File Viewer To Display The Selected Folder's Files. The Function Will
    Handle The Selection Of A Task Folder By The User And Update The UI
    Accordingly. It Will Also Handle The Case Where No Files Are Found In The
    Selected Folder. Now includes support for PNG and TXT files.

    Preconditions:
      1. The Task Folders List Should Be Populated With Task Folders
      2. The Function Should Be Called When The User Selects A Task Folder
      3. The Task Folder Expects File Types Of .tif, .png, .txt, .pdf, .ply, and .laz
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

    # Log The Task Selection
    self.logger.info(f"Results Viewer ID: {self}  -  Task folder selected: {self.task_folders_list.currentItem().text() if self.task_folders_list.currentItem() else 'None'}")

    # Clear Files And Viewer Content
    self.files_list.clear()
    self.file_viewers.setCurrentIndex(1)  # Empty State
    self.file_info.setText("No file selected")

    self.colormap_label.setVisible(False)
    self.colormap_selector.setVisible(False)
    self.export_btn.setEnabled(False)
    
    # Check For The Selected Task Folder 
    selected_items = self.task_folders_list.selectedItems()

    if len(selected_items) == 0:
        return
    
    # Get Our Selected Task File Path
    task_path = Path(selected_items[0].data(Qt.UserRole))
    self.current_task_path = task_path
    
    # List All Extracted File Types
    file_types = {
        "*.tif": "Digital Surface Model",
        "*.png": "Image File",
        "*.txt": "Text File", 
        "*.pdf": "Report Document"
    }
    
    # Initially Assume No Files Found
    files_found = False
    
    # Add Each Of Our Files To The List With Their Size
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

    # Prompt User When There's No Files Retrieved
    if not files_found:
      self.logger.info(f"Results Viewer ID: {self}  -  No output files found in task folder: {task_path}")
      self.files_list.addItem("No output files found in this folder")
    else:
      self.logger.info(f"Results Viewer ID: {self}  -  Found {self.files_list.count()} output files in task folder: {task_path}")


  """

    Desc: Function Will Handle The Selection Of A File From The Provided
    Viewer List. When A File Is Selected, It Will Check The File Type
    And Load The Appropriate Viewer For That Type. It Will Also
    Update The File Information Label With The Selected File's Name
    And Size. Now includes support for PNG and TXT files.

    Preconditions:
      1. File List Contains Files To Select From.
      2. The Function Is Called In Conjunction With The Selection Of A File.
      3. The File List Should Contain Files Of Type .tif, .png, .txt, .pdf, .ply, and .laz
    
    Postconditions:
      1. The File Viewer Will Be Updated To Display The Selected File.
      2. The File Information Label Will Be Updated With The Selected File's Name And Size
      3. The Colormap Selector Will Be Enabled For .tif Files To Change Filter Used.
      4. The Colormap Selected Will Be Hidden If Not A .tif File.
      5. The Export Button Will Be Enabled For All File Types.
      6. The File Viewer Will Be Set To An Empty State If No File Is Selected Or Selected Unsupported Format.

  """
  def _on_file_selected(self):

    # Log The File Selection
    self.logger.info(f"Results Viewer ID: {self}  -  File selected: {self.files_list.currentItem().text() if self.files_list.currentItem() else 'None'}")

    # Get Selected Item From The List
    selected_items = self.files_list.selectedItems()

    # Clear Viewer Content If No File Is Selected
    if not selected_items:
      self.logger.info(f"Results Viewer ID: {self}  -  No file selected, resetting viewer.")
      self.file_viewers.setCurrentIndex(1)  # Empty state
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
    if extension in ['.tif', '.tiff']:
      self.logger.info(f"Results Viewer ID: {self}  -  Loading TIF file: {file_path}")
      self._load_tif_file(file_path)
      # Show Colormap Only For .tif Files
      self._update_file_config(True)
    # If A .png File (View As Simple Image)
    elif extension == '.png':
      self.logger.info(f"Results Viewer ID: {self}  -  Loading PNG file: {file_path}")
      self._load_png_file(file_path)
      self._update_file_config(False)  # No Colormap For PNG
    # If A .txt file (View As Text) - NEW
    elif extension == '.txt':
      self.logger.info(f"Results Viewer ID: {self}  -  Loading TXT file: {file_path}")
      self._load_txt_file(file_path)
      self._update_file_config(False)  # No Colormap For Text
    else:
      # For Unsupported File Types, Show Empty State
      self.logger.warning(f"Results Viewer ID: {self}  -  Unsupported file type selected: {extension}")

      # For Other Files, Request Client To Open In External Viewer
      self.file_viewers.setCurrentIndex(1)  # Empty State
      self.empty_state.setText(f"File type {extension} cannot be previewed.\nUse 'Open in External Viewer' to view this file.")
      self._update_file_config(False)  # Hide Colormap And Export Button


  """
  
    Desc: Will Load A .png File And Display It In The Viewer.
    It Will Use QPixmap To Load The Image And Display Its Metadata
    Including Dimensions And File Size. If The Image Is Too Large,
    It Will Scale It Down For Comfortable Viewing.

    Preconditions:
      1. file_path Is A Valid Path Object Going To A .png File
      2. The Function Should Be Called When The User Selects A .png File In The Results Viewer

    Postconditions:
      1. The .png File Will Be Loaded And Save In self.png_image
  
  """
  def _load_png_file(self, file_path : Path):
    try:

      # Log The PNG File Loading
      self.logger.info(f"Results Viewer ID: {self}  -  Loading PNG file: {file_path}")

      # Load The .png Image Using QPixmap
      pixmap = QPixmap(str(file_path))
      
      if pixmap.isNull():
        self.logger.error(f"Results Viewer ID: {self}  -  Failed to load PNG file: {file_path}")
        raise Exception("Invalid PNG file or unsupported format")
      
      # Get Image Dimensions And File Size For Info Display
      width = pixmap.width()
      height = pixmap.height()
      size_mb = file_path.stat().st_size / (1024 * 1024)
      size_str = f"{size_mb:.1f} MB" if size_mb >= 1 else f"{file_path.stat().st_size / 1024:.1f} KB"
      
      # Update File Info With Image Dimensions
      self.file_info.setText(f"{file_path.name} - {width}x{height} pixels ({size_str})")
      
      # Scale Image If It's Too Large For Comfortable Viewing
      max_display_size = 1200
      if width > max_display_size or height > max_display_size:
          self.logger.info(f"Results Viewer ID: {self}  -  Scaling PNG image to fit within {max_display_size}px")
          pixmap = pixmap.scaled(max_display_size, max_display_size, 
                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
      
      # Set The Pixmap To The .png Image Label
      self.png_image.setPixmap(pixmap)
      self.png_image.setMinimumSize(QSize(1, 1))  # Allow Scaling
      
      # Switch To .png Viewer
      self.file_viewers.setCurrentIndex(2)
      # Log Successful PNG Load
      self.logger.info(f"Results Viewer ID: {self}  -  Successfully loaded PNG file: {file_path}")        

      
    except Exception as e:
      self.file_viewers.setCurrentIndex(1)  # Empty State
      self.empty_state.setText(f"Error loading PNG file: {str(e)}")
      self.logger.error(f"Results Viewer ID: {self}  -  Error loading PNG file: {str(e)}")


  """
  
    Desc: Load In The Contents Of A Given .txt File And Display It In The Text Viewer Panel
    Of Our Results Viewer. It Will Read The Contents Of The .txt File, And Display Its Metadata.
    We Attempt To Read Using The Standard UTF-8 Encoding, And If It Fails, We Attempt The 
    Latin-1 Encoding As A Fallback. If Both Fail, We Show An Error Message.

    Preconditions:
      1. file_path Is A Valid Path Object Going To A .txt File
      2. The Function Should Be Called When The User Selects A .txt File In The Results Viewer

    Postconditions:
      1. The .txt File Will Be Loaded And Displayed In The Text Viewer
      2. The File Info Label Will Show The Name, Line Count, Character Count, And Size
      3. If The File Is Too Large, It Will Be Truncated For Display Purposes
      4. If An Error Occurs While Reading The File, An Error Message Will Be Displayed
  
  """
  def _load_txt_file(self, file_path):
    try:

      # Log The TXT File Loading
      self.logger.info(f"Results Viewer ID: {self}  -  Loading TXT file: {file_path}")

      # Read The .txt File Content
      with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

      # Log Successful Read
      self.logger.info(f"Results Viewer ID: {self}  -  Successfully read TXT file: {file_path}")
      
      # Limit Content Size For Display (Prevent UI Freezing With Huge Files)
      max_chars = 50000  # ~50kb Of Text
      if len(content) > max_chars:
        content = content[:max_chars] + f"\n\n... [File truncated - showing first {max_chars:,} characters of {len(content):,} total]"
      
      # Set The Content To The Text Viewer
      self.text_viewer.setPlainText(content)
      
      # Get File Statistics
      line_count = content.count('\n') + 1
      char_count = len(content)
      size_mb = file_path.stat().st_size / (1024 * 1024)
      size_str = f"{size_mb:.1f} MB" if size_mb >= 1 else f"{file_path.stat().st_size / 1024:.1f} KB"
      
      # Update File Info
      self.file_info.setText(f"{file_path.name} - {line_count:,} lines, {char_count:,} characters ({size_str})")
      
      # Switch To Text Viewer
      self.file_viewers.setCurrentIndex(3)

      # Log Successful TXT Load
      self.logger.info(f"Results Viewer ID: {self}  -  Successfully loaded TXT file: {file_path}")
        
    except UnicodeDecodeError:
      try:
        # Log Attempting Latin-1 Encoding
        self.logger.warning(f"Results Viewer ID: {self}  -  UTF-8 decoding failed for {file_path}, trying latin-1 encoding.")

        # Try Different Encoding If Utf-8 Fails
        with open(file_path, 'r', encoding='latin-1') as f:
          content = f.read()
        
        self.text_viewer.setPlainText(content)
        self.file_info.setText(f"{file_path.name} - Loaded with latin-1 encoding")
        self.file_viewers.setCurrentIndex(3)
        self.logger.info(f"Results Viewer ID: {self}  -  Successfully loaded TXT file with latin-1 encoding: {file_path}")
          
      except Exception as e:
        # Log The Error And Show It In The UI
        self.logger.error(f"Results Viewer ID: {self}  -  Error loading TXT file with latin-1 encoding: {str(e)}")
        self.file_viewers.setCurrentIndex(1)  # Empty State
        self.empty_state.setText(f"Error loading text file: {str(e)}")
    except Exception as e:
      # Log The Error And Show It In The UI
      self.logger.error(f"Results Viewer ID: {self}  -  Error loading TXT file: {str(e)}")
      self.file_viewers.setCurrentIndex(1)  # Empty State
      self.empty_state.setText(f"Error loading text file: {str(e)}")


  """

    Desc: Will Quickly Handle The Toggling Of The Main UI Elements
    For Specifically Image Files. It Will Show Or Hide The Colormap Selector,
    Contour Slider, And Apply Button Based On The State Provided.
    This Should Be Called When The User Selects A File From The List
    And The File Is A .tif File. It Will Also Handle The Case Where
    The File Is Not A .tif File And Hide The Colormap Selector And
    Contour Slider.

    Preconditions:
      1. state Is A Boolean Value Indicating The State Of The File Viewer
      2. The Function Should Be Called When The User Selects A File From The List

    Postconditions:
      1. The Colormap Selector Will Be Shown Or Hidden Based On The State Provided
      2. The Contour Slider Will Be Shown Or Hidden Based On The State Provided
      3. The Apply Button Will Be Shown Or Hidden Based On The State Provided
      4. The Export Button Will Be Enabled Or Disabled Based On The State Provided

  """
  def _update_file_config(self, state : bool):
    # Log The Configuration Update
    self.logger.info(f"Results Viewer ID: {self}  -  Updated file viewer configuration to {'show' if state else 'hide'} colormap and contour options.")
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
      # Log The TIF File Loading
      self.logger.info(f"Results Viewer ID: {self}  -  Loading TIF file: {file_path}")

      with rasterio.Env(GDAL_CACHEMAX=512):
        with rasterio.open(str(file_path)) as src:
          # Single Band Photo (e.g. DSM, DTM) Or Multi-Band (e.g. RGB)
          if src.count == 1:

            self.logger.info(f"Results Viewer ID: {self}  -  Detected single-band TIF file.")

            # If Single-Band, Read The Data
            self.logger.info(f"Results Viewer ID: {self}  -  Reading single-band data from TIF file.")
            data_original = src.read(1).astype(np.float32) 
            self.logger.info(f"Results Viewer ID: {self}  -  Successfully read single-band data from TIF file.")
            # For Given NoData Value, Set To NaN For Visualization
            if src.nodata is not None:
              data_original[data_original == src.nodata] = np.nan

            # Calculate original statistics BEFORE any resizing or filtering
            original_min = np.nanmin(data_original)
            original_max = np.nanmax(data_original)
            original_mean = np.nanmean(data_original)

            # Make a copy for display processing if modifications will occur
            data_for_display = np.copy(data_original)
            
            # Create Our Figure...
            dpi = 15                                  # DPI Is Utilized For Content Scaling
            height, width = data_for_display.shape                # Get The Height And Width Of The Image
            
            if height * width > 4000000:              # 4 Megapixels Threshold
              self.logger.info(f"Results Viewer ID: {self}  -  Image size {height}x{width} exceeds 4MP, applying scaling.")
              if self.auto_scaling:
                # If Auto Scaling Is Enabled, Use A Scale Factor Based On Image Size
                self.logger.info(f"Results Viewer ID: {self}  -  Using automatic scaling based on image size.")

                # Use Automatic Scaling Based On Image Size 
                scale_factor = np.sqrt(5000000 / (height * width))
              else:
                self.logger.info(f"Results Viewer ID: {self}  -  Using user-defined scale factor override: {self.scale_factor_override}")
                # Use User-Defined Scaling Factor
                scale_factor = self.scale_factor_override
                  
              # Don't Scale Up If Scale Factor > 1
              if scale_factor < 1.0:
                self.logger.info(f"Results Viewer ID: {self}  -  Scaling image by factor: {scale_factor:.2f}")
                new_height = int(height * scale_factor)
                new_width = int(width * scale_factor)
                
                # Use High-Quality Lanczos Resampling
                data_for_display = cv2.resize(data_for_display, (new_width, new_height), 
                                interpolation=cv2.INTER_LANCZOS4)
                
                # Apply Subtle Sharpening To Preserve Perceived Detail
                kernel = np.array([[-0.1, -0.1, -0.1],
                                [-0.1,  1.8, -0.1],
                                [-0.1, -0.1, -0.1]])
                data_for_display = cv2.filter2D(data_for_display, -1, kernel)
                
                # Update Dimensions for display
                height, width = data_for_display.shape
                dpi = int(dpi / scale_factor) # This line was present, consider its effect
                
            # Log The Image Size After Scaling
            self.logger.info(f"Results Viewer ID: {self}  -  Displaying image of size {height}x{width} at {dpi} DPI.")

            figsize = (width/dpi, height/dpi)          # Figure Size Will Depend On Our DPI And Image Size
            fig = Figure(figsize=figsize, dpi=dpi)     # Setup Our Figures Size With Its Overall DPI

            # Create Our Key Axes For The Figure
            ax = fig.add_subplot(111)

            # Calculate Our Hillshade Filter For The Image
            from matplotlib.colors import LightSource
            ls = LightSource(azdeg=315, altdeg=35)
            
            # Compute Our Minimum And Maximum Values For The Data This Is Used For The Hillshade And Color Mapping
            # These percentiles are for visual contrast stretching of the displayed data
            vmin_display, vmax_display = np.nanpercentile(data_for_display, [2, 98])
            
            # Apply Our Colormap And Hillshade To The Provided .tif Data
            cmap = plt.get_cmap(self.current_colormap)
            rgb = ls.shade(data_for_display, cmap=cmap, blend_mode='soft', 
                        vmin=vmin_display, vmax=vmax_display, vert_exag=3)
            
            # Log The Colormap And Hillshade Application
            self.logger.info(f"Results Viewer ID: {self}  -  Applied colormap '{self.current_colormap}' with hillshading.")
            
            # Add Contour Lines On .tif Image To Help With Texturing (Optional To Avoid Cluttering In Small Images)
            # Use original min/max for contour levels if they should reflect true elevation
            levels = np.linspace(original_min, original_max, self.contour_line_count) 
            contour = ax.contour(data_for_display, levels=levels, colors='black', 
                            alpha=0.25, linewidths=0.4, linestyles='solid')
            
            # Log The Contour Lines Application
            self.logger.info(f"Results Viewer ID: {self}  -  Applied contour lines with {self.contour_line_count} levels.")

            # Display Our RGB Formatted Image To User
            ax.imshow(rgb)

            # Get The Normalization Of The Data For The Colorbar
            # Use original min/max for colorbar normalization and label
            norm = Normalize(vmin=original_min, vmax=original_max)
            sm = ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])

            # Add Colorbar To The Figure
            cbar = fig.colorbar(sm, ax=ax, shrink=0.9)

            # Save Our Exponentially Scaled Factor
            expon_factor = scale_factor * scale_factor

            cbar.set_label(f'Elevation ({original_min:.2f}ft - {original_max:.2f}ft)', 
                    fontsize=650 * expon_factor, fontweight='bold', labelpad=12)
            cbar.ax.tick_params(labelsize=600 * expon_factor, width=120 * expon_factor, length=245 * expon_factor)       

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

            stats = {
                  "Min elevation": f"{original_min:.2f}ft",
                  "Max elevation": f"{original_max:.2f}ft",
                  "Mean elevation": f"{original_mean:.2f}ft",
                  "Resolution": f"{src.res[0]:.2f}ft/pixel" # Original resolution
            }

            # Log The Statistics
            self.logger.info(f"Results Viewer ID: {self}  -  TIF file statistics: {stats}")

            # Format With Key: Value Pairs
            stats_str = " | ".join([f"{k}: {v}" for k, v in stats.items()])
            self.file_info.setText(f"{file_path.name} - {stats_str}")

              
          else:
            self.logger.info(f"Results Viewer ID: {self}  -  Detected multi-band TIF file with {src.count} bands.")

            # Multi-Band Image (RGB) Will Simply Just Be Displayed Without Filter
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
            self.file_info.setText(f"{file_path.name} - Minimum Elevation: {min_val:.2f}ft | Maximum Elevation: {max_val:.2f}ft")
            # Log The Pixmap Elevation Statistics
            self.logger.info(f"Results Viewer ID: {self}  -  Multi-band TIF file statistics: Min elevation {min_val:.2f}ft, Max elevation {max_val:.2f}ft")


          # Update The Image Label With The Pixmap
          self.tif_image.setPixmap(pixmap)
          self.tif_image.setMinimumSize(QSize(1, 1))  # Allow Our Images Scaling
          
          # Set Our Current View To The .tif Viewer
          self.file_viewers.setCurrentIndex(0)
          # Log Successful TIF Load
          self.logger.info(f"Results Viewer ID: {self}  -  Successfully loaded TIF file: {file_path}")
      
      # Else If We Fail, Set To Empty State And Return To User A Traceback Error
    except Exception as e:
      self.logger.error(f"Results Viewer ID: {self}  -  Error loading TIF file: {str(e)}")
      self.file_viewers.setCurrentIndex(1)  # Empty state
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
    # Log The Colormap Change
    self.logger.info(f"Results Viewer ID: {self}  -  Changing colormap to: {colormap_name}")
    # Set The Current Colormap To The Selected One
    self.current_colormap = colormap_name
    
    # Reload The .tif File With The New Colormap
    if self.current_file_path and self.current_file_path.suffix.lower() in ('.tif', '.tiff'):
      self.logger.info(f"Results Viewer ID: {self}  -  Reloading TIF file with new colormap: {colormap_name}")
      self._load_tif_file(self.current_file_path)
      # Log Successful Colormap Change
      self.logger.info(f"Results Viewer ID: {self}  -  Successfully applied colormap '{colormap_name}' to TIF file.")
    else:
      self.logger.warning(f"Results Viewer ID: {self}  -  No valid TIF file selected to apply colormap: {colormap_name}")


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
    # Log The External Open Request
    self.logger.info(f"Results Viewer ID: {self}  -  Attempting to open file in external viewer: {self.current_file_path.name if self.current_file_path else 'None'}")
    # If We Have No File Selected, Return
    if not self.current_file_path:
      self.logger.warning(f"Results Viewer ID: {self}  -  No file selected to open in external viewer.")
      return
    
    # Attempt To Open The Users File In Their Default Software
    try:
      import os
      import subprocess
      import platform
      
      # If Windows OS
      if platform.system() == 'Windows':
        # Log Opening File In Windows
        self.logger.info(f"Results Viewer ID: {self}  -  Opening file in Windows default viewer: {self.current_file_path}")
        os.startfile(str(self.current_file_path))
      # If MacOS OS
      elif platform.system() == 'Darwin':  # macOS
        # Log Opening File In MacOS
        self.logger.info(f"Results Viewer ID: {self}  -  Opening file in macOS default viewer: {self.current_file_path}")
        subprocess.call(('open', str(self.current_file_path)))
      # If Linux OS
      else:  # Linux
        # Log Opening File In Linux
        self.logger.info(f"Results Viewer ID: {self}  -  Opening file in Linux default viewer: {self.current_file_path}")
        subprocess.call(('xdg-open', str(self.current_file_path)))
    # Else If We Fail To Open A Provided File Prompt User With An Error Message
    except Exception as e:
      self.logger.error(f"Results Viewer ID: {self}  -  Error opening file in external viewer: {str(e)}")
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

    # Log The Export Request
    self.logger.info(f"Results Viewer ID: {self}  -  Attempting to export file: {self.current_file_path.name if self.current_file_path else 'None'}")

    # If We Selected No File, Return
    if not self.current_file_path:
      self.logger.warning(f"Results Viewer ID: {self}  -  No file selected to export.")
      return
    
    # Log Asking User
    self.logger.info(f"Results Viewer ID: {self}  -  Prompting user for export destination for file: {self.current_file_path.name}")

    # Get The Destination Path For Our File To Be Copied To
    dest_path, _ = QFileDialog.getSaveFileName(
        self, 
        "Export File", 
        str(self.current_file_path.name),
        f"*{self.current_file_path.suffix}"
    )
    # Log The Destination Path
    self.logger.info(f"Results Viewer ID: {self}  -  Selected export destination: {dest_path}")
    
    # IF Not A Valid Destination Path, Return
    if not dest_path:
      self.logger.warning(f"Results Viewer ID: {self}  -  No destination path selected for export.")
      return

    # Attempt To Copy Our File Into Our Destination Path
    try:
      import shutil
      shutil.copy2(self.current_file_path, dest_path)
      # Log Successful Export
      self.logger.info(f"Results Viewer ID: {self}  -  Successfully exported file to: {dest_path}")
      QMessageBox.information(self, "Success", f"File exported to {dest_path}")
    # If We Fail Copying Our File's Contents, Return Error Message
    except Exception as e:
      self.logger.error(f"Results Viewer ID: {self}  -  Error exporting file: {str(e)}")
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
    # Log The Return To Pipeline Request
    self.logger.info(f"Results Viewer ID: {self}  -  Returning to pipeline page.")

    # Close UI Window We're Associated With
    self.close()
    self.logger.info(f"Results Viewer ID: {self}  -  Closed results viewer window.")
    del self
