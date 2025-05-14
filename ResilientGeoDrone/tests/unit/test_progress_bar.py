import pytest
from PyQt5.QtWidgets import (QWidget, QProgressBar, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QSignalSpy

from ResilientGeoDrone.src.front_end.progress_bar import ProgressWidget


@pytest.fixture
def progress_widget(qtbot):
    """Create a ProgressWidget for testing"""
    widget = ProgressWidget()
    qtbot.addWidget(widget)
    return widget


@pytest.mark.unit
def test_progress_widget_initialization(progress_widget):
    """Test the initial state of the ProgressWidget"""
    # Check object names
    assert progress_widget.objectName() == "progressWidget"
    assert progress_widget.frame.objectName() == "progressFrame"
    assert progress_widget.title_label.objectName() == "progressTitle"
    assert progress_widget.status_label.objectName() == "statusLabel"
    assert progress_widget.detail_label.objectName() == "detailLabel"
    assert progress_widget.progress_bar.objectName() == "progressBar"
    assert progress_widget.cancel_button.objectName() == "cancelButton"
    
    # Check frame properties
    assert progress_widget.frame.frameShape() == QFrame.StyledPanel
    
    # Check initial text values
    assert progress_widget.title_label.text() == "Pipeline Progress"
    assert progress_widget.status_label.text() == "Initializing Pipeline..."
    assert progress_widget.detail_label.text() == "Loading Configuration..."
    assert progress_widget.cancel_button.text() == "Cancel"
    
    # Check progress bar initial state
    assert progress_widget.progress_bar.minimum() == 0
    assert progress_widget.progress_bar.maximum() == 100
    assert progress_widget.progress_bar.value() == 0
    
    # Check detail label word wrap
    assert progress_widget.detail_label.wordWrap() is True
    
    # Verify layouts
    assert isinstance(progress_widget.layout(), QVBoxLayout)
    assert isinstance(progress_widget.frame.layout(), QVBoxLayout)
    
    # Check that the cancel button is in the layout
    button_layout = None
    for i in range(progress_widget.frame.layout().count()):
        item = progress_widget.frame.layout().itemAt(i)
        if isinstance(item, QHBoxLayout):
            button_layout = item
            break
    
    assert button_layout is not None, "Button layout not found"
    assert button_layout.count() == 1, "Button layout should have exactly one widget"
    assert button_layout.itemAt(0).widget() == progress_widget.cancel_button


@pytest.mark.unit
def test_update_progress(progress_widget, qtbot):
    """Test updating the progress information"""
    # Update with integer progress
    progress_widget.update_progress(50, "Processing", "Processing images...")
    assert progress_widget.progress_bar.value() == 50
    assert progress_widget.status_label.text() == "Processing"
    assert progress_widget.detail_label.text() == "Processing images..."
    
    # Update with float progress (should convert to int)
    progress_widget.update_progress(75.5, "Generating", "Generating point clouds...")
    assert progress_widget.progress_bar.value() == 75
    assert progress_widget.status_label.text() == "Generating"
    assert progress_widget.detail_label.text() == "Generating point clouds..."
    
    # Test with extreme values
    progress_widget.update_progress(-10, "Error", "An error occurred")
    assert progress_widget.progress_bar.value() == 0  # Should be clamped to min
    
    progress_widget.update_progress(150, "Complete", "Process completed")
    assert progress_widget.progress_bar.value() == 100  # Should be clamped to max


@pytest.mark.unit
def test_set_title(progress_widget, qtbot):
    """Test setting the title of the progress widget"""
    # Change title
    progress_widget.set_title("Processing Pipeline")
    assert progress_widget.title_label.text() == "Processing Pipeline"
    
    # Change to empty title
    progress_widget.set_title("")
    assert progress_widget.title_label.text() == ""
    
    # Change to title with special characters
    special_title = "Image Processing & Point Cloud Generation"
    progress_widget.set_title(special_title)
    assert progress_widget.title_label.text() == special_title


@pytest.mark.unit
def test_cancel_button_signal(progress_widget, qtbot):
    """Test that clicking the cancel button emits the cancel_request signal"""
    # Setup signal spy
    spy = QSignalSpy(progress_widget.cancel_request)
    
    # Click the cancel button
    qtbot.mouseClick(progress_widget.cancel_button, Qt.LeftButton)
    
    # Verify signal was emitted exactly once
    assert len(spy) == 1


@pytest.mark.unit
def test_multiple_updates(progress_widget, qtbot):
    """Test multiple sequential updates to the progress widget"""
    # Series of updates simulating a processing pipeline
    updates = [
        (0, "Initializing", "Starting pipeline..."),
        (25, "Processing", "Processing images..."),
        (50, "Generating", "Generating point cloud..."),
        (75, "Analyzing", "Analyzing data..."),
        (100, "Complete", "Pipeline complete")
    ]
    
    # Apply each update and check results
    for progress, status, detail in updates:
        progress_widget.update_progress(progress, status, detail)
        assert progress_widget.progress_bar.value() == progress
        assert progress_widget.status_label.text() == status
        assert progress_widget.detail_label.text() == detail


@pytest.mark.unit
def test_visibility(progress_widget, qtbot):
    """Test showing and hiding the progress widget"""
    # Initially the widget is not visible
    assert not progress_widget.isVisible()
    
    # Show the widget
    progress_widget.show()
    assert progress_widget.isVisible()
    
    # Hide the widget
    progress_widget.hide()
    assert not progress_widget.isVisible()