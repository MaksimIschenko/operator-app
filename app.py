from PySide6.QtWidgets import QApplication
from src.utils.webengine import WebEngineMap
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WebEngineMap()
    window.show()
    app.exec()
    