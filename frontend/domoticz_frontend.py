# TBD Check settings !!!!!!!!!!!!!!!!!!!!!! and update accordingly
# Fix statemachine in loop

# -*- coding: utf-8 -*-
#########################################################
# SERVICE : domoticz_fromtend.py                        #
#           Inferface for domoticz frontend for Domotion#
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from threading import Thread, Event, Lock
import logging
from time import sleep
from engine import localaccess
from engine import commandqueue
from utilities import domoticz_api
#########################################################

####################### GLOBALS #########################
sleeptime = 0.1
maxcnt = (1000/sleeptime)
testcnt = (10/sleeptime)
updatecnt = (1/sleeptime)
hardwarename = "Domotion"
messagename = "Domotion Messages"

#########################################################
# Class : domoticz_frontend                             #
#########################################################
class domoticz_frontend(Thread):
    def __init__(self, commandqueue):
        self.commandqueue = commandqueue
        self.logger = logging.getLogger('Domotion.Domoticz_frontend')
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        self.mutex = Lock()
        self._updatesettings()
        self.Hardware = None
        self.SensorIDx = { }
        self.ActuatorIDx = { }
        self.MessageIDx = 0

    def __del__(self):
        del self.mutex
        del self.term
        self.logger.info("finished")

    def terminate(self):
        self.term.set()

    def updatesettings(self):
        return self._updatesettings()

    def updatesensorsactuators(self):
        return self._updateSensorsActuators()

    def SetSensor(self, key, value):
        return self._SetSensorDevice(key, value)

    def SetActuator(self, key, value):
        return self._SetActuatorDevice(key, value)

    def SendMessage(self, message):
        success = False
        self.mutex.acquire()
        idx = self.MessageIDx
        self.mutex.release()
        if (idx):
            success = domoticz_api.setDevice(idx, message, False)
        return success

    def run(self):
        connected = False
        firstconn = True
        counter = 0
        gethardware = True
        self.logger.info("running")

        while (not self.term.isSet()):
            if (not connected):
                gethardware = True
                if (counter % testcnt == 0):
                    connected = domoticz_api.getDummy()
                    if (connected):
                        self.logger.info("connection established")
                    elif (firstconn):
                        self.logger.info("no connection, retrying")
                    firstconn = False
            else:
                if (gethardware):
                    connected = self._DomotionHardware()
                    if connected:
                        self._updatemessageDevice()
                        self._updateSensorsActuators()
                    gethardware = False
                else:
                    if (counter % updatecnt == 0):
                        connected, sensorvalues, actuatorvalues = self._GetAllDevices()
                        if (connected):
                            for key in sensorvalues:
                                self.commandqueue.put_id("None",key, sensorvalues[key], True)
                            del sensorvalues
                            for key in actuatorvalues:
                                self.commandqueue.put_id("None",key, actuatorvalues[key], False)
                            del actuatorvalues
                            self._updatemessageDevice()
                if (not connected):
                    self.logger.warning("connection lost, retrying")

            sleep(sleeptime)
            if (counter < maxcnt):
                counter += 1
            else:
                counter = 0

        self.logger.info("terminating")

    def _updatesettings(self):
        self.mutex.acquire()
        self.devices = localaccess.GetSetting('Domoticz_devices')
        self.sensors_poll = localaccess.GetSetting('Domoticz_sensors_poll')
        self.actuators_poll = localaccess.GetSetting('Domoticz_actuators_poll')
        self.message = localaccess.GetSetting('Domoticz_message')
        self.mutex.release()
        return self.message

    def _updatemessageDevice(self):
        success = True
        if ((self.message) and (self.MessageIDx == 0)):
            # messaging switched on, but no IDx yet
            success, idx = self._DomotionIdx(messagename)
            if ((success) and (idx > 0)):
                self.mutex.acquire()
                self.MessageIDx = idx
                self.mutex.release()
            else:
                # Messagedevice doesn't exist, add (type 5 is text sensor)
                success = domoticz_api.addDevice(self.Hardware, messagename, [5])
                if (success):
                    success, idx = self._DomotionIdx(messagename)
                if (success):
                    self.mutex.acquire()
                    self.MessageIDx = idx
                    self.mutex.release()
        elif ((not self.message) and (self.MessageIDx != 0)):
            # messaging switched off, delete device
            success = domoticz_api.deleteDevice(self.MessageIDx)
            if (success):
                self.mutex.acquire()
                self.MessageIDx = 0
                self.mutex.release()
        return success

    def _updateSensorsActuators(self):
        #get all devices from domotics, filter HW --> fill self.SensorIDx and self.ActuatorIDx with domotion ids
        # search by names: localaccess.FindSensorbyName
        success,devices = self._DomotionDevices()
        if (success):
            #get all sensors and actuators domotion
            sensors = localaccess.GetSensorNames()
            actuators = localaccess.GetActuatorNames()
            # couple idx for update
            ActiveDev = self._UpdateIDx(devices,sensors,actuators)
            if (self.devices):
                # add new sensors
                for sensor in self.SensorIDx:
                    if (not success):
                        break
                    if not self.SensorIDx[sensor]:
                        success = self._AddSensor(sensors[sensor],sensor)    
                    else:
                        success = self._UpdateSensor(devices,sensors[sensor],sensor)
                # add new actuators
                for actuator in self.ActuatorIDx:
                    if (not success):
                        break
                    if not self.ActuatorIDx[actuator]:
                        success = self._AddActuator(actuators[actuator],actuator)
                    else:
                        success = self._UpdateActuator(devices,actuators[actuator],actuator)
                # remove devices that are not on the hw list anymore
                for idx in ActiveDev:
                    if (not success):
                        break
                    if not ActiveDev[idx]:
                        if (idx != self.MessageIDx):
                            success = self._DelDevice(devices,idx)
        return success

    def _UpdateIDx(self,devices,sensors,actuators):
        self.mutex.acquire()
        ActiveDev = {}
        for device in devices:
            ActiveDev[int(device['idx'])]=0
        del self.SensorIDx
        self.SensorIDx = {}
        for sensor in sensors:
            idx = 0
            for device in devices:
                if (device['Name'] == sensors[sensor]):
                    idx = device['idx']
                    break
            self.SensorIDx[sensor] = int(idx)
            if (idx != 0):
                ActiveDev[int(idx)]=1
        del self.ActuatorIDx
        self.ActuatorIDx = {}
        for actuator in actuators:
            idx = 0
            for device in devices:
                if (device['Name'] == actuators[actuator]):
                    idx = device['idx']
                    break
            self.ActuatorIDx[actuator] = int(idx)
            if (idx != 0):
                ActiveDev[int(idx)]=1
        self.mutex.release()
        return ActiveDev

    def _AddSensor(self,name,key):
        success = True
        sensortype=localaccess.GetSensorType(key)
        if (sensortype):
            success = domoticz_api.addDevice(self.Hardware, name, sensortype)
            if (success):
                success, IDx = self._DomotionIdx(name)
                if (success):
                    self.logger.info("Added sensor: %s", name)
                    self.mutex.acquire()
                    self.SensorIDx[key] = IDx
                    self.mutex.release()
                    success = domoticz_api.updateDevice(IDx, name, sensortype, True)
            else:
                self.logger.warning("Adding sensor failed: %s", name)
        return success

    def _AddActuator(self,name,key):
        success = True
        actuatortype=localaccess.GetActuatorType(key)
        if (actuatortype):
            success = domoticz_api.addDevice(self.Hardware, name, actuatortype)
            if (success):
                success, IDx = self._DomotionIdx(name)
                if (success):
                    self.logger.info("Added actuator: %s", name)
                    self.mutex.acquire()
                    self.ActuatorIDx[key] = IDx
                    self.mutex.release()
                    success = domoticz_api.updateDevice(IDx, name, actuatortype, True)
            else:
                self.logger.warning("Adding actuator failed: %s", name)
        return success
    
    def _UpdateSensor(self, devices, name, key):
        success = True
        sensortype=localaccess.GetSensorType(key)
        if (sensortype):
            for device in devices:
                if (device['Name'] == name):
                    devicetype = domoticz_api.GetDeviceType(device)
                    if (sensortype[0] != devicetype[0]):
                        success = self._DelDevice(devices,int(device['idx']))
                        if (success):
                            success = self._AddSensor(name,key)
                        if (success):
                            self.logger.info("Deleted/ added changed sensor: %s", name)
                        else:
                            self.logger.warning("Deleting/ adding changed sensor failed: %s", name)
                    elif (sensortype[1] != devicetype[1]):
                        success = domoticz_api.updateDevice(device['idx'], name, sensortype, True)
                        if (success):
                            self.logger.info("Updated changed sensor: %s", name)
                        else:
                            self.logger.warning("Updating changed sensor failed: %s", name)
                    break
        return success

    # Cannot be done from Domotion, do not execute
    def _UpdateActuator(self, devices, name, key):
        success = True
        actuatortype=localaccess.GetActuatorType(key)
        if (actuatortype):
            for device in devices:
                if (device['Name'] == name):
                    devicetype = domoticz_api.GetDeviceType(device)
                    if (actuatortype[0] != devicetype[0]):
                        success = self._DelDevice(devices,int(device['idx']))
                        if (success):
                            success = self._AddActuator(name,key)
                        if (success):
                            self.logger.info("Deleted/ added changed actuator: %s", name)
                        else:
                            self.logger.warning("Deleting/ adding changed actuator failed: %s", name)
                    elif (actuatortype[1] != devicetype[1]):
                        success = domoticz_api.updateDevice(device['idx'], name, actuatortype, True)
                        if (success):
                            self.logger.info("Updated changed actuator: %s", name)
                        else:
                            self.logger.warning("Updating changed actuator failed: %s", name)
                    break
        return success

    def _DelDevice(self,devices,IDx):
        success = True
        #get name
        name = "Unknown"
        found = False
        for device in devices:
            if (int(device['idx']) == IDx):
                name = device['Name']
                found = True
                break
        #delete
        if (found):
            success = domoticz_api.deleteDevice(IDx)
            if (success):
                self.logger.info("Deleted obsolete device: %s", name)
                #update sensors and actuators IDx
                self.mutex.acquire()
                for sensor in self.SensorIDx.copy():
                    if (self.SensorIDx[sensor] == IDx):
                        del self.SensorIDx[sensor]
                for actuator in self.ActuatorIDx.copy():
                    if (self.ActuatorIDx[actuator] == IDx):
                        del self.ActuatorIDx[actuator]
                self.mutex.release()
            else:
                self.logger.warning("Deleting obsolete device failed: %s", name)
        return success

    # Fill local sensor values and actuatorvalues
    # If not equal, send commands (get sensor like on basicwebaccess and send value)  
    def _GetAllDevices(self):
        success = True
        sensorvalues = {}
        actuatorvalues = {}
        if ((self.sensors_poll) or (self.actuators_poll)):
            success, devices = self._DomotionDevices()
            if (success):
                for device in devices:
                    IDx = int(device['idx'])
                    if (IDx != self.MessageIDx):
                        value = domoticz_api.GetValue(device)
                        if ((IDx in self.SensorIDx.values()) and (self.sensors_poll)):
                            id=self.SensorIDx.keys()[self.SensorIDx.values().index(IDx)]
                            curval = localaccess.GetSensor(id)
                            if (curval != value):
                                sensorvalues[id]=value
                        if ((IDx in self.ActuatorIDx.values()) and (self.actuators_poll)):    
                            id=self.ActuatorIDx.keys()[self.ActuatorIDx.values().index(IDx)]
                            curval = localaccess.GetActuator(id)
                            if (curval != value):
                                actuatorvalues[id]=value
        return success, sensorvalues, actuatorvalues

    def _SetSensorDevice(self, key, value):
        success = True
        if key in self.SensorIDx:
            IDx = self.SensorIDx[key]
        else:
            success = False
        if (success):
            digital=localaccess.GetSensorDigital(key)
            success = domoticz_api.setDevice(IDx, value, digital)
        return success

    def _SetActuatorDevice(self, key, value):
        success = True
        if key in self.ActuatorIDx:
            IDx = self.ActuatorIDx[key]
        else:
            success = False
        if (success):
            digital=localaccess.GetActuatorDigital(key)
            success = domoticz_api.setDevice(IDx, value, digital)
        return success

    def _DomotionHardware(self):
        success = False

        success, result = domoticz_api.getHardware()
        if (success):
            if (result["status"] == 'OK'):
                Hardware = None
                for res in result["result"]:
                    if ((res["Name"] == hardwarename) and (res["Type"] == 15)):
                        Hardware = res
                        if (Hardware["Enabled"] == "false"):
                            self.logger.info("Disabled hardware found, enable")
                            success,res = domoticz_api.enableHardware(Hardware["idx"])
                            if (success):
                                if (res["status"] != "OK"):
                                    self.logger.error("Cannot enable hardware, create a new one")
                                    Hardware = None
                        else:       
                            self.logger.debug("Hardware found")
                        break
                if not Hardware:
                    #create new
                    self.logger.info("No hardware found, create new one")
                    success,res = domoticz_api.createHardware()
                    if (success):
                        if (res["status"] != "OK"):
                            self.logger.error("Cannot create hardware")
            else:
                success = False
            self.mutex.acquire()
            self.Hardware = int(Hardware["idx"])
            self.mutex.release()
        return success

    def _DomotionDevices(self):
        retres = []
        self.mutex.acquire()
        Hardware = self.Hardware
        self.mutex.release()
        if (Hardware): 
            success,result = domoticz_api.getDevices()
        else:
            success = False
        if (success):
            if (result["status"] == 'OK'):
                for res in result["result"]:
                    if (res["HardwareID"] == Hardware):
                        retres.append(res)

        return success,retres

    def _DomotionIdx(self, name):
        success, devices = self._DomotionDevices()
        idx = 0
        if (success):
            for device in devices:
                if (device['Name'] == name):
                    idx = device['idx']
                    break
        return success, int(idx)


    # TBD: handle connection failures
    # 10 s retry for infinity, log only first 10 retries, then keep retrying in background. log when up
    # check connection by: http://localhost:8080/json.htm?type=command&param=getSunRiseSet, only check for 200 response
    # Done