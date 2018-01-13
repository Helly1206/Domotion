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
import signal
from time import localtime, strftime
import locale
from datetime import date
import os
import sys
import subprocess
#########################################################

####################### GLOBALS #########################

#########################################################
# Class : AppKiller                                     #
#########################################################
class AppKiller(object):
    def __init__(self):
        self.kill_now = False
        self.restart = True
        signal.signal(signal.SIGINT, self.exit_app)
        signal.signal(signal.SIGTERM, self.exit_app)
        self.reset_app()

    def reset_app(self):
        self.kill_now = False 
        self.restart = False

    def exit_app(self, signum, frame):
        self.kill_now = True 
        self.restart = False

    def shutdown(self):
        if self._RunShell("shutdown -h now"):
            self.kill_now = True 
            self.restart = False

    def reboot(self):
        if self._RunShell("shutdown -r now"):
            self.kill_now = True 
            self.restart = False

    def restart_app(self):
        self.kill_now = True 
        self.restart = True  

    def restart_all(self):
        self.restart_webservers()
        self.restart_app()  

    def restart_webservers(self):
        self._RunShell("systemctl restart DomoWeb")
        try:
            sFile = os.path.abspath(sys.modules['__main__'].__file__)
        except:
            sFile = "."
        cmd = os.path.join(os.path.dirname(sFile),"Apache2Config") + " -q"
        self._RunShell(cmd)

    def _RunShell(self, command):
        with open(os.devnull, 'w')  as devnull:
            try:
                osstdout = subprocess.check_call(command.split(), stdout=devnull, stderr=devnull)
            except subprocess.CalledProcessError:
                return 1
        return osstdout

#########################################################
# Class : localaccess                                   #
#########################################################
class localaccess(db_read):
    _WeekDayDict = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}
    def __init__(self, idbpath):
        self.SensorValues = { }
        self.SensorNames = { }
        self.ActuatorValues = { }
        self.ActuatorNames = { }
        self.TimerValues = { }
        self.TimerNames = { }
        self.mutex = None
        self.StatusBusy = False
        self.sunriseset = (0,0)
        self.todaytype = 0
        self._initmutex()
        self.SetStatusBusy()
        db_read.__init__(self, idbpath)
        locale.setlocale(locale.LC_TIME,'')

    def __del__(self):
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

    def _initmutex(self):
        self.mutex = Lock()

    def _delmutex(self):
        del self.mutex

    def _acquire(self):
        if (self.mutex):
            self.mutex.acquire()
            return True
        else:
            return False

    def _release(self):
        if (self.mutex):
            self.mutex.release()
            return True
        else:
            return False

    # Get/ set from DB
    def GetSensor(self, sensor):
        retval = None
        if (self._acquire()):
            if sensor in self.SensorValues:
                retval = self.SensorValues[sensor]
            self._release()
        return retval

    def GetSensorValues(self):
        retval = None
        if (self._acquire()):
            retval = self.SensorValues
            self._release()
        return retval

    def SetSensor(self, sensor, value):
        retval = None
        if (self._acquire()):
            if sensor in self.SensorValues:
                self.SensorValues[sensor] = value
                retval = value
            self._release()
        return retval

    def GetActuator(self, actuator):
        retval = None
        if (self._acquire()):
            if actuator in self.ActuatorValues:
                retval = self.ActuatorValues[actuator]
            self._release()
        return retval

    def GetActuatorValues(self):
        retval = None
        if (self._acquire()):
            retval = self.ActuatorValues
            self._release()
        return retval

    def SetActuator(self, actuator, value):
        retval = None
        if (self._acquire()):
            if actuator in self.ActuatorValues:
                self.ActuatorValues[actuator] = value
                retval = value
            self._release()
        return retval

    def GetTimerValues(self):
        retval = None
        if (self._acquire()):
            retval = self.TimerValues
            self._release()
        return retval

    def GetTimer(self, timer):
        retval = None
        if (self._acquire()):
            if timer in self.TimerValues:
                retval = self.TimerValues[timer]
            self._release()
        return retval

    def GetTimerIds(self):
        retval = None
        if (self._acquire()):
            retval = list(self.TimerValues.keys())
            self._release()
        return retval

    def SetTimer(self, timer, value):
        retval = None
        if (self._acquire()):
            if timer in self.TimerValues:
                if (value > 24*60-1):
                    value = value % (24*60)
                self.TimerValues[timer] = value
                retval = value
            self._release()
        return retval

    def FindSensorbyName(self, Name):
        retkey = None
        if (self._acquire()):
            for key in self.SensorNames:
                if (self.SensorNames[key].lower() == Name.lower()):
                    retkey = key
                    break
            self._release()
        return retkey

    def FindActuatorbyName(self, Name):
        retkey = None
        if (self._acquire()):
            for key in self.ActuatorNames:
                if (self.ActuatorNames[key].lower() == Name.lower()):
                    retkey = key
                    break
            self._release()
        return retkey

    def FindTimerbyName(self, Name):
        retkey = None
        if (self._acquire()):
            for key in self.TimerNames:
                if (self.TimerNames[key].lower() == Name.lower()):
                    retkey = key
                    break
            self._release()
        return retkey

    def GetSensorNames(self):
        retkey = None
        if (self._acquire()):
            retkey = self.SensorNames
            self._release()
        return retkey

    def GetSensorName(self, key):
        retkey = None
        if (self._acquire()):
            retkey = self.SensorNames[key]
            self._release()
        return retkey

    def GetActuatorNames(self):
        retkey = None
        if (self._acquire()):
            retkey = self.ActuatorNames
            self._release()
        return retkey

    def GetActuatorName(self, key):
        retkey = None
        if (self._acquire()):
            retkey = self.ActuatorNames[key]
            self._release()
        return retkey

    def GetTimerName(self, key):
        retkey = None
        if (self._acquire()):
            retkey = self.TimerNames[key]
            self._release()
        return retkey

    #def GetSensorProperties(self, key):
    #    return db_read.GetSensorProperties(self, key)

    #def GetActuatorProperties(self, key):
    #    return db_read.GetActuatorProperties(self, key)

    #def GetSensorType(self, key):
    #    return db_read.GetSensorType(self, key)

    #def GetActuatorType(self, key):
    #    return db_read.GetActuatorType(self, key)

    #def GetSensorDigital(self, key):
    #    return db_read.GetSensorDigital(self, key)

    #def GetActuatorDigital(self, key):
    #    return db_read.GetActuatorDigital(self, key)

    #def GetTimerProperties(self, key):
    #    return db_read.GetTimerProperties(self, key)

    # Settings

    #def GetSetting(self, Setting):
    #    Value, Format =  db_read.GetSetting(self.instance, Setting)
    #    return Value

    # Status light
    def SetStatusBusy(self):
        self.StatusBusy = True

    def GetStatusBusy(self):
        LocalStatusBusy = self.StatusBusy
        self.StatusBusy = False
        return (LocalStatusBusy)        

    # Date/ time
    def GetModTime(self):
        tm = localtime()
        return (tm.tm_hour*60+tm.tm_min)

    def GetDateDMY(self):
        tm = localtime()
        return (tm.tm_mday, tm.tm_mon, tm.tm_year, tm.tm_isdst)

    def GetWeekday(self):
        return self._WeekDayDict[int(strftime("%w", localtime()))]

    def GetAscTime(self):
        return strftime(self.datetime(), localtime())

    def GetSunRiseSetMod(self):
        retval = None
        if (self._acquire()):
            retval = self.sunriseset
            self._release()
        return retval

    def SetSunRiseSetMod(self,srise,sset):
        if (self._acquire()):
            self.sunriseset = (srise,sset)
            self._release()
        return 

    def GetToday(self):
        retval = None
        if (self._acquire()):
            retval = self.todaytype
            self._release()
        return retval    

    def UpdateToday(self):
        retval = None
        if (self._acquire()):
            data = db_read.GetHolidayValues(self)
            d,m,y,dst = self.GetDateDMY()
            today_ord = date(year=y, month=m, day=d).toordinal()
            # First delete old holdidays
            ids = []
            for row in data:
                if (today_ord > row[3]):
                    ids.append(row[0]) 
            for id in ids:
                self.DeleteHolidaysRow(id)
            # then update today
            data = db_read.GetHolidayValues(self)
            today = 0
            for row in data:
                if ((today_ord >= row[2]) and (today_ord <= row[3])):
                    if (row[1] == 0):
                        if (today < 2):
                            today = 1
                    else:
                        today = 2
            self.todaytype = today
            self._release()
        return retval   

    def datetime(self):
        strformat=("{} {}".format(locale.nl_langinfo(locale.D_FMT),locale.nl_langinfo(locale.T_FMT)))
        strformat=strformat.replace("%y", "%Y")
        return (strformat)       

    def Asc2Mod(self, asc):
        spl = asc.split(":")
        return int(spl[0])*60+int(spl[1])