from . import units

class property():
    def __init__(self, dispName, unit, valueType):
        self.dispName = dispName
        self.unit = unit
        self.valueType = valueType
        self.value = None

    def setValue(self, value):
        self.value = self.valueType(value)

    def getValue(self):
        return self.value

    def dispFormat(self):
        return str(self.value)

class floatProperty(property):
    def __init__(self, dispName, unit, minValue, maxValue):
        super().__init__(dispName, unit, float)
        self.min = minValue
        self.max = maxValue
        self.value = minValue

    def setValue(self, value):
        if value >= self.min and value <= self.max:
            super().setValue(value)

    def dispFormat(self, unit):
        return str(round(units.convert(self.value, self.unit, unit), 6)) + ' ' + unit

class enumProperty(property):
    def __init__(self, dispName, values):
        super().__init__(dispName, '', object)
        self.values = values
        self.value = self.values[0]

    def contains(self, value):
        return value in self.values

    def setValue(self, value):
        if self.contains(value):
            self.value = value

class intProperty(property):
    def __init__(self, dispName, unit, minValue, maxValue):
        super().__init__(dispName, unit, int)
        self.min = minValue
        self.max = maxValue
        self.value = minValue

    def setValue(self, value):
        if value >= self.min and value <= self.max:
            super().setValue(value)

class stringProperty(property):
    def __init__(self, dispName):
        super().__init__(dispName, '', str)

class polygonProperty(property):
    def __init__(self, dispName):
        super().__init__(dispName, '', list)
        self.value = []

class propertyCollection():
    def __init__(self):
        self.props = {}

    def setProperties(self, props):
        for p in props.keys():
            if p in self.props: # This allows loading settings when the name of a field has changed
                self.props[p].setValue(props[p])

    def getProperties(self, props = None):
        if props is None:
            props = self.props.keys()
        return {k:self.props[k].getValue() for k in props}

    def getProperty(self, prop):
        return self.props[prop].getValue()

    def setProperty(self, prop, value):
        self.props[prop].setValue(value)
