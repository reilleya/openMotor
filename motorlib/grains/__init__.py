from .endBurner import *
from .bates import *
from .finocyl import *

# Generate grain geometry name -> constructor lookup table
grainTypes = {}
grainClasses = [batesGrain, endBurningGrain, finocyl]
for grainType in grainClasses:
    grainTypes[grainType.geomName] = grainType
