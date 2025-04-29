from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QFrame)

from .styles import STYLE_SHEET

"""

  Desc: This Class Is Utilized To Create A Result Dialog That
  Displays The Results Of The Pipeline For A Given Worker. The
  Class Will Hold It's Title, Status Update, Result Details And
  A Button To Close The Dialog. The Result Dialog Will Emit Signals
  To Update The UI With Result Information.

"""
class ResultDialog(QDialog):
  """
  
    Desc: Initallizes Our Result Dialog With A Title, Status Update,
    Result Details And A Button To Close The Dialog. The Dialog Will
    Be Styled In The Forest Theme Of The Overall Application.

    Preconditions:
        1. None

    Postconditions:
  
  """
  def __init__(self, title, message, details, success=True, parent=None):
    # Initialize Our Dialog With Our Parent
    super().__init__(parent)

    # Set Our Dialog Title
    self.setWindowTitle(title)
    self.setMinimumSize(500, 350)
    self.setObjectName("resultDialog")

    # Create Our Layout
    layout = QVBoxLayout(self)

    # Frame For Progress Bar
    frame = QFrame()
    frame.setObjectName("resultFrame")
    frame.setFrameShape(QFrame.StyledPanel)
    frame_layout = QVBoxLayout(frame)

    # Create Our Status Update
    status_label = QLabel("✓ Success" if success else "❌ Error")
    status_label.setObjectName("statusLabelSuccess")
    frame_layout.addWidget(status_label)

    # Message
    msg_label = QLabel(message)
    msg_label.setObjectName("resultMessage")
    msg_label.setWordWrap(True)
    frame_layout.addWidget(msg_label)

    # Details In Text Edit
    details_label = QTextEdit()
    details_label.setObjectName("resultDetails")
    details_label.setReadOnly(True)
    details_label.setPlainText(details)
    frame_layout.addWidget(details_label)

    # Add Our Frame To The Layout
    layout.addWidget(frame)

    # Button Layout
    button_layout = QHBoxLayout()

    # Spacer 
    button_layout.addStretch()

    # Close Button
    close_button = QPushButton("Close")
    close_button.setObjectName("closeButton")
    close_button.clicked.connect(self.accept)
    button_layout.addWidget(close_button)

    # Add Button Layout To Main Layout
    layout.addLayout(button_layout)

    # Set Our Style Sheet
    self.setStyleSheet(STYLE_SHEET)
    self.setLayout(layout)
  
    