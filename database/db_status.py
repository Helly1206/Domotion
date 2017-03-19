# -*- coding: utf-8 -*-
#########################################################
# SERVICE : db_read                                     #
#           Reading and processing db for home control  #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from sqlitedb import sqlitedb

#########################################################

####################### GLOBALS #########################

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
            digital = self._GetDigital("actuators")
        else:
            cols=self.db.GetColNames("sensors")[:3]
            data=[seq[:3] for seq in self.db.ReadTable("sensors")]
            digital = self._GetDigital("sensors")
        return cols, data, digital

    def GetTimers(self):
        cols=self.db.GetColNames("timers")[:3]
        data=[seq[:3] for seq in self.db.ReadTable("timers")]
        return cols, data

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
