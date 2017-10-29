# -*- coding: utf-8 -*-
#########################################################
# SERVICE : common.py                                   #
#           Python common functions for web app         #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from webdatabase import db_webread
from hashlib import sha256
from os import access, path, urandom
from time import localtime, struct_time, strftime, strptime
from datetime import date, datetime
import locale

class common(db_webread):
    WeekDayDict = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}
    sessionpassword = None
    StatusBusy = False
    secret_key = "@%^&123_domotion_$%#!@"

    def __init__(self):
        self._MakeSessionPassword()
        db_webread.__init__(self, self.GetDBPath())

    def __del__(self):
        db_webread.__del__(self)

    def ErrorHtml(self,error):
        return "%d.html"%error

    def GetSetting(self, Setting):
        Value, Format =  db_webread.GetSetting(self, Setting)
        return Value

    def GetStatus(self, status=0):
        Status = "Unknown"
        if (status == 1):
            Status = "Set value"
        else:
            Status = "Running"
        return Status

    # Password 
    def GetKey(self):
        return self.secret_key

    def HashPass(self, password):
        salted_password = password + self.secret_key
        return sha256(salted_password).hexdigest()

    def IsPassword(self, password):
        result = None
        if (len(password)==64):
            try: result = match(r"([a-fA-F\d]{64})", password).group(0)
            except: pass
        return result is not None

    def _MakeSessionPassword(self):
        if (self.sessionpassword == None):
            self.sessionpassword = self.HashPass(urandom(32))

    def GetSessionPassword(self):
        if (self.sessionpassword == None):
            self._MakeSessionPassword()
        return self.sessionpassword

    # Find DB path
    def GetDBPath(self):
        etcpath = "/etc/Domotion/"
        DBpath = ""
        DB_FILENAME = "Domotion.db"
        # first look in etc
        if path.isfile(path.join(etcpath,DB_FILENAME)):
            DBpath = path.join(etcpath,DB_FILENAME)
        else:
            # then look in home folder
            if path.isfile(path.join(path.expanduser('~'),DB_FILENAME)):
                DBpath = path.join(path.expanduser('~'),DB_FILENAME)
            else:
                # Local folder doesn't work when running from external deployment
                # look in local folder, hope we may write
                if path.isfile(path.join(".",DB_FILENAME)):
                    if access(path.join(".",DB_FILENAME), os.W_OK):
                        DBpath = path.join(".",DB_FILENAME)
                    else: 
                        self.logger.critical("No write access to DB file, exit")
                        exit(1)
                else:
                    self.logger.critical("No DB file found, exit")
                    exit(1)
        return (DBpath)

    # Date/ time
    def TimeNoSec(self):
        strformat=format(locale.nl_langinfo(locale.T_FMT))
        strformat=strformat.replace(":%S", "")
        strformat=strformat.replace("%T", "%H:%M")
        strformat=strformat.replace("%R", "%H:%M")
        strformat=strformat.replace("%r", "%I:%M %p")
        return (strformat)  

    def date(self):
        strformat=format(locale.nl_langinfo(locale.D_FMT))
        strformat=strformat.replace("%y", "%Y")
        return (strformat)

    def GetDateOrd(self, mydate=None):
        if (mydate):
            dt=datetime.strptime(mydate,self.date())
        else:
            tm = localtime()
            dt=date(year=tm.tm_year, month=tm.tm_mon, day=tm.tm_mday)
        return dt.toordinal()

    def DateOrd2Asc(self, dord):
        dt = date.fromordinal(dord)
        return dt.strftime(self.date())

    def GetWeekdayDict(self):
        return self.WeekDayDict

    def HM2local(self, h, m):
        tm = struct_time((0, 0, 0, h, m, 0, 0, 0, 0))
        return (strftime(self.TimeNoSec(), tm))

    def local2HM(self, localtime):  
        tm = strptime(localtime, self.TimeNoSec())
        return [tm.tm_hour,tm.tm_min]

    def Mod2Asc(self, Mod):
        retval = ()
        for md in Mod:
            h = md/60
            m = md%60
            retval=retval+(self.HM2local(h,m),)
        return retval

    def Asc2Mod(self, asc, force=False):
        retval = ()
        if (force): # No localization used with domoticz, which is [hh:mm] !!!
            spl = asc.split(":")
        else:
            spl = self.local2HM(asc)
        return int(spl[0])*60+int(spl[1])

    def GetAscTime(self):
        strformat=("{} {}".format(locale.nl_langinfo(locale.D_FMT),locale.nl_langinfo(locale.T_FMT)))
        strformat=strformat.replace("%y", "%Y")
        return strftime(strformat, localtime())