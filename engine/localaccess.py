# -*- coding: utf-8 -*-
#########################################################
# SERVICE : localaccess.py                             #
#           Python current sensors, actators and timers #
#                    and db access                      #
#           I. Helwegen 2017                            #
#########################################################
# Make reading static, but thread prottected
####################### IMPORTS #########################
from database import db_read
from threading import Lock
from commandqueue import commandqueue
from utilities import localformat
from hashlib import sha256
from re import match
import signal
import logging
from time import sleep, localtime, strftime
from datetime import date, datetime
from os import urandom, system
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
#   Active = False #--> Time=-1

####################### GLOBALS #########################

#########################################################
# Class : AppKiller                                     #
#########################################################
class AppKiller(object):
    kill_now = False
    restart = True
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_app)
        signal.signal(signal.SIGTERM, self.exit_app)
        self.reset_app()

    @classmethod
    def reset_app(cls):
        cls.kill_now = False 
        cls.restart = False

    @classmethod
    def exit_app(cls, signum, frame):
        cls.kill_now = True 
        cls.restart = False

    @classmethod
    def shutdown(cls):
        system("sudo shutdown -h now")
        cls.kill_now = True 
        cls.restart = False

    @classmethod
    def reboot(cls):
        system("sudo shutdown -r now")
        cls.kill_now = True 
        cls.restart = False

    @classmethod
    def restart_app(cls):
        cls.kill_now = True 
        cls.restart = True  

#########################################################
# Class : localaccess                                   #
#########################################################
class localaccess(db_read):
    SensorValues = { }
    SensorNames = { }
    ActuatorValues = { }
    ActuatorNames = { }
    TimerValues = { }
    TimerNames = { }
    mutex = None
    dbpath = ""
    instance = None
    sessionpassword = None
    StatusBusy = False
    secret_key = "@%^&123_domotion_$%#!@"
    sunriseset = (0,0)
    todaytype = 0

    def __init__(self, idbpath):
        self._initmutex()
        self.SetDBPath(idbpath)
        self._SetInstance(self)
        self._MakeSessionPassword()
        self.SetStatusBusy()
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
        self.TimerNames = db_read.FillTimerNames(self, self.TimerValues, self.TimerNames)
        self._release()
        return

    def GetSensorPoll(self, stype):
        retkey = None
        if (self._acquire()):
            retkey = db_read.FindSensorPollbyHardware(self, stype)
            self._release()
        return retkey

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

    # Get/ set from DB

    @classmethod
    def GetSensor(cls, sensor):
        retval = None
        if (cls._acquire()):
            if sensor in cls.SensorValues:
                retval = cls.SensorValues[sensor]
            cls._release()
        return retval

    @classmethod
    def GetSensorValues(cls):
        retval = None
        if (cls._acquire()):
            retval = cls.SensorValues
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
    def GetActuatorValues(cls):
        retval = None
        if (cls._acquire()):
            retval = cls.ActuatorValues
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
    def GetTimerValues(cls):
        retval = None
        if (cls._acquire()):
            retval = cls.TimerValues
            cls._release()
        return retval

    @classmethod
    def GetTimerIds(cls):
        retval = None
        if (cls._acquire()):
            retval = list(cls.TimerValues.keys())
            cls._release()
        return retval

    @classmethod
    def SetTimer(cls, timer, value):
        retval = None
        if (cls._acquire()):
            if timer in cls.TimerValues:
                if (value > 24*60-1):
                    value = value % (24*60)
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
    def GetSensorName(cls, key):
        retkey = None
        if (cls._acquire()):
            retkey = cls.SensorNames[key]
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
    def GetActuatorName(cls, key):
        retkey = None
        if (cls._acquire()):
            retkey = cls.ActuatorNames[key]
            cls._release()
        return retkey

    @classmethod
    def GetTimerName(cls, key):
        retkey = None
        if (cls._acquire()):
            retkey = cls.TimerNames[key]
            cls._release()
        return retkey

    @classmethod
    def GetSensorProperties(cls, key):
        return db_read.GetSensorProperties(cls.instance, key)

    @classmethod
    def GetActuatorProperties(cls, key):
        return db_read.GetActuatorProperties(cls.instance, key)

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

    @classmethod
    def GetTimerProperties(cls, key):
        return db_read.GetTimerProperties(cls.instance, key)

    # Settings

    @classmethod
    def GetSettingFormat(cls, Setting):
        return db_read.GetSetting(cls.instance, Setting)

    @classmethod
    def GetSetting(cls, Setting):
        Value, Format =  db_read.GetSetting(cls.instance, Setting)
        return Value

    # Status light
    @classmethod
    def SetStatusBusy(cls):
        cls.StatusBusy = True

    @classmethod
    def GetStatusBusy(cls):
        LocalStatusBusy = cls.StatusBusy
        cls.StatusBusy = False
        return (LocalStatusBusy)        

    # Password 

    @classmethod 
    def get_key(cls):
        return cls.secret_key

    @classmethod 
    def hash_pass(cls, password):
        salted_password = password + cls.secret_key
        return sha256(salted_password).hexdigest()

    @classmethod
    def ispassword(cls, password):
        result = None
        if (len(password)==64):
            try: result = match(r"([a-fA-F\d]{64})", password).group(0)
            except: pass
        return result is not None

    @classmethod
    def _MakeSessionPassword(cls):
        if (cls.sessionpassword == None):
            cls.sessionpassword = cls.hash_pass(urandom(32))

    @classmethod
    def GetSessionPassword(cls):
        if (cls.sessionpassword == None):
            cls._MakeSessionPassword()
        return cls.sessionpassword

    # Domotion status

    @classmethod
    def GetStatus(cls, status=0):
        Status = "Unknown"
        if (cls.instance != None): 
            if (status == 1):
                Status = "Set value"
            else:
                Status = "Running"
        else:
            Status = "Finished"
        return Status

    # Date/ time

    @classmethod
    def GetAscTime(cls):
        return strftime(localformat.datetime(), localtime())

    @classmethod
    def GetModTime(cls):
        tm = localtime()
        return (tm.tm_hour*60+tm.tm_min)

    @classmethod
    def GetDateDMY(cls):
        tm = localtime()
        return (tm.tm_mday, tm.tm_mon, tm.tm_year, tm.tm_isdst)

    @classmethod
    def GetDateOrd(cls, mydate=None):
        if (mydate):
            dt=datetime.strptime(mydate,localformat.date())
        else:
            d,m,y,dst = cls.GetDateDMY();
            dt=date(year=y, month=m, day=d)
        return dt.toordinal()

    @classmethod
    def DateOrd2Asc(cls, dord):
        dt = date.fromordinal(dord)
        return dt.strftime(localformat.date())

    @classmethod
    def GetWeekday(cls):
        return localformat.GetWeekday(int(strftime("%w", localtime())))  

    @classmethod
    def GetSunRiseSetMod(cls):
        retval = None
        if (cls._acquire()):
            retval = cls.sunriseset
            cls._release()
        return retval

    @classmethod
    def SetSunRiseSetMod(cls,srise,sset):
        if (cls._acquire()):
            cls.sunriseset = (srise,sset)
            cls._release()
        return 

    @classmethod
    def GetToday(cls):
        retval = None
        if (cls._acquire()):
            retval = cls.todaytype
            cls._release()
        return retval    

    @classmethod
    def UpdateToday(cls):
        retval = None
        if (cls._acquire()):
            retval = cls._UpdateToday()
            cls.todaytype = retval
            cls._release()
        return retval   

    @classmethod
    def _UpdateToday(cls):
        data = db_read.GetHolidays(cls.instance)
        today_ord = cls.GetDateOrd()
        today = 0
        for row in data:
            if ((today_ord >= row[2]) and (today_ord <= row[3])):
                if (row[1] == 0):
                    if (today < 2):
                        today = 1
                else:
                    today = 2
        return today
