"""
Dummy device code for running and testing DySART measurement infrastructure.

Defines classes Fizzer, Fizzmeter and Carbonator, which represent a carbonated
liquid whose level of fizziness is monitored by a fizzmeter and controlled with
a feedback system.
"""

import time
import numpy as np
day_sec = 60*60*24


def shifted_logistic(x):
    return 2/(1 + np.exp(-x)) - 1


class Device:

    def __init__(self, decal_rate=1e-3, cal_delay=1):
        """
        Initializes device by setting decalibration rate in units/sqrt(second)
        and setting the cal time by a refresh() call.
        """
        self.decal_rate = decal_rate  # Decalibration rate in 1/second
        self.cal_delay = cal_delay
        self.refresh()

    def refresh(self, t_new):
        """
        Resets the calibration time
        """
        self.cal_time = t_new


class Fizzer(Device):
    """
    A cool glass of fizzy substance. Maintains carbonation level and fizziness,
    updating every time a public method is called.
    """

    def __init__(self, carbonation=1, time_constant_days=1):
        """
        Initializes Fizzer with time constant 1 day
        """
        self.carbonation = carbonation
        self.time_constant_sec = time_constant_days * day_sec
        super().__init__(0)

    def refresh(self):
        t_new = time.time()
        super().refresh(t_new)

    def add_carbonation(self, carbonation):
        self.carbonation += carbonation
        self.refresh()

    def get_carbonation(self):
        t_new = time.time()
        dt = t_new - self.cal_time
        carbonation = self.carbonation*np.exp(-dt/self.time_constant_sec)
        self.carbonation = carbonation
        super().refresh(t_new)
        return carbonation

    def get_fizziness(self):
        """
        Fizziness is some function of carbonation that's linear at low levels,
        and saturates to 1 ("most fizzy!") at high carbonation. This is not
        a physically or chemically accurate model.
        """
        carbonation = self.get_carbonation()
        fizziness = shifted_logistic(carbonation)
        return fizziness


class Fizzmeter(Device):
    """
    Measures the fizziness of a Fizzer. Measurement bias is controlled by
    decal_rate parameter, which must be routinely calibrated away.
    """

    def __init__(self, response_delay=0.5, uncertainty=0.1, decal_rate_days=1):
        self.response_delay = response_delay
        self.uncertainty = uncertainty
        self.bias = 0
        decal_rate_sec = decal_rate_days * day_sec
        super().__init__(decal_rate_sec)

    def refresh(self):
        t_new = time.time()
        dt = t_new - self.cal_time
        self.bias += np.random.normal(0, dt * self.decal_rate)
        super().refresh(t_new)

    def measure(self, fizzer):
        """
        Returns the fizziness of a Fizzer, delayed by response time, plus added
        noise.
        """
        time.sleep(self.response_delay)
        self.refresh()

        noise = np.random.normal(0, self.uncertainty)
        return fizzer.fizziness + self.bias + noise

    def calibrate(self):
        time.sleep(self.cal_delay)
        self.bias = 0
        self.refresh()


class Carbonator(Device):

    def __init__(self, response_delay=0.5, uncertainty=0.01):
        super().__init__()
        self.response_delay = response_delay
        self.uncertainty = uncertainty

    def refresh(self):
        t_new = time.time()
        super().refresh(t_new)

    def get_uncertainty(self):
        self.refresh()
        return self.uncertainty

    def carbonate(self, fizzer, carbonation):
        noise = np.random.normal(0, self.get_uncertainty())


class Buzzer(Device):

    def __init__(self):
        pass

    def get_buzziness(self):
        pass


class BuzzMeter(Device):

    def __init__(self):
        pass
