import pytest
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from PyQt5.QtCore import QMimeData, QUrl, Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QVBoxLayout, QLabel

from ResilientGeoDrone.src.front_end.drag_drop_widget import DragDropWidget
from ResilientGeoDrone.src.utils import FileHandler, ConfigLoader


@pytest.fixture
def mock_config():
    """Create a mock ConfigLoader object"""
    config = MagicMock(spec=ConfigLoader)
    return config


@pytest.fixture
def mock_file_handler(mock_config):
    """Create a mock FileHandler"""
    handler = MagicMock(spec=FileHandler)
    with patch('ResilientGeoDrone.src.front_end.drag_drop_widget.FileHandler', return_value=handler):
        yield handler


@pytest.fixture
def drag_drop_widget(qtbot, mock_config, mock_file_handler):
    """Create a DragDropWidget fixture with mocked dependencies"""
    widget = DragDropWidget(mock_config)
    qtbot.addWidget(widget)
    return widget


@pytest.mark.unit
def test_drag_drop_widget_init(drag_drop_widget, mock_file_handler):
    """Test that the widget is initialized correctly"""
    # Check object name
    assert drag_drop_widget.objectName() == "dragdrop"
    
    # Check that drag and drop events are accepted
    assert drag_drop_widget.acceptDrops() is True
    
    # Check that the layout is a QVBoxLayout
    assert isinstance(drag_drop_widget.layout(), QVBoxLayout)
    
    # Check that the label has the correct text and alignment
    assert isinstance(drag_drop_widget.label, QLabel)
    assert drag_drop_widget.label.text() == "Drag and drop image folder here"
    assert drag_drop_widget.label.alignment() == Qt.AlignCenter
    
    # Check that the file_handler is initialized
    assert drag_drop_widget.file_handler is mock_file_handler
    
    # Check that image_paths is initialized to an empty list
    assert drag_drop_widget.image_paths == []


@pytest.mark.unit
def test_drag_enter_with_urls(drag_drop_widget):
    """Test dragEnterEvent accepts events with URLs"""
    # Create mock mime data with URLs
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile("/test/path")])
    
    # Create mock drag enter event
    event = MagicMock(spec=QDragEnterEvent)
    event.mimeData.return_value = mime_data
    
    # Call dragEnterEvent
    drag_drop_widget.dragEnterEvent(event)
    
    # Check that the event was accepted
    event.accept.assert_called_once()
    event.ignore.assert_not_called()


@pytest.mark.unit
def test_drag_enter_without_urls(drag_drop_widget):
    """Test dragEnterEvent ignores events without URLs"""
    # Create mock mime data without URLs
    mime_data = QMimeData()
    
    # Create mock drag enter event
    event = MagicMock(spec=QDragEnterEvent)
    event.mimeData.return_value = mime_data
    
    # Call dragEnterEvent
    drag_drop_widget.dragEnterEvent(event)
    
    # Check that the event was ignored
    event.ignore.assert_called_once()
    event.accept.assert_not_called()


@pytest.mark.unit
def test_drop_event_with_valid_folder(drag_drop_widget, mock_file_handler, monkeypatch):
    """Test dropEvent with a valid folder"""
    # Path to a test folder
    test_folder = "/test/folder"
    
    # Mock os.path.isdir to return True
    monkeypatch.setattr('os.path.isdir', lambda x: True)
    
    # Mock FileHandler.get_image_files to return a list of test image paths
    test_image_paths = ["/test/folder/image1.jpg", "/test/folder/image2.jpg"]
    mock_file_handler.get_image_files.return_value = test_image_paths
    
    # Create mock mime data with URLs
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile(test_folder)])
    
    # Create mock drop event
    event = MagicMock(spec=QDropEvent)
    event.mimeData.return_value = mime_data
    
    # Call dropEvent
    drag_drop_widget.dropEvent(event)
    
    # Check that the label text was updated correctly
    assert drag_drop_widget.label.text() == f"Processing Folder Selected: {os.path.basename(test_folder)}"
    
    # Check that FileHandler.get_image_files was called with the correct folder path
    mock_file_handler.get_image_files.assert_called_once_with(test_folder)
    
    # Check that image_paths was updated
    assert drag_drop_widget.image_paths == test_image_paths


@pytest.mark.unit
def test_drop_event_with_multiple_valid_folders(drag_drop_widget, mock_file_handler, monkeypatch):
    """Test dropEvent with multiple valid folders"""
    # Paths to test folders
    test_folders = ["/test/folder1", "/test/folder2"]
    
    # Mock os.path.isdir to return True
    monkeypatch.setattr('os.path.isdir', lambda x: True)
    
    # Mock FileHandler.get_image_files to return different lists for each folder
    test_image_paths1 = ["/test/folder1/image1.jpg", "/test/folder1/image2.jpg"]
    test_image_paths2 = ["/test/folder2/image1.jpg", "/test/folder2/image2.jpg"]
    mock_file_handler.get_image_files.side_effect = [test_image_paths1, test_image_paths2]
    
    # Create mock mime data with URLs
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile(folder) for folder in test_folders])
    
    # Create mock drop event
    event = MagicMock(spec=QDropEvent)
    event.mimeData.return_value = mime_data
    
    # Call dropEvent
    drag_drop_widget.dropEvent(event)
    
    # Check that the label text was updated correctly (using the first folder)
    assert drag_drop_widget.label.text() == f"Processing Folder Selected: {os.path.basename(test_folders[0])}"
    
    # Check that FileHandler.get_image_files was called twice with the correct folder paths
    assert mock_file_handler.get_image_files.call_count == 2
    mock_file_handler.get_image_files.assert_any_call(test_folders[0])
    mock_file_handler.get_image_files.assert_any_call(test_folders[1])
    
    # Check that image_paths contains the paths from the last processed folder
    assert drag_drop_widget.image_paths == test_image_paths2


@pytest.mark.unit
def test_drop_event_with_invalid_input(drag_drop_widget, mock_file_handler):
    # Path To A Test File (Not A Folder)
    test_file = Path(__file__).parent / "data/utils/test_text.txt"
    
    # Create mock mime data with URLs
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile(test_file.__str__())])
    
    # Create mock drop event
    event = MagicMock(spec=QDropEvent)
    event.mimeData.return_value = mime_data

    # Call dropEvent
    drag_drop_widget.dropEvent(event)
    
    # Check that the label text was updated to show error
    assert drag_drop_widget.label.text() == "Please Drop One Or More Folders"
    
    # Check that FileHandler.get_image_files was not called
    mock_file_handler.get_image_files.assert_not_called()
    
    # Check that image_paths was not changed
    assert drag_drop_widget.image_paths == []


@pytest.mark.unit
def test_drop_event_with_empty_urls(drag_drop_widget, mock_file_handler):
    """Test dropEvent when no URLs are provided"""
    # Create mock mime data with no URLs
    mime_data = QMimeData()
    mime_data.setUrls([])
    
    # Create mock drop event
    event = MagicMock(spec=QDropEvent)
    event.mimeData.return_value = mime_data
    
    # Call dropEvent
    drag_drop_widget.dropEvent(event)
    
    # Check that the label text was updated to show error
    assert drag_drop_widget.label.text() == "Please Drop One Or More Folders"
    
    # Check that FileHandler.get_image_files was not called
    mock_file_handler.get_image_files.assert_not_called()