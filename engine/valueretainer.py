# -*- coding: utf-8 -*-
#########################################################
# SERVICE : valueretainer.py                            #
#           Python Domotion retainer for values on dsk  #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from .localaccess import localaccess
from base64 import b64encode, b64decode
import os
import json

#########################################################

####################### GLOBALS #########################
runpath = "/run"
runpath2 = "/run/user"
filename = "DomotionRetainer.dat"

#########################################################
# Class : valueretainer                                 #
#########################################################
class valueretainer(object):
    def __init__(self, localaccess):
        self.localaccess = localaccess
        self.Retainer = False
        self.RetainerPath = ""
        self.Update()

    def __del__(self):
        self.Retainer = False
        self.RetainerPath = ""

    def Update(self):
        if (self.localaccess.GetSetting('Retain_values')):
            self.Retainer = self._CheckLocation()
        else:
            self.Retainer = False
        self.UpdateDevices()

    def _CheckLocation(self): # To /run if uid == 0, or /run/user/xxx, where xxx = os.getuid()
        retval = False
        userid = os.getuid()
        if (userid == 0):
            destpath = runpath
        else:
            destpath = os.path.join(runpath2, str(userid))

        if os.path.exists(destpath):
            if os.access(destpath, os.W_OK):
                retainerpath = os.path.join(destpath, filename)
                if os.path.isfile(retainerpath):
                    if os.access(retainerpath, os.W_OK):
                        retval = True
                        self.RetainerPath = retainerpath
                else:
                    # File doesn't exist, make new
                    try:
                        open(retainerpath, 'a').close()
                        retval = True
                        self.RetainerPath = retainerpath
                    except:
                        pass

        return (retval)

    def UpdateDevices(self):
        if (self.Retainer):
            Devices = self._load_obj()
            if (Devices):
                if (len(Devices) == 2):
                    for Id in Devices[0]:
                        self.localaccess.SetSensor(int(Id), Devices[0][Id])
                    for Id in Devices[1]:
                        self.localaccess.SetActuator(int(Id), Devices[1][Id])
        return

    def SetDevices(self):
        if (self.Retainer):
            Devices = [self.localaccess.GetSensorValues(), self.localaccess.GetActuatorValues()]
            self._save_obj(Devices)
        return

    def _save_obj(self, obj):
        if ((self.Retainer) and (self.RetainerPath)):
            with open(self.RetainerPath, 'wb') as f:
                f.write(b64encode(bytes(json.dumps(obj),"utf-8")))
        return

    def _load_obj(self):
        if ((self.Retainer) and (self.RetainerPath)):
            with open(self.RetainerPath, 'rb') as f:
                try:
                    return json.loads(b64decode(f.read()))
                except:
                    return None
        else:
            return None



