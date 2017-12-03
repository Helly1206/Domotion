# -*- coding: utf-8 -*-
#########################################################
# SERVICE : basicwebaccess.py                           #
#           Accessing Domotion by http get requests     #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from engine import localaccess
from engine import commandqueue
#########################################################

####################### GLOBALS #########################

#########################################################
# Class : basicwebaccess                                #
#########################################################
#"STORED"
#"VALUE"
#"ERROR"
#["STORED","Name","Ivo"]

class basicwebaccess(object):
    def __init__(self, commandqueue, localaccess):
        self.commandqueue = commandqueue
        self.localaccess = localaccess

    def __del__(self):
        pass

    def get(self,tag):
        issensor, key = self._findtag(tag)
        if (not key):
            return '["ERROR","%s","NULL"]'%(tag)
        return '["VALUE","%s","%s"]'%(tag,self._getvalue(issensor, key))

    def set(self,tag,value):
        issensor, key = self._findtag(tag)
        if (not key):
            return '["ERROR","%s","NULL"]'%(tag)
        return '["STORED","%s","%s"]'%(tag,self._setvalue(issensor, key, value))


    def _findtag(self,tag):
        IsSensor = False
        # first look in sensors
        key = self.localaccess.FindSensorbyName(tag)

        if (key):
            IsSensor = True
        else: # then look in actuators
            key = self.localaccess.FindActuatorbyName(tag)
        return IsSensor,key

    def _getvalue(self,issensor,key):
        if (issensor):
            value = str(self.localaccess.GetSensor(key))
        else:
            value = str(self.localaccess.GetActuator(key))
        return value

    def _setvalue(self,issensor,key, ivalue):
        return self.commandqueue.put_id("None",key, ivalue, issensor)
