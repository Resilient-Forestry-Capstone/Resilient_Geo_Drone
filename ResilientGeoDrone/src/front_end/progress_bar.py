from PyQt5.QtWidgets import (QWidget, QProgressBar, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QFrame)
from PyQt5.QtCore import pyqtSignal



"""

  Desc: This Class Represents A Progress Bar For A Given QThread Worker.
  The Progress Bar Will Update Progress Information In The UI, Including
  Current Status Of Pipeline, Progress Bar, As Well As Cancel
  Button. The Progress Bar Will Emit Signals To Update The UI 
  With Progress Information. 

"""
class ProgressWidget(QWidget):

  # Define A Signal For Canceling The Request (Goes Up To The Parent Worker)
  cancel_request = pyqtSignal()

  """

    Desc: Utilized To Create A Progress Widget That
    Displays The Pipeline's Current Status, Progress Bar,
    As Well As A Cancel Button To Cancel The Pipeline.
    The Progress Widget Will Assume The Forest Theme Of
    The User Interface.

    Preconditions:
        1. None

    Postconditions:
        1. Create Progress Widget
        2. Display Progress Information
        3. Styles Progress Widget With Stylesheet

  """
  def __init__(self):
    super().__init__(objectName="progressWidget")
    
    # Create Our Main Layout
    mainLayout = QVBoxLayout(self)

    # Create A Bordered Frame
    self.frame = QFrame(objectName="progressFrame", frameShape=QFrame.StyledPanel)
    frame_layout = QVBoxLayout(self.frame)

    # Progress Title Header
    self.title_label = QLabel("Pipeline Progress", objectName="progressTitle")
    frame_layout.addWidget(self.title_label)

    # Status
    self.status_label = QLabel("Initializing Pipeline...", objectName="statusLabel")
    frame_layout.addWidget(self.status_label)

    # Detail Message
    self.detail_label = QLabel("Loading Configuration...", objectName="detailLabel", wordWrap=True)
    frame_layout.addWidget(self.detail_label)

    # Progress Bar
    self.progress_bar = QProgressBar(objectName="progressBar")
    self.progress_bar.setRange(0, 100)
    self.progress_bar.setValue(0)
    frame_layout.addWidget(self.progress_bar)

    # Control Buttons Horizontally
    button_layout = QHBoxLayout()

    # Cancellation Button
    self.cancel_button = QPushButton("Cancel", objectName="cancelButton")
    self.cancel_button.clicked.connect(self.cancel_request.emit)
    button_layout.addWidget(self.cancel_button)

    # Add Button Layout To Frame Layout
    frame_layout.addLayout(button_layout)

    # Add Frame To Main Layout
    mainLayout.addWidget(self.frame)


  """
  
    Desc: Update Our Widget With New Values For The Progress Bar,
    Status, And Detail Message. The Function Will Update The
    Progress Bar, Status, And Detail Message With New Values For
    Front End.

    Preconditions:
        1. progress: Progress Value
        2. status: Status Message
        3. detail: Detail Message
    
    Postconditions:
        1. Update Progress Bar
        2. Update Status Message
        3. Update Detail Message
  
  """
  def update_progress(self, progress : int, status : str, detail : str):
    # Normalize Progress To 0-100 Range
    if progress < 0:
      progress = 0
    elif progress > 100:
      progress = 100

    self.progress_bar.setValue(int(progress))
    self.status_label.setText(status)
    self.detail_label.setText(detail)


  """
  
    Desc: Set The Title Of The Progress Widget. The Function
    Will Set The Title Of The Progress Widget With A New Title.

    Preconditions:
        1. title: Title Of Progress Widget

    Postconditions:
        1. Set Title Of Progress Widget
  
  """
  def set_title(self, title: str):
    self.title_label.setText(title)