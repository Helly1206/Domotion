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
from utilities import localformat
#########################################################

####################### GLOBALS #########################
_domoticz_types = {'general':0, 'light/switch': 6, 'temp': 80, 'humidity': 81, 'rain': 85, 'wind': 86}
_domoticz_subtypes = {'switch':0, 'voltage': 4, 'percentage': 2, 'current': 19, 'pressure': 1}

#########################################################
# Class : domoticz_api                                  #
#########################################################
class domoticz_api(object):
    mutex = None
    url = ""
    auth = ""

    def __init__(self):
        self._initmutex()
        self._updatesettings()

    def __del__(self):
        self._delmutex()

    def updatesettings(self):
        return self._updatesettings()

    @classmethod
    def _initmutex(cls):
        cls.mutex = Lock()

    @classmethod
    def _delmutex(cls):
        del cls.mutex

    @classmethod
    def _acquire(cls):
        if (cls.mutex):
            cls.mutex.acquire()
            return True
        else:
            return False

    @classmethod
    def _release(cls):
        if (cls.mutex):
            cls.mutex.release()
            return True
        else:
            return False

    @classmethod
    def _updatesettings(cls):
        if (cls._acquire()):
            cls._buildauth(localaccess.GetSetting('Domoticz_username'),localaccess.GetSetting('Domoticz_password'))
            cls._buildURL(localaccess.GetSetting('Domoticz_URL'), localaccess.GetSetting('Domoticz_port'), localaccess.GetSetting('Domoticz_SSL'))
            cls._release()
        return

    @classmethod
    def _buildURL(cls, url, port, SSL):
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

        cls.url = "%s%s%s"%(pre,url,port)

        return cls.url

    @classmethod
    def _buildauth(cls,name,password):
        if name:
            cls.auth = (name, b64decode(password))
        else:
            cls.auth = None

        return cls.auth

    @classmethod
    def _builduri(cls,params):
        first = True
        uri = "%s/json.htm?"%(cls.url)
        for key in params:
            if not first:
                uri+="&"
            else:
                first = False
            uri+="%s=%s"%(key,params[key])

        return uri

    @classmethod
    def _httpget(cls,params):
        success = False
        retval = []
        if (cls._acquire()):
            try:
                if cls.auth:
                    result = requests.get(cls._builduri(params), auth=cls.auth, verify=False)
                else:
                    result = requests.get(cls._builduri(params), verify=False)
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
            cls._release()
        return success, retval

    @classmethod
    def getSunRiseSet(cls):
        success, result = cls._httpget({"type": "command", "param": "getSunRiseSet"})
        if success:
            sunrise = localformat.Asc2Mod(result['Sunrise'], True)
            sunset = localformat.Asc2Mod(result['Sunset'], True)
        else:
            sunrise = 0
            sunset = 0
        return success, sunrise, sunset

    @classmethod
    def getDummy(cls):
        success, result = cls._httpget({"type": "devices", "rid": "0"})
        return success

    @classmethod
    def getHardware(cls):
        return cls._httpget({"type": "hardware"})

    @classmethod
    def createHardware(cls):
        return cls._httpget({"type": "command", "param": "addhardware", "htype": "15", "name": hardwarename, "enabled": "true"})

    @classmethod
    def enableHardware(cls, idx):
        return cls._httpget({"type": "command", "param": "updatehardware", "htype": "15", "name": hardwarename, "idx": idx, "enabled": "true"})

    @classmethod
    def getDevices(cls):
        return cls._httpget({"type": "devices"})

    @classmethod
    def addDevice(cls, hardware, name, sensortype): #json.htm?type=createvirtualsensor&idx=2&sensorname=Ivo2&sensortype=6
        success, result = cls._httpget({"type": "createvirtualsensor", "idx": hardware, "sensorname": name, "sensortype": sensortype[0]})
        if success:
            if (result["status"] != 'OK'):
                success = False
        return success

    @classmethod
    def updateDevice(cls, idx, name, sensortype, image=False): #json.htm?type=setused&idx=22&name=Ivo2&switchtype=0&customimage=9&used=true
        if (image):
            success, result = cls._httpget({"type": "setused", "idx": idx, "name": name, "switchtype": sensortype[1], "customimage": sensortype[2], "used": "true"})
        else:
            success, result = cls._httpget({"type": "setused", "idx": idx, "name": name, "switchtype": sensortype[1], "used": "true"})
        if success:
            if (result["status"] != 'OK'):
                success = False
        return success

    @classmethod
    def deleteDevice(cls, idx):
        success, result = cls._httpget({"type": "deletedevice", "idx": idx})
        if success:
            if (result["status"] != 'OK'):
                success = False
        return success

    @classmethod
    def getDevice(cls, idx): #json.htm?type=devices&rid=27
        success, result = cls._httpget({"type": "devices", "rid": idx})
        if success:
            if (result["status"] != 'OK'):
                success = False
        return success, result        

    @classmethod
    def setDevice(cls, idx, value, digital=True): #json.htm?type=command&param=udevice&idx=IDX&nvalue=0&svalue=DISTANCE
        if (digital):
            success, result = cls._httpget({"type": "command", "param": "udevice", "idx": idx, "nvalue": value, "svalue": 0})
        else:
            success, result = cls._httpget({"type": "command", "param": "udevice", "idx": idx, "nvalue": 0, "svalue": value})
        if success:
            if (result["status"] != 'OK'):
                success = False
        return success       

    @classmethod
    def GetDeviceType(cls, device):
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

    @classmethod
    def GetValue(cls, device):
        value = 0
        Data = device['Data']
        DeviceType = _domoticz_types[device['Type'].lower()]
        if (DeviceType == 6): # Light/ Switch # SwitchTypeVal: 3 = blinds, 11 = lock
            if ((Data.lower() == "on") or ((Data.lower() == "closed") and (device['SwitchTypeVal'] == 3)) or ((Data.lower() == "open") and (device['SwitchTypeVal'] == 11))):
                value = 1
        else:
            value = float(''.join(c for c in Data if c in "0123456789."))
        return value