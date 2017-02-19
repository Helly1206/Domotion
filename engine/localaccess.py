# -*- coding: utf-8 -*-
#########################################################
# SERVICE : localaccess.py                             #
#           Python current sensors, actators and timers #
#                    and db access                      #
#           I. Helwegen 2017                            #
#########################################################
# Make reading static, but thread prototected
####################### IMPORTS #########################
from database import db_read
from threading import Lock
from engine import commandqueue
#########################################################

## WILL BE a dict !!!!
#class sensor:
#   Id = 0
#   Value = 0

#class actuator:
#   Id = 0
#   Value = 0

#class timer:
#   Id = 0
#   Time = 0
#   Active = False #--> time=-1

####################### GLOBALS #########################

#########################################################
# Class : localaccess                                   #
#########################################################
class localaccess(db_read):
    SensorValues = { }
    SensorNames = { }
    ActuatorValues = { }
    ActuatorNames = { }
    TimerValues = { }
    mutex = None
    dbpath = ""
    instance = None

    def __init__(self, idbpath):
        self._initmutex()
        self.SetDBPath(idbpath)
        self._SetInstance(self)
        db_read.__init__(self, idbpath)

    def __del__(self):
        self._SetInstance(None)
        self.SetDBPath("")
        db_read.__del__(self)
        self._delmutex()

    def InitBuffers(self):
        self._acquire()
        self.SensorValues = db_read.FillSensorBuffer(self, self.SensorValues)
        self.ActuatorValues = db_read.FillActuatorBuffer(self, self.ActuatorValues)
        self.TimerValues = db_read.FillTimerBuffer(self, self.TimerValues)
        self.SensorNames = db_read.FillSensorNames(self, self.SensorValues, self.SensorNames)
        self.ActuatorNames = db_read.FillActuatorNames(self, self.ActuatorValues, self.ActuatorNames)
        self._release()
        return

    @classmethod
    def _initmutex(cls):
        cls.mutex = Lock()

    @classmethod
    def _delmutex(cls):
        del cls.mutex

    @classmethod
    def _acquire(cls):
        if (cls.mutex):
            cls.mutex.acquire()
            return True
        else:
            return False

    @classmethod
    def _release(cls):
        if (cls.mutex):
            cls.mutex.release()
            return True
        else:
            return False

    @classmethod
    def SetDBPath(cls,idbpath):
        retval = None
        if (cls._acquire()):
            cls.dbpath = idbpath
            retval = idbpath
        cls._release()
        return retval

    @classmethod
    def GetDBPath(cls):
        if (cls._acquire()):
            idbpath = cls.dbpath
        cls._release()
        return idbpath

    @classmethod
    def _SetInstance(cls,_instance):
        retval = None
        if (cls._acquire()):
            cls.instance = _instance
            retval = _instance
        cls._release()
        return retval

    @classmethod
    def GetSensor(cls, sensor):
        retval = None
        if (cls._acquire()):
            if sensor in cls.SensorValues:
                retval = cls.SensorValues[sensor]
            cls._release()
        return retval

    @classmethod
    def SetSensor(cls, sensor, value):
        retval = None
        if (cls._acquire()):
            if sensor in cls.SensorValues:
                cls.SensorValues[sensor] = value
                retval = value
            cls._release()
        return retval

    @classmethod
    def GetActuator(cls, actuator):
        retval = None
        if (cls._acquire()):
            if actuator in cls.ActuatorValues:
                retval = cls.ActuatorValues[actuator]
            cls._release()
        return retval

    @classmethod
    def SetActuator(cls, actuator, value):
        retval = None
        if (cls._acquire()):
            if actuator in cls.ActuatorValues:
                cls.ActuatorValues[actuator] = value
                retval = value
            cls._release()
        return retval

    @classmethod
    def GetTimer(cls, timer):
        retval = None
        if (cls._acquire()):
            if timer in cls.TimerValues:
                retval = cls.TimerValues[timer]
            cls._release()
        return retval

    @classmethod
    def SetTimer(cls, timer, value):
        retval = None
        if (cls._acquire()):
            if timer in cls.TimerValues:
                cls.TimerValues[timer] = value
                retval = value
            cls._release()
        return retval

    @classmethod
    def FindSensorbyName(cls, Name):
        retkey = None
        if (cls._acquire()):
            for key in cls.SensorNames:
                if (cls.SensorNames[key].lower() == Name.lower()):
                    retkey = key
                    break
            cls._release()
        return retkey

    @classmethod
    def FindActuatorbyName(cls, Name):
        retkey = None
        if (cls._acquire()):
            for key in cls.ActuatorNames:
                if (cls.ActuatorNames[key].lower() == Name.lower()):
                    retkey = key
                    break
            cls._release()
        return retkey

    @classmethod
    def GetSensorNames(cls):
        retkey = None
        if (cls._acquire()):
            retkey = cls.SensorNames
            cls._release()
        return retkey

    @classmethod
    def GetActuatorNames(cls):
        retkey = None
        if (cls._acquire()):
            retkey = cls.ActuatorNames
            cls._release()
        return retkey

    @classmethod
    def GetSensorProperties(cls, key):
        return db_read.GetSensorProperties(cls.instance, key)

    @classmethod
    def GetActuatorProperties(cls, key):
        return db_read.GetActuatorProperties(cls.instance, key)

    @classmethod
    def GetSettingFormat(cls, Setting):
        return db_read.GetSetting(cls.instance, Setting)

    @classmethod
    def GetSetting(cls, Setting):
        Value, Format =  db_read.GetSetting(cls.instance, Setting)
        return Value

    @classmethod
    def GetSensorType(cls, key):
        return db_read.GetSensorType(cls.instance, key)

    @classmethod
    def GetActuatorType(cls, key):
        return db_read.GetActuatorType(cls.instance, key)

    @classmethod
    def GetSensorDigital(cls, key):
        return db_read.GetSensorDigital(cls.instance, key)

    @classmethod
    def GetActuatorDigital(cls, key):
        return db_read.GetActuatorDigital(cls.instance, key)