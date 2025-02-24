import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, QVBoxLayout, 
                           QLabel, QFrame)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication
from settings_window import SettingsWindow
from drag_drop_widget import DragDropWidget
from styles import STYLE_SHEET



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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resilient Geo Drone")

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
        
        # Drag & Drop Area
        self.drag_drop = DragDropWidget()
        layout.addWidget(self.drag_drop)
        
        # Settings Button
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.setObjectName("settingsButton")

        # Connect Settings Button To Open Settings Window
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn, alignment=Qt.AlignRight)
        
        # Status Bar
        self.statusBar().showMessage("Ready")
        

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