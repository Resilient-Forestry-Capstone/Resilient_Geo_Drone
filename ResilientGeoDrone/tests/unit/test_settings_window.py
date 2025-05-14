import random
import time
import os
import PyQt5
import yaml
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QTabWidget, QPushButton, QLineEdit, QSpinBox, 
                            QDoubleSpinBox, QListWidget, QGroupBox, QCheckBox, 
                            QComboBox, QMessageBox)
import tempfile

from ResilientGeoDrone.src.front_end.settings_window import SettingsWindow


"""

    Desc: Fixture For Setting Up A Settings Window For Testing

"""
@pytest.fixture
def settings_window(qtbot):
    window = SettingsWindow()
    qtbot.addWidget(window)
    return window


"""

    Desc: Fixture For Creating A Temporary Log Directory As Not To Mess With Current Ones

"""
@pytest.fixture
def tmp_log_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_path = Path(tmpdirname)
        yield temp_path


"""

    Desc: Test That Makes Sure We Catch Invalid Input Configs

"""
@pytest.mark.unit
def test_settings_window_init_invalid_config(qtbot):
    with pytest.raises(FileNotFoundError):
        window = SettingsWindow("invalid")
        qtbot.addWidget(window)


"""

    Desc: Test That We Pass Expected Initialization Parameters

"""
@pytest.mark.unit
def test_settings_window_init_default_valid_config():
    settings_window = SettingsWindow()
    assert settings_window
    assert settings_window.config_path == (Path(__file__).parent.parent.parent / "config/config.yaml")


"""

    Desc: Test That Adds Random Timestamped Logs Into A Temporary Log List
    To Make Sure We Are Properly Sorting Logs In The Order Expected

"""
@pytest.mark.unit
def test_settings_window_refresh(settings_window, tmp_log_dir, monkeypatch):
    """Test that log files are properly sorted by timestamp when refreshed"""
    
    # Create 10 Log Files with randomized timestamps
    timestamps = list(range(10))
    random.shuffle(timestamps)  # Randomize order
    
    log_files = []
    for idx, offset in enumerate(timestamps):
        log_file = tmp_log_dir / f"test_log_{idx}.log"
        log_file.write_text(f"Test Log File {idx}")
        
        # Set modification time - create files with different timestamps
        timestamp = time.time() - (offset * 3600.0)  # Hours apart
        os.utime(log_file, (timestamp, timestamp))
        
        log_files.append((log_file, timestamp))
    
    # Verify files are not already sorted by timestamp
    sorted_files = sorted(log_files, key=lambda x: x[1], reverse=True)
    unsorted = False
    for i in range(len(log_files)):
        if log_files[i][0] != sorted_files[i][0]:
            unsorted = True
            break
            
    assert unsorted, "Test files should not be in sorted order initially"
    
    # Monkey patch the settings window to use our temp directory
    monkeypatch.setattr(settings_window, "logs_dir", tmp_log_dir)
    
    # Call refresh_logs_list to load and sort the logs
    settings_window.refresh_logs_list()
    
    # Verify the correct number of logs were loaded
    assert settings_window.logs_list.count() == 10, "Should load all 10 log files"
    
    # Verify logs are now sorted by timestamp (newest first)
    for i in range(settings_window.logs_list.count() - 1):
        current_item = settings_window.logs_list.item(i)
        next_item = settings_window.logs_list.item(i + 1)
        
        current_path = Path(current_item.data(Qt.UserRole))
        next_path = Path(next_item.data(Qt.UserRole))
        
        # Current item should have newer timestamp than next item
        assert current_path.stat().st_mtime >= next_path.stat().st_mtime, \
            f"Log at position {i} should be newer than log at position {i+1}"


"""

    Desc: Test For When No Logs Directory Exists Or No Logs Are Present

"""
@pytest.mark.unit
def test_refresh_logs_nonexistent_dir(settings_window, monkeypatch):
    """Test refresh_logs_list when logs directory doesn't exist"""
    # Create a mock directory that doesn't exist
    nonexistent_dir = Path("/nonexistent/directory")
    monkeypatch.setattr(settings_window, "logs_dir", nonexistent_dir)
    
    # Verify the logs list is empty before refresh
    settings_window.logs_list.clear()
    assert settings_window.logs_list.count() == 0
    
    # Call refresh_logs_list
    settings_window.refresh_logs_list()
    
    # Verify the logs list is still empty
    assert settings_window.logs_list.count() == 0


"""

    Desc: Test That Makes Sure Our Settings Window Is Properly Saving
    Away The Config Settings Specified By A User Into The .yaml Config File

"""
@pytest.mark.unit
def test_save_settings(settings_window, tmp_path, monkeypatch):
    """Test saving settings to a file"""
    # Create a temporary config path
    temp_config_path = tmp_path / "temp_config.yaml"
    
    # Set the config path to our temp file
    settings_window.config_path = temp_config_path
    
    # Make changes to settings
    original_width = settings_window.width.value()
    settings_window.width.setValue(original_width + 100)
    
    # Mock QMessageBox to avoid popup
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.information', lambda *args, **kwargs: None)
    
    # Save settings (silent=False to ensure full flow is tested)
    settings_window.save_settings(silent=False)
    
    # Verify the file was created
    assert temp_config_path.exists()
    
    # Load and verify saved content
    with open(temp_config_path, 'r') as f:
        saved_config = yaml.safe_load(f)
    
    assert saved_config['preprocessing']['min_resolution'][0] == original_width + 100


"""

    Desc: Test For Checking The Error Handling In save_settings Function

"""
@pytest.mark.unit
def test_save_settings_error_handling(settings_window, monkeypatch):
    """Test error handling in save_settings function"""
    # Set up mock to raise an exception when writing to file
    def mock_open_that_raises(*args, **kwargs):
        if args[1] == 'w':  # Only raise when writing
            raise IOError("Failed to write to file")
        return mock_open()(args, kwargs)
    
    monkeypatch.setattr('builtins.open', mock_open_that_raises)
    
    # Mock QMessageBox to capture the error message
    critical_mock = MagicMock()
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.critical', critical_mock)
    
    # Call save_settings
    settings_window.save_settings(silent=False)
    
    # Verify error message was displayed
    critical_mock.assert_called_once()
    assert "Failed to save settings" in critical_mock.call_args[0][2]


"""

    Desc: Test For Checking If User Is Able To Alter The Supported Image Format
    List Through The UI. It Ensures We Can Add And Remove The Provided Formats
    With Our Add/Remove Buttons.

"""
@pytest.mark.unit
def test_format_list_interactions(settings_window, qtbot, monkeypatch):
    """Test adding and removing formats from the supported formats list"""
    # Find the right buttons
    add_btn = None
    remove_btn = None
    
    # Find buttons by searching through children
    for child in settings_window.children():
        if isinstance(child, QPushButton):
            if child.text() == "Add":
                add_btn = child
            elif child.text() == "Remove":
                remove_btn = child
    
    # Make sure we found the buttons
    if not add_btn:
        # Look for the add format button using layout hierarchy
        for child in settings_window.findChildren(QPushButton):
            if "Add" in child.text():
                add_btn = child
                break
    
    if not remove_btn:
        # Look for the remove format button using layout hierarchy
        for child in settings_window.findChildren(QPushButton):
            if "Remove" in child.text():
                remove_btn = child
                break
    
    assert add_btn, "Could not find Add Format button"
    assert remove_btn, "Could not find Remove Format button"
    
    # Get initial count
    initial_count = settings_window.formats_list.count()
    
    # Mock QInputDialog.getText
    monkeypatch.setattr('PyQt5.QtWidgets.QInputDialog.getText', 
                      lambda *args, **kwargs: (".xyz", True))
    
    # Click add format button
    qtbot.mouseClick(add_btn, Qt.LeftButton)
    
    # Verify format was added
    assert settings_window.formats_list.count() == initial_count + 1
    
    # Select the last item (the one we just added)
    settings_window.formats_list.setCurrentRow(settings_window.formats_list.count() - 1)
    
    # Click remove format button
    qtbot.mouseClick(remove_btn, Qt.LeftButton)
    
    # Verify format was removed
    assert settings_window.formats_list.count() == initial_count


"""

    Desc: Test Cancellation In Format Add Dialog

"""
@pytest.mark.unit
def test_add_format_cancel(settings_window, qtbot, monkeypatch):
    """Test cancellation when adding format"""
    # Get initial count
    initial_count = settings_window.formats_list.count()
    
    # Mock QInputDialog.getText to return cancel
    monkeypatch.setattr('PyQt5.QtWidgets.QInputDialog.getText', 
                      lambda *args, **kwargs: ("", False))
    
    # Call add_format directly
    settings_window.add_format()
    
    # Verify no format was added
    assert settings_window.formats_list.count() == initial_count


"""

    Desc: Test Remove Format With No Selection

"""
@pytest.mark.unit
def test_remove_format_no_selection(settings_window, qtbot):
    """Test removing format when nothing is selected"""
    # Get initial count
    initial_count = settings_window.formats_list.count()
    
    # Ensure nothing is selected
    settings_window.formats_list.clearSelection()
    
    # Call remove_format
    settings_window.remove_format()
    
    # Verify count hasn't changed
    assert settings_window.formats_list.count() == initial_count


"""

    Desc: Ensure Our Settings Window Is Able To Properly Cycle Through
    A Range Of Valid Values For The Resolution Spinbox. It Will 
    Adjust And Check If Adjustment Happend As Expected And Isn't
    Exceeding The Min/Max Values.

"""
@pytest.mark.unit
def test_spinbox_validation(settings_window, qtbot):
    """Test spinbox input validation"""
    # Test min resolution validation
    original_width = settings_window.width.value()
    
    # Set an invalid value (should be constrained by spinbox min/max)
    settings_window.width.setValue(-100)
    
    # Value should be constrained to minimum allowed
    assert settings_window.width.value() >= 0
    
    # Restore original value
    settings_window.width.setValue(original_width)


"""

    Desc: Test That Ensures That Swapping Tabs Doesn't Reset The Values
    Specified By The User In The Settings Window. It Will Adjust The
    Preprocessing Tab Resolution Spinbox Then Go Back To The Point Cloud
    Tab And Check If The Value Is Still The Same When Going Back To
    Preprocessing Tab.

"""
@pytest.mark.unit
def test_tab_switching_preserves_data(settings_window, qtbot):
    """Test that switching between tabs preserves data"""
    # Find the tab widget
    tab_widget = None
    for child in settings_window.children():
        if isinstance(child, QTabWidget):
            tab_widget = child
            break
    
    assert tab_widget, "Could not find TabWidget in settings window"
    
    # Make changes in first tab (Preprocessing)
    original_width = settings_window.width.value()
    new_value = original_width + 100
    settings_window.width.setValue(new_value)
    
    # Switch to another tab (Point Cloud)
    tab_widget.setCurrentIndex(1)
    
    # Switch back to first tab
    tab_widget.setCurrentIndex(0)
    
    # Verify value was preserved
    assert settings_window.width.value() == new_value


"""

    Desc: Test That Reset Settings Properly Reloads The Default Configuration 
    And Reinitializes The Window

"""
@pytest.mark.unit
def test_reset_settings(settings_window, qtbot, monkeypatch):
    """Test resetting settings to defaults"""
    # Find reset button
    reset_btn = None
    for child in settings_window.findChildren(QPushButton):
        if "Reset" in child.text():
            reset_btn = child
            break
    
    assert reset_btn, "Could not find Reset Settings button"
    
    # Store original width value
    original_width = settings_window.width.value()
    
    # Change width to a different value
    settings_window.width.setValue(original_width + 200)
    
    # Mock QMessageBox.information to avoid popup
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.information', 
                      lambda *args, **kwargs: None)
    
    # Mock open to handle different file opens
    mock_default_config = yaml.safe_dump({
        'preprocessing': {'min_resolution': [800, 600], 'supported_formats': ['.jpg'], 
                         'blur_threshold': 50, 'brightness_range': [30, 210], 'max_workers': 2},
        'point_cloud': {'webodm': {'host': 'test', 'port': 1234, 'environments': {'sunny': {}, 'rainy': {}, 'foggy': {}, 'night': {}}}},
        'geospatial': {'output_path': '/test', 'gap_detection': {'min_tree_height': 3.0, 'max_tree_height': 0.5},
                      'analysis': {'terrain': {'slope_threshold': 20.0, 'roughness_threshold': 0.3}},
                      'output': {'formats': ['.test'], 'resolution': 0.2}}
    })
    
    # Mock the file operations
    mock_file = mock_open(read_data=mock_default_config)
    monkeypatch.setattr('builtins.open', mock_file)
    
    # Mock __init__ to avoid actual reinitialization
    original_init = SettingsWindow.__init__
    init_mock = MagicMock()
    monkeypatch.setattr('ResilientGeoDrone.src.front_end.settings_window.SettingsWindow.__init__', init_mock)
    
    # Click reset button
    qtbot.mouseClick(reset_btn, Qt.LeftButton)
    
    # Verify __init__ was called with config_path
    init_mock.assert_called_once_with(settings_window.config_path)
    
    # Restore original __init__
    monkeypatch.setattr('ResilientGeoDrone.src.front_end.settings_window.SettingsWindow.__init__', original_init)


"""

    Desc: Test Error Handling During Reset Settings

"""
@pytest.mark.unit
def test_reset_settings_error(settings_window, qtbot, monkeypatch):
    """Test error handling when resetting settings"""
    # Find reset button
    reset_btn = None
    for child in settings_window.findChildren(QPushButton):
        if "Reset" in child.text():
            reset_btn = child
            break
    
    assert reset_btn, "Could not find Reset Settings button"
    
    # Mock open to raise an exception
    monkeypatch.setattr('builtins.open', MagicMock(side_effect=Exception("Failed to open default config")))
    
    # Mock QMessageBox.critical to capture error message
    critical_mock = MagicMock()
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.critical', critical_mock)
    
    # Click reset button
    qtbot.mouseClick(reset_btn, Qt.LeftButton)
    
    # Verify error message was displayed
    critical_mock.assert_called_once()
    assert "Failed to reset settings" in critical_mock.call_args[0][2]


"""

    Desc: Test Point Cloud Tab WebODM Setting Initialization

"""
@pytest.mark.unit
def test_point_cloud_tab_webodm_settings(settings_window, qtbot):
    """Test point cloud tab WebODM settings initialization"""
    # Find the tab widget
    tab_widget = None
    for child in settings_window.children():
        if isinstance(child, QTabWidget):
            tab_widget = child
            break
    
    assert tab_widget, "Could not find TabWidget in settings window"
    
    # Switch to Point Cloud tab
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i) == "Point Cloud":
            tab_widget.setCurrentIndex(i)
            break
    
    # Verify WebODM connection settings
    assert hasattr(settings_window, 'host')
    assert settings_window.host.text() == settings_window.config['point_cloud']['webodm']['host']
    
    assert hasattr(settings_window, 'port')
    assert settings_window.port.value() == settings_window.config['point_cloud']['webodm']['port']
    
    assert hasattr(settings_window, 'username')
    assert settings_window.username.text() == settings_window.config['point_cloud']['webodm']['username']
    
    assert hasattr(settings_window, 'password')
    assert settings_window.password.text() == settings_window.config['point_cloud']['webodm']['password']
    
    assert hasattr(settings_window, 'timeout')
    assert settings_window.timeout.value() == settings_window.config['point_cloud']['webodm']['timeout']


"""

    Desc: Test Point Cloud Environment Settings For All Weather Conditions

"""
@pytest.mark.unit
def test_point_cloud_environment_settings(settings_window, qtbot):
    """Test environment-specific settings in point cloud tab"""
    # Find the tab widget and switch to Point Cloud tab
    tab_widget = None
    for child in settings_window.children():
        if isinstance(child, QTabWidget):
            tab_widget = child
            break
    
    assert tab_widget, "Could not find TabWidget in settings window"
    
    # Switch to Point Cloud tab
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i) == "Point Cloud":
            tab_widget.setCurrentIndex(i)
            break
    
    # Find the environment tabs
    env_tabs = settings_window.env_tabs
    assert env_tabs, "Could not find environment tabs"
    
    # Test each environment tab
    for env_idx in range(env_tabs.count()):
        # Get environment name from tab text
        env_name = env_tabs.tabText(env_idx).lower()
        env_tabs.setCurrentIndex(env_idx)
        
        # Verify environment widgets exist
        assert env_name in settings_window.env_widgets
        
        # Get environment config
        env_config = settings_window.config['point_cloud']['webodm']['environments'][env_name]
        
        # Test a checkbox option
        if '3d-tiles' in settings_window.env_widgets[env_name]:
            checkbox = settings_window.env_widgets[env_name]['3d-tiles']
            assert isinstance(checkbox, QCheckBox)
            assert checkbox.isChecked() == env_config['3d-tiles']
        
        # Test a float option
        if 'dem-resolution' in settings_window.env_widgets[env_name]:
            spinbox = settings_window.env_widgets[env_name]['dem-resolution']
            assert isinstance(spinbox, QDoubleSpinBox)
            assert spinbox.value() == env_config['dem-resolution']
        
        # Test an int option
        if 'min-num-features' in settings_window.env_widgets[env_name]:
            spinbox = settings_window.env_widgets[env_name]['min-num-features']
            assert isinstance(spinbox, QSpinBox)
            assert spinbox.value() == env_config['min-num-features']
        
        # Test a dropdown option
        if 'feature-quality' in settings_window.env_widgets[env_name]:
            dropdown = settings_window.env_widgets[env_name]['feature-quality']
            assert isinstance(dropdown, QComboBox)
            assert dropdown.currentText() == env_config['feature-quality']
        
        # Test a string option
        if 'primary-band' in settings_window.env_widgets[env_name]:
            textfield = settings_window.env_widgets[env_name]['primary-band']
            assert isinstance(textfield, QLineEdit)
            assert textfield.text() == env_config['primary-band']


"""

    Desc: Test Browse File Dialog In Environment Settings

"""
@pytest.mark.unit
def test_env_browse_file_dialog(settings_window, qtbot, monkeypatch):
    """Test browse file dialog in environment settings"""
    # Setup point cloud tab
    tab_widget = None
    for child in settings_window.children():
        if isinstance(child, QTabWidget):
            tab_widget = child
            break
    
    # Switch to Point Cloud tab
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i) == "Point Cloud":
            tab_widget.setCurrentIndex(i)
            break
    
    # Get the environment tabs
    env_tabs = settings_window.env_tabs
    env_tabs.setCurrentIndex(0)  # Select the first environment
    
    # Find the boundary browse button
    env_name = env_tabs.tabText(0).lower()
    
    # Find all browse buttons
    browse_btns = []
    for child in settings_window.findChildren(QPushButton):
        if child.text() == "Browse...":
            browse_btns.append(child)
    
    assert len(browse_btns) > 0, "Could not find any Browse buttons"
    
    # Mock QFileDialog.getOpenFileName
    test_path = "/test/boundary.json"
    monkeypatch.setattr('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                      lambda *args, **kwargs: (test_path, "JSON Files (*.json)"))
    
    # Click the first browse button
    qtbot.mouseClick(browse_btns[0], Qt.LeftButton)
    
    # Mock QFileDialog.getOpenFileName to return empty value (cancel case)
    monkeypatch.setattr('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                      lambda *args, **kwargs: ("", "JSON Files (*.json)"))
    
    # Click the same browse button again
    qtbot.mouseClick(browse_btns[0], Qt.LeftButton)


"""

    Desc: Test Delete All Logs Functionality And UI Interaction

"""
@pytest.mark.unit
def test_delete_all_logs(settings_window, tmp_log_dir, monkeypatch, qtbot):
    """Test deleting all logs"""
    # Find delete button
    delete_btn = None
    for child in settings_window.findChildren(QPushButton):
        if "Delete All Logs" in child.text():
            delete_btn = child
            break
    
    assert delete_btn, "Could not find Delete All Logs button"
    
    # Create test log files
    for i in range(5):
        log_file = tmp_log_dir / f"test_log_{i}.log"
        log_file.write_text(f"Test log content {i}")
    
    # Check files were created
    assert len(list(tmp_log_dir.glob("*.log"))) == 5
    
    # Patch logs directory
    monkeypatch.setattr(settings_window, "logs_dir", tmp_log_dir)
    settings_window.refresh_logs_list()
    
    # Mock confirmation dialog to return "Yes"
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.question',
                      lambda *args, **kwargs: QMessageBox.Yes)
    
    # Mock success message
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.information',
                      lambda *args, **kwargs: None)
    
    # Click delete button
    qtbot.mouseClick(delete_btn, Qt.LeftButton)
    
    # Verify all logs were deleted
    assert settings_window.logs_list.count() == 0
    assert list(tmp_log_dir.glob("*.log")) == []


"""

    Desc: Test Delete All Logs When User Cancels Confirmation Dialog

"""
@pytest.mark.unit
def test_delete_all_logs_cancel(settings_window, tmp_log_dir, monkeypatch, qtbot):
    """Test cancellation when deleting all logs"""
    # Find delete button
    delete_btn = None
    for child in settings_window.findChildren(QPushButton):
        if "Delete All Logs" in child.text():
            delete_btn = child
            break
    
    assert delete_btn, "Could not find Delete All Logs button"
    
    # Create test log files
    for i in range(3):
        log_file = tmp_log_dir / f"test_log_{i}.log"
        log_file.write_text(f"Test log content {i}")
    
    # Patch logs directory
    monkeypatch.setattr(settings_window, "logs_dir", tmp_log_dir)
    settings_window.refresh_logs_list()
    
    # Mock confirmation dialog to return "No"
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.question',
                      lambda *args, **kwargs: QMessageBox.No)
    
    # Click delete button
    qtbot.mouseClick(delete_btn, Qt.LeftButton)
    
    # Verify logs were not deleted
    assert settings_window.logs_list.count() == 3
    assert len(list(tmp_log_dir.glob("*.log"))) == 3


"""

    Desc: Test Delete All Logs Error Handling

"""
@pytest.mark.unit
def test_delete_all_logs_error(settings_window, tmp_log_dir, monkeypatch, qtbot):
    """Test error handling when deleting all logs"""
    # Find delete button
    delete_btn = None
    for child in settings_window.findChildren(QPushButton):
        if "Delete All Logs" in child.text():
            delete_btn = child
            break
    
    assert delete_btn, "Could not find Delete All Logs button"
    
    # Create test log files
    for i in range(2):
        log_file = tmp_log_dir / f"test_log_{i}.log"
        log_file.write_text(f"Test log content {i}")
    
    # Patch logs directory
    monkeypatch.setattr(settings_window, "logs_dir", tmp_log_dir)
    
    # Mock Path.unlink to raise an exception
    monkeypatch.setattr(Path, 'unlink', MagicMock(side_effect=PermissionError("Permission denied")))
    
    # Mock QMessageBox for confirmation and error messages
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.question',
                      lambda *args, **kwargs: QMessageBox.Yes)
    
    critical_mock = MagicMock()
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.critical', critical_mock)
    
    # Refresh the logs list
    settings_window.refresh_logs_list()
    
    # Click delete button
    qtbot.mouseClick(delete_btn, Qt.LeftButton)
    
    # Verify error message was displayed
    critical_mock.assert_called_once()
    assert "Failed To Delete Log Files" in critical_mock.call_args[0][2]


"""

    Desc: Test Log Content Display

"""
@pytest.mark.unit
def test_display_log_content(settings_window, tmp_log_dir, monkeypatch):
    """Test displaying log content"""
    # Create a test log file
    log_file = tmp_log_dir / "test_log.log"
    log_content = "Test log content\nLine 2\nLine 3"
    log_file.write_text(log_content)
    
    # Patch logs directory
    monkeypatch.setattr(settings_window, "logs_dir", tmp_log_dir)
    settings_window.refresh_logs_list()
    
    # Verify log file was added to list
    assert settings_window.logs_list.count() == 1
    
    # Select the log file
    settings_window.logs_list.setCurrentRow(0)
    
    # Call display_log_content directly
    settings_window.display_log_content()
    
    # Verify content was displayed
    assert settings_window.log_content.toPlainText() == log_content
    
    # Test when no log is selected
    settings_window.logs_list.clearSelection()
    settings_window.log_content.setText("Previous content")
    settings_window.display_log_content()
    
    # Verify content was cleared
    assert settings_window.log_content.toPlainText() == ""


"""

    Desc: Test Log Content Display Error Handling

"""
@pytest.mark.unit
def test_display_log_content_error(settings_window, tmp_log_dir, monkeypatch):
    """Test error handling when displaying log content"""
    # Create a test log file
    log_file = tmp_log_dir / "test_log.log"
    log_file.write_text("Test log content")
    
    # Patch logs directory
    monkeypatch.setattr(settings_window, "logs_dir", tmp_log_dir)
    settings_window.refresh_logs_list()
    
    # Select the log file
    settings_window.logs_list.setCurrentRow(0)
    
    # Mock open to raise an exception
    monkeypatch.setattr('builtins.open', MagicMock(side_effect=IOError("Failed to read log file")))
    
    # Call display_log_content
    settings_window.display_log_content()
    
    # Verify error message was displayed
    assert "Error Reading Log File" in settings_window.log_content.toPlainText()


"""

    Desc: Test Browse Output Feature With Selection And Cancellation

"""
@pytest.mark.unit
def test_browse_output_with_cancellation(settings_window, monkeypatch):
    """Test browsing for output path with both selection and cancellation"""
    # Test with path selection
    test_path = "/selected/output/path"
    monkeypatch.setattr('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                      lambda *args, **kwargs: (test_path, ""))
    
    # Set initial path
    initial_path = "/initial/path"
    settings_window.output_path.setText(initial_path)
    
    # Call browse_output
    settings_window.browse_output()
    
    # Verify path was updated
    assert settings_window.output_path.text() == test_path
    
    # Test with cancellation (empty path)
    monkeypatch.setattr('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                      lambda *args, **kwargs: ("", ""))
    
    # Call browse_output again
    settings_window.browse_output()
    
    # Verify path was not changed
    assert settings_window.output_path.text() == test_path


"""

    Desc: Test Geospatial Tab Components

"""
@pytest.mark.unit
def test_geospatial_tab_components(settings_window, qtbot):
    """Test that geospatial tab has all expected components"""
    # Find the tab widget
    tab_widget = None
    for child in settings_window.children():
        if isinstance(child, QTabWidget):
            tab_widget = child
            break
    
    assert tab_widget, "Could not find TabWidget in settings window"
    
    # Find the geospatial tab
    geospatial_tab_index = None
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i) == "Geospatial":
            geospatial_tab_index = i
            break
    
    assert geospatial_tab_index is not None, "Could not find Geospatial tab"
    tab_widget.setCurrentIndex(geospatial_tab_index)
    
    # Verify all required components exist
    assert hasattr(settings_window, "output_path"), "Output path field not found"
    assert hasattr(settings_window, "tree_height"), "Tree height spinbox not found"
    assert hasattr(settings_window, "canopy"), "Canopy threshold spinbox not found"
    assert hasattr(settings_window, "geo_formats_list"), "Output formats list not found"
    assert hasattr(settings_window, "resolution"), "Resolution spinbox not found"
    
    # Verify component types
    assert isinstance(settings_window.output_path, QLineEdit), "Output path field should be QLineEdit"
    assert isinstance(settings_window.tree_height, QDoubleSpinBox), "Tree height should be QDoubleSpinBox"
    assert isinstance(settings_window.canopy, QDoubleSpinBox), "Canopy threshold should be QDoubleSpinBox"
    assert isinstance(settings_window.geo_formats_list, QListWidget), "Output formats should be QListWidget"
    assert isinstance(settings_window.resolution, QDoubleSpinBox), "Resolution should be QDoubleSpinBox"
    
    # Verify browse button exists
    browse_btn = None
    for child in settings_window.findChildren(QPushButton):
        if child.text() == "Browse...":
            browse_btn = child
            break
    
    assert browse_btn is not None, "Browse button not found"
    
    # Verify Group Boxes exist
    groups = settings_window.findChildren(QGroupBox)
    group_titles = [g.title() for g in groups]
    
    assert "Output Settings" in group_titles, "Output Settings group not found"
    assert "Analysis Settings" in group_titles, "Analysis Settings group not found"


"""

    Desc: Test Missing Slope and Roughness in Save Settings For Complete Coverage

"""
@pytest.mark.unit
def test_save_settings_missing_terrain_fields(settings_window, monkeypatch, tmp_path):
    """Test saving settings when slope and roughness aren't defined"""
    # Create a temporary config path
    temp_config_path = tmp_path / "temp_config.yaml"
    settings_window.config_path = temp_config_path
    
    # Remove terrain attributes if they exist
    if hasattr(settings_window, 'slope'):
        delattr(settings_window, 'slope')
    if hasattr(settings_window, 'roughness'):
        delattr(settings_window, 'roughness')
    
    # Mock QMessageBox
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.information', lambda *args, **kwargs: None)
    
    # Call save_settings
    settings_window.save_settings(silent=False)
    
    # Verify file was saved (should work even without slope/roughness)
    assert temp_config_path.exists()
    
    # Load saved config
    with open(temp_config_path, 'r') as f:
        saved_config = yaml.safe_load(f)
        
    # Verify geospatial output path was saved
    assert 'output_path' in saved_config['geospatial']
    assert saved_config['geospatial']['output_path'] == settings_window.output_path.text()
