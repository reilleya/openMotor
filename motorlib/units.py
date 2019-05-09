unitLabels = {'m': 'Length', 'm/s': 'Velocity', 'N': 'Force', 'Ns': 'Impulse', 'Pa': 'Pressure', 'kg': 'Mass', 'kg/m^3': 'Density', 'kg/s': 'Mass Flow', 'kg/(m^2*s)': 'Mass Flux', 'm/(s*Pa^n)': 'Burn Rate Coefficient'}

unitTable = [
('m', 'cm', 100),
('m', 'mm', 1000),
('m', 'in', 39.37),
('m', 'ft', 3.28),

('m/s', 'ft/s', 3.28),

('N', 'lbf', 0.2248),

('Ns', 'lbfs', 0.2248),

('Pa', 'MPa', 1/1000000),
('Pa', 'psi', 1/6895),

('kg', 'g', 1000),
('kg', 'lb', 2.205),
('kg', 'oz', 2.205 * 16),

('kg/m^3', 'lb/in^3', 3.61273e-5),
('kg/m^3', 'g/cm^3', 0.001),

('kg/s', 'lb/s', 2.205),
('kg/s', 'g/s', 1000),

('kg/(m^2*s)', 'lb/(in^2*s)', 0.001422),

('m/(s*Pa^n)', 'in/(s*psi^n)', 39.37) # Ratio converts m/s to in/s. The pressure conversion must be done separately.
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
