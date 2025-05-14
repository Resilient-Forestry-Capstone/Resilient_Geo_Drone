from pathlib import Path
from unittest.mock import MagicMock, patch
from matplotlib.backend_bases import MouseButton
from ResilientGeoDrone.src.front_end.client_window import MainClientWindow
from ResilientGeoDrone.src.front_end.drag_drop_widget import DragDropWidget
from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5.Qt import Qt
import pytest

from ResilientGeoDrone.src.front_end.progress_bar import ProgressWidget


"""

    Desc: Top-Level Fixture For A Consistent Client Window Object
    For Usage In Tests. This Will Be Used To Create A Client Window
    And Connect It To A Agent.

"""
@pytest.fixture
def client_window(qtbot):
    window = MainClientWindow()
    qtbot.addWidget(window)
    return window


"""

  Desc: Test Expected Initiailization Of The Main Client Window

"""
@pytest.mark.unit
@pytest.mark.fast
def test_client_window_init(client_window):
    assert client_window is not None
    assert client_window.windowTitle() == "Resilient Geo Drone"
    assert isinstance(client_window, QMainWindow)
    
    # Find Drag & Drop Widget
    assert client_window.findChild(DragDropWidget, "dragdrop")
    
    # Find Settings Button
    assert client_window.findChild(QPushButton, "settingsButton")

    # Find Launch Button
    assert client_window.findChild(QPushButton, "launchButton")

    # Find Progress Widget
    assert client_window.findChild(ProgressWidget, "progressWidget")

    # Find Status Bar
    assert client_window.statusBar() is not None

    # Find Viewer Button
    assert client_window.findChild(QPushButton, "viewResultsButton")


"""

  Desc: Test Of Dragging And Dropping Files Onto The Drag & Drop Widget
  In The Main Client Window

"""
@pytest.mark.unit
def test_drag_drop_connection(client_window, qtbot, monkeypatch):
    from PyQt5.QtCore import QUrl, QMimeData
    from PyQt5.QtGui import QDragEnterEvent, QDropEvent
    import os
    from pathlib import Path
    
    # Get the actual path to test images
    image_folder = Path(__file__).parent.parent / "data" / "images"
    assert image_folder.exists(), f"Test image folder not found: {image_folder}"
    
    # Find the drag & drop widget
    drag_drop = client_window.findChild(DragDropWidget, "dragdrop")
    
    # Create mime data with the folder URL
    mime_data = QMimeData()
    url = QUrl.fromLocalFile(str(image_folder))
    mime_data.setUrls([url])
    
    # Create drag enter event
    drag_enter_event = QDragEnterEvent(
        drag_drop.rect().center(),  # position
        Qt.CopyAction,              # actions
        mime_data,                  # data
        Qt.LeftButton,              # buttons
        Qt.NoModifier               # modifiers
    )
    
    # Create drop event
    drop_event = QDropEvent(
        drag_drop.rect().center(),  # position
        Qt.CopyAction,              # actions
        mime_data,                  # data
        Qt.LeftButton,              # buttons
        Qt.NoModifier,              # modifiers
        QDropEvent.Drop             # type
    )
    
    # Trigger the events
    drag_drop.dragEnterEvent(drag_enter_event)
    drag_drop.dropEvent(drop_event)
    
    # Check if images were processed
    assert len(drag_drop.image_paths) > 0, "No images were loaded from the test folder"
    assert all(Path(img).exists() for img in drag_drop.image_paths), "Some image paths don't exist"


"""
    Desc: Test Settings Button Opens Settings Window
"""
@pytest.mark.unit
def test_settings_button(client_window, qtbot, monkeypatch):
    """Test that settings button opens the settings window"""
    # Find settings button
    settings_button = None
    for button in client_window.findChildren(QPushButton):
        if button.objectName() == "settingsButton":
            settings_button = button
            break
    
    assert settings_button is not None
  
    qtbot.mouseClick(settings_button, Qt.LeftButton)
    


"""
    Desc: Test Progress Updates From Worker
"""
@pytest.mark.unit
def test_progress_update(client_window, qtbot):
    """Test progress bar updates correctly"""
    # Create a mock for progress_widget
    mock_progress_widget = MagicMock()
    client_window.progress_widget = mock_progress_widget
    
    # Mock the status bar
    mock_status_bar = MagicMock()
    client_window.statusBar = lambda: mock_status_bar
    
    # Call update_progress with test values
    test_progress = 50
    test_status = "Processing Images"
    test_detail = "Processing file 5 of 10"
    client_window.update_progress(test_progress, test_status, test_detail)
    
    # Check if progress_widget.update_progress was called with correct args
    mock_progress_widget.update_progress.assert_called_once_with(
        test_progress, test_status, test_detail
    )
    
    # Check if status bar was updated correctly
    mock_status_bar.showMessage.assert_called_once_with(
        f"Processing: {test_status} ({test_progress}%)"
    )


"""
    Desc: Test Launch Pipeline With No Images
"""
@pytest.mark.unit
def test_launch_pipeline_no_images(client_window, qtbot, monkeypatch):
    """Test that pipeline doesn't launch when no images are available"""
    # Mock drag_drop widget with no image paths
    client_window.drag_drop = MagicMock()
    client_window.drag_drop.image_paths = []
 
    # Mock status bar
    mock_status_bar = MagicMock()
    client_window.statusBar = lambda: mock_status_bar
    
    # Find launch button
    launch_button = client_window.findChild(QPushButton, "launchButton")
    assert launch_button is not None
    
    # Click launch button
    qtbot.mouseClick(launch_button, Qt.LeftButton)
    
    # Verify pipeline was not launched
    mock_status_bar.showMessage.assert_called_once_with("No Images To Process")


@pytest.mark.unit
def test_launch_pipeline_with_invalid_images(client_window, qtbot, monkeypatch):
    # Mock drag_drop Widget With Invalid Images
    client_window.drag_drop = MagicMock()
    client_window.drag_drop.image_paths = ["invalid_image_path.jpg"]
    
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    
    # Now Find Launch Button And Launch
    launch_button = client_window.findChild(QPushButton, "launchButton")
    assert launch_button is not None
    
    # Add a callback to handle the dialog when it appears
    def handle_dialog():
        # Find the dialog - it's the active modal widget
        dialog = QApplication.activeModalWidget()
        if dialog:
            # Find the close button in the dialog
            close_button = dialog.findChild(QPushButton, "closeButton")
            if close_button:
                qtbot.mouseClick(close_button, Qt.LeftButton)
    
    # Use a timer to check for the dialog after a short delay
    QTimer.singleShot(1500, handle_dialog)
    
    # Launch the pipeline
    qtbot.mouseClick(launch_button, Qt.LeftButton)

    # Verify That We Launched A Pipeline Worker Instance
    assert client_window.pipeline_worker

    # Wait for status bar to show Pipeline Failed
    qtbot.waitUntil(
        lambda: client_window.statusBar().currentMessage() == "Pipeline Failed",
        timeout=5000
    )

    # Verify That We Failed To Launch The Pipeline
    assert client_window.statusBar().currentMessage() == "Pipeline Failed"