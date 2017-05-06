# -*- coding: utf-8 -*-
#########################################################
# SERVICE : db_read                                     #
#           Reading and processing db for home control  #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from sqlitedb import sqlitedb
from engine import localaccess
from utilities import localformat

#########################################################

####################### GLOBALS #########################
HolidayDict = {0: "Home", 1: "Trip"}
DaytypeDict = {0: "Normal day", 1: "Home day", 2: "Trip day"}

#########################################################
# Class : db_read                                       #
#########################################################

class db_status(object):
    def __init__(self, dbpath):
        self.db=sqlitedb(dbpath)

    def __del__(self):
        del self.db

    def GetDevices(self, tableid): 
        # Id, Name, Description : Digital
        if (tableid == 'devices'):
            cols=self.db.GetColNames("actuators")[:3]
            data=[seq[:3] for seq in self.db.ReadTable("actuators")]
            cols, data=self._AddActuatorValues(cols, data)
            digital = self._GetDigital("actuators")
        else:
            cols=self.db.GetColNames("sensors")[:3]
            data=[seq[:3] for seq in self.db.ReadTable("sensors")]
            cols, data=self._AddSensorValues(cols, data)
            digital = self._GetDigital("sensors")
        return cols, data, digital

    def GetTimers(self, values=True):
        cols=self.db.GetColNames("timers")[:3]
        data=[seq[:3] for seq in self.db.ReadTable("timers")]
        if (values):
            cols, data=self._AddTimerValues(cols, data)
        return cols, data

    def GetHolidays(self):
        cols=self.db.GetColNames("holidays")[:4]
        cols+=("Today",)
        data=[seq[:4] for seq in self.db.ReadTable("holidays")]
        data=self._LookupType(cols, data)
        data=self._GetToday(cols, data)
        data=self._LookupAscDates(cols, data)
        return cols, data

    def DeleteOldHolidays(self):
        cols=self.db.GetColNames("holidays")[:4]
        data=[seq[:4] for seq in self.db.ReadTable("holidays")]
        ids = self._GetOldies(cols,data)
        for id in ids:
            self.DeleteHolidaysRow(id)
        return cols, data

    def AddHolidaysRow(self):
        rowdict = {}
        rowdict['Start'] = str(localaccess.GetDateOrd())
        rowdict['End'] = str(localaccess.GetDateOrd())
        return (self.db.AddRow("holidays",rowdict))

    def DeleteHolidaysRow(self, id):
        self.db.DeleteRow("holidays", "Id", id)
        return 

    def EditHolidaysRow(self, id, result):
        if not result['Button'] == 'Ok':
            return
        rowdict = {}
        cols=self.db.GetColNames("holidays")
        for col in cols:
            if (col == "Start") or (col == "End"):
                rowdict[col]=str(localaccess.GetDateOrd(result[col]))
            elif not col == "Id":
                if (result[col]):
                    rowdict[col]=result[col]
        self.db.UpdateRow("holidays", rowdict, "Id", id)
        return

    def BuildOptionsDicts(self, tableid):
        DictList = []
        
        if (tableid.lower() == "holidays"):
            DictList.append(HolidayDict)
        return DictList

    def GetTodayString(self):
        return DaytypeDict[localaccess.GetToday()] 

    def _GetDigital(self,table):
        digital = {}
        if (table.lower() == "sensors"):
            stypes = dict(self.db.SelectColumnFromTable("sensors", "Id,SensorType"))
            types = dict(self.db.SelectColumnFromTable("sensortypes", "Id,Digital"))
        elif (table.lower() == "actuators"):
            stypes = dict(self.db.SelectColumnFromTable("actuators", "Id,ActuatorType"))
            types = dict(self.db.SelectColumnFromTable("actuatortypes", "Id,Digital"))
        for key in stypes:
            digital[key] = types[int(stypes[key])]
        return digital

    def _GetColumn(self, cols, name):
        i = 0
        retcol = -1
        for colname in cols:
            if (colname.lower() == name.lower()):
                retcol = i
            i += 1

        return retcol

    def _LookupType(self, cols, data):
        type_col = self._GetColumn(cols,"type")
        newdata = []
        for row in data:
            type = HolidayDict[row[type_col]]
            newrow = row[:type_col] + (type,) + row[type_col+1:]
            newdata.append(newrow)
        return newdata

    def _GetToday(self, cols, data):
        start_col = self._GetColumn(cols,"start")
        end_col = self._GetColumn(cols,"end")
        today_ord = localaccess.GetDateOrd()
        newdata = []
        for row in data:
            if ((today_ord >= row[start_col]) and (today_ord <= row[end_col])):
                today = "True"
            else:
                today = "False"
            newrow = row + (today,)
            newdata.append(newrow)
        return newdata    

    def _GetOldies(self, cols, data):
        id_col = self._GetColumn(cols,"id")
        end_col = self._GetColumn(cols,"end")
        today_ord = localaccess.GetDateOrd()
        ids = []
        for row in data:
            if (today_ord > row[end_col]):
                ids.append(row[id_col])    
        return ids

    def _LookupAscDates(self, cols, data):
        start_col = self._GetColumn(cols,"start")
        end_col = self._GetColumn(cols,"end")
        newdata = []
        for row in data:
            startasc = localaccess.DateOrd2Asc(row[start_col])
            endasc = localaccess.DateOrd2Asc(row[end_col])
            newrow = row[:start_col] + (startasc,) + (endasc,) + row[end_col+1:]
            newdata.append(newrow)
        return newdata

    def _AddActuatorValues(self, cols, data):
        newcol = cols + ["Value"]
        vals = localaccess.GetActuatorValues()
        newdata = []
        for row in data:
            addval = 0
            for key in vals:
                if key == row[0]:
                    addval = vals[key]
            newrow = row + (addval,)
            newdata.append(newrow)
        return newcol, newdata

    def _AddSensorValues(self, cols, data):
        newcol = cols + ["Value"]
        vals = localaccess.GetSensorValues()
        newdata = []
        for row in data:
            addval = 0
            for key in vals:
                if key == row[0]:
                    addval = vals[key]
            newrow = row + (addval,)
            newdata.append(newrow)
        return newcol, newdata

    def _AddTimerValues(self, cols, data):
        newcol = cols + ["Time","Active"]
        vals = localaccess.GetTimerValues()
        newdata = []
        for row in data:
            ttime = localformat.Mod2Asc((0,))[0]
            active = 'False'
            for key in vals:
                if key == row[0]:
                    if (vals[key] >= 0):
                        ttime = localformat.Mod2Asc((vals[key],))[0]
                        active = 'True'
            newrow = row + (ttime,) + (active,)
            newdata.append(newrow)
        return newcol, newdata