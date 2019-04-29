import yaml
import platform
import os
import appdirs
from enum import Enum

appVersion = (0, 1, 0)
appVersionStr = '.'.join(map(str, appVersion))

class fileTypes(Enum):
    PREFERENCES = 1
    PROPELLANTS = 2
    MOTOR = 3

def futureVersion(a, b): # Returns true if a is newer than b
    return (a[0] > b[0]) or (a[0] == b[0] and a[1] > b[1]) or (a[0] == b[0] and a[1] == b[1] and a[2] > b[2])

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
        else:
            if futureVersion(fileData['version'], appVersion): # If the data is from a future version, it can't be loaded
                new = '.'.join(str(num) for num in fileData['version'])
                old = '.'.join(str(num) for num in appVersion)
                raise ValueError("Data is from a future version (" + new + " vs " + old + ") and can't be loaded.")
            else: # Otherwise it is from a past version and will be migrated
                pass # Migrate file, will be implemented later

def getConfigPath(): # Returns the path that files like preferences and propellant library should be in
    if platform.system() == 'Darwin': # On OSX, the configuration files should live in the library
        path = appdirs.user_data_dir('openMotor', 'openMotor')
        if not os.path.isdir(path): # Create directory if it doesn't exist
            os.mkdir(path)
        return path + '/'
    else: # On other platforms they can live in this directory
        return ''
