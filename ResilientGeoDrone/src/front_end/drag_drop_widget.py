from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
import os
from ..utils import FileHandler, ConfigLoader



"""

    Desc: Class Is Used In Our Main Client Window To Create A Drag And Drop
    Widget. The Widget Will Allow The User To Drag And Drop A Folder Containing
    Images. The Widget Will Provide The User With Feedback On The Status Of The
    Folder Processing. The Widget Will Be Utilized To Process Images And Generate
    Point Clouds.

"""
class DragDropWidget(QFrame):

    """
    
        Desc: Initializes Our Drag And Drop Widget With A Given Name Abd Sets
        It To Be Accepting Of Drag And Drop Events. It Also Creates A Vertical
        Box Layout That Its Set In As Well As Aligns It In The Center OF Our Screen.

        Preconditions:
            1. None
        
        Postconditions:
            1. Set Our Object Name
            2. Set Our Widget To Accept Drag And Drop Events
            3. Create A Vertical Layout
            4. Set Our Label To Display Drag And Drop Instructions
            5. Align Our Label In The Center Of The Widget
    
    """
    def __init__(self, config : ConfigLoader):
        super().__init__()
        self.setObjectName("dragdrop")
        self.setAcceptDrops(True)
        
        # Create A Vertical Layout For Our Widget
        layout = QVBoxLayout(self)
        self.label = QLabel("Drag and drop image folder here")
        self.label.setAlignment(Qt.AlignCenter)
        self.file_handler = FileHandler(config)
        self.image_paths = []
        layout.addWidget(self.label)
        
    
    """
    
        Desc: Function Is Used To Handle Drag Enter Events. The Function
        Will Check If The Drag Event Contains URLs And Accepts The Event
        If It Does. Otherwise, It Will Ignore The Event.

        Preconditions:
            1. Event Contains Mime Data
            2. Mime Data Contains URLs
        
        Postconditions:
            1. Accept The Event If It Contains URLs
            2. Ignore The Event Otherwise
    
    """
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            

    
    """
    
        Desc: Function Is Utilized To Handle Drop Events. The Function Will
        Extract The Folder Path From The Drop Event And Process The Folder
        By Running Our Pipeline. The Function Will Provide The User With
        Feedback On The Status Of The Folder Processing.

        Preconditions:
            1. Event Contains Mime Data
            2. Mime Data Contains URLs
            3. URLs Are Directories

        Postconditions:
            1. Extract Folder Path From Drop Event
            2. Process Folder By Running Pipeline
            3. Provide User With Feedback On Folder Processing
    
    """
    def dropEvent(self, event):
        # Copy Our Folder Directory(s) To A List
        folders = [u.toLocalFile() for u in event.mimeData().urls()]

        #  If We Have Multiple Folders
        if len(folders) != 0 and (os.path.isdir(file) for file in folders):

            for folder in folders:
                self.label.setText(f"Processing Folder Selected: {os.path.basename(folders[0])}")
                self.image_paths = self.file_handler.get_image_files(folder)
        else:
            # Else If User Provided Us With A File Or No Folder
            self.label.setText("Please Drop A Single Folder")