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

class db_read(object):
    def __init__(self, dbpath):
        self.db=sqlitedb(dbpath)

    def __del__(self):
        del self.db

    def FillSensorBuffer(self,SensorDict):
        sensors=dict(self.db.SelectColumnFromTable("sensors", "Id,Type"))
        isoutput=dict(self.db.SelectColumnFromTable("types", "Id,IsOutput"))

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
        actuators=dict(self.db.SelectColumnFromTable("actuators", "Id,Type"))
        isoutput=dict(self.db.SelectColumnFromTable("types", "Id,IsOutput"))

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
        timertups=self.db.SelectColumnFromTable("timers", "Id")
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
        sensors=dict(self.db.SelectColumnFromTable("sensors", "Id,Name"))
        # add new ones and update
        for key in SensorDict:
            Names[key]=sensors[key]

        #remove old ones
        for key in Names.copy():
            if not key in SensorDict:
                del Names[key]

        return Names

    def FillActuatorNames(self, ActuatorDict, Names):
        actuators=dict(self.db.SelectColumnFromTable("actuators", "Id,Name"))
        # add new ones and update
        for key in ActuatorDict:
            Names[key]=actuators[key]
        
        #remove old ones
        for key in Names.copy():
            if not key in ActuatorDict:
                del Names[key]

        return Names

    def FillTimerNames(self, TimerDict, Names):
        timers=dict(self.db.SelectColumnFromTable("timers", "Id,Name"))
        # add new ones and update
        for key in TimerDict:
            Names[key]=timers[key]
        
        #remove old ones
        for key in Names.copy():
            if not key in TimerDict:
                del Names[key]

        return Names

    def FindSensorPollbyHardware(self, Type):
        poll = []
        spoll=dict(self.db.SelectColumnFromTable("sensors", "Id,Poll"))
        stype=dict(self.db.SelectColumnFromTable("sensors", "Id,Type"))

        TypeId = self._GetTypeId(Type, False)

        for key in spoll:
            if ((stype[key] == TypeId) and (spoll[key])):
                poll.append(key)
        return (poll)

    def FindGPIOSensors(self):
        fsensors = []
        stype=dict(self.db.SelectColumnFromTable("sensors", "Id,Type"))
        scode=dict(self.db.SelectColumnFromTable("sensors", "Id,DeviceCode"))

        TypeId = self._GetTypeId("pigpio", False)

        for key in stype:
            if (stype[key] == TypeId):
                fsensors.append(scode[key])
        return (fsensors)

    def _GetTypeId(self, Type, OutputType):
        hwlink=dict(self.db.SelectColumnFromTable("types", "Id,HWlink"))
        isoutput=dict(self.db.SelectColumnFromTable("types", "Id,IsOutput"))

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
        sensor=self.db.SearchTableMultiple("sensors", "Id", SearchDict, False)
        if (sensor):
            return sensor[0][0]
        else:
            return 0

    def FindGPIOSensorbyCode(self, DeviceCode):
        SearchDict = {}
        SearchDict['Type']=str(self._GetTypeId("pigpio", False))
        SearchDict['DeviceCode']=str(DeviceCode)
        sensor=self.db.SearchTableMultiple("sensors", "Id", SearchDict, False)
        if (sensor):
            return sensor[0][0]
        else:
            return 0

    def FindSensorbyURL(self, URL, URLTag):
        SearchDict = {}
        SearchDict['DeviceURL']=URL
        SearchDict['KeyTag']=URLTag
        sensor=self.db.SearchTableMultiple("sensors", "Id", SearchDict, False)
        if (sensor):
            return sensor[0][0]
        else:
            return 0

    def FindSensorbyName(self, Name):
        sensor=self.db.SearchValueFromColumn("sensors", "Id", "Name", Name, False)
        if (sensor):
            return sensor[0][0]
        else:
            return 0

    def FindGPIOActuators(self):
        factuators = []
        stype=dict(self.db.SelectColumnFromTable("actuators", "Id,Type"))
        scode=dict(self.db.SelectColumnFromTable("actuators", "Id,DeviceCode"))

        TypeId = self._GetTypeId("pigpio", True)

        for key in stype:
            if (stype[key] == TypeId):
                factuators.append(scode[key])
        return (factuators)

    def FindActuatorbyName(self, Name):
        actuator=self.db.SearchValueFromColumn("actuators", "Id", "Name", Name, False)
        if (actuator):
            return actuator[0][0]
        else:
            return 0

    def GetSensorProperties(self, SensorId):
        cols=self.db.GetColNames("sensors")
        vals=self.db.SearchTable("sensors", "Id", SensorId, False)
        if (vals):
            return dict(zip(cols, list(vals[0])))
        else:
            return None

    def GetActuatorProperties(self, ActuatorId):
        cols=self.db.GetColNames("actuators")
        vals=self.db.SearchTable("actuators", "Id", ActuatorId, False)
        if (vals):
            return dict(zip(cols, list(vals[0])))
        else:
            return None

    def GetTimerProperties(self, TimerId):
        cols=self.db.GetColNames("timers")
        vals=self.db.SearchTable("timers", "Id", TimerId, False)
        if (vals):
            return dict(zip(cols, list(vals[0])))
        else:
            return None

    def GetSensorType(self, SensorId):
        result = self.db.SearchValueFromColumn("sensors", "SensorType", "Id", SensorId, False)
        if (result):
            sensortype = result[0][0]
        else:
            sensortype = 0
        result = self.db.SearchTable("sensortypes", "Id", sensortype, False)
        if (result):
            retval = result[0][4:]
        else:
            retval = None
        return retval

    def GetActuatorType(self, ActuatorId):
        result = self.db.SearchValueFromColumn("actuators", "ActuatorType", "Id", ActuatorId, False)
        if (result):
            actuatortype = result[0][0]
        else:
            actuatortype = 0
        result = self.db.SearchTable("actuatortypes", "Id", actuatortype, False)
        if (result):
            retval = result[0][4:]
        else:
            retval = None
        return retval

    def GetSensorDigital(self, SensorId):
        result = self.db.SearchValueFromColumn("sensors", "SensorType", "Id", SensorId, False)
        if (result):
            sensortype = result[0][0]
        else:
            sensortype = 0
        result = self.db.SearchTable("sensortypes", "Id", sensortype, False)
        if (result):
            retval = result[0][3]
        else:
            retval = False
        return retval

    def GetActuatorDigital(self, ActuatorId):
        result = self.db.SearchValueFromColumn("actuators", "ActuatorType", "Id", ActuatorId, False)
        if (result):
            actuatortype = result[0][0]
        else:
            actuatortype = 0
        result = self.db.SearchTable("actuatortypes", "Id", actuatortype, False)
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
            proc=self.db.SearchTableMultiple("processors", "Id", SearchDict, False)
        else:
            proc=self.db.SelectColumnFromTable("processors", "Id")

        if (proc):
            procs=map(lambda y: y[0], proc)
        else:
            procs=[]
        return procs

    def GetProcessorProperties(self, ProcId):
        cols=self.db.GetColNames("processors")
        vals=self.db.SearchTable("processors", "Id", ProcId, False)
        if (vals):
            dictdef=dict(zip(cols, list(vals[0])))
            dictdef,dictedit = self._SplitDict(dictdef, ['Sensor','Operator','Value'])
            actiontup = self._ParseProcessor(dictedit)
            dictdef['SensorProcessor']=actiontup
            return dictdef
        else:
            return None

    def GetCombinerProperties(self, CombId):
        cols=self.db.GetColNames("combiners")
        vals=self.db.SearchTable("combiners", "Id", CombId, False)
        if (vals):
            dictdef=dict(zip(cols, list(vals[0])))
            dictedit,dictdef = self._SplitDict(dictdef, ['Id','Name','Description','Dependency','Invert_Dependency'])
            actiontup = self._ParseCombiner(dictedit)
            dictdef['Combiner']=actiontup
            return dictdef
        else:
            return None

    def GetDependencyProperties(self, DepId):
        cols=self.db.GetColNames("dependencies")
        vals=self.db.SearchTable("dependencies", "Id", DepId, False)
        if (vals):
            dictdef=dict(zip(cols, list(vals[0])))
            dictedit,dictdef = self._SplitDict(dictdef, ['Id','Name','Description'])
            actiontup = self._ParseDependency(dictedit)
            dictdef['Dependency']=actiontup
            return dictdef
        else:
            return None

    def GetTypeProperties(self,TypeId):
        cols=self.db.GetColNames("types")
        vals=self.db.SearchTable("types", "Id", TypeId, False)
        if (vals):
            return dict(zip(cols, list(vals[0])))
        else:
            return None

    def GetSetting(self, Setting):
        vals=self.db.SearchTable("settings", "Parameter", Setting, False)
        if vals:
            return vals[0][3],vals[0][4]
        else:
            return None,None

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