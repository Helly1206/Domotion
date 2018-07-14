# -*- coding: utf-8 -*-
#########################################################
# SERVICE : fuel.py                                     #
#           Python fuel for the Domotion engine         #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
#import logging
#from commandqueue import commandqueue
#from localaccess import localaccess
#########################################################

####################### GLOBALS #########################

#########################################################
# Class : fuel                                          #
#########################################################
class fuel(object):
    def __init__(self):
        self.ActuatorRepeats = { }
        self.Flash50 = 0
        self.InitRepeats()
        pass

    def __del__(self):
        pass

    def InitRepeats(self):
        for key in self.localaccess.GetActuatorValues():
            self.ActuatorRepeats[key]=0
        return

    def process(self, timer, sensor, value):
        if (sensor):
            value = self._CheckToggle(sensor, value)
            if (self.domoticz_frontend):
                self.domoticz_frontend.SetSensor(sensor, value)
            self.localaccess.SetSensor(sensor, value)
            self.valueretainer.SetDevices()
            props=self.localaccess.GetSensorProperties(sensor)
            if not props['MuteLog']:
                self.logger.info("Sensor: %s, value: %f", self.localaccess.GetSensorName(sensor), value)
        if (timer):
            props=self.localaccess.GetTimerProperties(timer)
            if not props['MuteLog']:
                self.logger.info("Timer: %s, fired", self.localaccess.GetTimerName(timer))
        procs=self.localaccess.FindProcessors(timer, sensor)
        for proc in procs:
            procprop = self.localaccess.GetProcessorProperties(proc)
            if ((self._arithmic(procprop['SensorProcessor'], sensor, value)) or ((procprop['Timer'] == timer) and (timer))):
                self._combine(procprop['Combiner'])
        return

    def _combine(self, Id):
        combprop = None
        if (Id > 0):
            combprop = self.localaccess.GetCombinerProperties(Id)
        if (combprop):
            if (self._depend(combprop['Dependency'],combprop['Invert_Dependency'])):
                for combiner in combprop['Combiner']:
                    self._actuate(combiner[0],combiner[1])
            else:
                self.logger.info("Dependency failed, no action")
        return

    def _depend(self, Id, invert):
        retval = True
        depprop = None
        if (Id > 0):
            depprop = self.localaccess.GetDependencyProperties(Id)
        if (depprop):
            vals = []
            combs = []
            for dependency in depprop['Dependency']:
                if isinstance(dependency, tuple):
                    # Read sensor value and test
                    value = self.localaccess.GetActuator(dependency[0])
                    vals.append(self._arithmic(dependency, dependency[0], value))
                else:
                    # Dependency combiner
                    combs.append(dependency)
            retval = self._logiccombine(combs,vals)
            if (invert):
                retval = (not retval) 
        return (retval)

    def _actuate(self, Id, value):
        # actuator command in queue
        self.commandqueue.put_id("None", Id, value, False)
        return

    def _arithmic(self, process, Id, value):
        retval = False
        if ((Id) and (Id == process[0])):
            if (process[1] == 'eq'):
                retval = (process[2] == value)
            elif (process[1] == 'ne'):
                retval = (process[2] != value)
            elif (process[1] == 'gt'):
                retval = (process[2] > value)
            elif (process[1] == 'ge'):
                retval = (process[2] >= value)
            elif (process[1] == 'lt'):
                retval = (process[2] < value)
            elif (process[1] == 'le'):
                retval = (process[2] <= value)
        return (retval)

    def _logiccombine(self, combs, vals):
        retval = True
        for i in range(0, len(vals)):
            if (i<len(combs)):
                retval = self._logic(vals[i], combs[i], vals[i+1])
                vals[i+1] = retval
            elif (len(combs) == 0):
                retval = vals[i]
        return (retval)

    def _logic(self,val1, comb, val2):
        retval = False
        if (comb == 'and'):
            retval = (val1 and val2)
        elif (comb == 'nand'):
            retval = (not (val1 and val2))
        elif (comb == 'or'):
            retval = (val1 or val2)
        elif (comb == 'nor'):
            retval = (not (val1 or val2))
        elif (comb == 'xor'):
            retval = (val1 != val2)
        elif (comb == 'xnor'):
            retval = (val1 == val2)
        return (retval)

    def HandleRepeats(self):
        for rep in self.ActuatorRepeats:
            if (self.ActuatorRepeats[rep] > 0):
                self._DecRepeats(rep) 
                self.SetActuator(rep, self.localaccess.GetActuator(rep), (self.localaccess.GetSetting('Repeat_amount')-self.ActuatorRepeats[rep]))
        return

    def CheckFlash50(self):
        return (self.Flash50 > 0)

    def GetSensorId(self, queueresult):
        Id = 0
        if (self.commandqueue.hardware(queueresult) ==  "Pi433MHz"):
            Id = self.localaccess.FindSensorbyCode(self.commandqueue.syscode(queueresult), self.commandqueue.groupcode(queueresult), self.commandqueue.devicecode(queueresult))
            if (Id == 0):
                self.logger.info("Received unknown input from Pi433MHz: syscode: %d, groupcode: %d, devicecode: %d", self.commandqueue.syscode(queueresult), self.commandqueue.groupcode(queueresult), self.commandqueue.devicecode(queueresult))
        elif (self.commandqueue.hardware(queueresult) ==  "Lirc"):
            Id = self.localaccess.FindSensorbyURL(self.commandqueue.device(queueresult), self.commandqueue.tag(queueresult))
            if (Id == 0):
                self.logger.info("Received unknown input from Lirc: device: %s, tag: %s", self.commandqueue.device(queueresult), self.commandqueue.tag(queueresult))
        elif (self.commandqueue.hardware(queueresult) ==  "GPIO"):
            Id = self.localaccess.FindGPIOSensorbyCode(self.commandqueue.id(queueresult))
            if (Id == 0):
                self.logger.info("Received unknown GPIO input: %d", self.commandqueue.id(queueresult))
        else: # None, Url or Domoticz
            Id = self.commandqueue.id(queueresult)
            if (Id == 0):
                self.logger.info("Received unknown input: %d", self.commandqueue.id(queueresult))
        return (Id)

    def GetActuatorId(self, queueresult):
        # Actuators cannot be set directly from Pi433MHz or Lirc
        return (self.commandqueue.id(queueresult))

    def SetActuator(self, Id, value, RepeatAction = 0):
        retval = False
        props=self.localaccess.GetActuatorProperties(Id)
        curval = self.localaccess.GetActuator(Id)
        if ((props['SetOnce']) and (curval == value)):
            if not props['MuteLog']:
                self.logger.info("Actuator: %s not set; SetOnce active, value: %f", props['Name'], value)
            retval = True
        else:
            if (self._DoSetActuator(props, value)):
                if ((not RepeatAction) and (props['Repeat'])):
                    self._SetRepeats(Id)
                    if not props['MuteLog']:
                        self.logger.info("Actuator: %s, value: %f <repeat 0>", props['Name'], value)
                    self._UpdateFlash50(props, value, curval)
                else:
                    if (RepeatAction):
                        if not props['MuteLog']:
                            self.logger.info("Actuator: %s, value: %f <repeat %d>", props['Name'], value, RepeatAction)
                    else:
                        if not props['MuteLog']:
                            self.logger.info("Actuator: %s, value: %f", props['Name'], value)
                        self._UpdateFlash50(props, value, curval)
                retval = True
            else:
                if (props['Type'] == 8): # Timer
                    retval = True

        return (retval)

    def _DoSetActuator(self, props, value):
        retval = False
        setvalue = False
        if (props['Type'] == 2): # RF Output
            if (self.pi433MHz):
                retval = (self.pi433MHz.send(props['SysCode'], props['GroupCode'], props['DeviceCode'], value) > 0)
                setvalue = True
        elif (props['Type'] == 4): # IR Output
            if (self.lirc):
                retval = self.lirc.send(props['DeviceURL'], props['KeyTag'])
        elif (props['Type'] == 6): # URL output
            if (self.url):
                retval = self.url.SetActuator(props['Id'], value)
                setvalue = True
        elif (props['Type'] == 10): # Domoticz output
            if (self.domoticz_if):
                retval = self.domoticz_if.SetActuator(props['Id'], value)
                setvalue = True
        elif (props['Type'] == 12): # GPIO output
            if (self.domoticz_if):
                retval = self.gpio.SetActuator(props['DeviceCode'], value)
                setvalue = True
        elif (props['Type'] == 7): # Buffer
            retval = True
            setvalue = True
        elif (props['Type'] == 8): # Timer
            retval = False # Do not handle as output, only set timer
            self.timer.UpdateOffsetTimer(props['DeviceCode'])
            if not props['MuteLog']:
                self.logger.info("Actuator: %s, Timer set: %s", self.localaccess.GetActuatorName(props['Id']), self.localaccess.GetTimerName(props['DeviceCode']))
        elif (props['Type'] == 13): # Script
            retval = self.script.execute(props['DeviceURL'], props['KeyTag'])
        if (setvalue):
            if (self.domoticz_frontend):
                self.domoticz_frontend.SetActuator(props['Id'], value)
            self.localaccess.SetActuator(props['Id'], value)
            self.valueretainer.SetDevices()
            if (not retval):
                self.logger.warning("Actuator: %s, value: %f not set, hardware error", props['Name'], value)
        return (retval)

    def _SetRepeats(self, Id):
        self.ActuatorRepeats[Id]=self.localaccess.GetSetting('Repeat_amount')

    def _DecRepeats(self, Id):
        self.ActuatorRepeats[Id]=(self.ActuatorRepeats[Id]-1)

    def _CheckToggle(self, sensor, value):
        newval = value
        if ((self.localaccess.GetSensorProperties(sensor)['Toggle']) and (self.localaccess.GetSensorDigital(sensor))):
            curval = self.localaccess.GetSensor(sensor)
            if (curval == value):
                newval = (not value)
        return (newval)

    def _UpdateFlash50(self, props, value, oldval):
        if (props['StatusLightFlash']):
            curval = (oldval>0)
            newval = (value>0)
            if ((newval) and (not curval)):
                self.Flash50 += 1
            if ((not newval) and (curval)):
                if (self.Flash50 > 0):
                    self.Flash50 -= 1

    def UpdateActuatorsInit(self):
        for Id in self.localaccess.GetActuatorValues():
            props=self.localaccess.GetActuatorProperties(Id)
            if (props['StatusLightFlash']):
                if (self.localaccess.GetActuator(Id)>0):
                    self.Flash50 += 1
