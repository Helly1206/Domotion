# -*- coding: utf-8 -*-
#########################################################
# SERVICE : hw_domoticz.py                              #
#           Python handling for domoticz sensors        #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from threading import Thread, Event, Lock
import logging
from time import sleep
from engine.localaccess import localaccess
from engine.commandqueue import commandqueue
from frontend.domoticz_api import domoticz_api
#########################################################

####################### GLOBALS #########################
sleeptime = 0.1
maxcnt = (1000/sleeptime)
updatecnt = (1/sleeptime)

# Maybe a good idea to have a list of sensors and update them in a thread every 1 second ....
# Don't care about connections and non existing devices. failure means don't update

#########################################################
# Class : domoticz_if                                   #
#########################################################
class domoticz_if(Thread):
    def __init__(self, commandqueue, localaccess, domoticz_api):
        self.commandqueue=commandqueue
        self.localaccess=localaccess
        self.domoticz_api=domoticz_api
        self.logger = logging.getLogger('Domotion.Domoticz_if')
        self.sensors = []
        self.actuators = []
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        self.mutex = Lock()
        
    def __del__(self):
        del self.mutex
        del self.term
        self.logger.info("finished")

    def UpdateDevices(self,sensors,actuators):
        self.mutex.acquire()
        self.sensors = sensors
        self.actuators = actuators
        self.mutex.release()

    def SetSensor(self, key, value):
        return self._SetSensorDevice(key, value)

    def SetActuator(self, key, value):
        return self._SetActuatorDevice(key, value)

    def terminate(self):
            self.term.set()

    def run(self):
        try:
            counter = 0
            connected = False
            connectedprev = False
            self.logger.info("running")

            while (not self.term.isSet()):
                if (counter % updatecnt == 0):
                    self.mutex.acquire()
                    for sensor in self.sensors:
                        succes, value = self._GetSensorDevice(sensor)
                        if (success):
                            curval = self.localaccess.GetSensor(sensor)
                            if (curval != value):
                                self.commandqueue.put_id("Domoticz", sensor, value, True)
                        connected = success
                    for actuator in self.actuators:
                        succes, value = self._GetActuatorDevice(actuator)
                        if (success):
                            curval = self.localaccess.GetActuator(actuator)
                            if (curval != value):
                                self.commandqueue.put_id("Domoticz", actuator, value, False)
                        connected = success
                    self.mutex.release()
                    if (connected != connectedprev):
                        if (connected):
                            self.logger.info("connection established")
                        else:
                            self.logger.info("no connection")
                        connectedprev = connected
                sleep(sleeptime)
                if (counter < maxcnt):
                    counter += 1
                else:
                    counter = 0

            self.logger.info("terminating")
        except Exception as e:
            self.logger.exception(e)

    def _GetSensorDevice(self, key):
        success = True
        value = None
        IDx = int(self.localaccess.GetSensorProperties(key)['DeviceCode'])
        if (IDx == 0):
            success = False
        if (success):
            success, device = self.domoticz_api.getDevice(IDx)
        if (success):
            value = self.domoticz_api.GetValue(device)
        return success, value

    def _GetActuatorDevice(self, key):
        success = True
        value = None
        IDx = int(self.localaccess.GetActuatorProperties(key)['DeviceCode'])
        if (IDx == 0):
            success = False
        if (success):
            success, device = self.domoticz_api.getDevice(IDx)
        if (success):
            value = self.domoticz_api.GetValue(device)
        return success, value

    def _SetSensorDevice(self, key, value):
        success = True
        IDx = int(self.localaccess.GetSensorProperties(key)['DeviceCode'])
        if (IDx == 0):
            success = False
        if (success):
            digital=self.localaccess.GetSensorDigital(key)
            success = self.domoticz_api.setDevice(IDx, value, digital)
        return success

    def _SetActuatorDevice(self, key, value):
        success = True
        IDx = int(self.localaccess.GetActuatorProperties(key)['DeviceCode'])
        if (IDx == 0):
            success = False
        if (success):
            digital=self.localaccess.GetActuatorDigital(key)
            success = self.domoticz_api.setDevice(IDx, value, digital)
        return success