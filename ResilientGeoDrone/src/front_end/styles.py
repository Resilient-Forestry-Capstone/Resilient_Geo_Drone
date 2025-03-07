"""

    CSS Style Sheet Which Outlines Our Main Client Window Style
    It Provides A Dark Green And Brown Theme For The Application.

"""

STYLE_SHEET = """
QMainWindow {
    background-color: #1E2F23;
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
"""