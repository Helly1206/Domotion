# -*- coding: utf-8 -*-
#########################################################
# SERVICE : localformat.py                              #
#           Python locale formatting                    #
#           I. Helwegen 2017                            #
#########################################################
# Make reading static, but thread prottected
####################### IMPORTS #########################
from time import struct_time, strftime, strptime
import locale
#########################################################

####################### GLOBALS #########################
WeekDayDict = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}

#########################################################
# Class : localformat                                   #
#########################################################  
class localformat(object):
    @classmethod
    def init(cls):
        #locale.setlocale(locale.LC_TIME,'en_US.utf8')
        locale.setlocale(locale.LC_TIME,'')

    @classmethod
    def datetime(cls):
        strformat=("{} {}".format(locale.nl_langinfo(locale.D_FMT),locale.nl_langinfo(locale.T_FMT)))
        strformat=strformat.replace("%y", "%Y")
        return (strformat)

    @classmethod
    def date(cls):
        strformat=format(locale.nl_langinfo(locale.D_FMT))
        strformat=strformat.replace("%y", "%Y")
        return (strformat)

    @classmethod
    def time(cls):
        strformat=format(locale.nl_langinfo(locale.T_FMT))
        return (strformat)        

    @classmethod
    def timenosec(cls):
        strformat=format(locale.nl_langinfo(locale.T_FMT))
        strformat=strformat.replace(":%S", "")
        strformat=strformat.replace("%T", "%H:%M")
        strformat=strformat.replace("%R", "%H:%M")
        strformat=strformat.replace("%r", "%I:%M %p")
        return (strformat)  

    @classmethod
    def HM2local(cls, h, m):
        tm = struct_time((0, 0, 0, h, m, 0, 0, 0, 0))
        return (strftime(localformat.timenosec(), tm))

    @classmethod
    def local2HM(cls, localtime):  
        tm = strptime(localtime, localformat.timenosec())
        return [tm.tm_hour,tm.tm_min]

    @classmethod
    def Mod2Asc(cls, Mod):
        retval = ()
        for md in Mod:
            h = md/60
            m = md%60
            retval=retval+(localformat.HM2local(h,m),)
        return retval

    @classmethod
    def Asc2Mod(cls, asc, force=False):
        retval = ()
        if (force): # No localization used with domoticz, which is [hh:mm] !!!
            spl = asc.split(":")
        else:
            spl = localformat.local2HM(asc)
        return int(spl[0])*60+int(spl[1])

    @classmethod
    def GetWeekday(cls, day):
        return WeekDayDict[day]

    @classmethod
    def GetWeekdayDict(cls):
        return WeekDayDict