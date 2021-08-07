# -*- coding: utf-8 -*-
#########################################################
# SERVICE : engine.py                                   #
#           Python Domotion engine                      #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
import logging
from .commandqueue import commandqueue
from .localaccess import localaccess
from .timer import timer
from .fuel import fuel
from .scripts import scripts
from .valueretainer import valueretainer
from .statuslight import statuslight
#########################################################

####################### GLOBALS #########################
message = { 0: "Domotion Finished",
            1: "Domotion Running",
            2: "Domotion Error",
            3: "Domotion Finished",
            4: "Domotion Running",
            5: "Domotion Error",
            6: "Domotion Running (Normal day)",
            7: "Domotion Running (Home day)",
            8: "Domotion Running (Trip day)",
            9: "Domotion Running (Normal day) [Master]",
            10: "Domotion Running (Home day) [Master]",
            11: "Domotion Running (Trip day) [Master]"}
test = False

#########################################################
# Class : engine                                        #
#########################################################
class engine(fuel):
    def __init__(self, commandqueue, localaccess, scripts, LoopTime):
        self.commandqueue = commandqueue
        self.localaccess = localaccess
        self.scripts = scripts
        self.looptime = LoopTime
        self.logger = logging.getLogger('Domotion.Engine')
        self.logger.info("initialized")
        self.localaccess.InitBuffers()
        self.valueretainer = valueretainer(self.localaccess)
        self.domoticz_api = None
        self.domoticz_frontend = None
        self.gpio = None
        self.script = None
        self.url = None
        self.domoticz_if = None
        self.lirc = None
        self.pi433MHz = None
        self.mqtt = None
        self.timer = timer(self.commandqueue, self.localaccess)
        self.timer.start()
        self.messageid = 2
        self.message = self.localaccess.GetSetting('Domoticz_message')
        self.resend = False
        self.statuslight = statuslight(self.localaccess)
        self.statuslight.start()
        super(engine, self).__init__()
        self.UpdateSensorsPoll()
        self.UpdateSensorsActuatorsURL()
        self.UpdateSensorsActuatorsGPIO()
        self.UpdateActuatorsInit()
        self.loopcnt = 0
        self.repeattime = 0
        self.success = True
        self.testcnt=0

    def __del__(self):
        super(engine, self).__del__()
        if (self.statuslight != None):
            self.statuslight.terminate()
            self.statuslight.join(5)
            del self.statuslight
        del self.valueretainer
        if (self.timer != None):
            self.timer.terminate()
            self.timer.join(5)
            del self.timer
        self.domoticz_api = None
        self.domoticz_frontend = None
        self.gpio = None
        self.script = None
        self.url = None
        self.domoticz_if = None
        self.lirc = None
        self.pi433MHz = None
        self.mqtt = None
        self.logger.info("finished")

    def instances(self, domoticz_api, domoticz_frontend, gpio, url, domoticz_if, lirc, pi433MHz, script, mqtt):
        self.domoticz_api = domoticz_api
        self.domoticz_frontend = domoticz_frontend
        self.gpio = gpio
        self.url = url
        self.domoticz_if = domoticz_if
        self.lirc = lirc
        self.pi433MHz = pi433MHz
        self.script = script
        self.mqtt = mqtt
        self.timer.instances(domoticz_api)
        self.statuslight.instances(gpio)
        self.UpdateSensorsPoll()
        self.UpdateSensorsActuatorsURL()
        self.UpdateSensorsActuatorsGPIO()
        self.UpdateSensorsActuatorsMQTT()
        self.UpdateRepeat()

    def loop(self):
        if (test):
            if ((self.testcnt%10)==0):
                self.logger.info("Line of testing loop: %d"%(self.testcnt/10))
            self.testcnt+=1
        result = None
        if (self.resend):
            self.DomoticzMessenger(self.messageid)
        if (self.repeattime):
            if (self.loopcnt >= self.repeattime):
                self.loopcnt = 0
                self.HandleRepeats()
            else:
                self.loopcnt += 1
        if (self.statuslight):
            self.statuslight.SetFlash50(self.CheckFlash50())
        if (self.commandqueue):
            result = self.commandqueue.get()
        if (result):
            # Test for callback on changes in process or settings
            if (self.statuslight):
                self.statuslight.Busy()
            if (self.commandqueue.hardware(result) ==  "Callback"):
                retval = self.commandqueue.value(result).lower()
                if (retval ==  "process"):
                    self.localaccess.InitBuffers()
                    if (self.domoticz_frontend):
                        if (self.domoticz_frontend.updatesensorsactuators()):
                            self.logger.info("Sensors and actuators updated to Domoticz frontend")
                    self.UpdateSensorsPoll()
                    self.UpdateSensorsActuatorsURL()
                    self.UpdateSensorsActuatorsGPIO()
                    self.UpdateSensorsActuatorsMQTT()
                    self.UpdateRepeat()
                    self.InitRepeats()
                    self.timer.UpdateAll(True)
                    self.valueretainer.Update()
                    self.scripts.update()
                    self.UpdateAlways()
                    self.logger.info("Process updated")
                elif (retval ==  "settings"):
                    if (self.domoticz_api):
                        self.domoticz_api.updatesettings()
                    if (self.domoticz_frontend):
                        self.message = self.domoticz_frontend.updatesettings()
                    if (self.url):
                        self.url.updatesettings()
                    self.timer.UpdateAll()
                    self.UpdateRepeat()
                    self.UpdateSensorsActuatorsURL()
                    self.UpdateSensorsActuatorsGPIO()
                    self.UpdateSensorsActuatorsMQTT()
                    self.valueretainer.Update()
                    self.scripts.update()
                    self.UpdateAlways()
                    self.logger.info("Settings updated")
                elif (retval == "timerrecalc"):
                    self.timer.UpdateAll()
            elif (self.commandqueue.hardware(result) ==  "Timer"):
                if (self.commandqueue.value(result)):
                    self.process(self.commandqueue.id(result), 0, 0)
            else: # sensor or actuator set
                if (self.statuslight):
                    self.statuslight.SetDeviceSet()
                if self.commandqueue.issensor(result):
                    self.process(0, self.GetSensorId(result), self.commandqueue.value(result))
                else:
                    self.success = self.SetActuator(self.GetActuatorId(result), self.commandqueue.value(result))
                #self.logger.info(result)
        else: # No command in queue, process [always] and status
            self.processAlways()
            if (self.statuslight):
                if (self.success):
                    if (self.localaccess.GetStatusBusy()):
                        self.statuslight.Busy()
                    else:
                        self.statuslight.Ok()
                else:
                    self.statuslight.Error()
            if (not self.success):
                self.DomoticzMessenger(2)
            else:
                self.UpdateMessage()
        return result

    #def Check sensors poll ..... (for domo_if and URL)
    def UpdateSensorsPoll(self):
        if (self.domoticz_if):
            self.domoticz_if.UpdateDevices(self.localaccess.GetSensorPoll("Domoticz"),[])
        return

    def UpdateSensorsActuatorsURL(self):
        if (self.url):
            self.url.UpdateDevices(self.localaccess.FindSensorbyHardware("URL"),self.localaccess.FindActuatorbyHardware("URL"))
        return

    def UpdateSensorsActuatorsGPIO(self):
        if (self.gpio):
            self.gpio.UpdateDevices(self.localaccess.FindGPIOSensors(),self.statuslight.AddStatusActuators(self.localaccess.FindGPIOActuators()))
        return

    def UpdateSensorsActuatorsMQTT(self):
        if (self.mqtt):
            self.mqtt.UpdateDevices(self.localaccess.FindSensorbyHardware("MQTT"),self.localaccess.FindActuatorbyHardware("MQTT"))
        return

    def UpdateRepeat(self):
        self.repeattime = int(float(self.localaccess.GetSetting('Repeat_time')) / self.looptime)
        return

    def DomoticzMessenger(self, messageid):
        success = False
        if ((self.domoticz_frontend) and (self.message)):
            success = self.domoticz_frontend.SendMessage(message[messageid])
            self.messageid = messageid
            if (not success):
                self.resend = True
            else:
                self.resend = False
                self.messageid = 2

        return success

    def UpdateMessage(self):
        messageid = 6 + self.localaccess.GetToday()
        if (self.CheckFlash50()):
            messageid += 3
        if (messageid != self.messageid):
            self.DomoticzMessenger(messageid)
        return
