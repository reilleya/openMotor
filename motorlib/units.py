unitLabels = {'m': 'Length', 'ns': 'Impulse', 'pa': 'Pressure', 'kg/(m^2*s)': 'Mass Flux'}

unitTable = [
('m', 'cm', 100),
('m', 'mm', 1000),
('m', 'in', 39.37),
('m', 'ft', 3.28),

('ns', 'lbfs', 0.2248),

('pa', 'mpa', 1/1000000),
('pa', 'psi', 1/6895),

('kg/(m^2*s)', 'lb/(in^2*s)', 0.001422)
]

def getAllConversions(unit):
    allConversions = [unit]
    for conversion in unitTable:
        if conversion[0] == unit:
            allConversions.append(conversion[1])
        elif conversion[1] == unit:
            allConversions.append(conversion[0])
    return allConversions

def getConversion(originUnit, destUnit):
    if originUnit == destUnit:
        return 1
    for conversion in unitTable:
        if conversion[0] == originUnit and conversion[1] == destUnit:
            return conversion[2]
        if conversion[1] == originUnit and conversion[0] == destUnit:
            return 1/conversion[2]

def convert(quantity, originUnit, destUnit):
    return quantity * getConversion(originUnit, destUnit)

def convertAll(quantities, originUnit, destUnit):
    convRate = getConversion(originUnit, destUnit)
    return [q * convRate for q in quantities]
