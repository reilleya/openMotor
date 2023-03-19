from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QFileDialog, QApplication
from PyQt6.QtCore import pyqtSignal

class Converter(QObject):
    def __init__(self, manager, name, description, fileTypes):
        super().__init__()
        self.manager = manager
        self.name = name
        self.description = description
        self.fileTypes = fileTypes
        self.menu = None

    def getFileTypeString(self):
        return ";;".join([self.fileTypes[key] + " (*" + key + ")" for key in self.fileTypes.keys()])

    def showFileSelector(self):
        pass

    def exec(self):
        pass


class Exporter(Converter):
    def __init__(self, manager, name, description, fileTypes, confirmOverwrite=True):
        super().__init__(manager, name, description, fileTypes)
        self.requirements = []
        self.reqNotMet = "Requirement not met!"
        self.confirmOverwrite = confirmOverwrite

    def showFileSelector(self):
        """Open a dialog to pick the file to save to"""
        title = 'Export {}'.format(self.name)
        types = self.getFileTypeString()
        if not self.confirmOverwrite:
            path = QFileDialog.getSaveFileName(None, title, '', types, options=QFileDialog.DontConfirmOverwrite)[0]
        else:
            path = QFileDialog.getSaveFileName(None, title, '', types)[0]
        if path == '' or path is None:
            return
        if not any([path.endswith(ext) for ext in self.fileTypes.keys()]):
            path += list(self.fileTypes.keys())[0] # if they didn't specify a file type, just pick one
        return path

    def exec(self):
        if self.checkRequirements():
            config = None
            if self.menu is not None:
                config = self.menu.exec()
                if config is None:
                    return
            path = self.showFileSelector()
            if path is None:
                return
            try:
                self.doConversion(path, config)
            except Exception as error:
                QApplication.instance().outputException(error, "Export to '{}' failed:".format(path))
        else:
            self.manager.app.outputMessage(self.reqNotMet)

    def doConversion(self, path, config):
        pass

    def checkRequirements(self):
        for req in self.requirements:
            pass


class Importer(Converter):
    def __init__(self, manager, name, description, fileTypes):
        super().__init__(manager, name, description, fileTypes)

    def showFileSelector(self):
        """Open a dialog to pick the file to load"""
        if self.manager.unsavedCheck():
            path = QFileDialog.getOpenFileName(None, 'Import {}'.format(self.name), '', self.getFileTypeString())[0]
            if path != '':
                return path
        return None

    def doConversion(self, path):
        pass

    def exec(self):
        path = self.showFileSelector()
        if path is None:
            return
        try:
            self.doConversion(path)
        except Exception as error:
            QApplication.instance().outputException(error, "Import of '{}' failed:".format(path))
