# -*- coding: utf-8 -*-
#########################################################
# SERVICE : statuslight.py                              #
#           Inferface for status light for Domotion     #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from threading import Thread, Event, Lock
import logging
from time import sleep
from engine import localaccess
from enum import Enum
#########################################################

# Green everything ok
# Yellow busy processing
# Red unable to set output

# input/ output set: flash 3 LEDs 1 second

# 0.2 / 0.8 nothing set
# 0.5 / 0.5 output set
# based on StatusLightFlash output set

# not running, all LEDs off

####################### GLOBALS #########################
sleeptime = 0.1
seccnt = (1/sleeptime)
secflash = (0.2/sleeptime)
secflash50 = (0.5/sleeptime)
secbusy = (3/sleeptime)

class State(Enum):
    OK, BUSY, ERROR = range(3)

#########################################################
# Class : statuslight                                   #
#########################################################
class statuslight(Thread):
    def __init__(self):
        self.light=[0,0,0]
        self.gpio=None
        self.Flash50=False
        self.DeviceSet=False
        self.state=State.BUSY
        self.logger = logging.getLogger('Domotion.StatusLight')
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        self.mutex = Lock()

    def __del__(self):
        self.light=[0,0,0]
        self.gpio=None
        del self.mutex
        del self.term
        self.logger.info("finished")

    def AddStatusActuators(self, Actuators):
        self.light[0]=localaccess.GetSetting('Status_red')
        if (self.light[0]):
            Actuators.append(self.light[0])
        self.light[1]=localaccess.GetSetting('Status_yellow')
        if (self.light[1]):
            Actuators.append(self.light[1])
        self.light[2]=localaccess.GetSetting('Status_green')
        if (self.light[2]):
            Actuators.append(self.light[2])
        return (Actuators)

    def instances(self, gpio):
        self.gpio=gpio

    def terminate(self):
        self.term.set()

    def run(self):
        try:
            self.logger.info("running")
            secint = 0
            secbusyint = 0
            state = self.state
            DeviceSet = False
            Flash50 = False

            while (not self.term.isSet()):
                if (secint < seccnt-1):
                    secint += 1
                else:
                    secint = 0
                    DeviceSet = False

                self.mutex.acquire()
                if (self.DeviceSet):
                    self.DeviceSet = False
                    DeviceSet = True
                    secint = 0
                    self._SetLights(1,1,1)
                if ((state == State.BUSY) and (secbusyint<secbusy)):
                    secbusyint += 1
                    if (self.state == State.BUSY):
                        secbusyint = 0
                    else:
                        secbusyint += 1
                elif (self.state != state):
                    state = self.state
                    secint = 0
                    secbusyint = 0
                Flash50 = self.Flash50
                self.mutex.release()   

                if (not DeviceSet):
                    if (secint == 0):
                        if (state == State.OK):
                            self._SetLights(0,0,1)
                        elif (state == State.BUSY):
                            self._SetLights(0,1,0)
                        else: #(state == State.ERROR)
                            self._SetLights(1,0,0)
                    elif ((secint == secflash) and (not Flash50)):
                        self._SetLights(0,0,0)                    
                    elif ((secint == secflash50) and (Flash50)):
                        self._SetLights(0,0,0)

                sleep(sleeptime)

            self._SetLights(0,0,0)
            self.logger.info("terminating")
        except Exception, e:
            self.logger.exception(e)

    def SetFlash50(self, val):
        self.mutex.acquire()
        self.Flash50=val
        self.mutex.release()

    def SetDeviceSet(self):
        self.mutex.acquire()
        self.DeviceSet=True
        self.mutex.release()

    def Ok(self):
        self.mutex.acquire()
        self.state=State.OK
        self.mutex.release()

    def Busy(self):
        self.mutex.acquire()
        self.state=State.BUSY
        self.mutex.release()

    def Error(self):
        self.mutex.acquire()
        self.state=State.ERROR
        self.mutex.release()

    def _SetLights(self, red, yellow, green):
        # set directly, not via commandqueue !!!
        if (self.gpio):
            if (self.light[0]):
                self.gpio.SetActuator(self.light[0], red)
            if (self.light[1]):
                self.gpio.SetActuator(self.light[1], yellow)
            if (self.light[2]):
                self.gpio.SetActuator(self.light[2], green)