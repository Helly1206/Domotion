# -*- coding: utf-8 -*-
#########################################################
# SERVICE : hw_pi433MHz.py                              #
#           Python pi433MHz handling for Domotion       #
#           I. Helwegen 2017                            #
#########################################################

####################### IMPORTS #########################
from threading import Thread, Event, Lock
import logging
from time import sleep
try:
    from Pi433MHzif import Pi433MHzif
    ifinstalled = True                     
except ImportError:
    ifinstalled = False
#########################################################

####################### GLOBALS #########################
sleeptime = 0.1
retrytime = 10 / sleeptime # test every 10s
retries = 10
maxsize = 4 # array size, for c array

#########################################################
# Class : hw_pi433MHz                                   #
#########################################################
class pi433MHz(Thread):
    def __init__(self, commandqueue):
        self.commandqueue=commandqueue
        self.logger = logging.getLogger('Domotion.Pi433MHz')
        Thread.__init__(self)
        self.term = Event()
        self.term.clear()
        self.mutex = Lock()
        if ifinstalled:
            self.client = Pi433MHzif()
        else:
            self.client = None
        self.Pi433MHzrunning = True # assume running
        
    def __del__(self):
        del self.mutex
        del self.term
        if self.client:
            del self.client
        self.logger.info("finished")

    def terminate(self):
            self.term.set()

    def run(self):
        try:
            testing = False
            testcnt = retrytime 
            testretries = retries 

            self.logger.info("running")

            if (not self.client):
                self.logger.warning("pi433MHzd not installed, terminating")
            else:
                while (not self.term.isSet() and (testretries>0)):
                    res, array = self.client.ReadMessage(maxsize)
                    if (testing):
                        sleep(sleeptime)
                        if (testcnt > 0):
                            testcnt -= 1
                        else:
                            testcnt = retrytime
                            if (res<0):
                                if (retries == testretries):
                                    self.logger.warning("pi433MHzd not running, retrying")
                                elif (testretries <= 1):
                                    self.logger.warning("pi433MHzd not running, terminating")
                                testretries -= 1
                            else:
                                testing = False
                                self.logger.info("pi433MHzd connection established")
                    if (not testing):
                        if (res<0):
                            self._IsPi433MHz(reset = True)
                            testing = True
                            testcnt = retrytime 
                            testretries = retries 
                        elif (res>0):
                            if (self.commandqueue):
                                syscode, groupcode, devicecode, value = self._array2code(array)
                                self.commandqueue.put_code("Pi433MHz", syscode, groupcode, devicecode, value)
                        else:
                            sleep(sleeptime)     

            self.logger.info("terminating")
        except Exception, e:
            self.logger.exception(e)

    def _IsPi433MHz(self, set = False, reset = False):
        self.mutex.acquire()
        if (not self.client):
            self.Pi433MHzrunning = False
        else:
            if (set):
                self.Pi433MHzrunning = True
            if (reset):
                self.Pi433MHzrunning = False
        self.mutex.release()
        return self.Pi433MHzrunning

    def send(self, syscode, groupcode, devicecode, value):
        res = -1
        if (self._IsPi433MHz()):
            array = self._code2array(syscode, groupcode, devicecode, value)
            res = self.client.WriteMessage(array, len(array))
            if (res<0):
                self._IsPi433MHz(reset = True)
        return res

    def _code2array(self, syscode, groupcode, devicecode, value):
        array = []
        if (syscode>0):
            array.append(syscode)
        if (groupcode>0):
            array.append(groupcode)
        array.append(devicecode)
        array.append(int(value))

        return array

    def _array2code(self, array):
        size = len(array)
        syscode = 0
        groupcode = 0
        devicecode = 0
        value = 0
        if (size == 2):
            devicecode = array[0]
            value = array[1] 
        else:
            syscode = array[0]
            if (size == 3):
                devicecode = array[1]
                value = array[2]  
            elif (size == 4):
                groupcode = array[1]
                devicecode = array[2]
                value = array[3] 

        return syscode, groupcode, devicecode, value
