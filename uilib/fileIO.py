from enum import Enum
import os
import platform

from PyQt5.QtWidgets import QApplication
import yaml
import appdirs

from .defaults import defaultPreferencesDict, defaultPropellants

appVersion = (0, 5, 0)
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
        return doMigration(fileData)['data']

def getConfigPath(): # Returns the path that files like preferences and propellant library should be in
    if platform.system() == 'Darwin': # On OSX, the configuration files should live in the library
        path = appdirs.user_data_dir('openMotor', 'openMotor')
        if not os.path.isdir(path): # Create directory if it doesn't exist
            os.mkdir(path)
        return path + '/'
    # On other platforms they can live in this directory
    return ''

def passthrough(data):
    return data

def tabularizePropellant(data):
    newProp = {}
    newProp['name'] = data['name']
    newProp['density'] = data['density']
    newProp['tabs'] = [{}]
    newProp['tabs'][-1]['a'] = data['a']
    newProp['tabs'][-1]['n'] = data['n']
    newProp['tabs'][-1]['k'] = data['k']
    newProp['tabs'][-1]['t'] = data['t']
    newProp['tabs'][-1]['m'] = data['m']
    newProp['tabs'][-1]['minPressure'] = 0
    newProp['tabs'][-1]['maxPressure'] = 1.0342e+7
    return newProp

def migratePref_0_3_0_to_0_4_0(data):
    data['general']['igniterPressure'] = defaultPreferencesDict()['general']['igniterPressure']
    data['units']['(m*Pa)/s'] = '(in*psi)/s'
    data['units']['m/(s*Pa)'] = 'thou/(s*psi)'
    return data

def migrateProp_0_3_0_to_0_4_0(data):
    for i in range(0, len(data)):
        data[i] = tabularizePropellant(data[i])
    # Add default propellants in if they don't replace existing ones
    for propellant in defaultPropellants():
        if propellant['name'] not in [cProp['name'] for cProp in data]:
            data.append(propellant)
    return data

def migrateMotor_0_3_0_to_0_4_0(data):
    data['propellant'] = tabularizePropellant(data['propellant'])
    data['config']['igniterPressure'] = defaultPreferencesDict()['general']['igniterPressure']
    return data

def migratePref_0_2_0_to_0_3_0(data):
    defPref = defaultPreferencesDict()
    data['general']['maxPressure'] = defPref['general']['maxPressure']
    data['general']['maxMassFlux'] = defPref['general']['maxMassFlux']
    data['general']['minPortThroat'] = defPref['general']['minPortThroat']
    return data

def migrateMotor_0_2_0_to_0_3_0(data):
    if QApplication.instance().preferencesManager:
        config = QApplication.instance().preferencesManager.preferences.getDict()['general']
    else:
        config = defaultPreferencesDict()['general']
    data['config'] = config
    data['nozzle']['divAngle'] = 15
    data['nozzle']['convAngle'] = 55
    data['nozzle']['throatLength'] = 0.35 * data['nozzle']['throat']
    return data

migrations = {
    (0, 4, 0): {
        'to': (0, 5, 0),
        fileTypes.PREFERENCES: passthrough,
        fileTypes.PROPELLANTS: passthrough,
        fileTypes.MOTOR: passthrough,
    },
    (0, 3, 0): {
        'to': (0, 4, 0),
        fileTypes.PREFERENCES: migratePref_0_3_0_to_0_4_0,
        fileTypes.PROPELLANTS: migrateProp_0_3_0_to_0_4_0,
        fileTypes.MOTOR: migrateMotor_0_3_0_to_0_4_0
    },
    (0, 2, 0): {
        'to': (0, 3, 0),
        fileTypes.PREFERENCES: migratePref_0_2_0_to_0_3_0,
        fileTypes.PROPELLANTS: passthrough,
        fileTypes.MOTOR: migrateMotor_0_2_0_to_0_3_0
    },
    (0, 1, 0): {
        'to': (0, 2, 0),
        fileTypes.PREFERENCES: passthrough,
        fileTypes.PROPELLANTS: passthrough,
        fileTypes.MOTOR: passthrough
    }
}

def doMigration(fileData):
    print('Doing a migration of a ' + str(fileData["type"]) + ' from ' + str(fileData["version"]))
    while fileData["version"] != appVersion:
        migration = migrations[fileData["version"]]
        print("\tUpgrading " + str(fileData["version"]) + " to " + str(migration["to"]))
        fileData["data"] = migration[fileData["type"]](fileData["data"])
        fileData["version"] = migration["to"]
    return fileData
