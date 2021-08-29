# -*- coding: utf-8 -*-
#########################################################
# SERVICE : hw_url.py                                   #
#           Python handling for basic device access     #
#           I. Helwegen 2018                            #
#########################################################

####################### IMPORTS #########################
from threading import Lock
import logging
from engine.localaccess import localaccess
from engine.commandqueue import commandqueue
from frontend.bdaserver import bdaserver
from frontend.basicwebaccess import basicwebaccess
#########################################################

####################### GLOBALS #########################

#########################################################
# Class : url                                           #
#########################################################
class url(bdaserver):
    def __init__(self, commandqueue, localaccess, memorylog):
        self.commandqueue=commandqueue
        self.localaccess=localaccess
        self.memorylog=memorylog
        self.logger = logging.getLogger('Domotion.url')
        self.sensors = []
        self.actuators = []
        self.mutex = Lock()
        self.updatesettings()
        super(url, self).__init__(self._update, self._trustedupdate, port=int(self.localaccess.GetSetting('URL_port')),
            maxclients=int(self.localaccess.GetSetting('URL_maxclients')),
            username=self.localaccess.GetSetting('URL_username'), password=self.localaccess.GetSetting('URL_password'),
            trusted=self.localaccess.GetSetting('URL_trusted'))

    def __del__(self):
        super(url, self).__del__()
        del self.mutex
        #self.logger.info("finished")

    def UpdateDevices(self, sensors, actuators):
        self.mutex.acquire()
        self.sensors = sensors
        self.actuators = actuators
        self.mutex.release()

    def updatesettings(self):
        #if (self.mutex):
        #    self.mutex.acquire()
        #    self.mutex.release()
        return

    def SetSensor(self, key, value):
        return self._SetSensorURL(key, value)

    def SetActuator(self, key, value):
        return self._SetActuatorURL(key, value)

    # Callback
    def _update(self, data):
        tag=None
        value=None
        self.mutex.acquire()
        if data[0]:
            for sensor in self.sensors:
                prop = self.localaccess.GetSensorProperties(sensor)
                if data[0] == prop['KeyTag']:
                    tag=data[0]
                    curval=self.localaccess.GetSensor(sensor)
                    if len(data)<2: # Get request
                        value=curval
                    else: # Set request
                        value=data[1]
                        #if (curval != value):
                        self.commandqueue.put_id("Url", sensor, value, True)
            if not value:
                for actuator in self.actuators:
                    prop = self.localaccess.GetActuatorProperties(actuator)
                    if data[0] == prop['KeyTag']:
                        tag=data[0]
                        curval=self.localaccess.GetActuator(actuator)
                        if len(data)<2: # Get request
                            value=curval
                        else: # Set request
                            value=data[1]
                            #if (curval != value):
                            self.commandqueue.put_id("None", actuator, value, False)
        self.mutex.release()
        return tag, value

    # Callback
    def _trustedupdate(self, data):
        ReturnData = None
        if data[2].lower() == "set":
            ReturnData = basicwebaccess(self.commandqueue, self.localaccess, self.memorylog).set(data[0], data[1])
        elif data[2].lower() == "get":
            ReturnData = basicwebaccess(self.commandqueue, self.localaccess, self.memorylog).get(data[0])
        elif data[2].lower() == "getall":
            ReturnData = basicwebaccess(self.commandqueue, self.localaccess, self.memorylog).getall(data[0])
        elif data[2].lower() == "getinfo":
            ReturnData = basicwebaccess(self.commandqueue, self.localaccess, self.memorylog).getinfo(data[0])
        return ReturnData

    def _SetSensorURL(self, key, value):
        success = True
        prop = self.localaccess.GetSensorProperties(key)
        rtag, rvalue = self.Send(prop['DeviceURL'], prop['KeyTag'], str(value))
        if (rtag and rvalue):
           success = True
        else:
            success = False
        return success

    def _SetActuatorURL(self, key, value):
        success = True
        prop = self.localaccess.GetActuatorProperties(key)
        rtag, rvalue = self.Send(prop['DeviceURL'], prop['KeyTag'], str(value))
        if (rtag and rvalue):
           success = True
        else:
            success = False
        return success
