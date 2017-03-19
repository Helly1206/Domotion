# -*- coding: utf-8 -*-
#########################################################
# SERVICE : engine.py                                   #
#           Python Domotion engine                      #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
import logging
from commandqueue import commandqueue
from localaccess import localaccess
from timer import timer
from fuel import fuel
from valueretainer import valueretainer
#########################################################

####################### GLOBALS #########################

#########################################################
# Class : engine                                        #
#########################################################
class engine(fuel):
    def __init__(self, commandqueue, dbpath, LoopTime):
        self.commandqueue=commandqueue
        self.looptime=LoopTime
        self.logger = logging.getLogger('Domotion.Engine')
        self.logger.info("initialized")
        self.localaccess = localaccess(dbpath)
        self.localaccess.InitBuffers()
        self.valueretainer = valueretainer()
        self.domoticz_api = None
        self.domoticz_frontend = None
        self.url = None
        self.domoticz_if = None
        self.lirc = None
        self.pi433MHz = None
        self.timer = timer(self.commandqueue)
        self.timer.start()
        self.messagetext = ""
        self.message = localaccess.GetSetting('Domoticz_message')
        self.resend = False
        super(engine, self).__init__()
        self.UpdateSensorsPoll()
        self.loopcnt = 0
        self.repeattime = 0

    def __del__(self):
        super(engine, self).__del__()
        if (self.timer != None):
            self.timer.terminate()
            self.timer.join()
            del self.timer
        del self.localaccess
        self.domoticz_api = None
        self.domoticz_frontend = None
        self.url = None
        self.domoticz_if = None
        self.lirc = None
        self.pi433MHz = None
        self.logger.info("finished")

    def instances(self, domoticz_api, domoticz_frontend, url, domoticz_if, lirc, pi433MHz):
        self.domoticz_api = domoticz_api
        self.domoticz_frontend = domoticz_frontend
        self.url = url
        self.domoticz_if = domoticz_if
        self.lirc = lirc
        self.pi433MHz = pi433MHz
        self.timer.instances(domoticz_api)
        self.UpdateSensorsPoll()
        self.UpdateRepeat()

    def loop(self):
        result = None
        if (self.resend):
            self.DomoticzMessenger(self.messagetext)
        if (self.repeattime):
            if (self.loopcnt >= self.repeattime):
                self.loopcnt = 0
                self.HandleRepeats()
            else:
                self.loopcnt += 1
        if (self.commandqueue):
            result = self.commandqueue.get()
        if (result):
            # Test for callback on changes in process or settings
            if (self.commandqueue.hardware(result) ==  "Callback"):
                retval = self.commandqueue.device(result).lower()
                if (retval ==  "process"):
                    self.localaccess.InitBuffers()
                    if (self.domoticz_frontend):
                        if (self.domoticz_frontend.updatesensorsactuators()):
                            self.logger.info("Sensors and actuators updated to Domoticz frontend")
                    self.UpdateSensorsPoll()
                    self.UpdateRepeat()
                    self.InitRepeats()
                    self.timer.UpdateAll()
                    self.valueretainer.Update()
                    self.logger.info("Process updated")
                    pass
                elif (retval ==  "settings"):
                    if (self.domoticz_api):
                        self.domoticz_api.updatesettings()
                    if (self.domoticz_frontend):
                        self.message = self.domoticz_frontend.updatesettings()
                    if (self.url):
                        self.url.updatesettings()
                    self.timer.UpdateAll()
                    self.UpdateRepeat()
                    self.valueretainer.Update()
                    self.logger.info("Settings updated")
                    pass
                elif (retval == "timerrecalc"):
                    self.timer.UpdateAll()
            elif (self.commandqueue.hardware(result) ==  "Timer"):
                if (self.commandqueue.value(result)):
                    self.process(self.commandqueue.devicecode(result), 0, 0)
            else: # sensor or actuator set
                if self.commandqueue.issensor(result):
                    self.process(0, self.GetSensorId(result), self.commandqueue.value(result))
                else:
                    self.SetActuator(self.GetActuatorId(result), self.commandqueue.value(result))
                #self.logger.info(result)
        return result

    #def Check sensors poll ..... (for domo_if and URL)
    def UpdateSensorsPoll(self):
        if (self.url):
            self.url.UpdateDevices(self.localaccess.GetSensorPoll("URL"),[])
        if (self.domoticz_if):
            self.domoticz_if.UpdateDevices(self.localaccess.GetSensorPoll("Domoticz"),[])
        return

    def UpdateRepeat(self):
        self.repeattime = int(float(self.localaccess.GetSetting('Repeat_time')) / self.looptime)
        return

    def DomoticzMessenger(self, message):
        success = False
        if ((self.domoticz_frontend) and (self.message)):
            success = self.domoticz_frontend.SendMessage(message)
            if (not success):
                self.resend = True     
                self.messagetext = message
            else:
                self.resend = False
                self.messagetext = ""   

        return success