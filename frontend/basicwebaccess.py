# -*- coding: utf-8 -*-
#########################################################
# SERVICE : basicwebaccess.py                           #
#           Accessing Domotion by http get requests     #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from json import dumps, loads
from engine import localaccess
from engine import commandqueue
#########################################################

####################### GLOBALS #########################
_type = {"None": 0, "Sensor": 1, "Actuator": 2, "Timer": 3, "Holiday": 4}

#########################################################
# Class : basicwebaccess                                #
#########################################################

class basicwebaccess(object):
    def __init__(self, commandqueue, localaccess, memorylog):
        self.commandqueue = commandqueue
        self.localaccess = localaccess
        self.memorylog = memorylog

    def __del__(self):
        pass

    def get(self, tag):
        self.localaccess.SetStatusBusy()
        itype, key = self._findtag(tag)
        if (not key):
            return dumps(["ERROR", tag, "NULL"])
        return dumps(["VALUE", tag, self._getvalue(itype, key)])

    def set(self, tag, value):
        self.localaccess.SetStatusBusy()
        itype, key = self._findtag(tag)
        if (not key):
            return dumps(["ERROR", tag, "NULL"])
        return dumps(["STORED",tag, self._setvalue(itype, key, value)])

    def getall(self, tag):
        self.localaccess.SetStatusBusy()
        retval = None
        if (tag.lower() == "sensors"):
            retval=dumps(["ALL", tag, self.localaccess.GetAscTime(), self.localaccess.GetSensorValues()])
        elif (tag.lower() == "actuators"):
            retval=dumps(["ALL", tag, self.localaccess.GetAscTime(), self.localaccess.GetActuatorValues()])
        elif (tag.lower() == "timers"):
            retval=dumps(["ALL", tag, self.localaccess.GetAscTime(), self.localaccess.GetSunRiseSetMod(), self.localaccess.GetTimerValues()])
        elif (tag.lower() == "holidays"):
            retval=dumps(["ALL", tag, self.localaccess.GetAscTime(), self._values2Dict(self.localaccess.GetHolidayValues())])
        elif (tag.lower() == "log"):
            retval=dumps(["ALL", tag, self.memorylog.readlines()])
        else:
            retval=dumps(["ERROR", tag, "NULL"])
        return retval

    def getinfo(self, tag):
        self.localaccess.SetStatusBusy()
        retval = None
        if (tag.lower() == "sensors"):
            retval=dumps(["INFO", tag, self.localaccess.GetSensors()])
        elif (tag.lower() == "actuators"):
            retval=dumps(["INFO", tag, self.localaccess.GetActuators()])
        elif (tag.lower() == "timers"):
            retval=dumps(["INFO", tag, self.localaccess.GetTimers()])
        elif (tag.lower() == "holidays"):
            retval=dumps(["INFO", tag, self.localaccess.GetHolidays()])
        elif (tag.lower() == "log"):
            retval=dumps(["INFO", tag, self.memorylog.getvalue()])
        else:
            retval=dumps(["ERROR", tag, "NULL"])
        return retval

    def _values2Dict(self, HolidayValues):
        valuesDict = {}
        for value in HolidayValues:
            valuesDict[value[0]] = [value[1],value[2],value[3]]
        return valuesDict

    def _findtag(self, tag):
        itype = _type["None"]
        # first look in sensors
        key = self.localaccess.FindSensorbyName(tag)
        if (key):
            itype = _type["Sensor"]

        if not key: # then look in actuators
            key = self.localaccess.FindActuatorbyName(tag)
            if (key):
                itype = _type["Actuator"]

        if not key: # then look in timers
            key = self.localaccess.FindTimerbyName(tag)
            if (key):
                itype = _type["Timer"]

        if tag.lower() == "timerrecalc":
            itype = _type["Timer"]
            key = -1            
        elif tag.lower() == "holidays":
            itype = _type["Holiday"]
            key = -1            

        return itype, key

    def _getvalue(self, itype, key):
        value = "NA"
        if (itype == _type["Sensor"]):
            value = str(self.localaccess.GetSensor(key))
        elif (itype == _type["Actuator"]):
            value = str(self.localaccess.GetActuator(key))
        elif (itype == _type["Timer"]):
            value = str(self.localaccess.GetTimer(key)) 
        elif (itype == _type["Holiday"]):
            value = str(self.localaccess.GetToday()) 
        return value


    # TBD: setvalue, getall {"1": [0, 123,124]}
    # maxyear
    # test overwriting data
    def _setvalue(self, itype,key, ivalue):
        value = "NA"
        if (itype == _type["Sensor"]):
            value = str(self.commandqueue.put_id("None", key, ivalue, True))
        elif (itype == _type["Actuator"]):
            value = str(self.commandqueue.put_id("None", key, ivalue, False))
        elif (itype == _type["Timer"]):
            try:
                if (key == -1):
                    self.commandqueue.callback("timerrecalc")
                else:
                    val = int(ivalue)
                    value = str(self.localaccess.SetTimer(key, val))
            except:
                value = "ERROR"
        elif (itype == _type["Holiday"]):
            try:
                lst = loads(ivalue)
                __id = list(lst.keys())[0]
                _atype = int(lst[__id][0])
                _start = int(lst[__id][1])
                _end = int(lst[__id][2])
                _id = int(__id)
                if ((_id > 0) and (_start < 1000000) and (_end < 1000000)):
                    if (_start == 0) and (_end == 0):
                        self.localaccess.DeleteHolidaysRow(_id)
                    else:
                        self.localaccess.EditHolidaysRow(_id, _atype, _start, _end)
                    value = {_id: [_atype, _start, _end]}
                    self.commandqueue.callback("timerrecalc")
                else:
                    value = "ERROR"
            except:
                value = "ERROR"
        return value

