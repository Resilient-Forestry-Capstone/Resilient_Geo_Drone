from pathlib import Path    
import sys

from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QVBoxLayout, 
                           QLabel, QStackedWidget, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from .settings_window import SettingsWindow
from .drag_drop_widget import DragDropWidget
from .styles import STYLE_SHEET
from .progress_bar import ProgressWidget
from .pipeline_worker import PipelineWorker
from .result_dialog import ResultDialog
from ..utils.config_loader import ConfigLoader
from.result_viewer import ResultsViewerWidget



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
    def __init__(self, config_path : Path = Path(__file__).parent.parent.parent / "config/config.yaml"):
        super().__init__()
        self.setWindowTitle("Resilient Geo Drone")
        self.setWindowIcon(QIcon(str(Path(__file__).parent.parent.parent.parent / "data/bin/icon.png")))

        # While A Little Redundant, Good To Have Config Path As A Variable
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
        title = QLabel("Resilient Geo Drone", objectName="title")
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
        self.tasks_pane = QWidget(objectName="tasksPane")
        self.stacked_widget.addWidget(self.tasks_pane)

        tasks_layout = QVBoxLayout(self.tasks_pane)
        tasks_layout.setContentsMargins(0, 0, 0, 0)
        tasks_layout.setSpacing(0)
        
        # Start On Drag & Drop Page
        self.stacked_widget.setCurrentIndex(0)

        # Settings Button
        settings_btn = QPushButton("⚙ Settings", objectName="settingsButton")

        # Connect Settings Button To Open Settings Window
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn, alignment=Qt.AlignRight)

        # Status Bar
        self.statusBar().showMessage("Ready")

        self.view_results_button = QPushButton("📁 View Results", objectName="viewResultsButton")
        self.view_results_button.clicked.connect(self.open_tasks_pane)
        layout.addWidget(self.view_results_button, alignment=Qt.AlignRight)

        # Add Launch PIpeline Button
        self.launch_button = QPushButton("🚀 Launch Pipeline", objectName="launchButton")

        # Connect Settings Button To Open Settings Window
        self.launch_button.clicked.connect(self.launch_pipeline)
        layout.addWidget(self.launch_button, alignment=Qt.AlignRight)
        

    """
    
        Desc: Function Will Launch Off Our Results Viewer Window And Display It
        As A Pop-Up Window. The Results Viewer Will Allow The User To View The
        Results Of The Pipeline Processing.

        Preconditions:
            1. None

        Postconditions:
            1. Launch Off Results Viewer Pop-Up Window
            2. Display Results Of The Pipeline Processing
            3. Set The Style Sheet For The Results Viewer
    
    """
    def open_tasks_pane(self):
        results_viewer = ResultsViewerWidget()
        results_viewer.setStyleSheet(STYLE_SHEET)
        results_viewer.show()


    """
    
        Desc: Function Will Launch Off Our Pipeline Processing. The Function
        Will Check If We Have Images To Process. If We Do, The Function Will
        Update The UI And Create A Pipeline Worker. The Worker Will Handle
        Updating The UI With Progress Information. The Function Will Also
        Handle The Completion Of The Pipeline Processing.

        Preconditions:
            1. None

        Postconditions:
            1. Launch Off Pipeline Processing
            2. Update UI With Progress Information
            3. Handle Completion Of The Pipeline Processing
            4. Show Resulting Dialog To User
            
    """
    def launch_pipeline(self):
        # Check If We Not Have Images To Process
        if not self.drag_drop.image_paths:
            self.statusBar().showMessage("No Images To Process")
            return
        
        # Update UI
        self.statusBar().showMessage("Launching Pipeline...")
        self.stacked_widget.setCurrentIndex(1)
        self.launch_button.setEnabled(False)

        # Create Our Pipeline Worker
        self.pipeline_worker = PipelineWorker(self.config_path, self.drag_drop.image_paths)

        # Link Our UI Status Update Signals To The Worker
        self.pipeline_worker.progress_updated_status.connect(self.update_progress)
        self.pipeline_worker.progress_completion_status.connect(self.pipeline_complete)
        self.pipeline_worker.start()


    """
    
        Desc: Function Will Update The Progress Bar And Status Bar With
        Progress Information. The Function Will Update The Progress Bar
        With The Current Progress, Status, And Detail Information. The
        Function Will Also Update The Status Bar With The Current Status
        And Progress Information.

        Preconditions:
            1. progress: Current Integer Progress Percentage [0-100]
            2. status: Current String Status Message
            3. detail: Current String Detail Message

    """ 
    def update_progress(self, progress : int, status : str, detail : str):
        self.progress_widget.update_progress(progress, status, detail)
        self.statusBar().showMessage(f"Processing: {status} ({progress}%)")


    """
    
        Desc: Function Will Handle The Completion Of The Pipeline Processing.
        The Function Will Update The UI With The Completion Status. The
        Function Will Show A Resulting Dialog To The User With The Completion
        Status, Detail, And Success Information.

        Preconditions:
            1. success: Boolean Success Status
            2. status: String Completion Status Message
            3. detail: String Completion Detail Message

        Postconditions:
            1. Update UI With Completion Status
            2. Show Resulting Dialog To User With Completion Status
            3. Update Status Bar With Completion Status

    
    """
    def pipeline_complete(self, success : bool, status : str, detail : str):
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


    """
    
        Desc: Function Will Handle The Cancellation Of The Pipeline Processing.
        The Function Will Show A Confirmation Dialog To The User And Wait For A Response.
        If The User Confirms, The Function Will Cancel The Pipeline Processing.
        The Function Will Update The UI With The Cancellation Status.
        The Function Will Also Update The Status Bar With The Cancellation
        Status.

        Preconditions:
            1. None

        Postconditions:
            1. Show Confirmation Dialog To User
            2. Cancel The Pipeline Processing
            3. Update UI With Cancellation Status
            4. Update Status Bar With Cancellation Status
            5. Wait For The Pipeline Worker To Cleanup

    """
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