# -*- coding: utf-8 -*-
#########################################################
# SERVICE : commandqueue.py                             #
#           Python commandqueue for Domotion            #
#           I. Helwegen 2017                            #
#########################################################
# Format tuple(Hardware{key}, SysCode, GroupCode, DeviceCode, URL/Device, Tag, Value, Sensor)

####################### IMPORTS #########################
from queue import Queue

#########################################################

####################### GLOBALS #########################

#########################################################
# Class : commandqueue                                  #
#########################################################
class commandqueue(object):
    _hardware = {0: "None", 1: "Pi433MHz", 2: "Lirc", 3: "Url", 4: "Domoticz", 5: "GPIO", 99: "Timer", 999: "Callback"}
    def __init__(self):
        self.queue = Queue()

    def __del__(self):
        if (self.queue):
            del self.queue

    def get(self):
        if self.queue.empty():
            return None
        else:
            return self.queue.get()

    def put(self, format):
            return self.queue.put(format)

    def put_all(self, hardware, syscode, groupcode, devicecode, URL, Tag, value, sensor = True):
        return self.put(self.build_format(hardware, syscode, groupcode, devicecode, URL, Tag, value, sensor))

    def put_id(self, hardware, id, value, sensor = True):
        ivalue = 0
        try:
            ivalue = int(value)
        except ValueError:
            try:
                ivalue = float(value)
            except:
                ivalue = 0
        self.put(self.build_id(hardware, id, ivalue, sensor))
        return ivalue

    def put_code(self, hardware, syscode, groupcode, devicecode, value, sensor = True):
        return self.put(self.build_code(hardware, syscode, groupcode, devicecode, value, sensor))   

    def put_device(self, hardware, URL, Tag, value, sensor = True):
        return self.put(self.build_device(hardware, URL, Tag, value, sensor)) 

    def callback(self, type):
        return self.put(self.build_callback(type))  

    def build_format(self, hardware, syscode, groupcode, devicecode, URL, Tag, value, sensor = True):
        return (self.getkey(hardware), syscode, groupcode, devicecode, URL, Tag, value, sensor)

    def build_id(self, hardware, id, value, sensor = True):
        return (self.getkey(hardware), 0, 0, id, "", "", value, sensor)

    def build_code(self, hardware, syscode, groupcode, devicecode, value, sensor = True):
        return (self.getkey(hardware), syscode, groupcode, devicecode, "", "", value, sensor)  

    def build_device(self, hardware, URL, Tag, value, sensor = True):
        return (self.getkey(hardware), 0, 0, 0, URL, Tag, value, sensor)

    def build_callback(self, type):
        return (self.getkey("Callback"), 0, 0, 0, "", "", type, False)

    def join(self):
        return self.queue.task_done()

    def task_done(self):
        return self.queue.join()

    def hardware(self, format):
        return (self._hardware[format[0]])

    def syscode(self, format):
        return (format[1])

    def groupcode(self, format):
        return (format[2])

    def devicecode(self, format):
        return (format[3])

    def id(self, format):
        return (format[3])

    def device(self, format): # URL
        return (format[4])

    def tag(self, format):
        return (format[5])

    def value(self, format):
        return (format[6])

    def issensor(self ,format):
        return (format[7])

    def getkey(self, hardware):
        retkey = None
        for key in list(self._hardware.keys()):
            if (self._hardware[key].lower() == hardware.lower()):
                retkey = key
                break
        return retkey


