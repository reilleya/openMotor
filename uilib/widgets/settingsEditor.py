from .collectionEditor import CollectionEditor

class SettingsEditor(CollectionEditor):
    def __init__(self, parent):
        super().__init__(parent, False)
