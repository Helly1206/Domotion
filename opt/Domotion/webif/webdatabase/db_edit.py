# -*- coding: utf-8 -*-
#########################################################
# SERVICE : db_edit                                     #
#           Accessing and editing db for home control   #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################

from .sqlitedb import sqlitedb
import random

#########################################################

####################### GLOBALS #########################

MethodDict = {0: "Fixed", 1: "Sunrise", 2: "Sunset", 3: "Offset"}
#WeekDayDict = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}
ActiveDict = {0: "-", 1: "Active", 2: "Inactive"}
OperatorDict = {0: "-", 1: "eq", 2: "ne", 3: "gt", 4: "ge", 5: "lt", 6: "le"}
DepCombDict = {0: "-", 1: "and", 2: "nand", 3: "or", 4: "nor", 5: "xor", 6: "xnor"}
#SensorValDict = {0: "-", 1: "False", 2: "True", 3: "0.0", 4: "1.0", 5: "2.0", 6: "3.0", 7: "4.0", 9: "5.0"}
#ActuatorValDict = {0: "-", 1: "Off", 2: "On", 3: "0.0", 4: "1.0", 5: "2.0", 6: "3.0", 7: "4.0", 9: "5.0"}
#TableDict = {0: "-", 1: "sensors", 2: "actuators", 3: "timers", 4: "processors", 5: "dependencies", 6: "combiners", 7: "types"}

#########################################################
# Class : db_edit                                       #
#########################################################

class db_edit(object):
    def __init__(self, app):
        self.app = app
        self.db=sqlitedb(self.app.common.GetDBPath())

    def __del__(self):
        del self.db

    def ReadTable(self, tableid):
        return self._PrettyEditData(tableid)

    def EditTableRow(self, tableid, id, result):
        if not result['Button'] == 'Ok':
            return

        rowdict = {}

        cols = []
        if (tableid.lower() != "scripts"):
            cols = self.db.GetColNames(tableid)

        if (tableid.lower() == "sensors"):
            types = dict(self.db.SelectColumnFromTable("types", "Id,Name"))
            typename = types[int(result['Type'])].lower()
            rowdict['SysCode'] = "0"
            rowdict['GroupCode'] = "0"
            rowdict['DeviceCode'] = "0"
            rowdict['DeviceURL'] = "-"
            rowdict['KeyTag'] = "-"
            for col in cols:
                if (col == "Name"):
                    if col in result:
                        rowdict[col] = self._checkDuplicateName(tableid.lower(), result[col])
                    else:
                        rowdict[col] = self._checkDuplicateName(tableid.lower(), self._generateName())
                elif col == "SysCode":
                    if ('rf' in typename):
                        rowdict[col] = result[col]
                elif col == "GroupCode":
                    if ('rf' in typename):
                        rowdict[col] = result[col]
                elif col == "DeviceCode":
                    if ('rf' in typename) or ('domoticz' in typename) or ('gpio' in typename):
                        rowdict[col] = result[col]
                elif col == "DeviceURL":
                    if ('url' in typename) or ('ir' in typename) or ('mqtt' in typename):
                        rowdict[col] = result[col]
                elif col == "KeyTag":
                    if ('url' in typename) or ('ir' in typename) or ('mqtt' in typename):
                        rowdict[col] = result[col]
                elif not col == "Id":
                    if (result[col]):
                        rowdict[col] = result[col]
            self.db.UpdateRow(tableid, rowdict, "Id", id)
        elif (tableid.lower() == "actuators"):
            types = dict(self.db.SelectColumnFromTable("types", "Id,Name"))
            typename = types[int(result['Type'])].lower()
            actuatortypes = dict(self.db.SelectColumnFromTable("actuatortypes", "Id,Name"))
            actuatortypename = actuatortypes[int(result['ActuatorType'])].lower()
            rowdict['SysCode'] = "0"
            rowdict['GroupCode'] = "0"
            rowdict['DeviceCode'] = "0"
            rowdict['DeviceURL'] = "-"
            rowdict['KeyTag'] = "-"
            for col in cols:
                if (col == "Name"):
                    if col in result:
                        rowdict[col] = self._checkDuplicateName(tableid.lower(), result[col])
                    else:
                        rowdict[col] = self._checkDuplicateName(tableid.lower(), self._generateName())
                elif col == "SysCode":
                    if ('rf' in typename):
                        rowdict[col] = result[col]
                elif col == "GroupCode":
                    if ('rf' in typename):
                        rowdict[col] = result[col]
                elif col == "DeviceCode":
                    if ('rf' in typename) or ('timer' in typename) or ('domoticz' in typename) or ('gpio' in typename):
                        rowdict[col] = result[col]
                elif col == "DeviceURL":
                    if ('url' in typename) or ('ir' in typename) or ('script' in typename) or ('mqtt' in typename):
                        rowdict[col] = result[col]
                elif col == "KeyTag":
                    if ('url' in typename) or ('ir' in typename) or ('script' in typename) or ('mqtt' in typename):
                        rowdict[col] = result[col]
                elif not col == "Id":
                    if (result[col]):
                        rowdict[col] = result[col]
            self.db.UpdateRow(tableid, rowdict, "Id", id)
        elif (tableid.lower() == "timers"):
            method=MethodDict[int(result['Method'])].lower()
            rowdict['Time'] = "0"
            rowdict['Minutes_Offset'] = "0"
            for col in cols:
                if (col == "Name"):
                    if col in result:
                        rowdict[col] = self._checkDuplicateName(tableid.lower(), result[col])
                    else:
                        rowdict[col] = self._checkDuplicateName(tableid.lower(), self._generateName())
                elif col == "Time":
                    if ('sunrise' in method) or ('sunset' in method) or ('offset' in method):
                        rowdict[col] = "0"
                    else:
                        rowdict[col] = str(self.app.common.Asc2Mod(result['Time']))
                elif col == "Minutes_Offset":
                    if ('fixed' in method):
                        rowdict[col]="0"
                    else:
                        rowdict[col] = result[col]
                elif not col == "Id":
                    if (result[col]):
                        rowdict[col] = result[col]
            self.db.UpdateRow(tableid, rowdict, "Id", id)
        elif (tableid.lower() == "processors"):
            for col in cols:
                if (col == "Name"):
                    if col in result:
                        rowdict[col] = self._checkDuplicateName(tableid.lower(), result[col])
                    else:
                        rowdict[col] = self._checkDuplicateName(tableid.lower(), self._generateName())
                elif (col == "Description"):
                    if col in result:
                        rowdict[col] = result[col]
                    else:
                        rowdict[col] = "None"
                elif (col == "Combiner") or (col == "Timer"):
                    if col in result:
                        rowdict[col] = result[col]
                    else:
                        rowdict[col] = "0"
                elif (col == "Script"):
                    if col in result:
                        if result[col] == "-":
                            rowdict[col] = ""
                        else:
                            rowdict[col] = result[col]
                    else:
                        rowdict[col] = ""
            rowdict = self._SetSensorValue(result, rowdict)
            self.db.UpdateRow(tableid, rowdict, "Id", id)
        elif (tableid.lower() == "scripts"):
            if "Name" in result:
                name = self._checkDuplicateName(tableid.lower(), result["Name"])
            else:
                name = self._checkDuplicateName(tableid.lower(), self._generateName())
            if "Script" in result:
                error, commres = self.app.domotionaccess.Call("SetScript", name, result["Script"].replace("\r", ""))
        elif (tableid.lower() == "dependencies"):
            for col in cols:
                if (col == "Name"):
                    rowdict[col] = self._checkDuplicateName(tableid.lower(), result[col])
                elif (col == "Description"):
                    rowdict[col] = result[col]
            rowdict = self._SetDependencyValues(result, rowdict)
            self.db.UpdateRow(tableid, rowdict, "Id", id)
        elif (tableid.lower() == "combiners"):
            for col in cols:
                if (col == "Name"):
                    if col in result:
                        rowdict[col] = self._checkDuplicateName(tableid.lower(), result[col])
                    else:
                        rowdict[col] = self._checkDuplicateName(tableid.lower(), self._generateName())
                elif (col == "Description") or (col == "Dependency") or (col == "Invert_Dependency"):
                    rowdict[col] = result[col]
            rowdict = self._SetCombinerValues(result, rowdict)
            self.db.UpdateRow(tableid, rowdict, "Id", id)
        return

    def DeleteTableRow(self, tableid, id):
        if (tableid.lower() != "scripts"):
            self.db.DeleteRow(tableid, "Id", id)
        else:
            name = ""
            data = self._getScriptsData()
            for datum in data:
                if datum[0] == id:
                     name = datum[1]
                     break
            if name:
                error, commres = self.app.domotionaccess.Call("SetScript", name, "")
        return

    def AddTableRow(self, tableid):
        retval = 0
        if (tableid.lower() != "scripts"):
            rowdict = {}
            rowdict['Name'] = self._checkDuplicateName(tableid.lower(), self._generateName())
            retval = (self.db.AddRow(tableid, rowdict))
        else:
            data = self._getScriptsData()
            retval = len(data) + 1
        return retval

    def AddScriptData(self, id, data):
        DictList = []
        error, content = self.app.domotionaccess.Call("GetScript", "___nonexistingscript___")
        if not error:
            DictList.append(content)
            name = self._checkDuplicateName("scripts", self._generateName())
            data.append((id, name, "<shown when editing>"))
        return DictList

    def BuildOptionsDicts(self, tableid, id):
        DictList = []

        if (tableid.lower() == "sensors"):
            # options: type, sensortype
            types=self._getTypes(False)
            DictList.append(types)
            sensortypes=dict(self.db.SelectColumnFromTable("sensortypes", "Id,Name"))
            DictList.append(sensortypes)
        elif (tableid.lower() == "actuators"):
            # options: type, actuatortype
            types=self._getTypes(True)
            DictList.append(types)
            actuatortypes=dict(self.db.SelectColumnFromTable("actuatortypes", "Id,Name"))
            DictList.append(actuatortypes)
        elif (tableid.lower() == "timers"):
            # options: method, weekdays
            DictList.append(MethodDict)
            DictList.append(self.app.common.GetWeekdayDict())
            DictList.append(ActiveDict)
        elif (tableid.lower() == "processors"):
            # options: timers, sensors, digital, operator, sensorval, combiners
            timers=dict(self.db.SelectColumnFromTable("timers", "Id,Name"))
            timers.update({-1: "[always]"})
            timers.update({0: "-"})
            DictList.append(timers)
            sensors=dict(self.db.SelectColumnFromTable("sensors", "Id,Name"))
            sensors.update({0: "-"})
            DictList.append(sensors)
            sendig=self._GetDigital("sensors")
            sendig.update({0: 0})
            DictList.append(sendig)
            DictList.append(OperatorDict)
            combiners=dict(self.db.SelectColumnFromTable("combiners", "Id,Name"))
            combiners.update({0: "-"})
            DictList.append(combiners)
            scripts=dict(self._getScriptsData(True))
            scripts.update({0: "-"})
            DictList.append(scripts)
        elif (tableid.lower() == "scripts"):
            name = ""
            data = self._getScriptsData()
            for datum in data:
                if datum[0] == id:
                     name = datum[1]
                     break
            if name:
                error, contents = self.app.domotionaccess.Call("GetScript", name)
                DictList.append(contents)
        elif (tableid.lower() == "dependencies"):
            # options: actuators, digital, operator, sensorval, dependency combiners
            actuators=dict(self.db.SelectColumnFromTable("actuators", "Id,Name"))
            actuators.update({0: "-"})
            DictList.append(actuators)
            actdig=self._GetDigital("actuators")
            actdig.update({0: 0})
            DictList.append(actdig)
            DictList.append(OperatorDict)
            DictList.append(DepCombDict)
        elif (tableid.lower() == "combiners"):
            # options: dependencies, actuators, digital, actuatorval
            dependencies=dict(self.db.SelectColumnFromTable("dependencies", "Id,Name"))
            dependencies.update({0: "-"})
            DictList.append(dependencies)
            actuators=dict(self.db.SelectColumnFromTable("actuators", "Id,Name"))
            actuators.update({0: "-"})
            DictList.append(actuators)
            actdig=self._GetDigital("actuators")
            actdig.update({0: 0})
            DictList.append(actdig)

        return DictList

    def _getTypes(self, IsOutput):
        types = dict(self.db.SelectColumnFromTable("types", "Id,Name"))
        output = dict(self.db.SelectColumnFromTable("types", "Id,IsOutput"))

        for key in types.copy():
            if (output[key] != IsOutput):
                del types[key]

        return types

    def _SetSensorValue(self, result, rowdict):
        rowdict["Sensor"]="0"
        rowdict["Operator"]="-"
        rowdict["Value"]="0"
        if 'Sensor' in result:
            if (result['Sensor'] != '0'):
                digital = self._GetDigital("sensors")
                IsDigital=digital[int(result['Sensor'])]
                if (IsDigital):
                    if 'Value' in result:
                        rowdict["Sensor"]=result['Sensor']
                        rowdict["Operator"]="eq"
                        rowdict["Value"]=result['Value']
                else:
                    if ('NValue' in result) and ('Operator' in result):
                        rowdict["Sensor"]=result['Sensor']
                        rowdict["Operator"]=OperatorDict[int(result['Operator'])]
                        rowdict["Value"]=result['NValue']
        return (rowdict)

    def _SetDependencyValues(self, result, rowdict):
        Id = 1
        HasDepComb = False
        DepComb = '-'
        digital = self._GetDigital("actuators")
        # clear all
        for j in range(0,4):
            rowdict["actuator%d_id"%(j+1)] = '0'
            rowdict["actuator%d_operator"%(j+1)] = '-'
            rowdict["actuator%d_value"%(j+1)] = '0'
            if (j<3):
                rowdict["Actuator%d%d_combiner"%(j+1,j+2)] = '-'
        for i in range(0,4):
            if (result['ActuatorId%d'%i] != '0'):
                # valid actuator
                IsDigital=digital[int(result['ActuatorId%d'%i])]
                if (IsDigital):
                    if (result['Value%d'%i]):
                        if (Id>1):
                            if (HasDepComb):
                                rowdict["Actuator%d%d_combiner"%(Id-1,Id)] = DepComb
                                HasDepComb = False
                            else:
                                rowdict["Actuator%d%d_combiner"%(Id-1,Id)] = 'and'
                        rowdict["actuator%d_id"%Id]=result['ActuatorId%d'%i]
                        rowdict["actuator%d_operator"%Id]="eq"
                        rowdict["actuator%d_value"%Id]=result['Value%d'%i]
                        Id += 1
                else:
                    if (result['NValue%d'%i]):
                        if (Id>1):
                            if (HasDepComb):
                                rowdict["Actuator%d%d_combiner"%(Id-1,Id)] = DepComb
                                HasDepComb = False
                            else:
                                rowdict["Actuator%d%d_combiner"%(Id-1,Id)] = 'and'
                        rowdict["actuator%d_id"%Id]=result['ActuatorId%d'%i]
                        rowdict["actuator%d_operator"%Id]=OperatorDict[int(result['OperatorId%d'%i])]
                        rowdict["actuator%d_value"%Id]=result['NValue%d'%i]
                        Id += 1
            if (result['CombinerId%d'%i] != '0'):
                HasDepComb = True
                DepComb = DepCombDict[int(result['CombinerId%d'%i])]
        return (rowdict)

    def _SetCombinerValues(self, result, rowdict):
        Id = 1
        digital = self._GetDigital("actuators")
        for j in range(0,16):
            rowdict["Output%d"%(j+1)] = '0'
            rowdict["Output%d_Value"%(j+1)] = '0'
        for i in range(0,16):
            if (result['ActuatorId%d'%i] != '0'):
                # valid actuator
                IsDigital=digital[int(result['ActuatorId%d'%i])]
                if (IsDigital):
                    if (result['Value%d'%i]):
                        rowdict["Output%d"%Id]=result['ActuatorId%d'%i]
                        rowdict["Output%d_Value"%Id]=result['Value%d'%i]
                        Id += 1
                else:
                    if (result['NValue%d'%i]):
                        rowdict["Output%d"%Id]=result['ActuatorId%d'%i]
                        rowdict["Output%d_Value"%Id]=result['NValue%d'%i]
                        Id += 1

        return (rowdict)

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

    def _PrettyEditData(self, tableid):
        if (tableid.lower() != "scripts"):
            cols = self.db.GetColNames(tableid)
            data = self.db.ReadTable(tableid)
        else:
            cols = self._getScriptsCols()
            data = self._getScriptsData()

        if (tableid.lower() == "sensors"):
            # Lookup types, boolean
            data = self._LookupType(cols, data)
            data = self._LookupSensorType(cols, data)
            data = self._LookupBoolean(cols, data, "poll")
            data = self._LookupBoolean(cols, data, "toggle")
            data = self._LookupBoolean(cols, data, "mutelog")
        elif (tableid.lower() == "actuators"):
            # Lookup types, boolean
            data = self._LookupType(cols, data)
            data = self._LookupBoolean(cols, data, "setonce")
            data = self._LookupBoolean(cols, data, "repeat")
            data = self._LookupActuatorType(cols, data)
            data = self._LookupBoolean(cols, data, "statuslightflash")
            data = self._LookupBoolean(cols, data, "mutelog")
        elif (tableid.lower() == "timers"):
            # Lookup method, weekdays
            data = self._LookupMethod(cols, data)
            cols, data = self._LookupTime(cols, data)
            cols, data = self._LookupWeekdays(cols, data)
            data = self._LookupHomeTrip(cols, data, "home")
            data = self._LookupHomeTrip(cols, data, "trip")
            data = self._LookupBoolean(cols, data, "mutelog")
        elif (tableid.lower() == "processors"):
            # Lookup arithmic, combiner
            cols,data = self._LookupProcessorsArithmic(cols, data)
            data = self._LookupCombiner(cols, data)
            data = self._LookupScript(cols, data)
        elif (tableid.lower() == "dependencies"):
            # Lookup arithmic
            cols,data = self._LookupDependencyArithmic(cols, data)
        elif (tableid.lower() == "combiners"):
            # Lookup arithmic, dependencies, boolean
            cols,data = self._LookupCombinerArithmic(cols,data)
            data = self._LookupDependency(cols, data)
            data = self._LookupBoolean(cols, data, "Invert_Dependency")
        elif (tableid.lower() == "types"):
            data = self._LookupBoolean(cols, data, "IsOutput")

        return cols, data, (tableid.lower() != "types")

    def _GetColumn(self, cols, name):
        i = 0
        retcol = -1
        for colname in cols:
            if (colname.lower() == name.lower()):
                retcol = i
            i += 1

        return retcol

    def _GetIdName(self, table, id):
        Name=("-",)
        if (id):
            result=self.db.SearchValueFromColumn(table, "Name", "Id", id, False)
            if (result):
                Name = result[0]
        return (Name)

    def _GetIdDigital(self, table, id):
        Digital=""
        if (id):
            if (table.lower() == "sensors"):
                result=self.db.SearchValueFromColumn(table, "SensorType", "Id", id, False)
                if (result):
                    TypeId = result[0][0]
                else:
                    TypeId = 0
                if (TypeId > 0):
                    result=self.db.SearchValueFromColumn("SensorTypes", "Digital", "Id", TypeId, False)
                    if (result):
                        Digital=result[0][0]
                    else:
                        Digital=False
                else:
                    Digital=False
            elif (table.lower() == "actuators"):
                result=self.db.SearchValueFromColumn(table, "ActuatorType", "Id", id, False)
                if (result):
                    TypeId = result[0][0]
                else:
                    TypeId = 0
                if (TypeId > 0):
                    result=self.db.SearchValueFromColumn("ActuatorTypes", "Digital", "Id", TypeId, False)
                    if (result):
                        Digital=result[0][0]
                    else:
                        Digital=False
                else:
                    Digital=False
            else:
                Digital=False
        else:
            Digital=False
        return (Digital)

    def _LookupType(self, cols, data):
        type_col = self._GetColumn(cols,"type")
        newdata = []
        for row in data:
            type = self._GetIdName("types", row[type_col])
            newrow = row[:type_col] + type + row[type_col+1:]
            newdata.append(newrow)
        return newdata

    def _LookupSensorType(self, cols, data):
        type_col = self._GetColumn(cols,"sensortype")
        newdata = []
        for row in data:
            type = self._GetIdName("sensortypes", row[type_col])
            newrow = row[:type_col] + type + row[type_col+1:]
            newdata.append(newrow)
        return newdata

    def _LookupActuatorType(self, cols, data):
        type_col = self._GetColumn(cols,"actuatortype")
        newdata = []
        for row in data:
            type = self._GetIdName("actuatortypes", row[type_col])
            newrow = row[:type_col] + type + row[type_col+1:]
            newdata.append(newrow)
        return newdata

    def _LookupCombiner(self, cols, data):
        comb_col = self._GetColumn(cols,"combiner")
        newdata = []
        for row in data:
            comb = self._GetIdName("combiners", row[comb_col])
            newrow = row[:comb_col] + comb + row[comb_col+1:]
            newdata.append(newrow)
        return newdata

    def _LookupScript(self, cols, data):
        scr_col = self._GetColumn(cols,"script")
        newdata = []
        for row in data:
            if row[scr_col]:
                scr = (row[scr_col],)
            else:
                scr = ("-",)
            newrow = row[:scr_col] + scr + row[scr_col+1:]
            newdata.append(newrow)
        return newdata

    def _LookupDependency(self, cols, data):
        dep_col = self._GetColumn(cols,"dependency")
        newdata = []
        for row in data:
            dep = self._GetIdName("dependencies", row[dep_col])
            newrow = row[:dep_col] + dep + row[dep_col+1:]
            newdata.append(newrow)
        return newdata

    def _LookupBoolean(self, cols, data, column):
        bool_col = self._GetColumn(cols,column)
        newdata = []
        for row in data:
            if row[bool_col] > 0:
                _bool = ("True",)
            else:
                _bool = ("False",)
            newrow = row[:bool_col] + _bool + row[bool_col+1:]
            newdata.append(newrow)
        return newdata

    def _LookupMethod(self, cols, data):
        method_col = self._GetColumn(cols,"method")
        newdata = []
        for row in data:
            if row[method_col] == 1:
                method = ("Sunrise",)
            elif row[method_col] == 2:
                method = ("Sunset",)
            elif row[method_col] == 3:
                method = ("Offset",)
            else:
                method = ("Fixed",)
            newrow = row[:method_col] + method + row[method_col+1:]
            newdata.append(newrow)
        return newdata

    def _LookupHomeTrip(self, cols, data, column):
        ht_col = self._GetColumn(cols,column)
        newdata = []
        for row in data:
            if row[ht_col] == 1:
                ht = ("Active",)
            elif row[ht_col] == 2:
                ht = ("Inactive",)
            else:
                ht = ("-",)
            newrow = row[:ht_col] + ht + row[ht_col+1:]
            newdata.append(newrow)
        return newdata

    def _LookupTime(self, cols, data):
        # Modify columns
        Offset_col = self._GetColumn(cols,"Method")
        newcols = cols[:Offset_col+1] + ["Time"] + cols[Offset_col+2:]
        # Modify data
        newdata = []
        for row in data:
            newrow = row[:Offset_col+1] + (self.app.common.Mod2Asc((row[Offset_col+1],)),)[0] + row[Offset_col+2:]
            newdata.append(newrow)

        return newcols, newdata

    def _LookupWeekdays(self, cols, data):
        # Modify columns
        Offset_col = self._GetColumn(cols,"Minutes_Offset")
        Offset_col2 = self._GetColumn(cols,"Saturday")
        newcols = cols[:Offset_col+1] + ["Weekdays"] + cols[Offset_col2+1:]
        # Modify data
        newdata = []
        for row in data:
            hadday = False
            weekdata = ""
            i = Offset_col+1
            for col in cols[Offset_col+1:Offset_col2+1]:
                if (row[i]):
                    if (hadday):
                        weekdata += ", "+col
                    else:
                        weekdata += col
                    hadday = True
                i += 1
            if (not hadday):
                weekdata = "-"
            newrow = row[:Offset_col+1] + (weekdata,) + row[Offset_col2+1:]
            newdata.append(newrow)

        return newcols, newdata

    def _LookupProcessorsArithmic(self, cols, data):
        # Modify columns
        InvDep_col = self._GetColumn(cols,"Description")
        newcols = cols[:InvDep_col+1] + ["Processors"] + cols[InvDep_col+5:]
        # Modify data
        newdata = []
        for row in data:
            procdata = ""
            if row[InvDep_col+1] < 0:
                timer = "[always]"
            else:
                timer = self._GetIdName("timers", row[InvDep_col+1])[0]
            sensor = self._GetIdName("sensors", row[InvDep_col+2])[0]
            if (timer != '-'):
                procdata += timer
                if (sensor != '-'):
                    procdata += ' or '
            if (sensor != '-'):
                Digital = self._GetIdDigital("sensors", row[InvDep_col+2])
                operator = row[InvDep_col+3].lower()
                if (Digital):
                    if (row[InvDep_col+4]):
                        value="True"
                    else:
                        value="False"
                else:
                    value = str(row[InvDep_col+4])
                procdata += "("+sensor+" "+operator+" "+value+")"

            newrow = row[:InvDep_col+1] + (procdata,) + row[InvDep_col+5:]
            newdata.append(newrow)

        return newcols, newdata

    def _LookupDependencyArithmic(self, cols, data):
        # Modify columns
        Descr_col = self._GetColumn(cols,"Description")
        newcols = cols[:Descr_col+1] + ["Dependencies"]
        # Modify data
        newdata = []
        for row in data:
            depok = True
            depdata = ""
            i = Descr_col+1
            while (depok):
                if (row[i]):
                    actuator=self._GetIdName("actuators", row[i])[0]
                    if (actuator != '-'):
                        Digital=self._GetIdDigital("actuators", row[i])
                        operator=row[i+1].lower()
                        if (Digital):
                            if (row[i+2]):
                                value="On"
                            else:
                                value="Off"
                        else:
                            value=str(row[i+2])
                        depdata += "("+actuator+" "+operator+" "+value+")"
                        if (len(row) > i+3):
                            if (row[i+3] != '-'):
                                depdata += " "+row[i+3].lower()+" "
                                i+=4
                            else:
                                depok = False
                        else:
                            depok = False
                    else:
                        depok = False
                else:
                    depok = False
            newrow = row[:Descr_col+1] + (depdata,)
            newdata.append(newrow)

        return newcols, newdata

    def _LookupCombinerArithmic(self, cols, data):
        # Modify columns
        InvDep_col = self._GetColumn(cols,"Invert_Dependency")
        newcols = cols[:InvDep_col+1] + ["Combiners"]
        # Modify data
        newdata = []
        for row in data:
            comok = True
            comdata = ""
            i = InvDep_col+1
            while (comok):
                if (row[i]):
                    actuator=self._GetIdName("actuators", row[i])[0]
                    if (actuator != '-'):
                        Digital=self._GetIdDigital("actuators", row[i])
                        if (Digital):
                            if (row[i+1]):
                                value="On"
                            else:
                                value="Off"
                        else:
                            value=str(row[i+1])
                        comdata += "("+actuator+" is "+value+")"
                        if (row[i+2]):
                            comdata += ", "
                            i+=2
                        else:
                            comok = False
                    else:
                        comok = False
                else:
                    comok = False
            newrow = row[:InvDep_col+1] + (comdata,)
            newdata.append(newrow)

        return newcols, newdata

    def _getScriptsCols(self):
        return ["Id", "Name", "Script"]

    def _getScriptsData(self, noContents = False):
        data = []
        id = 0
        error, names = self.app.domotionaccess.Call("ScriptsList")
        if not error:
            for name in names:
                if name:
                    id += 1
                    if noContents:
                        data.append((id, name))
                    else:
                        data.append((id, name, "<shown when editing>"))
        return data

    def _generateName(self):
        return "_" + str(random.randint(0, 100000)) + "_"

    def _checkDuplicateName(self, tableid, name):
        names = list(map(lambda x: x[0], self.db.SelectColumnFromTable(tableid, "Name")))
        while name in names:
            name = self._generateName()
        return name
