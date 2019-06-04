from enum import Enum
import os
import platform

import yaml
import appdirs

appVersion = (0, 2, 0)
appVersionStr = '.'.join(map(str, appVersion))

class fileTypes(Enum):
    PREFERENCES = 1
    PROPELLANTS = 2
    MOTOR = 3

def futureVersion(verA, verB): # Returns true if a is newer than b
    major = verA[0] > verB[0]
    minor = verA[0] == verB[0] and verA[1] > verB[1]
    fix = verA[0] == verB[0] and verA[1] == verB[1] and verA[2] > verB[2]
    return major or minor or fix

def saveFile(path, data, dataType):
    output = {
                'version': appVersion,
                'type': dataType,
                'data': data
    }

    with open(path, 'w') as saveLocation:
        yaml.dump(output, saveLocation)

def loadFile(path, dataType):
    with open(path, 'r') as readLocation:
        fileData = yaml.load(readLocation)

        if 'data' not in fileData or 'type' not in fileData or 'version' not in fileData:
            raise ValueError('File did not contain the required fields. It may be corrupted or from an old version.')

        if fileData['type'] != dataType:
            raise TypeError('Loaded data type did not match expected type.')

        if fileData['version'] == appVersion: # Check if the file is from the current version
            return fileData['data'] # If so, the data is current and can be returned

        # If the data is from a future version, it can't be loaded
        if futureVersion(fileData['version'], appVersion):
            new = '.'.join(str(num) for num in fileData['version'])
            old = '.'.join(str(num) for num in appVersion)
            raise ValueError("Data is from a future version (" + new + " vs " + old + ") and can't be loaded.")

        # Otherwise it is from a past version and will be migrated
        return fileData['data'] # Migrate file, will be implemented later when an incompatible version is made

def getConfigPath(): # Returns the path that files like preferences and propellant library should be in
    if platform.system() == 'Darwin': # On OSX, the configuration files should live in the library
        path = appdirs.user_data_dir('openMotor', 'openMotor')
        if not os.path.isdir(path): # Create directory if it doesn't exist
            os.mkdir(path)
        return path + '/'
    # On other platforms they can live in this directory
    return ''
