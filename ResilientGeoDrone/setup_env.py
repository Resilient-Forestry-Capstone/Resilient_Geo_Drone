import sys
from pathlib import Path
from qgis.core import *
from qgis.gui import *
from PyQt5.QtWidgets import QMainWindow, QApplication

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QGIS Window")
        self.canvas = QgsMapCanvas()
        self.setCentralWidget(self.canvas)
        self.resize(800, 600)

def run_qgis_test():
    # Supply path to QGIS installation
    qgis_path = r"C:\Program Files\QGIS 3.40.1"
    QgsApplication.setPrefixPath(qgis_path, True)

    # Create QgsApplication with GUI
    qgs = QgsApplication([], True)
    qgs.initQgis()

    # Create and show window
    window = MainWindow()
    window.show()

    # Start application event loop
    exitcode = qgs.exec_()

    # Clean up
    qgs.exitQgis()
    return exitcode

if __name__ == "__main__":
    run_qgis_test()