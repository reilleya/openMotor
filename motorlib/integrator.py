
class Integrator():
    def __init__(self, timestep=0.001, time=0):
        self.tolerance = 0.00001
        self.time = time
        self.ts = timestep

    def doRK45Step(self, func, y):

        k1 = self.ts * func(self.time, y)
        k2 = self.ts * func(self.time + (1/4) * self.ts, y + (1/4) * k1)
        k3 = self.ts * func(self.time + (3/8) * self.ts, y + (3/32) * k1 + (9/32) * k2)
        k4 = self.ts * func(self.time + (12/13) * self.ts, y + (1932/2197) * k1 - (7200/2197) * k2 + (7296/2197) * k3)
        k5 = self.ts * func(self.time + self.ts, y + (439/216) * k1 - 8 * k2 + (3680/513) * k3 - (845/4104) * k4)
        k6 = self.ts * func(self.time + (1/2) * self.ts, y - (8/27) * k1 + 2 * k2 - (3544/2565) * k3 + (1859/4104) * k4 - (11/40) * k5)

        ynext4 = y + (25/216) * k1 + (1408/2565) * k3 + (2197/4101) * k4 - (1/5) * k5
        ynext5 = y + (16/135) * k1 + (6656/12825) * k3 + (28561/56430) * k4 - (9/50) * k5 + (2/55) * k6

        self.time += self.ts

        if ynext5 != ynext4:
            self.ts = self.ts * (self.tolerance/ (2 * abs(ynext4 - ynext5))) ** 0.25

        print("x = {}, y = {}, ts = {}".format(self.time, ynext5, self.ts))

        return ynext5
