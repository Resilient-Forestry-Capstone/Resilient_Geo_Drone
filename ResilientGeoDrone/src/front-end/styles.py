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
"""