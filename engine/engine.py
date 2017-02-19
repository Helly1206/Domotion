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
#########################################################

####################### GLOBALS #########################

#########################################################
# Class : engine                                        #
#########################################################
class engine(fuel):
    def __init__(self, commandqueue, dbpath):
        self.commandqueue=commandqueue
        self.logger = logging.getLogger('Domotion.Engine')
        self.logger.info("initialized")
        self.localaccess = localaccess(dbpath)
        self.localaccess.InitBuffers()
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

    def loop(self):
        result = None
        if (self.resend):
            self.DomoticzMessenger(self.messagetext)
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
                    #print "Process changed"
                    #TBD internal things on local access.
                    pass
                elif (retval ==  "settings"):
                    if (self.domoticz_api):
                        self.domoticz_api.updatesettings()
                    if (self.domoticz_frontend):
                        self.message = self.domoticz_frontend.updatesettings()
                    if (self.url):
                            self.url.updatesettings()
                    self.logger.info("Settings updated")
                    #print "Setting changed"
                    #TBD timezone settings Lon/ Lat/ Timezone --> Timer class
                    pass
            elif (self.commandqueue.hardware(result) ==  "None"):
                if self.commandqueue.issensor(result):
                    localaccess.SetSensor(self.commandqueue.devicecode(result),self.commandqueue.value(result))
                else:
                    localaccess.SetActuator(self.commandqueue.devicecode(result),self.commandqueue.value(result))
                self.logger.info(result)
        return result

    #def Check sensors poll ..... (for domo_if and URL)
    def UpdateSensorsPoll(self):
        # Update devices domo_if and URL
        # Set and update sensors to be updated in domoticz_if: UpdateDevices(self,sensors,actuators)
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