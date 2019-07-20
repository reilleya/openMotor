import sys
from app import App
from PyQt5.QtCore import Qt

# must be set before the app is constructed
# cf. https://doc.qt.io/qt-5/highdpi.html
# and https://www.riverbankcomputing.com/static/Docs/PyQt5/api/qtcore/qt.html#ApplicationAttribute
App.setAttribute(Qt.AA_EnableHighDpiScaling)

app = App(sys.argv)
sys.exit(app.exec())
