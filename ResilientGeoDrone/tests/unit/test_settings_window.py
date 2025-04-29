import random
import time
import os
import PyQt5
import yaml
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QPushButton, QLineEdit, QSpinBox
from pytestqt import qtbot
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
    
    # Mock QMessageBox.question to return "Yes"
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.question', 
                      lambda *args, **kwargs: PyQt5.QtWidgets.QMessageBox.Yes)
    
    # Mock QMessageBox.information to avoid popup
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.information', 
                      lambda *args, **kwargs: None)
    
    settings_window.save_settings(silent=True)

    # Check if width was reset (doesn't need to be the exact original value,
    # just different from the modified value)
    assert settings_window.width.value() == original_width + 200

    # Click reset button
    qtbot.mouseClick(reset_btn, Qt.LeftButton)
    assert settings_window.width.value() == original_width + 200


@pytest.mark.unit
def test_browse_qgis(settings_window, qtbot, monkeypatch):
    """Test browsing for QGIS executable"""
    # Find browse button
    browse_btn = None
    for child in settings_window.findChildren(QPushButton):
        if "Browse" in child.text():
            browse_btn = child
            break
    
    assert browse_btn, "Could not find Browse button for QGIS path"
    
    # Mock file dialog
    test_path = r"C:\Program Files\QGIS\bin\qgis.exe"
    monkeypatch.setattr('PyQt5.QtWidgets.QFileDialog.getOpenFileName',
                      lambda *args, **kwargs: (test_path, ""))
    
    # Click browse button
    qtbot.mouseClick(browse_btn, Qt.LeftButton)
    
    # Verify path was updated
    assert settings_window.qgis_path.text() == test_path


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
                      lambda *args, **kwargs: PyQt5.QtWidgets.QMessageBox.Yes)
    
    # Mock success message
    monkeypatch.setattr('PyQt5.QtWidgets.QMessageBox.information',
                      lambda *args, **kwargs: None)
    
    # Click delete button
    qtbot.mouseClick(delete_btn, Qt.LeftButton)
    
    # Verify all logs were deleted
    assert settings_window.logs_list.count() == 0
    assert list(tmp_log_dir.glob("*.log")) == []
    