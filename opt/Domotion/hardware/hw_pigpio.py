# -*- coding: utf-8 -*-
#########################################################
# SERVICE : hw_pigpio.py                                #
#           Python pigpio handling for Domotion         #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from threading import Thread, Event, Lock
import logging
from time import sleep
try:
    import pigpio
    ifinstalled = True
except ImportError:
    ifinstalled = False
#########################################################

####################### GLOBALS #########################
sleeptime = 0.1
retrytime = 10 / sleeptime # test every 10s
retries = 10

#########################################################
# Class : gpio                                          #
#########################################################
class gpio(Thread):
    def __init__(self, commandqueue):
        self.commandqueue=commandqueue
        self.logger = logging.getLogger('Domotion.Pigpio')
        self.sensorcallbacks = {}
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        self.mutex = Lock()
        if ifinstalled:
            self.pi = pigpio.pi()
            self.PiGPIOrunning = self.pi.connected
        else:
            self.pi = None
            self.PiGPIOrunning = False

    def __del__(self):
        self._RemoveCallbacks()
        del self.mutex
        del self.term
        if self.pi:
            self.pi.stop()
            del self.pi
        self.logger.info("finished")

    def UpdateDevices(self, sensors, actuators):
        # add BSL outputs in engine, for pigpio they are just normal outputs
        self.mutex.acquire()
        self._InitSensors(sensors)
        self._InitActuators(actuators)
        self._InitCallbacks(sensors)
        self.mutex.release()

    def terminate(self):
            self.term.set()

    def run(self):
        try:
            testing = False
            testcnt = retrytime
            testretries = retries

            self.logger.info("running")

            if (not self.pi):
                self.logger.warning("pigpio not installed, terminating")
            else:
                while (not self.term.isSet() and (testretries>0)):
                    if (not self.PiGPIOrunning):
                        if (testcnt > 0):
                            testcnt -= 1
                        else:
                            testcnt = retrytime
                            self._TestGPIO()
                            if (not self.PiGPIOrunning):
                                if (retries == testretries):
                                    self.logger.warning("pigpio not running, retrying")
                                elif (testretries <= 1):
                                    self.logger.warning("pigpio not running, terminating")
                                testretries -= 1
                            else:
                                self.logger.info("pigpio connection established")
                    else:
                        testcnt = retrytime
                        testretries = retries
                        self._TestGPIO()
                        if (not self.PiGPIOrunning):
                            self._TestGPIO(reset = True)
                        # Nothing to be done here, everything is callback based
                    sleep(sleeptime)

            self.logger.info("terminating")
        except Exception as e:
            self.logger.exception(e)

    def _TestGPIO(self, reset = False):
        self.mutex.acquire()
        if (not self.PiGPIOrunning or reset):
            if self.pi:
                self.pi.stop()
                del self.pi
            self.pi = pigpio.pi()
        self.PiGPIOrunning = self.pi.connected
        self.mutex.release()
        return self.PiGPIOrunning

    def SetActuator(self, gpio, level):
        res = False
        if (self.PiGPIOrunning):
            self.pi.write(gpio, level)
            res = True
        return (res)

    def _Callback(self, gpio, level, tick):
        self.commandqueue.put_code("GPIO", 0, 0, gpio, level)
        return (gpio)

    def _InitSensors(self, sensors):
        if (self.PiGPIOrunning):
            for sensor in sensors:
                self.pi.set_mode(sensor, pigpio.INPUT)
                self.pi.set_pull_up_down(sensor, pigpio.PUD_OFF)

    def _InitActuators(self, actuators):
        if (self.PiGPIOrunning):
            for actuator in actuators:
                self.pi.set_mode(actuator, pigpio.OUTPUT)
                self.pi.set_pull_up_down(actuator, pigpio.PUD_OFF)

    def _InitCallbacks(self, sensors):
        if (self.PiGPIOrunning):
            # Add new ones, don't update existing values
            for sensor in sensors:
                if sensor != 0:
                    if not sensor in self.sensorcallbacks:
                        self.sensorcallbacks[sensor] = self.pi.callback(sensor, pigpio.EITHER_EDGE, self._Callback)
            #remove old ones
            for sensor in self.sensorcallbacks.copy():
                if not sensor in sensors:
                    self.sensorcallbacks[sensor].cancel()
                    del self.sensorcallbacks[sensor]

    def _RemoveCallbacks(self):
        if (self.PiGPIOrunning):
            for sensor in self.sensorcallbacks.copy():
                if self.sensorcallbacks[sensor] is not None:
                    self.sensorcallbacks[sensor].cancel()
                    del self.sensorcallbacks[sensor]
