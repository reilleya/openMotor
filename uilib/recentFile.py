from PyQt5.QtCore import QObject
import os

class RecentFile(QObject):
    def __init__(self, filepath, manager):
        super().__init__()
        self.manager = manager
        tail , self.name = os.path.split(filepath)
        self.filepath = filepath
        
    def open(self):
        self.manager.load(self.filepath)
