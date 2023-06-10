import os

from PyQt5.QtWidgets import QApplication
import yaml
import appdirs

from .defaults import DEFAULT_PREFERENCES, DEFAULT_PROPELLANTS, KNSU_PROPS
from .enums.fileType import FileType
from .logger import logger

appVersion = (0, 6, 0)
appVersionStr = '.'.join(map(str, appVersion))

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
        fileData = yaml.load(readLocation, Loader=yaml.Loader)

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

 # Returns the path that files like preferences and propellant library should be in. Previously, all platforms except
 # Mac OS put these files alongside the executable, but the v0.5.0 added an installer for windows so it makes more
 # sense to use the user's data directory now.
def getConfigPath():
    path = appdirs.user_data_dir('openMotor', 'openMotor')
    if not os.path.isdir(path): # Create directory if it doesn't exist
        os.mkdir(path)
    return '{}/'.format(path)

def passthrough(data):
    return data
    
    
#0.5.0 to 0.6.0
def migrateMotor_0_5_0_to_0_6_0(data):
    data['config']['sepPressureRatio'] = DEFAULT_PREFERENCES['general']['sepPressureRatio']
    data['config']['flowSeparationWarnPercent'] = DEFAULT_PREFERENCES['general']['flowSeparationWarnPercent']
    return data

# 0.4.0 to 0.5.0

def migrateProp_0_4_0_to_0_5_0(data):
    for propellant in data:
        if propellant['name'] == 'MIT - Cherry Limeade':
            propellant['density'] = 1670
            propellant['tabs'][0]['t'] = 2800
        elif propellant['name'] == 'MIT - Ocean Water':
            propellant['density'] = 1650
            propellant['tabs'][0]['t'] = 2600
    if not 'Nakka - KNSU' in [cProp['name'] for cProp in data]:
        data.append(KNSU_PROPS)
    return data

def migratePref_0_4_0_to_0_5_0(data):
    del data['general']['igniterPressure']
    data['general']['burnoutWebThres'] = DEFAULT_PREFERENCES['general']['burnoutWebThres']
    return data

def migrateMotor_0_4_0_to_0_5_0(data):
    if data['config']['igniterPressure']:
        del data['config']['igniterPressure']
    return data

# 0.3.0 to 0.4.0

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
    data['general']['igniterPressure'] = DEFAULT_PREFERENCES['general']['igniterPressure']
    data['units']['(m*Pa)/s'] = '(in*psi)/s'
    data['units']['m/(s*Pa)'] = 'thou/(s*psi)'
    return data

def migrateProp_0_3_0_to_0_4_0(data):
    for i in range(0, len(data)):
        data[i] = tabularizePropellant(data[i])
    # Add default propellants in if they don't replace existing ones
    for propellant in DEFAULT_PROPELLANTS:
        if propellant['name'] not in [cProp['name'] for cProp in data]:
            data.append(propellant)
    return data

def migrateMotor_0_3_0_to_0_4_0(data):
    data['propellant'] = tabularizePropellant(data['propellant'])
    data['config']['igniterPressure'] = DEFAULT_PREFERENCES['general']['igniterPressure']
    return data

# 0.2.0 to 0.3.0

def migratePref_0_2_0_to_0_3_0(data):
    defPref = DEFAULT_PREFERENCES
    data['general']['maxPressure'] = defPref['general']['maxPressure']
    data['general']['maxMassFlux'] = defPref['general']['maxMassFlux']
    data['general']['minPortThroat'] = defPref['general']['minPortThroat']
    return data

def migrateMotor_0_2_0_to_0_3_0(data):
    if QApplication.instance().preferencesManager:
        config = QApplication.instance().preferencesManager.preferences.getDict()['general']
    else:
        config = DEFAULT_PREFERENCES['general']
    data['config'] = config
    data['nozzle']['divAngle'] = 15
    data['nozzle']['convAngle'] = 55
    data['nozzle']['throatLength'] = 0.35 * data['nozzle']['throat']
    return data

migrations = {
    (0, 5, 0): {
        'to': (0, 6, 0),
        FileType.PREFERENCES: passthrough,
        FileType.PROPELLANTS: passthrough,
        FileType.MOTOR: migrateMotor_0_5_0_to_0_6_0
    },
    (0, 4, 0): {
        'to': (0, 5, 0),
        FileType.PREFERENCES: migratePref_0_4_0_to_0_5_0,
        FileType.PROPELLANTS: migrateProp_0_4_0_to_0_5_0,
        FileType.MOTOR: migrateMotor_0_4_0_to_0_5_0,
    },
    (0, 3, 0): {
        'to': (0, 4, 0),
        FileType.PREFERENCES: migratePref_0_3_0_to_0_4_0,
        FileType.PROPELLANTS: migrateProp_0_3_0_to_0_4_0,
        FileType.MOTOR: migrateMotor_0_3_0_to_0_4_0
    },
    (0, 2, 0): {
        'to': (0, 3, 0),
        FileType.PREFERENCES: migratePref_0_2_0_to_0_3_0,
        FileType.PROPELLANTS: passthrough,
        FileType.MOTOR: migrateMotor_0_2_0_to_0_3_0
    },
    (0, 1, 0): {
        'to': (0, 2, 0),
        FileType.PREFERENCES: passthrough,
        FileType.PROPELLANTS: passthrough,
        FileType.MOTOR: passthrough
    }
}

def doMigration(fileData):
    logger.log('Doing a migration of a {} from {}'.format(fileData["type"], fileData["version"]))
    while fileData["version"] != appVersion:
        migration = migrations[fileData["version"]]
        logger.log('\tUpgrading {} to {}'.format(fileData["version"], migration["to"]))
        fileData["data"] = migration[fileData["type"]](fileData["data"])
        fileData["version"] = migration["to"]
    return fileData
