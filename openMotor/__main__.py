import sys
from openMotor.app import App
from PyQt5.QtCore import Qt

def main():
    app = App(sys.argv)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
