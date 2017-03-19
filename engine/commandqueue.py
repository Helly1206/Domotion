# -*- coding: utf-8 -*-
#########################################################
# SERVICE : commandqueue.py                             #
#           Python commandqueue for Domotion            #
#           I. Helwegen 2017                            #
#########################################################
# Format tuple(Hardware{key}, SysCode, GroupCode, DeviceCode, URL/Device, Tag, Value, Sensor)

####################### IMPORTS #########################
from Queue import Queue

#########################################################

####################### GLOBALS #########################

#########################################################
# Class : commandqueue                                  #
#########################################################
class commandqueue(object):
    _hardware = {0: "None", 1: "Pi433MHz", 2: "Lirc", 3: "Url", 4: "Domoticz", 99: "Timer", 999: "Callback"}
    _queue = None
    def __init__(self):
        self.queue = Queue()
        self._initqueue(self.queue)

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
        return self.put(self.build_id(hardware, id, value, sensor))

    def put_code(self, hardware, syscode, groupcode, devicecode, value, sensor = True):
        return self.put(self.build_code(hardware, syscode, groupcode, devicecode, value, sensor))   

    def put_device(self, hardware, URL, Tag, value, sensor = True):
        return self.put(self.build_device(hardware, URL, Tag, value, sensor)) 

    def callback(self, type):
        return self.put(self.getkey("Callback"), 0, 0, 0, "", "", int(type), False)  

    def build_format(self, hardware, syscode, groupcode, devicecode, URL, Tag, value, sensor = True):
        return (self.getkey(hardware), syscode, groupcode, devicecode, URL, Tag, value, sensor)

    def build_id(self, hardware, id, value, sensor = True):
        return (self.getkey(hardware), 0, 0, id, "", "", value, sensor)

    def build_code(self, hardware, syscode, groupcode, devicecode, value, sensor = True):
        return (self.getkey(hardware), syscode, groupcode, devicecode, "", "", value, sensor)  

    def build_device(self, hardware, URL, Tag, value, sensor = True):
        return (self.getkey(hardware), 0, 0, 0, URL, Tag, value)

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

    def device(self, format): # URL
        return (format[4])

    def tag(self, format):
        return (format[5])

    def value(self, format):
        return (format[6])

    def issensor(self ,format):
        return (format[7])

    @classmethod
    def getkey(cls, hardware):
        retkey = None
        for key in cls._hardware.keys():
            if (cls._hardware[key].lower() == hardware.lower()):
                retkey = key
                break

        return retkey

    @classmethod
    def _initqueue(cls, queue):
        cls._queue = queue

    @classmethod
    def put_id2(cls, hardware, id, value, sensor = True):
        ivalue = 0
        try:
            ivalue = int(value)
        except ValueError:
            ivalue = float(value)
        if (cls._queue):
            cls._queue.put((cls.getkey(hardware), 0, 0, id, "", "", ivalue, sensor))
            return value
        else:
            return None

    @classmethod
    def callback2(cls, type):
        if (cls._queue):
            cls._queue.put((cls.getkey("Callback"), 0, 0, 0, type, "", 0, False))
            return type
        else:
            return None    
