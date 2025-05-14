import pytest
from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QFrame, QApplication)
from PyQt5.QtCore import Qt

from ResilientGeoDrone.src.front_end.result_dialog import ResultDialog
from ResilientGeoDrone.src.front_end.styles import STYLE_SHEET


@pytest.fixture
def mock_parent(qtbot):
    """Create a mock parent widget for testing"""
    parent = QDialog()
    qtbot.addWidget(parent)
    return parent


@pytest.mark.unit
def test_result_dialog_success_initialization(qtbot):
    """Test ResultDialog initialization with success parameters"""
    # Create dialog with success parameters
    title = "Test Success"
    message = "Operation completed successfully"
    details = "Process completed in 2.5 seconds\nAll tasks were successful"
    dialog = ResultDialog(title, message, details, True)
    qtbot.addWidget(dialog)
    
    # Check window properties
    assert dialog.windowTitle() == title
    assert dialog.objectName() == "resultDialog"
    assert dialog.minimumSize().width() >= 500
    assert dialog.minimumSize().height() >= 350
    
    # Check layout structure
    main_layout = dialog.layout()
    assert isinstance(main_layout, QVBoxLayout)
    
    # Check frame
    frame = dialog.findChild(QFrame, "resultFrame")
    assert frame is not None
    assert frame.frameShape() == QFrame.StyledPanel
    
    # Check status label
    status_label = dialog.findChild(QLabel, "statusLabelSuccess")
    assert status_label is not None
    assert status_label.text() == "✓ Success"
    
    # Check message label
    message_label = dialog.findChild(QLabel, "resultMessage")
    assert message_label is not None
    assert message_label.text() == message
    assert message_label.wordWrap() is True
    
    # Check details text edit
    details_text = dialog.findChild(QTextEdit, "resultDetails")
    assert details_text is not None
    assert details_text.toPlainText() == details
    assert details_text.isReadOnly() is True
    
    # Check close button
    close_button = dialog.findChild(QPushButton, "closeButton")
    assert close_button is not None
    assert close_button.text() == "Close"
    
    # Check stylesheet
    assert dialog.styleSheet() == STYLE_SHEET


@pytest.mark.unit
def test_result_dialog_error_initialization(qtbot):
    """Test ResultDialog initialization with error parameters"""
    # Create dialog with error parameters
    title = "Test Error"
    message = "Operation failed"
    details = "Error: Could not complete the operation\nReason: Invalid input"
    dialog = ResultDialog(title, message, details, False)
    qtbot.addWidget(dialog)
    
    # Check status label shows error
    status_label = dialog.findChild(QLabel, "statusLabelSuccess")
    assert status_label is not None
    assert status_label.text() == "❌ Error"
    
    # Other properties remain the same
    assert dialog.windowTitle() == title
    message_label = dialog.findChild(QLabel, "resultMessage")
    assert message_label.text() == message
    details_text = dialog.findChild(QTextEdit, "resultDetails")
    assert details_text.toPlainText() == details


@pytest.mark.unit
def test_result_dialog_with_parent(qtbot, mock_parent):
    """Test ResultDialog initialization with a parent widget"""
    # Create dialog with parent
    title = "Child Dialog"
    message = "This dialog has a parent"
    details = "Testing parent-child relationship"
    dialog = ResultDialog(title, message, details, True, mock_parent)
    qtbot.addWidget(dialog)
    
    # Check parent relationship
    assert dialog.parent() == mock_parent


@pytest.mark.unit
def test_result_dialog_empty_parameters(qtbot):
    """Test ResultDialog with empty string parameters"""
    # Create dialog with empty strings
    title = ""
    message = ""
    details = ""
    dialog = ResultDialog(title, message, details)
    qtbot.addWidget(dialog)
    
    # Check empty strings are handled properly
    assert dialog.windowTitle() == ""
    message_label = dialog.findChild(QLabel, "resultMessage")
    assert message_label.text() == ""
    details_text = dialog.findChild(QTextEdit, "resultDetails")
    assert details_text.toPlainText() == ""


@pytest.mark.unit
def test_result_dialog_long_content(qtbot):
    """Test ResultDialog with very long content"""
    # Create dialog with long content
    title = "Long Content Test"
    message = "This is a very long message that should wrap to multiple lines " * 5
    details = "Detailed information line 1\n" * 50
    dialog = ResultDialog(title, message, details)
    qtbot.addWidget(dialog)
    
    # Check content is set correctly
    message_label = dialog.findChild(QLabel, "resultMessage")
    assert message_label.text() == message
    details_text = dialog.findChild(QTextEdit, "resultDetails")
    assert details_text.toPlainText() == details


@pytest.mark.unit
def test_result_dialog_special_characters(qtbot):
    """Test ResultDialog with special characters"""
    # Create dialog with special characters
    title = "Special Characters: äöü€$%&"
    message = "Message with special characters: ©®™✓✗☺♠♣♥♦"
    details = "Details with special characters:\n<html><body>Test</body></html>\n" 
    details += "Greek: αβγδε\nCyrillic: абвгд\nChinese: 你好世界"
    
    dialog = ResultDialog(title, message, details)
    qtbot.addWidget(dialog)
    
    # Check content is set correctly
    assert dialog.windowTitle() == title
    message_label = dialog.findChild(QLabel, "resultMessage")
    assert message_label.text() == message
    details_text = dialog.findChild(QTextEdit, "resultDetails")
    assert details_text.toPlainText() == details


@pytest.mark.unit
def test_result_dialog_close_button(qtbot):
    """Test close button functionality"""
    # Create dialog
    dialog = ResultDialog("Test Close", "Testing close button", "Details")
    qtbot.addWidget(dialog)
    dialog.show()
    
    # Get close button
    close_button = dialog.findChild(QPushButton, "closeButton")
    
    # Set up to check if dialog is accepted when button is clicked
    accepted = False
    def on_accepted():
        nonlocal accepted
        accepted = True
    
    dialog.accepted.connect(on_accepted)
    
    # Click close button
    qtbot.mouseClick(close_button, Qt.LeftButton)
    
    # Check dialog was accepted
    assert accepted is True


@pytest.mark.unit
def test_result_dialog_layout_structure(qtbot):
    """Test the detailed structure of the dialog layout"""
    dialog = ResultDialog("Layout Test", "Testing layout structure", "Layout details")
    qtbot.addWidget(dialog)
    
    # Get main layout
    main_layout = dialog.layout()
    assert main_layout.count() == 2  # Frame + button layout
    
    # Check first item is the frame
    frame_item = main_layout.itemAt(0)
    frame = frame_item.widget()
    assert isinstance(frame, QFrame)
    assert frame.objectName() == "resultFrame"
    
    # Check frame layout
    frame_layout = frame.layout()
    assert isinstance(frame_layout, QVBoxLayout)
    assert frame_layout.count() == 3  # Status label + message label + details text
    
    # Check second item is the button layout
    button_layout_item = main_layout.itemAt(1)
    button_layout = button_layout_item.layout()
    assert isinstance(button_layout, QHBoxLayout)
    
    # Check button layout has a stretch and a button
    assert button_layout.count() == 2  # Stretch + close button
    assert button_layout.itemAt(1).widget().objectName() == "closeButton"


@pytest.mark.unit
def test_result_dialog_resize(qtbot):
    """Test that the dialog can be resized"""
    dialog = ResultDialog("Resize Test", "Testing resizing", "Resize details")
    qtbot.addWidget(dialog)
    dialog.show()
    
    # Initial size
    initial_size = dialog.size()
    
    # Resize dialog
    new_width = initial_size.width() + 100
    new_height = initial_size.height() + 100
    dialog.resize(new_width, new_height)
    
    # Check new size
    assert dialog.width() == new_width
    assert dialog.height() == new_height
    
    # Check that content widgets adjust with resize
    frame = dialog.findChild(QFrame, "resultFrame")
    assert frame.width() <= new_width