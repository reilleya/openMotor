"""This module includes a properties, which are objects that contain different datatypes and enforce conditions on
them, such as allowed ranges. They also can optionally associate a unit with the value, which aids with display and
conversion of the value."""

from . import units

class Property():
    """The base class that properties inherit from. It associates a human-readable display name with the data, as well
    as a unit and value type that it casts all inputs to."""
    def __init__(self, dispName, unit, valueType):
        self.dispName = dispName
        self.unit = unit
        self.valueType = valueType
        self.value = None

    def setValue(self, value):
        """Set the value of the property, casting if necessary"""
        self.value = self.valueType(value)

    def getValue(self):
        """Returns the value of the property"""
        return self.value

    def dispFormat(self, unit):
        """Returns a human-readable version of the property's current value, including the unit."""
        return '{} {}'.format(self.value, unit)


class FloatProperty(Property):
    """A property that handles floats. It forces the value to be in a certain range."""
    def __init__(self, dispName, unit, minValue, maxValue):
        super().__init__(dispName, unit, float)
        self.min = minValue
        self.max = maxValue
        self.value = minValue

    def setValue(self, value):
        if self.min <= value <= self.max:
            super().setValue(value)

    def dispFormat(self, unit):
        return '{:.6g} {}'.format(units.convert(self.value, self.unit, unit), unit)


class EnumProperty(Property):
    """This property operates on strings, but only allows values from a list that is set when the property is
    defined"""
    def __init__(self, dispName, values):
        super().__init__(dispName, '', object)
        self.values = values
        self.value = self.values[0]

    def contains(self, value):
        """Checks if a value is in the allowed list"""
        return value in self.values

    def setValue(self, value):
        if self.contains(value):
            self.value = value


class IntProperty(Property):
    """A property with an integer as the value that is clamped to a certain range."""
    def __init__(self, dispName, unit, minValue, maxValue):
        super().__init__(dispName, unit, int)
        self.min = minValue
        self.max = maxValue
        self.value = minValue

    def setValue(self, value):
        if self.min <= value <= self.max:
            super().setValue(value)


class StringProperty(Property):
    """A property that works on the set of all strings"""
    def __init__(self, dispName):
        super().__init__(dispName, '', str)


class PolygonProperty(Property):
    """A property that contains a list of polygons, each a list of points"""
    def __init__(self, dispName):
        super().__init__(dispName, '', list)
        self.value = []


class TabularProperty(Property):
    """A property that is composed of a number of 'tabs', each of which is a property collection of its own."""
    def __init__(self, dispName, collection):
        super().__init__(dispName, '', list)
        self.collection = collection
        self.tabs = []

    def addTab(self, tab):
        """Add a tab to the property's list of tabs."""
        self.tabs.append(tab)

    def getValue(self):
        return [tab.getProperties() for tab in self.tabs]

    def setValue(self, value):
        self.tabs = [self.collection(data) for data in value]


class PropertyCollection():
    """Holds a set of properties and allows batch operations on them through dictionaries"""
    def __init__(self):
        self.props = {}

    def setProperties(self, props):
        """Sets the value(s) of one of more properties at a time by passing in a dictionary of property names and
        values"""
        for prop in props.keys():
            if prop in self.props: # This allows loading settings when the name of a field has changed
                self.props[prop].setValue(props[prop])

    def getProperties(self, props=None):
        """Get a dictionary of property names and values. The optional argument is a list of which properties are
        being requested. It defaults to None, which returns all properties."""
        if props is None:
            props = self.props.keys()
        return {k:self.props[k].getValue() for k in props}

    def getProperty(self, prop):
        """Returns the value of a specific property."""
        return self.props[prop].getValue()

    def setProperty(self, prop, value):
        """Set the value of a specific property"""
        self.props[prop].setValue(value)
