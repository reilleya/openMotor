from motorlib.propellant import Propellant
from .collectionEditor import CollectionEditor
from .propellantPreviewWidget import PropellantPreviewWidget

class PropellantEditor(CollectionEditor):
    def __init__(self, parent):
        super().__init__(parent, False)

        self.propellantPreview = PropellantPreviewWidget()
        self.propellantPreview.hide()
        self.stats.addWidget(self.propellantPreview)

    def cleanup(self):
        self.propellantPreview.hide()
        super().cleanup()

    def setPreferences(self, pref):
        super().setPreferences(pref)
        self.propellantPreview.setPreferences(self.preferences)

    def propertyUpdate(self):
        previewProp = Propellant(self.getProperties())
        self.propellantPreview.loadPropellant(previewProp)

    def loadProperties(self, obj):
        super().loadProperties(obj)
        self.propellantPreview.show()
