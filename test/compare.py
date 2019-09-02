import sys
import os
import matplotlib
import yaml
import warnings

import motorlib.motor
from uilib.fileIO import loadFile, fileTypes

class colors:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def color(string, name):
    return str(name) + string + str(colors.ENDC)

def runSim(path):
    print('Loading motor from ' + path)
    res = loadFile(path, fileTypes.MOTOR)
    if res is not None:
        motor = motorlib.motor.Motor(res)
        print('Simulating burn...')
        return motor.runSimulation()
    else:
        print('Error loading motor for test!')

def compareStat(title, a, b):
    error = abs(a - b) / b
    if error < 1 / 100:
        c = colors.OK
    elif error < 5 / 100:
        c = colors.WARNING
    else:
        c = colors.FAIL
    dispError = color(str(round(error * 100, 3))+'%', c)
    print('\t' + title + ': ' + str(round(a, 3)) + ' vs ' + str(round(b, 3)) + ' (' + dispError + ')')
    return error

def compareStats(simRes, stats):
    print('Comparing basic stats:')
    btError = compareStat('Burn Time', simRes.getBurnTime(), stats['burnTime'])
    ispError = compareStat('ISP', simRes.getISP(), stats['isp'])
    propmassError = compareStat('Propellant Mass', simRes.getPropellantMass(), stats['propMass'])


def runTests(path):
    print('-'*50)
    with open(path, 'r') as readLocation:
        fileData = yaml.load(readLocation)
        print("Running tests for '" + fileData['name'] + "'")
        simRes = runSim(fileData['motor'])
        if fileData['data']['real']:
            print('Comparing to real data...')
            compareStats(simRes, fileData['data']['real']['stats'])
    print('-'*50)

warnings.filterwarnings('ignore') # Todo: get rid of this
os.system('color')
if len(sys.argv) > 1:
    runTests(sys.argv[1])
else:
    with open('data/tests.yaml', 'r') as readLocation:
        fileData = yaml.load(readLocation)
        for category in fileData.keys():
            print("Running tests from category '" + category + "'")
            for test in fileData[category]:
                runTests(test)
