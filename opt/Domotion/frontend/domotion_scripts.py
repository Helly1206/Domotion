# -*- coding: utf-8 -*-
#########################################################
# SERVICE : domotion_scripts.py                         #
#           API for scripts built-in functions          #
#           I. Helwegen 2021                            #
#########################################################

####################### IMPORTS #########################
import logging

#########################################################

####################### GLOBALS #########################

#########################################################
# Class : domotion_scripts                              #
#########################################################

class domotion_scripts(object):
    currentValue = 0
    posEdge = 1
    negEdge = 2

    def __init__(self):
        pass

    def __del__(self):
        pass

    def init(self, commandqueue, localaccess, filename):
        self.commandqueue = commandqueue
        self.localaccess = localaccess
        self.logger = logging.getLogger("Domotion.script[" + filename + "]")
        self.logger.info("loaded script")
        self.sensorvalues = self.localaccess.GetSensorValues().copy()
        self.actuatorvalues = self.localaccess.GetActuatorValues().copy()

    def getSensor(self, name, edge = currentValue):
        retval = None
        id = self.localaccess.FindSensorbyName(name)
        value = self.localaccess.GetSensor(id)
        if edge == self.posEdge:
            if value > self.sensorvalues[id]:
                self.sensorvalues[id] = value
                retval = True
            else:
                retval = False
        elif edge == self.negEdge:
            if value < self.sensorvalues[id]:
                self.sensorvalues[id] = value
                retval = True
            else:
                retval = False
        else:
            self.sensorvalues[id] = value
            retval = value
        return retval

    def getActuator(self, name, edge = currentValue):
        retval = None
        id = self.localaccess.FindActuatorbyName(name)
        value = self.localaccess.GetActuator(id)
        if edge == self.posEdge:
            if value > self.actuatorvalues[id]:
                self.actuatorvalues[id] = value
                retval = True
            else:
                retval = False
        elif edge == self.negEdge:
            if value < self.actuatorvalues[id]:
                self.actuatorvalues[id] = value
                retval = True
            else:
                retval = False
        else:
            self.actuatorvalues[id] = value
            retval = value
        return retval

    def setSensor(self, name, value):
        id = self.localaccess.FindSensorbyName(name)
        self.sensorvalues[id] = value
        self.commandqueue.put_id("None", id, value, True)

    def setActuator(self, name, value):
        id = self.localaccess.FindActuatorbyName(name)
        self.actuatorvalues[id] = value
        self.commandqueue.put_id("None", id, value, False)

    def log(self, logString):
        self.logger.info(logString)
