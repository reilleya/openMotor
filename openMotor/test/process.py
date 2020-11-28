import sys

filename = sys.argv[1]
outname = filename.replace('.txt', '.csv')

header = "time (s),force (n),pressure (pa)\n"
firstTime = None
massFlowRate = None
out = []

with open(filename, 'r') as rawData:
    propMass = float(input('Enter propellant mass in N> '))
    for line in rawData.read().split('\n'):
        out.append([])
        # Process time
        time, data = line.split(':')
        if firstTime is None:
            firstTime = int(time)
            time = 0
        else:
            time = int(time) - firstTime
        force, pressure = data.split(',')[:2]
        # Process pressure
        pressure = (float(pressure) + 14.7) * 6895
        # Process force
        force = float(force)

        out[-1].append(time)
        out[-1].append(force)
        out[-1].append(pressure)

    massFlowRate = propMass / out[-1][0]

    for lineIndex, line in enumerate(out):
        out[lineIndex][1] += massFlowRate * line[0]
    
    with open(outname, 'w') as outFile:
        outFile.write(header)
        for line in out:
            o = str(line[0] / 1000) + ',' + str(line[1]) + ',' + str(line[2]) + '\n'
            outFile.write(o)
        print('Results written to ' + outname)
