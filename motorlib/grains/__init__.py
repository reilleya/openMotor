from .endBurner import *
from .bates import *
from .finocyl import *
from .moonBurner import *
from .star import *
from .xCore import *
from .cGrain import *
from .dGrain import *

# Generate grain geometry name -> constructor lookup table
grainTypes = {}
grainClasses = [batesGrain, endBurningGrain, finocyl, moonBurner, starGrain, xCore, cGrain, dGrain]
for grainType in grainClasses:
    grainTypes[grainType.geomName] = grainType
