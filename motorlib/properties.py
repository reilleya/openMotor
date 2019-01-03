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
        if value > self.min and value < self.max:
            super().setValue(value)

    def dispFormat(self, unit):
        return str(round(units.convert(self.value, self.unit, unit), 3)) + ' ' + unit

class intProperty(property):
    def __init__(self, dispName, unit, minValue, maxValue):
        super().__init__(dispName, unit, int)
        self.min = minValue
        self.max = maxValue
        self.value = minValue

    def setValue(self, value):
        if value >= self.min and value <= self.max:
            super().setValue(value)

class propellantProperty(property):
    def __init__(self, dispName):
        super().__init__(dispName, '', dict)
        #self.proplist = proplist
        self.value = {'name': None, 'density': None, 'a': None, 'n': None, 'k': None, 't': None, 'm':None}

    def setValue(self, value):
        #TODO: check for proper properties
        self.value = value

class propertyCollection():
    def __init__(self):
        self.props = {}

    def setProperties(self, props):
        for p in props.keys():
            self.props[p].setValue(props[p])

    def getProperties(self, props = None):
        if props is None:
            props = self.props.keys()
        return {k:self.props[k].getValue() for k in props}