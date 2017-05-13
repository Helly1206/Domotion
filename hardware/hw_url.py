# -*- coding: utf-8 -*-
#########################################################
# SERVICE : hw_url.py                                   #
#           Python handling for basic web access URLs   #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from threading import Thread, Event, Lock
import logging
from time import sleep
from engine import localaccess
from engine import commandqueue
from base64 import b64decode
import requests
#########################################################

####################### GLOBALS #########################
sleeptime = 0.1
maxcnt = (1000/sleeptime)
updatecnt = (1/sleeptime)

# Maybe a good idea to have a list of sensors and update them in a thread every 1 second ....
# Don't care about connections and non existing devices. failure means don't update

#########################################################
# Class : url                                           #
#########################################################
class url(Thread):
    def __init__(self, commandqueue):
        self.commandqueue=commandqueue
        self.logger = logging.getLogger('Domotion.url')
        self.sensors = []
        self.actuators = []
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        self.mutex = Lock()
        self.updatesettings()
        
    def __del__(self):
        del self.mutex
        del self.term
        self.logger.info("finished")

    def UpdateDevices(self,sensors,actuators):
        self.mutex.acquire()
        self.sensors = sensors
        self.actuators = actuators
        self.mutex.release()

    def updatesettings(self):
        if (self.mutex):
            self.mutex.acquire()
            self._buildauth(localaccess.GetSetting('URL_username'),localaccess.GetSetting('URL_password'))
            self.SSL=localaccess.GetSetting('URL_SSL')
            self.mutex.release()
        return

    def SetSensor(self, key, value):
        return self._SetSensorURL(key, value)

    def SetActuator(self, key, value):
        return self._SetActuatorURL(key, value)

    def terminate(self):
            self.term.set()

    def run(self):
        try:
            counter = 0
            connected = False
            connectedprev = False
            self.logger.info("running")

            while (not self.term.isSet()):
                if (counter % updatecnt == 0):
                    for sensor in self.sensors:
                        success, value = self._GetSensorURL(sensor)
                        if (success):
                            curval = localaccess.GetSensor(sensor)
                            if (curval != value):
                                self.commandqueue.put_id("Url", sensor, value, True)
                        connected = success
                    for actuator in self.actuators:
                        success, value = self._GetActuatorURL(actuator)
                        if (success):
                            curval = localaccess.GetActuator(actuator)
                            if (curval != value):
                                self.commandqueue.put_id("Url", actuator, value, False)
                        connected = success
                    if (connected != connectedprev):
                        if (connected):
                            self.logger.info("connection established")
                        else:
                            self.logger.info("no connection")
                        connectedprev = connected
                sleep(sleeptime)
                if (counter < maxcnt):
                    counter += 1
                else:
                    counter = 0

            self.logger.info("terminating")
        except Exception, e:
            self.logger.exception(e)

    def _buildauth(self,name,password):
        if name:
            self.auth = (name, b64decode(password))
        else:
            self.auth = None

        return self.auth

    def _buildURL(self, url):
        URLspl = url.split("/",2)
        #remove http or https
        if (URLspl[0].lower() == "http:") or (URLspl[0].lower() == "https:"):
            url = URLspl[2]
        if (self.SSL):
            pre = "https://"
        else:
            pre = "http://"

        return "%s%s"%(pre,url)

    def _builduri(self, url, params):
        first = True
        uri = "%s/json.htm?"%(self._buildURL)
        for key in params:
            if not first:
                uri+="&"
            else:
                first = False
            uri+="%s=%s"%(key,params[key])

        return uri

    def _httpget(self,url,params):
        success = False
        retval = []
        if (self.mutex):
            self.mutex.acquire()
            try:
                if self.auth:
                    result = requests.get(self._builduri(url, params), auth=self.auth, verify=False)
                else:
                    result = requests.get(self._builduri(url, params), verify=False)
                if (result.status_code == 200):
                    retval = result.json()
                    success = True
                #else:
                #    self.logger.warning("Connection response error %d",result.status_code)
            except requests.exceptions.ConnectionError:
                pass
                #self.logger.warning("No connection")
            except:
                pass
                #self.logger.warning("Connection error")
            self.mutex.release()
        return success, retval

    def _GetSensorURL(self, key):
        success = True
        value = None
        prop = localaccess.GetSensorProperties(key)
        success, result = self._httpget(prop['DeviceURL'],{"tag": prop['KeyTag']})
        if (success):
            if ((result[0].lower == 'value') and (result[1] == prop['KeyTag'])):
                value = int(result[2])
            else:
                success = False
        return success, value

    def _GetActuatorURL(self, key):
        success = True
        value = None
        prop = localaccess.GetActuatorProperties(key)
        success, result = self._httpget(prop['DeviceURL'],{"tag": prop['KeyTag']})
        if (success):
            if ((result[0].lower == 'value') and (result[1] == prop['KeyTag'])):
                value = int(result[2])
            else:
                success = False
        return success, value

    def _SetSensorURL(self, key, value):
        success = True
        prop = localaccess.GetSensorProperties(key)
        success, result = self._httpget(prop['DeviceURL'],{"tag": prop['KeyTag'], "value": str(value)})
        if (success):
            if ((result[0].lower == 'stored') and (result[1] == prop['KeyTag'])):
                success = True
            else:
                success = False
        return success

    def _SetActuatorURL(self, key, value):
        success = True
        prop = localaccess.GetActuatorProperties(key)
        success, result = self._httpget(prop['DeviceURL'],{"tag": prop['KeyTag'], "value": str(value)})
        if (success):
            if ((result[0].lower == 'stored') and (result[1] == prop['KeyTag'])):
                success = True
            else:
                success = False
        return success