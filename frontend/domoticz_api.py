# -*- coding: utf-8 -*-
#########################################################
# SERVICE : domoticz_api.py                             #
#           Inferface for domoticz api for Domotion     #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from base64 import b64decode
import requests
from threading import Lock
from engine import localaccess
#########################################################

####################### GLOBALS #########################
_domoticz_types = {'general':0, 'light/switch': 6, 'temp': 80, 'humidity': 81, 'rain': 85, 'wind': 86}
_domoticz_subtypes = {'switch':0, 'voltage': 4, 'percentage': 2, 'current': 19, 'pressure': 1}

#########################################################
# Class : domoticz_api                                  #
#########################################################
class domoticz_api(object):

    def __init__(self, localaccess):
        self.localaccess=localaccess
        self.mutex = None
        self.url = ""
        self.auth = ""
        self._initmutex()
        self._updatesettings()

    def __del__(self):
        self._delmutex()

    def updatesettings(self):
        return self._updatesettings()

    def _initmutex(self):
        self.mutex = Lock()

    def _delmutex(self):
        del self.mutex

    def _acquire(self):
        if (self.mutex):
            self.mutex.acquire()
            return True
        else:
            return False

    def _release(self):
        if (self.mutex):
            self.mutex.release()
            return True
        else:
            return False

    def _updatesettings(self):
        if (self._acquire()):
            self._buildauth(self.localaccess.GetSetting('Domoticz_username'),self.localaccess.GetSetting('Domoticz_password'))
            self._buildURL(self.localaccess.GetSetting('Domoticz_URL'), self.localaccess.GetSetting('Domoticz_port'), self.localaccess.GetSetting('Domoticz_SSL'))
            self._release()
        return

    def _buildURL(self, url, port, SSL):
        URLspl = url.split("/",2)
        #remove http or https
        if (URLspl[0].lower() == "http:") or (URLspl[0].lower() == "https:"):
            url = URLspl[2]
        if (SSL):
            pre = "https://"
        else:
            pre = "http://"

        try:
            p = int(port)
        except:
            p = 0
        if (p > 0):
            port = ":%s"%port
        else:
            port = ""

        self.url = "%s%s%s"%(pre,url,port)

        return self.url

    def _buildauth(self,name,password):
        if name:
            self.auth = (name, b64decode(password))
        else:
            self.auth = None

        return self.auth

    def _builduri(self,params):
        first = True
        uri = "%s/json.htm?"%(self.url)
        for key in params:
            if not first:
                uri+="&"
            else:
                first = False
            uri+="%s=%s"%(key,params[key])

        return uri

    def _httpget(self,params):
        success = False
        retval = []
        if (self._acquire()):
            try:
                if self.auth:
                    result = requests.get(self._builduri(params), auth=self.auth, verify=False)
                else:
                    result = requests.get(self._builduri(params), verify=False)
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
            self._release()
        return success, retval

    def getSunRiseSet(self):
        success, result = self._httpget({"type": "command", "param": "getSunRiseSet"})
        if success:
            sunrise = self.localaccess.Asc2Mod(result['Sunrise'])
            sunset = self.localaccess.Asc2Mod(result['Sunset'])
        else:
            sunrise = 0
            sunset = 0
        return success, sunrise, sunset

    def getDummy(self):
        success, result = self._httpget({"type": "devices", "rid": "0"})
        return success

    def getHardware(self):
        return self._httpget({"type": "hardware"})

    def createHardware(self):
        return self._httpget({"type": "command", "param": "addhardware", "htype": "15", "name": hardwarename, "enabled": "true"})

    def enableHardware(self, idx):
        return self._httpget({"type": "command", "param": "updatehardware", "htype": "15", "name": hardwarename, "idx": idx, "enabled": "true"})

    def getDevices(self):
        return self._httpget({"type": "devices"})

    def addDevice(self, hardware, name, sensortype): #json.htm?type=createvirtualsensor&idx=2&sensorname=Ivo2&sensortype=6
        success, result = self._httpget({"type": "createvirtualsensor", "idx": hardware, "sensorname": name, "sensortype": sensortype[0]})
        if success:
            if (result["status"] != 'OK'):
                success = False
        return success

    def updateDevice(self, idx, name, sensortype, image=False): #json.htm?type=setused&idx=22&name=Ivo2&switchtype=0&customimage=9&used=true
        if (image):
            success, result = self._httpget({"type": "setused", "idx": idx, "name": name, "switchtype": sensortype[1], "customimage": sensortype[2], "used": "true"})
        else:
            success, result = self._httpget({"type": "setused", "idx": idx, "name": name, "switchtype": sensortype[1], "used": "true"})
        if success:
            if (result["status"] != 'OK'):
                success = False
        return success

    def deleteDevice(self, idx):
        success, result = self._httpget({"type": "deletedevice", "idx": idx})
        if success:
            if (result["status"] != 'OK'):
                success = False
        return success

    def getDevice(self, idx): #json.htm?type=devices&rid=27
        success, result = self._httpget({"type": "devices", "rid": idx})
        if success:
            if (result["status"] != 'OK'):
                success = False
        return success, result        

    def setDevice(self, idx, value, digital=True): #json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=DISTANCE
        if (digital):
            success, result = self._httpget({"type": "command", "param": "udevice", "idx": idx, "nvalue": value, "svalue": 0})
        else:
            success, result = self._httpget({"type": "command", "param": "udevice", "idx": idx, "nvalue": 0, "svalue": value})
        if success:
            if (result["status"] != 'OK'):
                success = False
        return success       

    def GetDeviceType(self, device):
        DeviceType = [0, 0, 0]
        if (device['Type'].lower() == 'general'):
            DeviceType[0] = _domoticz_subtypes[device['SubType'].lower()]
        else:
            DeviceType[0] = _domoticz_types[device['Type'].lower()]
            if (device['Type'].lower() == 'light/switch'):
                DeviceType[1] = device['SwitchTypeVal']
                # customimage will not be updated when subtype doesn't change
                DeviceType[2] = device['CustomImage']
        return tuple(DeviceType)

    def GetValue(self, device):
        value = 0
        Data = device['Data']
        DeviceType = _domoticz_types[device['Type'].lower()]
        if (DeviceType == 6): # Light/ Switch # SwitchTypeVal: 3 = blinds, 11 = lock
            if ((Data.lower() == "on") or ((Data.lower() == "closed") and (device['SwitchTypeVal'] == 3)) or ((Data.lower() == "open") and (device['SwitchTypeVal'] == 11))):
                value = 1
        else:
            value = float(''.join(c for c in Data if c in "0123456789."))
        return value