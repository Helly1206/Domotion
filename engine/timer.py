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
        try:
            counter = 0
            UpdateDone = False
            Modd = localaccess.GetModTime() - 1 # Stating point for first update
            self.logger.info("running")

            while (not self.term.isSet()):
                if (counter <= 0):
                    if (not UpdateDone):
                        UpdateDone = self.UpdateSunRiseSet()
                        if (UpdateDone):
                            localaccess.UpdateToday()
                            UpdateDone = self.UpdateTimers()
                    else:
                        Mod = localaccess.GetModTime()
                        ModAbsDiff = abs(Mod-Modd)
                        if (ModAbsDiff != 0):
                            self.mutex.acquire()
                            if ((Mod == 0) or (ModAbsDiff>1)): # A brand new day or DST switch, recalc
                                UpdateDone = False
                            self._CheckTimersNow(Mod)
                            self.mutex.release()
                            Modd = Mod
                    counter = updatecnt
                sleep(sleeptime)
                counter -= 1

            self.logger.info("terminating")
        except Exception, e:
            self.logger.exception(e)

    def UpdateAll(self, Settings=False):
        retval = self.UpdateSunRiseSet()
        if (retval):
            localaccess.UpdateToday()
            self.UpdateTimers(Settings)
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
        return timecalc().SunRiseSet(date[2], date[1], date[0], lon, lat, zone, date[3])

    def UpdateTimers(self, Settings=False):
        retval = True
        self.mutex.acquire()
        Ids=localaccess.GetTimerIds()

        for Id in Ids:
            self._UpdateTimer(Id, Settings=Settings)
        self.mutex.release()
        return (retval)

    def UpdateOffsetTimer(self, Id):
        self.mutex.acquire()
        self._UpdateTimer(Id, UpdateOffset=True)
        self.mutex.release()

    def _UpdateTimer(self, Id, UpdateOffset=False, Settings=False):
        props=localaccess.GetTimerProperties(Id)
        if (self._TimerToday(props)):
            if (props['Method'] == 0): # Fixed
                localaccess.SetTimer(Id,props['Time'])
            elif (props['Method'] == 1): # Sunrise
                localaccess.SetTimer(Id,localaccess.GetSunRiseSetMod()[0]+props['Minutes_Offset'])
            elif (props['Method'] == 2): # Sunset
                localaccess.SetTimer(Id,localaccess.GetSunRiseSetMod()[1]+props['Minutes_Offset'])
            elif (props['Method'] == 3): # Offset
                if (UpdateOffset):
                    localaccess.SetTimer(Id,localaccess.GetModTime()+props['Minutes_Offset'])
                elif (Settings):
                    localaccess.SetTimer(Id, -1)        
        else:
            localaccess.SetTimer(Id, -1)
        return

    #ActiveDict = {0: "-", 1: "Active", 2: "Inactive"}
    #DaytypeDict = {0: "Normal day", 1: "Home day", 2: "Trip day"}
    def _TimerCheckHoliday(self, home, trip):
        retval = True
        Today = localaccess.GetToday()
        if (Today == 0): #normal day
            if ((home == 1) or (trip == 1)): # active during home or trip, then inactive during normal day
                retval = False
        elif (Today == 1): #home day
            if (home == 2): #inactive during home
                retval = False
            #elif (trip == 1): # active during trip, then inactive during home day
            #    retval = False
        else: #trip day
            if (trip == 2): #inactive during trip
                retval = False
            #elif (home == 1): # active during home, then inactive during trip day
            #    retval = False

        return retval

    def _TimerToday(self, props):
        retval = False
        if self._TimerCheckHoliday(props['Home'],props['Trip']):
            day = localaccess.GetWeekday()
            retval = props[day]
        return (retval)

    def _CheckTimersNow(self, Mod):
        TimerValues = localaccess.GetTimerValues()
        for Id in TimerValues:
            if (TimerValues[Id] == Mod):
                self.commandqueue.put_id("Timer", Id, 1)
                # remove on offset timer, keep the rest intact
                props=localaccess.GetTimerProperties(Id)
                if (props['Method'] == 3): # Offset
                    localaccess.SetTimer(Id, -1)
        return