from .endBurner import *
from .bates import *
from .finocyl import *
from .moonBurner import *
from .star import *
from .xCore import *
from .cGrain import *
from .dGrain import *
from .rodTube import *
from .custom import *

# Generate grain geometry name -> constructor lookup table
grainTypes = {}
grainClasses = [BatesGrain, EndBurningGrain, Finocyl, MoonBurner, StarGrain, XCore, CGrain, DGrain, RodTubeGrain,
                CustomGrain]
for grainType in grainClasses:
    grainTypes[grainType.geomName] = grainType
