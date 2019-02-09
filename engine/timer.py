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
from .localaccess import localaccess
from .commandqueue import commandqueue
from utilities.timecalc import timecalc
#########################################################

####################### GLOBALS #########################
sleeptime = 0.1
updatecnt = (1/sleeptime)

#########################################################
# Class : timer                                         #
#########################################################
class timer(Thread):
    def __init__(self, commandqueue, localaccess):
        self.domoticz_api = None
        self.instances_loaded = False
        self.commandqueue=commandqueue
        self.localaccess=localaccess
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
            Modd = self.localaccess.GetModTime() - 1 # Stating point for first update
            self.logger.info("running")

            while (not self.term.isSet()):
                if (counter <= 0):
                    if (not UpdateDone):
                        UpdateDone = self.UpdateSunRiseSet()
                        if (UpdateDone):
                            self.localaccess.UpdateToday()
                            UpdateDone = self.UpdateTimers()
                    else:
                        Mod = self.localaccess.GetModTime()
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
        except Exception as e:
            self.logger.exception(e)

    def UpdateAll(self, Settings=False):
        retval = self.UpdateSunRiseSet()
        if (retval):
            self.localaccess.UpdateToday()
            self.UpdateTimers(Settings)
        return (retval)

    def UpdateSunRiseSet(self):
        retval = False
        self.mutex.acquire()
        if (self.instances_loaded):
            retval = True
            if (self.localaccess.GetSetting('Domoticz_sun') and self.localaccess.GetSetting('Domoticz_frontend') and (self.domoticz_api)):
                success, srise, sset = self.domoticz_api.getSunRiseSet()
                if (success):
                    self.logger.info("Updating sunrise/ sunset: from domoticz")
            else:
                success = False
            if (not success):
                srise, sset = self._UpdateFromTimecalc()
                self.logger.info("Updating sunrise/ sunset: calculated locally")
            self.localaccess.SetSunRiseSetMod(srise,sset)
        self.mutex.release()
        return (retval)

    def _UpdateFromTimecalc(self):
        date = self.localaccess.GetDateDMY()
        lon = self.localaccess.GetSetting('Longitude')
        lat = self.localaccess.GetSetting('Latitude')
        zone = self.localaccess.GetSetting('Timezone')
        return timecalc().SunRiseSet(date[2], date[1], date[0], lon, lat, zone, date[3])

    def UpdateTimers(self, Settings=False):
        retval = True
        self.mutex.acquire()
        Ids=self.localaccess.GetTimerIds()

        for Id in Ids:
            self._UpdateTimer(Id, Settings=Settings)
        self.mutex.release()
        return (retval)

    def UpdateOffsetTimer(self, Id):
        self.mutex.acquire()
        self._UpdateTimer(Id, UpdateOffset=True)
        self.mutex.release()

    def _UpdateTimer(self, Id, UpdateOffset=False, Settings=False):
        props=self.localaccess.GetTimerProperties(Id)
        if (self._TimerToday(props)):
            if (props['Method'] == 0): # Fixed
                self.localaccess.SetTimer(Id,props['Time'])
            elif (props['Method'] == 1): # Sunrise
                self.localaccess.SetTimer(Id,self.localaccess.GetSunRiseSetMod()[0]+props['Minutes_Offset'])
            elif (props['Method'] == 2): # Sunset
                self.localaccess.SetTimer(Id,self.localaccess.GetSunRiseSetMod()[1]+props['Minutes_Offset'])
            elif (props['Method'] == 3): # Offset
                if (UpdateOffset):
                    self.localaccess.SetTimer(Id,self.localaccess.GetModTime()+props['Minutes_Offset'])
                elif (Settings):
                    self.localaccess.SetTimer(Id, -1)        
        else:
            self.localaccess.SetTimer(Id, -1)
        return

    #ActiveDict = {0: "-", 1: "Active", 2: "Inactive"}
    #DaytypeDict = {0: "Normal day", 1: "Home day", 2: "Trip day"}
    def _TimerCheckHoliday(self, home, trip):
        retval = True
        Today = self.localaccess.GetToday()
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
            day = self.localaccess.GetWeekday()
            retval = props[day]
        return (retval)

    def _CheckTimersNow(self, Mod):
        TimerValues = self.localaccess.GetTimerValues()
        for Id in TimerValues:
            if (TimerValues[Id] == Mod):
                self.commandqueue.put_id("Timer", Id, 1)
                # remove on offset timer, keep the rest intact
                props=self.localaccess.GetTimerProperties(Id)
                if (props['Method'] == 3): # Offset
                    self.localaccess.SetTimer(Id, -1)
        return