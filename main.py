import sys
from app import App
from PyQt5.QtCore import Qt

# Hide the hi-dpi switch behind a platform check
# Works on Windows, unneccessary on macOS, and breaks GNOME
# cf. https://github.com/reilleya/openMotor/pull/103#issuecomment-513507028
if sys.platform == 'win32':
    # must be set before the app is constructed
    # cf. https://doc.qt.io/qt-5/highdpi.html
    # and https://www.riverbankcomputing.com/static/Docs/PyQt5/api/qtcore/qt.html#ApplicationAttribute
    App.setAttribute(Qt.AA_EnableHighDpiScaling)

app = App(sys.argv)
sys.exit(app.exec())
