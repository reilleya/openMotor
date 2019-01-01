table = [
("m", "in", 39.37),
("m", "f", 3.28),

("mpa", "psi", 1/6895)

]

def getAllConversions(unit):
    allConversions = []
    for conversion in table:
        if conversion[0] == unit:
            allConversions.append(conversion[1])
        elif conversion[1] == unit:
            allConversions.append(conversion[0])

def getConversion(originUnit, destUnit):
    if originUnit == destUnit:
        return 1
    for conversion in table:
        if conversion[0] == originUnit and conversion[1] == destUnit:
            return conversion[2]
        if conversion[1] == originUnit and conversion[0] == destUnit:
            return 1/conversion[2]

def convert(quantity, originUnit, destUnit):
    return quantity * getConversion(originUnit, destUnit)

def convertAll(quantities, originUnit, destUnit):
    convRate = getConversion(originUnit, destUnit)
    return [q * convRate for q in quantities]
