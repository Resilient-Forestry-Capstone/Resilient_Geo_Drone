import pytest
import os
import sys
from unittest.mock import patch, MagicMock, PropertyMock
from pathlib import Path
import numpy as np
import rasterio

from PyQt5.QtWidgets import (QApplication, QDialog, QMessageBox, QListWidgetItem,
                             QFileDialog, QWidget)
from PyQt5.QtCore import Qt, QEvent, QPoint, QSize
from PyQt5.QtGui import QPixmap, QImage

from ResilientGeoDrone.src.front_end.result_viewer import ResultsViewerWidget


@pytest.fixture
def mock_rasterio_env():
    """Mock rasterio.Env context manager"""
    with patch('rasterio.Env') as mock_env:
        mock_env.return_value.__enter__.return_value = None
        mock_env.return_value.__exit__.return_value = None
        yield mock_env


@pytest.fixture
def mock_rasterio_open():
    """Mock rasterio.open context manager"""
    with patch('rasterio.open') as mock_open:
        # Create a mock src object with required properties
        mock_src = MagicMock()
        mock_src.__enter__.return_value = mock_src
        mock_src.__exit__.return_value = None
        
        # Set up default values for single-band TIF
        mock_src.count = 1
        mock_src.read.return_value = np.ones((100, 100))
        mock_src.nodata = None
        mock_src.res = [0.5, 0.5]
        
        mock_open.return_value = mock_src
        yield mock_open, mock_src


@pytest.fixture
def mock_file_system():
    """Mock file system operations"""
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.iterdir') as mock_iterdir, \
         patch('pathlib.Path.glob') as mock_glob, \
         patch('pathlib.Path.stat') as mock_stat:
        
        # Default: path exists
        mock_exists.return_value = True
        
        # Create mock task directories
        mock_dir1 = MagicMock()
        mock_dir1.name = "20230101_120000"
        mock_dir1.is_dir.return_value = True
        mock_dir1.__str__.return_value = "/path/to/20230101_120000"
        
        mock_dir2 = MagicMock()
        mock_dir2.name = "20230102_120000"
        mock_dir2.is_dir.return_value = True
        mock_dir2.__str__.return_value = "/path/to/20230102_120000"
        
        mock_iterdir.return_value = [mock_dir1, mock_dir2]
        
        # Stat for modification time sorting
        def mock_stat_func():
            stat = MagicMock()
            stat.st_mtime = 12345
            stat.st_size = 1024 * 1024  # 1 MB
            return stat
        
        mock_stat.return_value = mock_stat_func()
        
        # Mock file glob results
        mock_tif_file = MagicMock()
        mock_tif_file.name = "test.tif"
        mock_tif_file.suffix = ".tif"
        mock_tif_file.__str__.return_value = "/path/to/test.tif"
        
        mock_pdf_file = MagicMock()
        mock_pdf_file.name = "report.pdf"
        mock_pdf_file.suffix = ".pdf"
        mock_pdf_file.__str__.return_value = "/path/to/report.pdf"
        
        def glob_side_effect(pattern):
            if pattern == "*.tif":
                return [mock_tif_file]
            elif pattern == "*.pdf":
                return [mock_pdf_file]
            return []
        
        mock_glob.side_effect = glob_side_effect
        
        yield mock_exists, mock_iterdir, mock_glob, mock_stat, mock_dir1, mock_dir2, mock_tif_file, mock_pdf_file


@pytest.fixture
def mock_shutil():
    """Mock shutil for file export testing"""
    with patch('shutil.copy2') as mock_copy:
        mock_copy.return_value = None
        yield mock_copy


@pytest.fixture
def mock_platform_windows():
    """Mock platform for Windows OS"""
    with patch('platform.system') as mock_sys:
        mock_sys.return_value = 'Windows'
        yield mock_sys


@pytest.fixture
def mock_os_startfile():
    """Mock os.startfile for external file opening"""
    with patch('os.startfile') as mock_start:
        mock_start.return_value = None
        yield mock_start


@pytest.fixture
def mock_matplotlib(monkeypatch): # Added monkeypatch for potentially patching np.array if needed by QImage
    """Mock matplotlib components"""
    with patch('matplotlib.figure.Figure') as mock_figure_cls, \
         patch('matplotlib.pyplot.get_cmap') as mock_get_cmap, \
         patch('matplotlib.colors.LightSource') as mock_light_source_cls, \
         patch('matplotlib.colors.Normalize') as mock_normalize_cls, \
         patch('matplotlib.cm.ScalarMappable') as mock_scalar_mappable_cls:
        
        mock_ax = MagicMock()
        mock_fig_instance = MagicMock()
        mock_fig_instance.add_subplot.return_value = mock_ax
        
        mock_canvas = MagicMock()
        # Simulate a buffer: height, width, 4 channels (RGBA)
        buffer_height, buffer_width = 50, 50 # Small, manageable dimensions
        # Ensure buffer is bytes and matches QImage expectations (e.g., RGBA8888)
        rgba_data = np.zeros((buffer_height, buffer_width, 4), dtype=np.uint8)
        rgba_data[:, :, 0] = 255 # Red channel
        rgba_data[:, :, 3] = 255 # Alpha channel (opaque)
        mock_canvas.buffer_rgba.return_value = rgba_data.tobytes()
        mock_canvas.get_width_height.return_value = (buffer_width, buffer_height) # width, height
        mock_fig_instance.canvas = mock_canvas
        
        mock_figure_cls.return_value = mock_fig_instance
        
        mock_cmap_instance = MagicMock()
        mock_get_cmap.return_value = mock_cmap_instance
        
        mock_ls_instance = MagicMock()
        # Hillshade result should be (H, W, 4) for RGBA
        mock_ls_instance.shade.return_value = np.random.randint(0, 256, (100, 100, 4), dtype=np.uint8)
        mock_light_source_cls.return_value = mock_ls_instance
        
        mock_normalize_cls.return_value = MagicMock()
        mock_scalar_mappable_cls.return_value = MagicMock()
        
        yield mock_figure_cls, mock_ax, mock_get_cmap, mock_light_source_cls, mock_normalize_cls, mock_scalar_mappable_cls


@pytest.fixture
def mock_cv2():
    """Mock cv2 for image processing"""
    with patch('cv2.resize') as mock_resize, \
         patch('cv2.filter2D') as mock_filter:
        
        mock_resize.return_value = np.ones((50, 50))
        mock_filter.return_value = np.ones((50, 50))
        
        yield mock_resize, mock_filter


@pytest.fixture
def mock_qfiledialog():
    """Mock QFileDialog.getSaveFileName"""
    with patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName') as mock_get_save:
        mock_get_save.return_value = ("/path/to/save/file.tif", "*.tif")
        yield mock_get_save


@pytest.fixture
def mock_qmessagebox():
    """Mock QMessageBox for information and warning dialogs"""
    with patch.object(QMessageBox, 'information') as mock_info, \
         patch.object(QMessageBox, 'warning') as mock_warn:
        
        mock_info.return_value = QMessageBox.Ok
        mock_warn.return_value = QMessageBox.Ok
        
        yield mock_info, mock_warn


@pytest.fixture
def viewer(qtbot, mock_file_system):
    """Create a ResultsViewerWidget instance for testing"""
    widget = ResultsViewerWidget()
    qtbot.addWidget(widget)
    return widget


@pytest.mark.unit
def test_initialization(viewer):
    """Test proper initialization of the ResultsViewerWidget"""
    # Check window properties
    assert viewer.objectName() == "resultsViewer"
    assert viewer.windowTitle() == "Results Viewer"
    assert viewer.minimumSize().width() == 900
    assert viewer.minimumSize().height() == 600
    
    # Check default variables
    assert viewer.output_base_dir == Path("data/output/point_cloud")
    assert viewer.current_task_path is None
    assert viewer.current_file_path is None
    assert viewer.scale_factor_override == 1.0
    assert viewer.auto_scaling is True
    assert viewer.contour_line_count == 5
    assert viewer.current_colormap == 'viridis'
    
    # Check UI components
    assert hasattr(viewer, 'task_folders_list')
    assert hasattr(viewer, 'files_list')
    assert hasattr(viewer, 'file_viewers')
    assert hasattr(viewer, 'tif_viewer')
    assert hasattr(viewer, 'tif_image')
    assert hasattr(viewer, 'colormap_selector')
    assert hasattr(viewer, 'contour_slider')
    assert hasattr(viewer, 'scale_slider')


@pytest.mark.unit
def test_update_contour_value(viewer):
    """Test the _update_contour_value method"""
    # Set initial value
    assert viewer.contour_value.text() == "5"
    
    # Update to new value
    viewer._update_contour_value(10)
    assert viewer.contour_value.text() == "10"
    
    # Test with extreme values
    viewer._update_contour_value(1)
    assert viewer.contour_value.text() == "1"
    
    viewer._update_contour_value(1000)
    assert viewer.contour_value.text() == "1000"


@pytest.mark.unit
def test_apply_contour_changes_without_file(viewer, monkeypatch):
    """Test the _apply_contour_changes method when no file is loaded"""
    # Setup a spy for _load_tif_file
    mock_load_tif = MagicMock()
    monkeypatch.setattr(viewer, '_load_tif_file', mock_load_tif)
    
    # Set slider value
    viewer.contour_slider.setValue(20)
    
    # Apply changes without a file
    viewer.current_file_path = None
    viewer._apply_contour_changes()
    
    # Check contour_line_count is updated but _load_tif_file is not called
    assert viewer.contour_line_count == 20
    mock_load_tif.assert_not_called()


@pytest.mark.unit
def test_apply_contour_changes_with_tif_file(viewer, monkeypatch):
    """Test the _apply_contour_changes method with a TIF file loaded"""
    # Setup a spy for _load_tif_file
    mock_load_tif = MagicMock()
    monkeypatch.setattr(viewer, '_load_tif_file', mock_load_tif)
    
    # Set slider value
    viewer.contour_slider.setValue(30)
    
    # Set a mock file path with .tif extension
    mock_file_path = MagicMock()
    mock_file_path.suffix.lower.return_value = '.tif'
    viewer.current_file_path = mock_file_path
    
    # Apply changes with a TIF file
    viewer._apply_contour_changes()
    
    # Check contour_line_count is updated and _load_tif_file is called
    assert viewer.contour_line_count == 30
    mock_load_tif.assert_called_once_with(mock_file_path)


@pytest.mark.unit
def test_update_file_config(viewer, qtbot):
    # Open Up Our Viewer Window So Our Visibility Tests Work
    viewer.show()
    viewer._update_file_config(True)

    assert viewer.colormap_label.isVisible() is True
    assert viewer.colormap_selector.isVisible() is True
    assert viewer.contour_label.isVisible() is True
    assert viewer.contour_slider.isVisible() is True
    assert viewer.contour_value.isVisible() is True
    assert viewer.apply_btn.isVisible() is True
    
    # Test disabling UI elements
    viewer._update_file_config(False)
    assert viewer.colormap_label.isVisible() is False
    assert viewer.colormap_selector.isVisible() is False
    assert viewer.contour_label.isVisible() is False
    assert viewer.contour_slider.isVisible() is False
    assert viewer.contour_value.isVisible() is False
    assert viewer.apply_btn.isVisible() is False


@pytest.mark.unit
def test_toggle_scale_slider(viewer, monkeypatch):
    """Test the _toggle_scale_slider method"""
    # Setup a spy for _load_tif_file
    mock_load_tif = MagicMock()
    monkeypatch.setattr(viewer, '_load_tif_file', mock_load_tif)
    
    # Initially auto_scaling is True and scale_slider is disabled
    assert viewer.auto_scaling is True
    assert viewer.scale_slider.isEnabled() is False
    
    # Toggle to manual scaling
    viewer._toggle_scale_slider(False)
    assert viewer.auto_scaling is False
    assert viewer.scale_slider.isEnabled() is True
    mock_load_tif.assert_not_called()
    
    # Setup a file path
    mock_file_path = MagicMock()
    mock_file_path.suffix.lower.return_value = '.tif'
    viewer.current_file_path = mock_file_path
    
    # Toggle back to auto scaling with file loaded
    viewer._toggle_scale_slider(True)
    assert viewer.auto_scaling is True
    assert viewer.scale_slider.isEnabled() is False
    mock_load_tif.assert_called_once_with(mock_file_path)


@pytest.mark.unit
def test_update_scale_value(viewer):
    """Test the _update_scale_value method"""
    # Default value
    assert viewer.scale_value.text() == "100%"
    assert viewer.scale_factor_override == 1.0
    
    # Update to 50%
    viewer._update_scale_value(50)
    assert viewer.scale_value.text() == "50%"
    assert viewer.scale_factor_override == 0.5  # Note: There's a bug in the code, should be 0.5
    
    # Update to minimum
    viewer._update_scale_value(10)
    assert viewer.scale_value.text() == "10%"
    assert viewer.scale_factor_override == 0.1  # Note: Should be 0.1
    
    # Update to maximum
    viewer._update_scale_value(100)
    assert viewer.scale_value.text() == "100%"
    assert viewer.scale_factor_override == 1.0  # Note: Should be 1.0


@pytest.mark.unit
def test_on_image_clicked_no_pixmap(viewer, qtbot):
    """Test _on_image_clicked with no pixmap set"""
    # Mock event
    event = MagicMock()
    event.button.return_value = Qt.LeftButton
    
    # Create spy for _show_full_screen_image
    with patch.object(viewer, '_show_full_screen_image') as mock_show:
        # Call with no pixmap set
        viewer._on_image_clicked(event)
        mock_show.assert_not_called()


@pytest.mark.unit
def test_on_image_clicked_with_pixmap(viewer, qtbot):
    """Test _on_image_clicked with a pixmap set"""
    # Create a small test pixmap
    pixmap = QPixmap(10, 10)
    pixmap.fill(Qt.red)
    viewer.tif_image.setPixmap(pixmap)
    
    # Mock event
    event = MagicMock()
    event.button.return_value = Qt.LeftButton
    
    # Create spy for _show_full_screen_image
    with patch.object(viewer, '_show_full_screen_image') as mock_show:
        # Call with pixmap set
        viewer._on_image_clicked(event)
        mock_show.assert_called_once()


@pytest.mark.unit
def test_show_full_screen_image(viewer, qtbot, monkeypatch):
    """Test _show_full_screen_image method"""
    # Create a pixmap
    pixmap = QPixmap(10, 50)
    pixmap.fill(Qt.blue)
    
    viewer._show_full_screen_image(pixmap)
    
    # Check that fullscreen overlay was created and shown
    assert hasattr(viewer, 'fullscreen_overlay')
    assert hasattr(viewer, 'fullscreen_image')
    assert hasattr(viewer, 'fullscreen_scroll_area')
    assert viewer.current_scale_factor == 1.0
    assert viewer.original_pixmap_size.width() == 10
    assert viewer.original_pixmap_size.height() == 50

    # Close Overlay
    viewer.fullscreen_overlay.close()


@pytest.mark.unit
def test_update_fullscreen_zoom_no_image(viewer):
    """Test _update_fullscreen_zoom with no image set"""
    # Clear attributes
    viewer.fullscreen_image = None
    viewer.original_pixmap_size = None
    
    # Should not raise exceptions
    viewer._update_fullscreen_zoom()


@pytest.mark.unit
def test_update_fullscreen_zoom_with_image(viewer, qtbot):
    """Test _update_fullscreen_zoom with image set"""
    # Create pixmap and set it
    pixmap = QPixmap(20, 20)
    pixmap.fill(Qt.green)
    viewer.tif_image.setPixmap(pixmap)
    
    # Setup fullscreen image mock
    viewer.fullscreen_image = MagicMock()
    viewer.original_pixmap_size = QSize(20, 20)
    viewer.current_scale_factor = 2.0  # Double size
    
    # Call the method
    viewer._update_fullscreen_zoom()
    
    # The setPixmap should have been called with a scaled pixmap (40x40)
    viewer.fullscreen_image.setPixmap.assert_called_once()


@pytest.mark.unit
def test_eventfilter_key_escape(viewer, qtbot):
    """Test eventFilter handling ESC key press to exit fullscreen"""
    # Create a mock overlay
    mock_overlay = MagicMock()
    viewer.fullscreen_overlay = mock_overlay
    
    # Create key event
    event = MagicMock()
    event.type.return_value = QEvent.KeyPress
    event.key.return_value = Qt.Key_Escape
    
    # Call eventFilter
    result = viewer.eventFilter(mock_overlay, event)
    
    # Check overlay was closed and event was handled
    mock_overlay.close.assert_called_once()
    assert result is True


@pytest.mark.unit
def test_eventfilter_wheel_zoom(viewer, qtbot, monkeypatch):
    """Test eventFilter handling mouse wheel zoom"""
    # Setup mocks
    event = MagicMock()
    event.type.return_value = QEvent.Wheel
    event.angleDelta().y.return_value = 120  # Positive = zoom in
    
    viewer.fullscreen_image = MagicMock()
    
    # Mock the zoom update method
    mock_update_zoom = MagicMock()
    monkeypatch.setattr(viewer, '_update_fullscreen_zoom', mock_update_zoom)
    
    # Initial scale factor
    viewer.current_scale_factor = 1.0
    
    # Call eventFilter
    result = viewer.eventFilter(None, event)
    
    # Check scale factor was increased (zoom in)
    assert viewer.current_scale_factor > 1.0
    mock_update_zoom.assert_called_once()
    assert result is True
    
    # Test zoom out
    event.angleDelta().y.return_value = -120  # Negative = zoom out
    mock_update_zoom.reset_mock()
    
    # Call eventFilter again
    initial_scale = viewer.current_scale_factor
    result = viewer.eventFilter(None, event)
    
    # Check scale factor was decreased (zoom out)
    assert viewer.current_scale_factor < initial_scale
    mock_update_zoom.assert_called_once()
    assert result is True


@pytest.mark.unit
def test_eventfilter_mouse_pan(viewer, qtbot):
    """Test eventFilter handling mouse panning"""
    # Setup viewport mock
    mock_viewport = MagicMock()
    mock_scrollbar_h = MagicMock()
    mock_scrollbar_v = MagicMock()
    
    viewer.fullscreen_scroll_area = MagicMock()
    viewer.fullscreen_scroll_area.viewport.return_value = mock_viewport
    viewer.fullscreen_scroll_area.horizontalScrollBar.return_value = mock_scrollbar_h
    viewer.fullscreen_scroll_area.verticalScrollBar.return_value = mock_scrollbar_v
    
    # Mouse press event
    press_event = MagicMock()
    press_event.type.return_value = QEvent.MouseButtonPress
    press_event.button.return_value = Qt.LeftButton
    press_event.pos.return_value = QPoint(100, 100)
    
    # Call eventFilter with mouse press
    result = viewer.eventFilter(mock_viewport, press_event)
    
    # Check dragging started
    assert viewer.is_dragging is True
    assert viewer.drag_start_pos == QPoint(100, 100)
    mock_viewport.setCursor.assert_called_once()
    assert result is True
    
    # Mouse move event
    move_event = MagicMock()
    move_event.type.return_value = QEvent.MouseMove
    move_event.pos.return_value = QPoint(50, 50)  # Moved left and up 50px
    
    # Call eventFilter with mouse move
    result = viewer.eventFilter(mock_viewport, move_event)
    
    # Check scrollbars were adjusted
    mock_scrollbar_h.setValue.assert_called_once()
    mock_scrollbar_v.setValue.assert_called_once()
    assert result is True
    
    # Mouse release event
    release_event = MagicMock()
    release_event.type.return_value = QEvent.MouseButtonRelease
    release_event.button.return_value = Qt.LeftButton
    
    # Call eventFilter with mouse release
    result = viewer.eventFilter(mock_viewport, release_event)
    
    # Check dragging stopped
    assert viewer.is_dragging is False
    assert mock_viewport.setCursor.call_count == 2
    assert result is True


@pytest.mark.unit
def test_refresh_task_folders_directory_not_exists(viewer, mock_file_system):
    """Test refresh_task_folders when directory doesn't exist"""
    mock_exists, _, _, _, _, _, _, _ = mock_file_system
    mock_exists.return_value = False
    
    # Call refresh
    viewer.refresh_task_folders()
    
    # Check error message is shown
    assert viewer.task_folders_list.count() == 1
    assert viewer.task_folders_list.item(0).text() == "No output directory found"


@pytest.mark.unit
def test_refresh_task_folders_empty_directory(viewer, mock_file_system):
    """Test refresh_task_folders with empty directory"""
    mock_exists, mock_iterdir, _, _, _, _, _, _ = mock_file_system
    mock_exists.return_value = True
    mock_iterdir.return_value = []
    
    # Call refresh
    viewer.refresh_task_folders()
    
    # Check message is shown
    assert viewer.task_folders_list.count() == 1
    assert viewer.task_folders_list.item(0).text() == "No task folders found"


@pytest.mark.unit
def test_refresh_task_folders_with_directories(viewer, mock_file_system):
    """Test refresh_task_folders with valid directories"""
    # Unpack mocks from the fixture. Note that mock_iterdir_patch is the patch for pathlib.Path.iterdir,
    # and mock_stat_patch is the patch for pathlib.Path.stat.
    # mock_dir1 and mock_dir2 are the MagicMock objects representing directories.
    _, _, _, _, mock_dir1, mock_dir2, _, _ = mock_file_system
    
    # Configure mock_dir1
    mock_dir1.name = "20230101_120000"  # Expected format
    mock_dir1.is_dir.return_value = True
    mock_stat_obj1 = MagicMock()
    mock_stat_obj1.st_mtime = 1672531200  # Timestamp for 2023-01-01
    mock_dir1.stat = MagicMock(return_value=mock_stat_obj1)
    # Ensure __str__ is set if setData(Qt.UserRole, str(folder_path)) is used
    mock_dir1.__str__ = MagicMock(return_value="/mock/path/20230101_120000")


    # Configure mock_dir2
    mock_dir2.name = "20230102_120000"  # Expected format
    mock_dir2.is_dir.return_value = True
    mock_stat_obj2 = MagicMock()
    mock_stat_obj2.st_mtime = 1672617600  # Timestamp for 2023-01-02 (newer)
    mock_dir2.stat = MagicMock(return_value=mock_stat_obj2)
    mock_dir2.__str__ = MagicMock(return_value="/mock/path/20230102_120000")

    # Configure the mock for viewer.output_base_dir
    # Using spec=Path helps catch incorrect attribute access on the mock.
    mock_viewer_output_base_dir = MagicMock(spec=Path) 
    mock_viewer_output_base_dir.exists.return_value = True
    # This iterdir will be called by viewer.refresh_task_folders
    mock_viewer_output_base_dir.iterdir.return_value = [mock_dir1, mock_dir2] 
    
    # Override the viewer's output_base_dir with our fully controlled mock
    viewer.output_base_dir = mock_viewer_output_base_dir
    
    # Call the method under test
    viewer.refresh_task_folders()
    
    # Assertions
    current_count = viewer.task_folders_list.count()
    
    # For debugging if the assertion fails:
    if current_count != 2:
        print(f"AssertionError: Expected 2 items, got {current_count}")
        for i in range(current_count):
            print(f"Item {i}: {viewer.task_folders_list.item(i).text()}")

    assert current_count == 2, f"Expected 2 task folders, found {current_count}"
    
    # Folders are sorted by modification time, newest first (reverse=True)
    # mock_dir2 (newer mtime) should be item 0
    # mock_dir1 (older mtime) should be item 1
    assert "Task 2023-01-02 12:00:00" in viewer.task_folders_list.item(0).text()
    assert "Task 2023-01-01 12:00:00" in viewer.task_folders_list.item(1).text()

    # Verify stored data if necessary
    assert viewer.task_folders_list.item(0).data(Qt.UserRole) == str(mock_dir2)
    assert viewer.task_folders_list.item(1).data(Qt.UserRole) == str(mock_dir1)


@pytest.mark.unit
def test_refresh_task_folders_error_handling(viewer, mock_file_system):
    """Test refresh_task_folders error handling"""
    mock_exists, mock_iterdir, _, _, _, _, _, _ = mock_file_system
    mock_exists.return_value = True
    mock_iterdir.side_effect = PermissionError("Access denied")
    
    # Call refresh
    viewer.refresh_task_folders()
    
    # Check error message is shown
    assert viewer.task_folders_list.count() == 1
    assert "Error scanning directory:" in viewer.task_folders_list.item(0).text()


@pytest.mark.unit
def test_on_task_selected_no_selection(viewer):
    """Test _on_task_selected with no folder selected"""
    # Clear selection
    viewer.task_folders_list.clearSelection()
    
    # Call method
    viewer._on_task_selected()
    
    # Check state
    assert viewer.current_task_path is None
    assert viewer.files_list.count() == 0



@pytest.mark.unit
def test_on_task_selected_with_empty_folder(viewer, mock_file_system, qtbot):
    """Test _on_task_selected with empty folder"""
    # mock_file_system provides:
    #   mock_exists_patch (idx 0), mock_iterdir_patch (idx 1), 
    #   mock_glob_patch (idx 2), mock_stat_patch (idx 3),
    #   mock_dir1 (idx 4), mock_dir2 (idx 5), 
    #   mock_tif_file (idx 6), mock_pdf_file (idx 7)

    # Get the global mock for pathlib.Path.glob from the fixture
    mock_glob_patch = mock_file_system[2] 
    
    # For this test, force glob to always return an empty list,
    # overriding the fixture's default side_effect.
    mock_glob_patch.side_effect = lambda pattern: []

    # We use one of the mock directories from the fixture (e.g., mock_dir1)
    # just for its string representation to simulate a selected task path.
    mock_dir1_from_fixture = mock_file_system[4]
    path_data_for_role = str(mock_dir1_from_fixture) # This calls mock_dir1_from_fixture.__str__()

    # Pre-assertions to ensure our test setup data is correct
    assert isinstance(path_data_for_role, str)
    assert path_data_for_role is not None

    # Create and add the QListWidgetItem
    item = QListWidgetItem("Task 2023-01-01 12:00:00")
    item.setData(Qt.UserRole, path_data_for_role)

    # Verify data was set on the item instance
    assert item.data(Qt.UserRole) == path_data_for_role

    viewer.task_folders_list.addItem(item)

    # Programmatically select the item. This should trigger the currentItemChanged signal,
    # which in turn calls _on_task_selected.
    # Use qtbot.waitSignal to ensure the slot execution completes.
    with qtbot.waitSignal(viewer.task_folders_list.currentItemChanged, timeout=1000, raising=True):
        viewer.task_folders_list.setCurrentItem(item)

    # Now, _on_task_selected should have executed.
    # Because mock_glob_patch.side_effect forces glob to return [],
    # the 'all_files' list in _on_task_selected should be empty.
    # Therefore, the "No output files found..." message should have been added.

    current_files_count = viewer.files_list.count()
    expected_message = "No output files found in this folder"
    
    assert current_files_count == 1
    
    if current_files_count > 0: # This check is now more robust due to the assertion above
        actual_message = viewer.files_list.item(0).text()
        assert actual_message == expected_message
    
    # Verify that current_task_path was set correctly in the viewer instance.
    # The Path object created inside _on_task_selected will use the globally patched methods.
    assert viewer.current_task_path == Path(path_data_for_role)



@pytest.mark.unit
def test_on_task_selected_with_files(viewer, mock_file_system, qtbot, monkeypatch):
    """Test _on_task_selected with files in folder"""
    # Unpack mocks from the fixture
    # mock_glob_patch is the globally patched pathlib.Path.glob
    _, _, mock_glob_patch, mock_stat_patch, \
        mock_dir1_fixture, _, mock_tif_file_fixture, mock_pdf_file_fixture = mock_file_system

    # --- Configure mock files (mock_tif_file_fixture, mock_pdf_file_fixture) ---
    # These are the objects that will be returned by glob and then processed.
    # They need a .stat().st_size that is numeric.
    # The mock_file_system fixture already sets a default .stat().st_size for its mock_stat.
    # We need to ensure these specific file mocks also have it.

    # Configure mock_tif_file_fixture
    mock_tif_stat = MagicMock()
    mock_tif_stat.st_size = 2048  # Example size in bytes
    mock_tif_file_fixture.stat = MagicMock(return_value=mock_tif_stat)
    # Ensure .name and .suffix are as expected by the code if not already set by fixture
    mock_tif_file_fixture.name = "test_dsm.tif"
    mock_tif_file_fixture.suffix = ".tif"
    # __str__ is already mocked by the fixture to return a path string

    # Configure mock_pdf_file_fixture
    mock_pdf_stat = MagicMock()
    mock_pdf_stat.st_size = 1024  # Example size in bytes
    mock_pdf_file_fixture.stat = MagicMock(return_value=mock_pdf_stat)
    mock_pdf_file_fixture.name = "report_doc.pdf"
    mock_pdf_file_fixture.suffix = ".pdf"
    # __str__ is already mocked by the fixture

    # Configure the side_effect for the globally patched Path.glob
    # This will be called when Path(task_path_str).glob('*') is executed.
    def specific_glob_side_effect(pattern):
        # This side_effect is now on the globally patched mock_glob_patch
        # It doesn't know about 'self' (the Path instance) directly.
        # We assume the pattern is sufficient.
        if pattern == "*.tif":
            return [mock_tif_file_fixture]
        elif pattern == "*.pdf":
            return [mock_pdf_file_fixture]
        elif pattern == "*": # For the combined glob
            return [mock_tif_file_fixture, mock_pdf_file_fixture]
        return []
    mock_glob_patch.side_effect = specific_glob_side_effect

    # Prepare the data for the QListWidgetItem (the task folder)
    path_data_for_role = str(mock_dir1_fixture) # Uses mock_dir1_fixture.__str__()

    # Pre-assertions for test setup data
    assert isinstance(path_data_for_role, str), "Path data for UserRole is not a string"
    assert path_data_for_role is not None, "Path data for UserRole is None"

    # Create and add the QListWidgetItem for the task folder
    item = QListWidgetItem("Task 2023-01-01 12:00:00")
    item.setData(Qt.UserRole, path_data_for_role)
    assert item.data(Qt.UserRole) == path_data_for_role, "Data mismatch on QListWidgetItem"
    viewer.task_folders_list.addItem(item)

    # Programmatically select the item and wait for the slot to execute
    with qtbot.waitSignal(viewer.task_folders_list.currentItemChanged, timeout=1000, raising=True):
        viewer.task_folders_list.setCurrentItem(item)
        # viewer.task_folders_list.setCurrentRow(0) # Alternative

    # _on_task_selected should have executed.
    # mock_glob_patch.side_effect should have returned mock_tif_file_fixture and mock_pdf_file_fixture.
    # These files should now be listed in viewer.files_list.

    # Assertions
    current_files_count = viewer.files_list.count()
    assert current_files_count == 2, \
        (f"Expected 2 files in files_list, got {current_files_count}. Items: "
         f"{[viewer.files_list.item(i).text() for i in range(current_files_count)] if current_files_count > 0 else 'None'}")

    # Check file descriptions (order might vary depending on glob or internal sorting)
    file_texts = sorted([viewer.files_list.item(i).text() for i in range(current_files_count)])
    
    assert any("Digital Surface Model - test_dsm.tif" in text for text in file_texts), \
        f"DSM file not found in list. Items: {file_texts}"
    assert any("Report Document - report_doc.pdf" in text for text in file_texts), \
        f"PDF file not found in list. Items: {file_texts}"

    # Verify current_task_path
    assert viewer.current_task_path == Path(path_data_for_role), \
        f"viewer.current_task_path is {viewer.current_task_path}, expected {Path(path_data_for_role)}"

@pytest.mark.unit
def test_on_file_selected_no_selection(viewer):
    """Test _on_file_selected with no file selected"""
    # Clear selection
    viewer.files_list.clearSelection()
    
    # Call method
    viewer._on_file_selected()
    
    # Check state
    assert viewer.current_file_path is None
    assert viewer.file_info.text() == "No file selected"
    assert not viewer.export_btn.isEnabled()
    assert not viewer.colormap_label.isVisible()


@pytest.mark.unit
def test_on_file_selected_tif_file(viewer, mock_file_system, qtbot, monkeypatch):
    """Test _on_file_selected with .tif file"""
    # Mock the _load_tif_file method
    mock_load_tif_file = MagicMock()
    monkeypatch.setattr(viewer, '_load_tif_file', mock_load_tif_file)
    
    # Mock _update_file_config
    mock_update_file_config = MagicMock()
    monkeypatch.setattr(viewer, '_update_file_config', mock_update_file_config)
    
    # Setup file data from fixture
    _, _, _, _, _, _, mock_tif_file_fixture, _ = mock_file_system
    path_data_for_role = str(mock_tif_file_fixture) # Uses mock_tif_file_fixture.__str__()

    # Ensure the mock_tif_file_fixture has a .stat().st_size for file info display
    mock_tif_stat = MagicMock()
    mock_tif_stat.st_size = 1024 * 1024 # 1MB
    mock_tif_file_fixture.stat = MagicMock(return_value=mock_tif_stat)
    mock_tif_file_fixture.name = "test.tif" # Ensure name is set for display
    
    # Add file to list
    # The text here should match what _on_task_selected would generate
    item_text = f"Digital Surface Model - {mock_tif_file_fixture.name} (1.0 MB)"
    item = QListWidgetItem(item_text)
    item.setData(Qt.UserRole, path_data_for_role)
    viewer.files_list.addItem(item)
    
    # Programmatically select the item and wait for the slot to execute
    with qtbot.waitSignal(viewer.files_list.currentItemChanged, timeout=1000, raising=True):
        viewer.files_list.setCurrentItem(item)
        # viewer.files_list.setCurrentRow(0) # Alternative
    
    # _on_file_selected should have been called once via the signal.
    
    # Check state
    assert viewer.current_file_path == Path(path_data_for_role)
    assert f"Selected: {mock_tif_file_fixture.name}" in viewer.file_info.text()
    mock_load_tif_file.assert_called_once_with(Path(path_data_for_role))
    mock_update_file_config.assert_called_once_with(True)



@pytest.mark.unit
def test_on_file_selected_non_tif_file(viewer, mock_file_system, qtbot, monkeypatch):
    """Test _on_file_selected with non-tif file"""
    # Mock _update_file_config
    mock_update_file_config = MagicMock()
    monkeypatch.setattr(viewer, '_update_file_config', mock_update_file_config)

    # Mock _load_tif_file to ensure it's NOT called for non-TIF
    mock_load_tif_file = MagicMock()
    monkeypatch.setattr(viewer, '_load_tif_file', mock_load_tif_file)
    
    # Setup file data from fixture
    _, _, _, _, _, _, _, mock_pdf_file_fixture = mock_file_system
    path_data_for_role = str(mock_pdf_file_fixture) # Uses mock_pdf_file_fixture.__str__()

    # Ensure the mock_pdf_file_fixture has a .stat().st_size for file info display
    mock_pdf_stat = MagicMock()
    mock_pdf_stat.st_size = 512 * 1024 # 0.5MB
    mock_pdf_file_fixture.stat = MagicMock(return_value=mock_pdf_stat)
    mock_pdf_file_fixture.name = "report.pdf" # Ensure name is set for display

    # Add file to list
    item_text = f"Report Document - {mock_pdf_file_fixture.name} (0.5 MB)"
    item = QListWidgetItem(item_text)
    item.setData(Qt.UserRole, path_data_for_role)
    viewer.files_list.addItem(item)
    
    # Programmatically select the item and wait for the slot to execute
    with qtbot.waitSignal(viewer.files_list.currentItemChanged, timeout=1000, raising=True):
        viewer.files_list.setCurrentItem(item)
        # viewer.files_list.setCurrentRow(0) # Alternative

    # _on_file_selected should have been called once via the signal.

    # Check state
    assert viewer.current_file_path == Path(path_data_for_role)
    assert f"Selected: {mock_pdf_file_fixture.name}" in viewer.file_info.text()
    assert viewer.file_viewers.currentIndex() == 1  # PDF viewer (index 1)
    assert "cannot be previewed" in viewer.empty_state.text() # empty_state is used by PDF page
    mock_update_file_config.assert_called_once_with(False)
    mock_load_tif_file.assert_not_called() # Ensure TIF loading wasn't attempted


@pytest.mark.unit
def test_on_colormap_changed(viewer, monkeypatch):
    """Test _on_colormap_changed method"""
    # Mock _load_tif_file method
    mock_load = MagicMock()
    monkeypatch.setattr(viewer, '_load_tif_file', mock_load)
    
    # Setup current file
    mock_file = MagicMock()
    mock_file.suffix.lower.return_value = '.tif'
    viewer.current_file_path = mock_file
    
    # Change colormap
    viewer._on_colormap_changed('plasma')
    
    # Check state
    assert viewer.current_colormap == 'plasma'
    mock_load.assert_called_once_with(mock_file)
    
    # Test with no file
    mock_load.reset_mock()
    viewer.current_file_path = None
    viewer._on_colormap_changed('inferno')
    
    # Check state
    assert viewer.current_colormap == 'inferno'
    mock_load.assert_not_called()



@pytest.mark.unit
def test_load_tif_file_single_band_success(viewer):
  # Grab Test Orthophoto
  chm_path = Path(__file__).parent.parent / "data/utils/test_chm.tif"

  # Call Our Method With The Path
  viewer._load_tif_file(chm_path)

  # Check that the TIF file was loaded and displayed
  assert viewer.file_viewers.currentIndex() == 0, \
      f"Expected TIF viewer (index 0), got {viewer.file_viewers.currentIndex()}. Empty state: '{viewer.empty_state.text()}'"
  assert "test_chm.tif" in viewer.file_info.text()
  assert viewer.tif_image.pixmap() is not None, "Pixmap was not set on tif_image"
  if viewer.tif_image.pixmap():
      assert not viewer.tif_image.pixmap().isNull(), "Pixmap on tif_image is null"
  

@pytest.mark.unit
def test_load_tif_file_multi_band(viewer):
  # Grab Test CHM 
  ortho_path = Path(__file__).parent.parent / "data/utils/test_ortho.tif"

  # Call Our Method With The Path
  viewer._load_tif_file(ortho_path)

  # Check that the TIF file was loaded and displayed
  assert viewer.file_viewers.currentIndex() == 0, \
      f"Expected TIF viewer (index 0), got {viewer.file_viewers.currentIndex()}. Empty state: '{viewer.empty_state.text()}'"
  assert "test_ortho.tif" in viewer.file_info.text()
  assert viewer.tif_image.pixmap() is not None, "Pixmap was not set on ortho_image"
  if viewer.tif_image.pixmap():
      assert not viewer.tif_image.pixmap().isNull(), "Pixmap on ortho_image is null"
  

@pytest.mark.unit
def test_load_tif_file_error(viewer, mock_rasterio_env, mock_rasterio_open):
    
    # Call Method With Non-Existent File
    viewer._load_tif_file(Path("non_existent.tif"))
    
    # Ensure Our Warnings Were Raised
    assert viewer.empty_state.text().startswith("Error loading TIF file:")
    assert viewer.tif_image.pixmap() is None, "Pixmap should be None on error"



@pytest.mark.unit
def test_open_external_no_file(viewer):
    """Test _open_external with no file selected"""
    viewer.current_file_path = None
    
    # This should just return without error
    viewer._open_external()


@pytest.mark.unit
def test_open_external_windows(viewer, mock_platform_windows, mock_os_startfile, mock_file_system):
    """Test _open_external on Windows"""
    _, _, _, _, _, _, mock_tif_file, _ = mock_file_system
    viewer.current_file_path = mock_tif_file
    
    # Call method
    viewer._open_external()
    
    # Check file was opened
    mock_os_startfile.assert_called_once_with(str(mock_tif_file))


@pytest.mark.unit
def test_open_external_error(viewer, mock_platform_windows, mock_os_startfile, mock_qmessagebox, mock_file_system):
    """Test _open_external with error"""
    _, _, _, _, _, _, mock_tif_file, _ = mock_file_system
    viewer.current_file_path = mock_tif_file
    
    # Setup error
    mock_os_startfile.side_effect = Exception("Cannot open file")
    mock_info, mock_warn = mock_qmessagebox
    
    # Call method
    viewer._open_external()
    
    # Check warning was shown
    mock_warn.assert_called_once()
    assert "Could not open file" in mock_warn.call_args[0][2]


@pytest.mark.unit
def test_export_file_no_file(viewer):
    """Test _export_file with no file selected"""
    viewer.current_file_path = None
    
    # This should just return without error
    viewer._export_file()


@pytest.mark.unit
def test_export_file_cancel(viewer, mock_qfiledialog, mock_shutil, mock_file_system):
    """Test _export_file with cancel"""
    _, _, _, _, _, _, mock_tif_file, _ = mock_file_system
    viewer.current_file_path = mock_tif_file
    
    mock_qfiledialog.return_value = ("", "")
    
    # Call method
    viewer._export_file()
    
    # Check no copy was performed
    mock_shutil.assert_not_called()


@pytest.mark.unit
def test_export_file_success(viewer, mock_qfiledialog, mock_shutil, mock_qmessagebox, mock_file_system):
    """Test _export_file success"""
    _, _, _, _, _, _, mock_tif_file, _ = mock_file_system
    viewer.current_file_path = mock_tif_file
    mock_info, mock_warn = mock_qmessagebox
    
    # Call method
    viewer._export_file()
    
    # Check file was copied and success message shown
    mock_shutil.assert_called_once_with(mock_tif_file, "/path/to/save/file.tif")
    mock_info.assert_called_once()
    assert "Success" in mock_info.call_args[0][1]


@pytest.mark.unit
def test_export_file_error(viewer, mock_qfiledialog, mock_shutil, mock_qmessagebox, mock_file_system):
    """Test _export_file with error"""
    _, _, _, _, _, _, mock_tif_file, _ = mock_file_system
    viewer.current_file_path = mock_tif_file
    
    # Setup error
    mock_shutil.side_effect = Exception("Permission denied")
    mock_info, mock_warn = mock_qmessagebox
    
    # Call method
    viewer._export_file()
    
    # Check warning was shown
    mock_warn.assert_called_once()
    assert "Could not export file" in mock_warn.call_args[0][2]


@pytest.mark.unit
def test_go_back_to_pipeline(viewer, monkeypatch):
    """Test _go_back_to_pipeline method"""
    # Mock close method
    mock_close = MagicMock()
    monkeypatch.setattr(viewer, 'close', mock_close)
    
    # Call method
    viewer._go_back_to_pipeline()
    
    # Check widget was closed
    mock_close.assert_called_once()