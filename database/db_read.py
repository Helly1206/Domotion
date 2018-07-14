# -*- coding: utf-8 -*-
#########################################################
# SERVICE : db_read sqlitedb                            #
#           Reading and processing db for home control  #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
import sqlite3

#########################################################

####################### GLOBALS #########################

#########################################################
# Class : db_read                                       #
#########################################################

class db_read(object):
    def __init__(self, dbpath):
        self.conn = sqlite3.connect(dbpath, check_same_thread=False)
        self.OperationalError = sqlite3.OperationalError

    def __del__(self):
        # Closing the connection to the database file
        self.conn.close()

    def FillSensorBuffer(self,SensorDict):
        sensors=dict(self._SelectColumnFromTable("sensors", "Id,Type"))
        isoutput=dict(self._SelectColumnFromTable("types", "Id,IsOutput"))

        # Add new ones, don't update existing values
        for key in sensors:
            if sensors[key] != 0:
                if not isoutput[sensors[key]]:
                    if not key in SensorDict:
                        SensorDict[key]=0

        #remove old ones
        for key in SensorDict.copy():
            if not key in sensors:
                del SensorDict[key]
            elif sensors[key] == 0:
                del SensorDict[key]
            elif isoutput[sensors[key]]:
                del SensorDict[key]
                
        return SensorDict

    def FillActuatorBuffer(self,ActuatorDict):
        actuators=dict(self._SelectColumnFromTable("actuators", "Id,Type"))
        isoutput=dict(self._SelectColumnFromTable("types", "Id,IsOutput"))

        # Add new ones, don't update existing values
        for key in actuators:
            if actuators[key] != 0:
                if isoutput[actuators[key]]:
                    if not key in ActuatorDict:
                        ActuatorDict[key]=0

        #remove old ones
        for key in ActuatorDict.copy():
            if not key in actuators:
                del ActuatorDict[key]
            elif actuators[key] == 0:
                del ActuatorDict[key]
            elif not isoutput[actuators[key]]:
                del ActuatorDict[key]

        return ActuatorDict

    def FillTimerBuffer(self,TimerDict):
        timertups=self._SelectColumnFromTable("timers", "Id")
        timers=map(lambda y: y[0], timertups)

        # Add new ones, don't update existing values
        for key in timers:
            if not key in TimerDict:
                TimerDict[key]=-1

        #remove old ones
        for key in TimerDict.copy():
            if not key in timers:
                del TimerDict[key]

        return TimerDict

    def FillSensorNames(self, SensorDict, Names):
        sensors=dict(self._SelectColumnFromTable("sensors", "Id,Name"))
        # add new ones and update
        for key in SensorDict:
            Names[key]=sensors[key]

        #remove old ones
        for key in Names.copy():
            if not key in SensorDict:
                del Names[key]

        return Names

    def FillActuatorNames(self, ActuatorDict, Names):
        actuators=dict(self._SelectColumnFromTable("actuators", "Id,Name"))
        # add new ones and update
        for key in ActuatorDict:
            Names[key]=actuators[key]
        
        #remove old ones
        for key in Names.copy():
            if not key in ActuatorDict:
                del Names[key]

        return Names

    def FillTimerNames(self, TimerDict, Names):
        timers=dict(self._SelectColumnFromTable("timers", "Id,Name"))
        # add new ones and update
        for key in TimerDict:
            Names[key]=timers[key]
        
        #remove old ones
        for key in Names.copy():
            if not key in TimerDict:
                del Names[key]

        return Names

    def GetSensors(self):
        digital = {}
        cols=self._GetColNames("sensors")[:3]+[self._GetColNames("sensors")[9]]+[self._GetColNames("sensortypes")[3]]
        stypes = dict(self._SelectColumnFromTable("sensors", "Id,SensorType"))
        types = dict(self._SelectColumnFromTable("sensortypes", "Id,Digital"))
        for key in stypes:
            digital[key] = types[int(stypes[key])]
        data=[seq[:3]+(seq[9],digital[seq[0]]) for seq in self._ReadTable("sensors")]
        #digital, dtype = self._GetDigitalType("sensors")
        return cols, data

    def GetActuators(self):
        digital = {}
        cols=self._GetColNames("actuators")[:3]+[self._GetColNames("actuators")[11]]+[self._GetColNames("actuatortypes")[3]]
        atypes = dict(self._SelectColumnFromTable("actuators", "Id,ActuatorType"))
        types = dict(self._SelectColumnFromTable("actuatortypes", "Id,Digital"))
        for key in atypes:
            digital[key] = types[int(atypes[key])]
        data=[seq[:3]+(seq[11],digital[seq[0]]) for seq in self._ReadTable("actuators")]
        #digital, dtype = self._GetDigitalType("actuators")
        return cols, data

    def GetTimers(self):
        cols=self._GetColNames("timers")[:3]
        data=[seq[:3] for seq in self._ReadTable("timers")]
        return cols, data

    def FindSensorPollbyHardware(self, Type):
        poll = []
        spoll=dict(self._SelectColumnFromTable("sensors", "Id,Poll"))
        stype=dict(self._SelectColumnFromTable("sensors", "Id,Type"))

        TypeId = self._GetTypeId(Type, False)

        for key in spoll:
            if ((stype[key] == TypeId) and (spoll[key])):
                poll.append(key)
        return (poll)

    def FindSensorbyHardware(self, Type):
        sensors = []
        stype=dict(self._SelectColumnFromTable("sensors", "Id,Type"))

        TypeId = self._GetTypeId(Type, False)

        for key in stype:
            if (stype[key] == TypeId):
                sensors.append(key)
        return (sensors)

    def FindGPIOSensors(self):
        fsensors = []
        stype=dict(self._SelectColumnFromTable("sensors", "Id,Type"))
        scode=dict(self._SelectColumnFromTable("sensors", "Id,DeviceCode"))

        TypeId = self._GetTypeId("pigpio", False)

        for key in stype:
            if (stype[key] == TypeId):
                fsensors.append(scode[key])
        return (fsensors)

    def _GetTypeId(self, Type, OutputType):
        hwlink=dict(self._SelectColumnFromTable("types", "Id,HWlink"))
        isoutput=dict(self._SelectColumnFromTable("types", "Id,IsOutput"))

        TypeId = 0
        for key in hwlink:
            if ((isoutput[key] == OutputType) and (hwlink[key].lower() == Type.lower())):
                TypeId = key
        return (TypeId)

    def FindSensorbyCode(self, SysCode, GroupCode, DeviceCode):
        SearchDict = {}
        SearchDict['SysCode']=str(SysCode)
        SearchDict['GroupCode']=str(GroupCode)
        SearchDict['DeviceCode']=str(DeviceCode)
        sensor=self._SearchTableMultiple("sensors", "Id", SearchDict, False)
        if (sensor):
            return sensor[0][0]
        else:
            return 0

    def FindGPIOSensorbyCode(self, DeviceCode):
        SearchDict = {}
        SearchDict['Type']=str(self._GetTypeId("pigpio", False))
        SearchDict['DeviceCode']=str(DeviceCode)
        sensor=self._SearchTableMultiple("sensors", "Id", SearchDict, False)
        if (sensor):
            return sensor[0][0]
        else:
            return 0

    def FindSensorbyURL(self, URL, URLTag):
        SearchDict = {}
        SearchDict['DeviceURL']=URL
        SearchDict['KeyTag']=URLTag
        sensor=self._SearchTableMultiple("sensors", "Id", SearchDict, False)
        if (sensor):
            return sensor[0][0]
        else:
            return 0

    def FindSensorbyName(self, Name):
        sensor=self._SearchValueFromColumn("sensors", "Id", "Name", Name, False)
        if (sensor):
            return sensor[0][0]
        else:
            return 0

    def FindGPIOActuators(self):
        factuators = []
        stype=dict(self._SelectColumnFromTable("actuators", "Id,Type"))
        scode=dict(self._SelectColumnFromTable("actuators", "Id,DeviceCode"))

        TypeId = self._GetTypeId("pigpio", True)

        for key in stype:
            if (stype[key] == TypeId):
                factuators.append(scode[key])
        return (factuators)

    def FindActuatorbyName(self, Name):
        actuator=self._SearchValueFromColumn("actuators", "Id", "Name", Name, False)
        if (actuator):
            return actuator[0][0]
        else:
            return 0

    def FindActuatorbyHardware(self, Type):
        actuators = []
        stype=dict(self._SelectColumnFromTable("actuators", "Id,Type"))

        TypeId = self._GetTypeId(Type, False)

        for key in stype:
            if (stype[key] == TypeId):
                actuators.append(key)
        return (actuators)

    def GetSensorProperties(self, SensorId):
        cols=self._GetColNames("sensors")
        vals=self._SearchTable("sensors", "Id", SensorId, False)
        if (vals):
            return dict(zip(cols, list(vals[0])))
        else:
            return None

    def GetActuatorProperties(self, ActuatorId):
        cols=self._GetColNames("actuators")
        vals=self._SearchTable("actuators", "Id", ActuatorId, False)
        if (vals):
            return dict(zip(cols, list(vals[0])))
        else:
            return None

    def GetTimerProperties(self, TimerId):
        cols=self._GetColNames("timers")
        vals=self._SearchTable("timers", "Id", TimerId, False)
        if (vals):
            return dict(zip(cols, list(vals[0])))
        else:
            return None

    def GetSensorType(self, SensorId):
        result = self._SearchValueFromColumn("sensors", "SensorType", "Id", SensorId, False)
        if (result):
            sensortype = result[0][0]
        else:
            sensortype = 0
        result = self._SearchTable("sensortypes", "Id", sensortype, False)
        if (result):
            retval = result[0][4:]
        else:
            retval = None
        return retval

    def GetActuatorType(self, ActuatorId):
        result = self._SearchValueFromColumn("actuators", "ActuatorType", "Id", ActuatorId, False)
        if (result):
            actuatortype = result[0][0]
        else:
            actuatortype = 0
        result = self._SearchTable("actuatortypes", "Id", actuatortype, False)
        if (result):
            retval = result[0][4:]
        else:
            retval = None
        return retval

    def GetSensorDigital(self, SensorId):
        result = self._SearchValueFromColumn("sensors", "SensorType", "Id", SensorId, False)
        if (result):
            sensortype = result[0][0]
        else:
            sensortype = 0
        result = self._SearchTable("sensortypes", "Id", sensortype, False)
        if (result):
            retval = result[0][3]
        else:
            retval = False
        return retval

    def GetActuatorDigital(self, ActuatorId):
        result = self._SearchValueFromColumn("actuators", "ActuatorType", "Id", ActuatorId, False)
        if (result):
            actuatortype = result[0][0]
        else:
            actuatortype = 0
        result = self._SearchTable("actuatortypes", "Id", actuatortype, False)
        if (result):
            retval = result[0][3]
        else:
            retval = False
        return retval

    def FindProcessors(self, TimerId, SensorId):
        SearchDict = {}
        if (TimerId >0):
            SearchDict['Timer']=str(TimerId)
        if (SensorId >0):
            SearchDict['Sensor']=str(SensorId)

        if SearchDict:
            proc=self._SearchTableMultiple("processors", "Id", SearchDict, False)
        else:
            proc=self._SelectColumnFromTable("processors", "Id")

        if (proc):
            procs=map(lambda y: y[0], proc)
        else:
            procs=[]
        return procs

    def GetProcessorProperties(self, ProcId):
        cols=self._GetColNames("processors")
        vals=self._SearchTable("processors", "Id", ProcId, False)
        if (vals):
            dictdef=dict(zip(cols, list(vals[0])))
            dictdef,dictedit = self._SplitDict(dictdef, ['Sensor','Operator','Value'])
            actiontup = self._ParseProcessor(dictedit)
            dictdef['SensorProcessor']=actiontup
            return dictdef
        else:
            return None

    def GetCombinerProperties(self, CombId):
        cols=self._GetColNames("combiners")
        vals=self._SearchTable("combiners", "Id", CombId, False)
        if (vals):
            dictdef=dict(zip(cols, list(vals[0])))
            dictedit,dictdef = self._SplitDict(dictdef, ['Id','Name','Description','Dependency','Invert_Dependency'])
            actiontup = self._ParseCombiner(dictedit)
            dictdef['Combiner']=actiontup
            return dictdef
        else:
            return None

    def GetDependencyProperties(self, DepId):
        cols=self._GetColNames("dependencies")
        vals=self._SearchTable("dependencies", "Id", DepId, False)
        if (vals):
            dictdef=dict(zip(cols, list(vals[0])))
            dictedit,dictdef = self._SplitDict(dictdef, ['Id','Name','Description'])
            actiontup = self._ParseDependency(dictedit)
            dictdef['Dependency']=actiontup
            return dictdef
        else:
            return None

    def GetTypeProperties(self,TypeId):
        cols=self._GetColNames("types")
        vals=self._SearchTable("types", "Id", TypeId, False)
        if (vals):
            return dict(zip(cols, list(vals[0])))
        else:
            return None

    def GetSetting(self, Setting):
        vals=self._SearchTable("settings", "Parameter", Setting, False)
        if vals:
            return vals[0][3] #,vals[0][4]
        else:
            return None #,None

    def GetHolidays(self):
        cols=self._GetColNames("holidays")[:4]
        data=[seq[:1] for seq in self._ReadTable("holidays")]
        return cols, data

    def GetHolidayValues(self):
        data=[seq[:4] for seq in self._ReadTable("holidays")]
        return (data)

    def DeleteHolidaysRow(self, _id):
        self._DeleteRow("holidays", "Id", _id)
        return 

    def EditHolidaysRow(self, _id, _type, start, end):
        rowdict = {}
        cols=self._GetColNames("holidays")
        for col in cols:
            if (col == "Start"):
                rowdict[col]=str(start)
            elif (col == "End"):
                rowdict[col]=str(end)
            elif (col == "Type"):
                rowdict[col]=str(_type)
        ids = self._SelectColumnFromTable("holidays", "Id")
        if (_id,) in ids:
            self._UpdateRow("holidays", rowdict, "Id", _id)
        else:
            self._AddRow("holidays",rowdict)
        return

    def _SplitDict(self, dict1, keys):
        dict2={}
        for key in keys:
            dict2[key]=dict1[key]
            del dict1[key]

        return dict1,dict2

    def _ParseProcessor(self, indict):
        return (indict['Sensor'],indict['Operator'],indict['Value'])

    def _ParseCombiner(self, indict):
        rettup = ()
        for i in range(0,16):
            if indict["Output%d"%(i+1)]:
                    rettup += ((indict["Output%d"%(i+1)],indict["Output%d_Value"%(i+1)]),)

        return (rettup)

    def _ParseDependency(self, indict):
        rettup = ()
        HasDepComb = False 
        DepComb = '-'
        for i in range(0,4):
            if (indict["actuator%d_id"%(i+1)]) and (indict["actuator%d_operator"%(i+1)]):
                if (i>0):
                    if (HasDepComb):
                        rettup += (DepComb)
                        HasDepComb = False
                    else:
                        rettup += (('and'),)
                rettup += ((indict["actuator%d_id"%(i+1)],indict["actuator%d_operator"%(i+1)],indict["actuator%d_value"%(i+1)]),)
            if (i<3):
                if (indict["actuator%d%d_combiner"%(i+1,i+2)]):
                    if (indict["actuator%d%d_combiner"%(i+1,i+2)] != '-'):
                        DepComb = (indict["actuator%d%d_combiner"%(i+1,i+2)],)
                        HasDepComb = True

        return (rettup)

    def UpdateDB(self, version):
        dbversion="0.00"
        try:
            dbversion=self._SearchTable("miscellaneous", "Parameter", "Version", False)[0][2]
        except self.OperationalError:
            sql_params_misc_table = """ Id INTEGER PRIMARY KEY,
                                        Parameter TEXT NOT NULL,
                                        Value TEXT
                                    """    
            self._CreateTable("miscellaneous", sql_params_misc_table)
            rowdict = {}
            rowdict['Parameter'] = "Version"
            rowdict['Value'] = "0.00"
            self._AddRow("miscellaneous", rowdict)
        except:
            version=""
        if ((version == dbversion) or (version=="")):
            return ("") #nothing to be done
        if (float(dbversion) < 1.00):
            self._UpdateDB100()
        if (float(dbversion) < 1.10):
            self._UpdateDB110()
        if (float(dbversion) < 1.11):
            self._UpdateDB111()
        rowdict = {}
        rowdict['Parameter'] = "Version"
        rowdict['Value'] = version
        self._UpdateRow("miscellaneous", rowdict, "Parameter", "Version")            
        # More to be done in later versions
        return(version)

    def _UpdateDB100(self):
        self._DeleteRowAndSort("settings", "Parameter", "Webport", "Id")
        self._DeleteRowAndSort("settings", "Parameter", "SSL", "Id")
        self._AddRowAndSort("settings","Parameter","Timezone", "Id", (1, u'DomoWeb_port', u'Port for webserver communication (restart required)', 51402, u'INT', 2))
        self._AddRowAndSort("settings","Parameter","DomoWeb_port", "Id", (1, u'DomoWeb_prefix', u'Prefix for webpage (restart required)', u'/', u'STRING', 2))
        self._AddRowAndSort("types","Name","GPIO Output", "Id", (1, u'Script Output', u'Run a script output', u'-', 1))
        rowdict = {}
        rowdict['Restart'] = "2"
        self._UpdateRow("settings", rowdict, "Parameter", "Username")
        self._UpdateRow("settings", rowdict, "Parameter", "Password")
        return

    def _UpdateDB110(self):
        self._DeleteRowAndSort("settings", "Parameter", "URL_SSL", "Id")
        self._AddRowAndSort("settings","Parameter","Timezone", "Id", (1, u'URL_port', u'Port for BDA URL communication (restart required)', 60004, u'INT', 2))
        self._AddRowAndSort("settings","Parameter","URL_port", "Id", (1, u'URL_maxclients', u'Maximum Clients for BDA URL communication (restart required)', 20, u'INT', 2))
        rowdict = {}
        rowdict['Description'] = "Username for BDA URL login or leave empty (restart required)"
        rowdict['Restart'] = "2"
        self._UpdateRow("settings", rowdict, "Parameter", "URL_username")
        rowdict['Description'] = "Password for BDA URL login or leave empty (restart required)"
        self._UpdateRow("settings", rowdict, "Parameter", "URL_password")
        return

    def _UpdateDB111(self):
        self._AddColumn("sensors", "MuteLog", "INTEGER", 0)
        self._AddColumn("actuators", "MuteLog", "INTEGER", 0)
        self._AddColumn("timers", "MuteLog", "INTEGER", 0)
        return

    def _GetColNames(self, table_name):
        #this works beautifully given that you know the table name
        c = self.conn.cursor()
        c.execute("SELECT * FROM {tn}".format(tn=table_name))
        return [member[0] for member in c.description]

    def _ReadTable(self, table_name):
        c = self.conn.cursor()
        c.execute("SELECT * FROM {tn}".format(tn=table_name))
        return c.fetchall()        

    def _SearchTable(self, table_name, field, searchdata, like=True):
        c = self.conn.cursor()
        # like makes searching slower. Set false if you require speed.
        if like:
            c.execute("SELECT * FROM {tn} WHERE {fn} LIKE '{sd}'".format(tn=table_name, fn=field, sd=searchdata))
        else:
            c.execute("SELECT * FROM {tn} WHERE {fn}='{sd}'".format(tn=table_name, fn=field, sd=searchdata))
        return c.fetchall()

    def _SearchTableMultiple(self, table_name, column, searchdict, like=True):
        searchdata=""
        c = self.conn.cursor()
        for field in searchdict:
            if like:
                searchdata += field + " LIKE '" + searchdict[field] + "' AND "
            else:
                searchdata += field + "='" + searchdict[field] + "' AND "
        searchdata = searchdata[:-5]

        c.execute("SELECT {cl} FROM {tn} WHERE {sd}".format(cl=column, tn=table_name, sd=searchdata))
        return c.fetchall()

    def _SelectColumnFromTable(self, table_name, column):
        c = self.conn.cursor()
        c.execute("SELECT {cl} from {tn}".format(cl=column, tn=table_name))
        return c.fetchall()

    def _SearchValueFromColumn(self, table_name, column, field, searchdata, like=True):
        c = self.conn.cursor()
        # like makes searching slower. Set false if you require speed.
        if like:
            c.execute("SELECT {cl} FROM {tn} WHERE {fn} LIKE '{sd}'".format(cl=column, tn=table_name, fn=field, sd=searchdata))
        else:
            c.execute("SELECT {cl} FROM {tn} WHERE {fn}='{sd}'".format(cl=column, tn=table_name, fn=field, sd=searchdata))
        return c.fetchall()

    def _CreateTable(self, table_name, params):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS {tn} ({pm});".format(tn=table_name, pm=params))
        self.conn.commit()
        return

    def _ClearTable(self, table_name):
        c = self.conn.cursor()
        c.execute("DELETE FROM {tn}".format(tn=table_name))
        self.conn.commit()
        return

    def _AddColumn(self, table_name, name, type, default):
        c = self.conn.cursor()
        c.execute("ALTER TABLE {tn} ADD COLUMN {cn} {tp} NOT NULL DEFAULT {df}".format(tn=table_name, cn=name, tp=type, df=default))
        self.conn.commit()
        return

    def _AddRow(self, table_name, rowdict):
        names = ""
        values = ""
        c = self.conn.cursor()

        for key in rowdict:
            names += key + ", "
            values += "'" + rowdict[key] + "', "
        names = "(" + names[:-2] + ")"
        values = "(" + values[:-2] + ")"

        c.execute("INSERT INTO {tn} {nm} VALUES {vl}".format(tn=table_name,nm=names, vl=values))
        self.conn.commit()

        return (c.lastrowid)

    def _DeleteRow(self, table_name, field, fieldvalue):
        c = self.conn.cursor()
        c.execute("DELETE FROM {tn} WHERE {fn}='{sd}'".format(tn=table_name, fn=field, sd=fieldvalue))
        self.conn.commit()
        return

    def _DeleteRowAndSort(self, table_name, field, fieldvalue, Id):
        columns=self._GetColNames(table_name)
        colnrid=0
        for col in columns:
            if col.lower() == Id.lower():
                break
            colnrid+=1
        colnrfield=0
        for col in columns:
            if col.lower() == field.lower():
                break
            colnrfield+=1
        # Read complete table
        table = self._ReadTable(table_name)
        # Remove row and update numbering
        rowid = -1
        for row in table:
            if row[colnrfield].lower() == fieldvalue.lower():
                rowid=row[colnrid]
        newtable = []
        for row in table:
            if rowid<0:
                newtable.append(row)
            elif row[colnrid]<rowid:
                newtable.append(row)
            elif row[colnrid]>rowid:
                row = row[:colnrid] + (row[colnrid]-1,) + row[colnrid+1:]
                newtable.append(row)
        # Delete table
        del table
        self._ClearTable(table_name)
        # Add newtable
        fmt = "("
        for col in columns:
            fmt +="?, "
        fmt = fmt[:-2] + ")"
        c = self.conn.cursor()
        c.executemany("INSERT INTO {tn} VALUES{fm}".format(tn=table_name, fm=fmt), newtable)
        self.conn.commit()
        return

    def _AddRowAndSort(self, table_name, field, fieldvalue, Id, newrow):
        columns=self._GetColNames(table_name)
        colnrid=0
        for col in columns:
            if col.lower() == Id.lower():
                break
            colnrid+=1
        colnrfield=0
        for col in columns:
            if col.lower() == field.lower():
                break
            colnrfield+=1
        # Read complete table
        table = self._ReadTable(table_name)
        # Remove row and update numbering
        rowid = -1
        for row in table:
            if row[colnrfield].lower() == fieldvalue.lower():
                rowid=row[colnrid]
        newtable = []
        for row in table:
            if rowid<0:
                newtable.append(row)
            elif row[colnrid]<rowid:
                newtable.append(row)
            elif row[colnrid]==rowid:
                newtable.append(row)
                newrow = newrow[:colnrid] + (row[colnrid]+1,) + newrow[colnrid+1:]
                newtable.append(newrow)
            elif row[colnrid]>rowid:
                row = row[:colnrid] + (row[colnrid]+1,) + row[colnrid+1:]
                newtable.append(row)
        # Delete table
        del table
        self._ClearTable(table_name)
        # Add newtable
        fmt = "("
        for col in columns:
            fmt +="?, "
        fmt = fmt[:-2] + ")"
        c = self.conn.cursor()
        c.executemany("INSERT INTO {tn} VALUES{fm}".format(tn=table_name, fm=fmt), newtable)
        self.conn.commit()
        return

    def _UpdateRow(self, table_name, rowdict, field, fieldvalue):
        columns = ""
        c = self.conn.cursor()

        for key in rowdict:
            columns += key + " = '" + rowdict[key] + "', "
        columns = columns[:-2]

        c.execute("UPDATE {tn} SET {cl} WHERE {fn}='{sd}'".format(tn=table_name, cl=columns, fn=field, sd=fieldvalue))
        self.conn.commit()
        return

        

    







