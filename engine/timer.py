# -*- coding: utf-8 -*-
#########################################################
# SERVICE : timer.py                                    #
#           Python timer handling Domotion              #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from threading import Thread, Event, Lock
import logging
from time import sleep
from localaccess import localaccess
from commandqueue import commandqueue
from utilities import timecalc
#########################################################

####################### GLOBALS #########################
sleeptime = 0.1
updatecnt = (1/sleeptime)

#########################################################
# Class : timer                                         #
#########################################################
class timer(Thread):
    def __init__(self, commandqueue):
        self.domoticz_api = None
        self.instances_loaded = False
        self.commandqueue=commandqueue
        self.logger = logging.getLogger('Domotion.Timer')
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        self.mutex = Lock()
        
    def __del__(self):
        del self.mutex
        del self.term
        self.domoticz_api = None
        self.instances_loaded = False
        self.logger.info("finished")

    def instances(self, domoticz_api):
        self.mutex.acquire()
        self.domoticz_api = domoticz_api
        self.instances_loaded = True
        self.mutex.release()

    def terminate(self):
        self.term.set()

    def run(self):
        counter = 0
        Modd = 0
        UpdateDone = False
        self.logger.info("running")

        while (not self.term.isSet()):
            if (counter <= 0):
                if (not UpdateDone):
                    UpdateDone = self.UpdateSunRiseSet()
                    if (UpdateDone):
                        UpdateDone = self.UpdateTimers()
                else:
                    Mod = localaccess.GetModTime()
                    if (Mod != Modd):
                        self.mutex.acquire()
                        if (Mod == 0): # A brand new day
                            UpdateDone = False
                        self._CheckTimersNow(Mod)
                        self.mutex.release()
                counter = updatecnt
            sleep(sleeptime)
            counter -= 1

        self.logger.info("terminating")

    def UpdateAll(self):
        retval = self.UpdateSunRiseSet()
        if (retval):
            self.UpdateTimers()
        return (retval)

    def UpdateSunRiseSet(self):
        retval = False
        self.mutex.acquire()
        if (self.instances_loaded):
            retval = True
            if (localaccess.GetSetting('Domoticz_sun') and localaccess.GetSetting('Domoticz_frontend') and (self.domoticz_api)):
                success, srise, sset = self.domoticz_api.getSunRiseSet()
                if (not success):
                    self.logger.info("Updating sunrise/ sunset from domoticz failed, calculate locally")
            else:
                success = False
            if (not success):
                srise, sset = self._UpdateFromTimecalc()
            localaccess.SetSunRiseSetMod(srise,sset)
        self.mutex.release()
        return (retval)

    def _UpdateFromTimecalc(self):
        date = localaccess.GetDateDMY()
        lon = localaccess.GetSetting('Longitude')
        lat = localaccess.GetSetting('Latitude')
        zone = localaccess.GetSetting('Timezone')
        return timecalc().SunRiseSet(date[2], date[1], date[0], lon, lat, zone)

    def UpdateTimers(self):
        retval = True
        self.mutex.acquire()
        Ids=localaccess.GetTimerIds()

        for Id in Ids:
            self._UpdateTimer(Id)
        self.mutex.release()
        return (retval)

    def UpdateOffsetTimer(self, Id):
        self.mutex.acquire()
        self._UpdateTimer(Id, True)
        self.mutex.release()

    def _UpdateTimer(self, Id, UpdateOffset=False):
        props=localaccess.GetTimerProperties(Id)
        if (self._TimerToday(props)):
            if (props['Method'] == 0): # Fixed
                localaccess.SetTimer(Id,props['Hour']*60+props['Minute'])
            elif (props['Method'] == 1): # Sunrise
                localaccess.SetTimer(Id,localaccess.GetSunRiseSetMod()[0]+props['Minutes_Offset'])
            elif (props['Method'] == 2): # Sunset
                localaccess.SetTimer(Id,localaccess.GetSunRiseSetMod()[1]+props['Minutes_Offset'])
            elif (props['Method'] == 3): # Offset
                if (UpdateOffset):
                    localaccess.SetTimer(Id,localaccess.GetModTime()+props['Minutes_Offset'])
                else:
                    localaccess.SetTimer(Id, -1)        
        else:
            localaccess.SetTimer(Id, -1)

        return

    def _TimerToday(self, props):
        day = localaccess.GetWeekday()
        return (props[day])

    def _CheckTimersNow(self, Mod):
        TimerValues = localaccess.GetTimerValues()
        for Id in TimerValues:
            if (TimerValues[Id] == Mod):
                self.commandqueue.put_id("Timer", Id, 1)
        return