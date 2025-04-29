"""

    CSS Style Sheet Which Outlines Our Main Client Window Style
    It Provides A Dark Green And Brown Theme For The Application.

"""

STYLE_SHEET = """
QMainWindow {
    background-color: #1E2F23;
}

/* Results Viewer Styles */
QLabel#sectionHeader {
    font-size: 20px;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 10px;
}

QLabel#sectionDescription {
    font-size: 14px;
    color: #7f8c8d;
    margin-bottom: 15px;
}

QLabel#fileInfoHeader {
    font-size: 15px;
    font-weight: bold;
    color: #2c3e50;
    padding: 5px 0;
    border-bottom: 1px solid #bdc3c7;
}

QWidget#resultsViewer QGroupBox {
    font-weight: bold;
    padding-top: 15px;
}

QWidget#resultsViewer QListWidget {
    background-color: #f8f9fa;
    border-radius: 5px;
    border: 1px solid #dfe4ea;
    padding: 5px;
}

QWidget#resultsViewer QListWidget::item {
    padding: 6px;
    border-bottom: 1px solid #ecf0f1;
}

QWidget#resultsViewer QListWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QWidget#resultsViewer QScrollArea {
    background-color: #f8f9fa;
    border-radius: 5px;
    border: 1px solid #dfe4ea;
}

QWidget#resultsViewer QPushButton {
    background-color: #3498db;
    color: white;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}

QWidget#resultsViewer QPushButton:hover {
    background-color: #2980b9;
}

QWidget#resultsViewer QPushButton:disabled {
    background-color: #bdc3c7;
}

QWidget#resultsViewer QComboBox {
    padding: 5px;
    border-radius: 4px;
    border: 1px solid #bdc3c7;
}

QLabel#title {
    color: #D4C5B9;
    font-size: 24px;
    font-weight: bold;
    margin: 20px;
}

QFrame#dragdrop {
    background-color: #2A3F2F;
    border: 2px dashed #8B7355;
    border-radius: 10px;
    min-height: 200px;
    padding: 20px;
}

QFrame#dragdrop QLabel {
    color: #D4C5B9;
    font-size: 16px;
}

QPushButton#settingsButton {
    background-color: #4A5D4A;
    color: #D4C5B9;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 14px;
}

QPushButton#settingsButton:hover {
    background-color: #5A6D5A;

}

QPushButton#viewResultsButton {
    background-color: #4A5D4A;
    color: #D4C5B9;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 14px;
}

QPushButton#viewResultsButton:hover {
    background-color: #5A6D5A;

}

QPushButton#launchButton {
    background-color: #4A5D4A;
    color: #D4C5B9;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 14px;
}

QPushButton#launchButton:hover {
    background-color: #5A6D5A;
}

QTabWidget {
    background-color: #2A3F2F;
}

QTabWidget::pane {
    border: 1px solid #8B7355;
    border-radius: 5px;
}

QTabBar::tab {
    background-color: #4A5D4A;
    color: #D4C5B9;
    padding: 8px 20px;
    margin: 2px;
}

QTabBar::tab:selected {
    background-color: #5A6D5A;
}
/* Progress Widget Styles */
QFrame#progressFrame {
    background-color: #2A3F2F;
    border: 1px solid #8B7355;
    border-radius: 8px;
    padding: 20px;
    margin: 0px;
}

QLabel#progressTitle {
    color: #D4C5B9;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 15px;
}

QLabel#statusLabel {
    color: #D4C5B9;
    font-size: 16px;
    font-weight: bold;
    margin: 5px 0;
}

QLabel#detailLabel {
    color: #B5A696;
    font-size: 14px;
    margin-bottom: 10px;
}

QProgressBar {
    background-color: #1A2F1F;
    border: 1px solid #8B7355;
    border-radius: 5px;
    color: #D4C5B9;
    height: 25px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #6B8E23;
    border-radius: 4px;
}

QPushButton#cancelButton {
    background-color: #8B5A55;
    color: #D4C5B9;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-size: 14px;
}

QPushButton#cancelButton:hover {
    background-color: #9B6A65;
}

/* Results Dialog Styles */
QDialog#resultDialog {
    background-color: #2A3F2F;
}

QFrame#resultFrame {
    background-color: #2A3F2F;
    border: 1px solid #8B7355;
    border-radius: 8px;
    padding: 20px;
}

QLabel#resultStatusSuccess {
    color: #7FCA9F;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
}

QLabel#resultStatusError {
    color: #FF6B6B;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
}

QLabel#resultMessage {
    color: #D4C5B9;
    font-size: 16px;
    margin: 10px 0;
}

QTextEdit#resultDetails {
    background-color: #1A2F1F;
    color: #B5A696;
    border: 1px solid #8B7355;
    border-radius: 5px;
    padding: 10px;
    font-family: monospace;
}

QPushButton#closeButton {
    background-color: #4A5D4A;
    color: #D4C5B9;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-size: 14px;
}

QPushButton#closeButton:hover {
    background-color: #5A6D5A;
}


QGroupBox#taskFoldersGroup {
    font-weight: bold;
    font-size: 12px;
    padding-top: 12px;
}

QGroupBox#availableFilesGroup {
    font-weight: bold;
    font-size: 12px;
    padding-top: 12px;
}


QWidget#resultsViewer QListWidget::item {
    padding: 4px;
    border-bottom: 1px solid #ecf0f1;
    font-size: 11px;
}



"""